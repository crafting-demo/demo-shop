package repository

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/google/uuid"
	pb "demoshop/transaction/gen/proto/demoshop/v1"
	"google.golang.org/protobuf/types/known/timestamppb"
)

type CartRepository interface {
	GetCart(ctx context.Context, id string) (*pb.Cart, error)
	CreateCart(ctx context.Context, cart *pb.Cart) (*pb.Cart, error)
	UpdateCart(ctx context.Context, cart *pb.Cart) (*pb.Cart, error)
	AddCartItem(ctx context.Context, cartID string, product *pb.Product, quantity int32) error
	UpdateCartItem(ctx context.Context, cartID, productID string, quantity int32) error
	RemoveCartItem(ctx context.Context, cartID, productID string) error
	ClearCart(ctx context.Context, cartID string) error
}

type PostgreSQLCartRepository struct {
	db *sql.DB
}

func NewPostgreSQLCartRepository(db *sql.DB) *PostgreSQLCartRepository {
	return &PostgreSQLCartRepository{db: db}
}

func (r *PostgreSQLCartRepository) GetCart(ctx context.Context, id string) (*pb.Cart, error) {
	tx, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	cartQuery := `
		SELECT id, created_at, updated_at
		FROM carts
		WHERE id = $1
	`

	var cart pb.Cart
	var createdAt, updatedAt time.Time

	err = tx.QueryRowContext(ctx, cartQuery, id).Scan(
		&cart.Id,
		&createdAt,
		&updatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, ErrCartNotFound
	}
	if err != nil {
		return nil, fmt.Errorf("failed to scan cart: %w", err)
	}

	itemsQuery := `
		SELECT ci.quantity, p.id, p.name, p.description, p.image_data, p.price_per_unit, p.count_in_stock, p.state, p.created_at, p.updated_at
		FROM cart_items ci
		JOIN products p ON ci.product_id = p.id
		WHERE ci.cart_id = $1 AND p.is_deleted = FALSE
		ORDER BY ci.created_at
	`

	rows, err := tx.QueryContext(ctx, itemsQuery, id)
	if err != nil {
		return nil, fmt.Errorf("failed to query cart items: %w", err)
	}
	defer rows.Close()

	var items []*pb.CartItem
	for rows.Next() {
		var item pb.CartItem
		var product pb.Product
		var productCreatedAt, productUpdatedAt time.Time
		var description sql.NullString
		var imageData []byte

		err := rows.Scan(
			&item.Quantity,
			&product.Id,
			&product.Name,
			&description,
			&imageData,
			&product.PricePerUnit,
			&product.CountInStock,
			&product.State,
			&productCreatedAt,
			&productUpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan cart item: %w", err)
		}

		if description.Valid {
			product.Description = description.String
		}
		if imageData != nil {
			product.ImageData = imageData
		}

		product.CreatedAt = timestamppb.New(productCreatedAt)
		product.UpdatedAt = timestamppb.New(productUpdatedAt)

		item.Product = &product
		items = append(items, &item)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("failed to iterate cart items: %w", err)
	}

	cart.Items = items
	cart.CreatedAt = timestamppb.New(createdAt)
	cart.UpdatedAt = timestamppb.New(updatedAt)

	if err = tx.Commit(); err != nil {
		return nil, fmt.Errorf("failed to commit transaction: %w", err)
	}

	return &cart, nil
}

func (r *PostgreSQLCartRepository) CreateCart(ctx context.Context, cart *pb.Cart) (*pb.Cart, error) {
	if cart.Id == "" {
		cart.Id = uuid.New().String()
	}

	query := `
		INSERT INTO carts (id)
		VALUES ($1)
		RETURNING created_at, updated_at
	`

	var createdAt, updatedAt time.Time
	err := r.db.QueryRowContext(ctx, query, cart.Id).Scan(&createdAt, &updatedAt)
	if err != nil {
		return nil, fmt.Errorf("failed to create cart: %w", err)
	}

	cart.CreatedAt = timestamppb.New(createdAt)
	cart.UpdatedAt = timestamppb.New(updatedAt)
	cart.Items = []*pb.CartItem{}

	return cart, nil
}

