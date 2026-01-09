package repository

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/google/uuid"
	"google.golang.org/protobuf/types/known/timestamppb"

	pb "demoshop/gen/proto/demoshop/v1"
)

type ProductRepository interface {
	GetProduct(ctx context.Context, id string) (*pb.Product, error)
	CreateProduct(ctx context.Context, product *pb.Product) (*pb.Product, error)
	UpdateProduct(ctx context.Context, product *pb.Product) (*pb.Product, error)
	DeleteProduct(ctx context.Context, id string) error
	QueryProducts(ctx context.Context, stateFilter pb.Product_State, limit int, after string) ([]*pb.Product, int32, error)
}

type PostgreSQLProductRepository struct {
	db *sql.DB
}

func NewPostgreSQLProductRepository(db *sql.DB) *PostgreSQLProductRepository {
	return &PostgreSQLProductRepository{db: db}
}

func (r *PostgreSQLProductRepository) GetProduct(ctx context.Context, id string) (*pb.Product, error) {
	query := `
		SELECT id, name, description, image_data, price_per_unit, count_in_stock, state, created_at, updated_at
		FROM products
		WHERE id = $1 AND is_deleted = FALSE
	`

	row := r.db.QueryRowContext(ctx, query, id)

	var product pb.Product
	var createdAt, updatedAt time.Time
	var description sql.NullString
	var imageData []byte

	err := row.Scan(
		&product.Id,
		&product.Name,
		&description,
		&imageData,
		&product.PricePerUnit,
		&product.CountInStock,
		&product.State,
		&createdAt,
		&updatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, ErrProductNotFound
	}
	if err != nil {
		return nil, fmt.Errorf("failed to scan product: %w", err)
	}

	if description.Valid {
		product.Description = description.String
	}
	if imageData != nil {
		product.ImageData = imageData
	}

	product.CreatedAt = timestamppb.New(createdAt)
	product.UpdatedAt = timestamppb.New(updatedAt)

	return &product, nil
}

func (r *PostgreSQLProductRepository) CreateProduct(ctx context.Context, product *pb.Product) (*pb.Product, error) {
	if product.Id == "" {
		product.Id = uuid.New().String()
	}

	query := `
		INSERT INTO products (id, name, description, image_data, price_per_unit, count_in_stock, state)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
		RETURNING created_at, updated_at
	`

	var description *string
	if product.Description != "" {
		description = &product.Description
	}

	var imageData []byte
	if len(product.ImageData) > 0 {
		imageData = product.ImageData
	}

	var createdAt, updatedAt time.Time
	err := r.db.QueryRowContext(ctx, query,
		product.Id,
		product.Name,
		description,
		imageData,
		product.PricePerUnit,
		product.CountInStock,
		product.State,
	).Scan(&createdAt, &updatedAt)

	if err != nil {
		return nil, fmt.Errorf("failed to create product: %w", err)
	}

	product.CreatedAt = timestamppb.New(createdAt)
	product.UpdatedAt = timestamppb.New(updatedAt)

	return product, nil
}

func (r *PostgreSQLProductRepository) UpdateProduct(ctx context.Context, product *pb.Product) (*pb.Product, error) {
	query := `
		UPDATE products
		SET name = $2, description = $3, image_data = $4, price_per_unit = $5, count_in_stock = $6, state = $7
		WHERE id = $1 AND is_deleted = FALSE
		RETURNING updated_at
	`

	var description *string
	if product.Description != "" {
		description = &product.Description
	}

	var imageData []byte
	if len(product.ImageData) > 0 {
		imageData = product.ImageData
	}

	var updatedAt time.Time
	err := r.db.QueryRowContext(ctx, query,
		product.Id,
		product.Name,
		description,
		imageData,
		product.PricePerUnit,
		product.CountInStock,
		product.State,
	).Scan(&updatedAt)

	if err == sql.ErrNoRows {
		return nil, ErrProductNotFound
	}
	if err != nil {
		return nil, fmt.Errorf("failed to update product: %w", err)
	}

	product.UpdatedAt = timestamppb.New(updatedAt)

	return product, nil
}

func (r *PostgreSQLProductRepository) DeleteProduct(ctx context.Context, id string) error {
	query := `
		UPDATE products
		SET state = $2, is_deleted = TRUE
		WHERE id = $1 AND is_deleted = FALSE
	`

	result, err := r.db.ExecContext(ctx, query, id, pb.Product_OFF_SHELF)
	if err != nil {
		return fmt.Errorf("failed to delete product: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return ErrProductNotFound
	}

	return nil
}

func (r *PostgreSQLProductRepository) QueryProducts(ctx context.Context, stateFilter pb.Product_State, limit int, after string) ([]*pb.Product, int32, error) {
	var args []interface{}
	whereClause := "WHERE is_deleted = FALSE"

	if stateFilter != pb.Product_UNSPECIFIED {
		whereClause += " AND state = $1"
		args = append(args, stateFilter)
	}

	countQuery := fmt.Sprintf("SELECT COUNT(*) FROM products %s", whereClause)

	var totalCount int32
	err := r.db.QueryRowContext(ctx, countQuery, args...).Scan(&totalCount)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to count products: %w", err)
	}

	query := fmt.Sprintf(`
		SELECT id, name, description, image_data, price_per_unit, count_in_stock, state, created_at, updated_at
		FROM products
		%s
		ORDER BY created_at DESC
		LIMIT $%d
	`, whereClause, len(args)+1)

	args = append(args, limit)

	if after != "" {
		query = fmt.Sprintf(`
			SELECT id, name, description, image_data, price_per_unit, count_in_stock, state, created_at, updated_at
			FROM products
			%s AND created_at < (SELECT created_at FROM products WHERE id = $%d)
			ORDER BY created_at DESC
			LIMIT $%d
		`, whereClause, len(args)+1, len(args)+2)
		args = append(args, after, limit)
	}

	rows, err := r.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to query products: %w", err)
	}
	defer rows.Close()

	var products []*pb.Product
	for rows.Next() {
		var product pb.Product
		var createdAt, updatedAt time.Time
		var description sql.NullString
		var imageData []byte

		err := rows.Scan(
			&product.Id,
			&product.Name,
			&description,
			&imageData,
			&product.PricePerUnit,
			&product.CountInStock,
			&product.State,
			&createdAt,
			&updatedAt,
		)
		if err != nil {
			return nil, 0, fmt.Errorf("failed to scan product: %w", err)
		}

		if description.Valid {
			product.Description = description.String
		}
		if imageData != nil {
			product.ImageData = imageData
		}

		product.CreatedAt = timestamppb.New(createdAt)
		product.UpdatedAt = timestamppb.New(updatedAt)

		products = append(products, &product)
	}

	if err = rows.Err(); err != nil {
		return nil, 0, fmt.Errorf("failed to iterate products: %w", err)
	}

	return products, totalCount, nil
}

var ErrProductNotFound = fmt.Errorf("product not found")