func (r *PostgreSQLCartRepository) UpdateCart(ctx context.Context, cart *pb.Cart) (*pb.Cart, error) {
	query := `
		UPDATE carts
		SET updated_at = NOW()
		WHERE id = $1
		RETURNING updated_at
	`

	var updatedAt time.Time
	err := r.db.QueryRowContext(ctx, query, cart.Id).Scan(&updatedAt)
	if err == sql.ErrNoRows {
		return nil, ErrCartNotFound
	}
	if err != nil {
		return nil, fmt.Errorf("failed to update cart: %w", err)
	}

	cart.UpdatedAt = timestamppb.New(updatedAt)
	return cart, nil
}

func (r *PostgreSQLCartRepository) AddCartItem(ctx context.Context, cartID string, product *pb.Product, quantity int32) error {
	query := `
		INSERT INTO cart_items (cart_id, product_id, quantity)
		VALUES ($1, $2, $3)
		ON CONFLICT (cart_id, product_id)
		DO UPDATE SET quantity = cart_items.quantity + $3, updated_at = NOW()
	`

	_, err := r.db.ExecContext(ctx, query, cartID, product.Id, quantity)
	if err != nil {
		return fmt.Errorf("failed to add cart item: %w", err)
	}

	_, err = r.db.ExecContext(ctx, "UPDATE carts SET updated_at = NOW() WHERE id = $1", cartID)
	if err != nil {
		return fmt.Errorf("failed to update cart timestamp: %w", err)
	}

	return nil
}

func (r *PostgreSQLCartRepository) UpdateCartItem(ctx context.Context, cartID, productID string, quantity int32) error {
	if quantity == 0 {
		return r.RemoveCartItem(ctx, cartID, productID)
	}

	query := `
		UPDATE cart_items
		SET quantity = $3, updated_at = NOW()
		WHERE cart_id = $1 AND product_id = $2
	`

	result, err := r.db.ExecContext(ctx, query, cartID, productID, quantity)
	if err != nil {
		return fmt.Errorf("failed to update cart item: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return ErrCartItemNotFound
	}

	_, err = r.db.ExecContext(ctx, "UPDATE carts SET updated_at = NOW() WHERE id = $1", cartID)
	if err != nil {
		return fmt.Errorf("failed to update cart timestamp: %w", err)
	}

	return nil
}

func (r *PostgreSQLCartRepository) RemoveCartItem(ctx context.Context, cartID, productID string) error {
	query := `
		DELETE FROM cart_items
		WHERE cart_id = $1 AND product_id = $2
	`

	result, err := r.db.ExecContext(ctx, query, cartID, productID)
	if err != nil {
		return fmt.Errorf("failed to remove cart item: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}

	if rowsAffected == 0 {
		return ErrCartItemNotFound
	}

	_, err = r.db.ExecContext(ctx, "UPDATE carts SET updated_at = NOW() WHERE id = $1", cartID)
	if err != nil {
		return fmt.Errorf("failed to update cart timestamp: %w", err)
	}

	return nil
}

func (r *PostgreSQLCartRepository) ClearCart(ctx context.Context, cartID string) error {
	query := `
		DELETE FROM cart_items
		WHERE cart_id = $1
	`

	_, err := r.db.ExecContext(ctx, query, cartID)
	if err != nil {
		return fmt.Errorf("failed to clear cart: %w", err)
	}

	_, err = r.db.ExecContext(ctx, "UPDATE carts SET updated_at = NOW() WHERE id = $1", cartID)
	if err != nil {
		return fmt.Errorf("failed to update cart timestamp: %w", err)
	}

	return nil
}

var (
	ErrCartNotFound     = fmt.Errorf("cart not found")
	ErrCartItemNotFound = fmt.Errorf("cart item not found")
)