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

type OrderRepository interface {
	GetOrder(ctx context.Context, id string) (*pb.Order, error)
	CreateOrder(ctx context.Context, order *pb.Order) (*pb.Order, error)
	UpdateOrder(ctx context.Context, order *pb.Order) (*pb.Order, error)
	QueryOrders(ctx context.Context, stateFilter *pb.Order_State, customerEmail string, limit int, after string) ([]*pb.Order, int32, error)
}

type PostgreSQLOrderRepository struct {
	db *sql.DB
}

func NewPostgreSQLOrderRepository(db *sql.DB) *PostgreSQLOrderRepository {
	return &PostgreSQLOrderRepository{db: db}
}

func (r *PostgreSQLOrderRepository) GetOrder(ctx context.Context, id string) (*pb.Order, error) {
	// Validate UUID format
	if _, err := uuid.Parse(id); err != nil {
		return nil, ErrOrderNotFound
	}

	tx, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	orderQuery := `
		SELECT id, total_amount, state, customer_name, customer_email, shipping_address, created_at, updated_at
		FROM orders
		WHERE id = $1
	`

	var order pb.Order
	var createdAt, updatedAt time.Time

	err = tx.QueryRowContext(ctx, orderQuery, id).Scan(
		&order.Id,
		&order.TotalAmount,
		&order.State,
		&order.CustomerName,
		&order.CustomerEmail,
		&order.ShippingAddress,
		&createdAt,
		&updatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, ErrOrderNotFound
	}
	if err != nil {
		return nil, fmt.Errorf("failed to scan order: %w", err)
	}

	itemsQuery := `
		SELECT oi.quantity, oi.price_at_purchase, oi.product_name, oi.product_description, oi.product_image_data, p.id, p.price_per_unit, p.count_in_stock, p.state, p.created_at, p.updated_at
		FROM order_items oi
		JOIN products p ON oi.product_id = p.id
		WHERE oi.order_id = $1
		ORDER BY oi.created_at
	`

	rows, err := tx.QueryContext(ctx, itemsQuery, id)
	if err != nil {
		return nil, fmt.Errorf("failed to query order items: %w", err)
	}
	defer rows.Close()

	var items []*pb.OrderItem
	for rows.Next() {
		var item pb.OrderItem
		var product pb.Product
		var productCreatedAt, productUpdatedAt time.Time
		var productDescription sql.NullString
		var productImageData []byte

		err := rows.Scan(
			&item.Quantity,
			&item.PriceAtPurchase,
			&product.Name,
			&productDescription,
			&productImageData,
			&product.Id,
			&product.PricePerUnit,
			&product.CountInStock,
			&product.State,
			&productCreatedAt,
			&productUpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan order item: %w", err)
		}

		if productDescription.Valid {
			product.Description = productDescription.String
		}
		if productImageData != nil {
			product.ImageData = productImageData
		}

		product.CreatedAt = timestamppb.New(productCreatedAt)
		product.UpdatedAt = timestamppb.New(productUpdatedAt)

		item.Product = &product
		items = append(items, &item)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("failed to iterate order items: %w", err)
	}

	order.Items = items
	order.CreatedAt = timestamppb.New(createdAt)
	order.UpdatedAt = timestamppb.New(updatedAt)

	if err = tx.Commit(); err != nil {
		return nil, fmt.Errorf("failed to commit transaction: %w", err)
	}

	return &order, nil
}

func (r *PostgreSQLOrderRepository) CreateOrder(ctx context.Context, order *pb.Order) (*pb.Order, error) {
	tx, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	if order.Id == "" {
		order.Id = uuid.New().String()
	}

	orderQuery := `
		INSERT INTO orders (id, total_amount, state, customer_name, customer_email, shipping_address)
		VALUES ($1, $2, $3, $4, $5, $6)
		RETURNING created_at, updated_at
	`

	var createdAt, updatedAt time.Time
	err = tx.QueryRowContext(ctx, orderQuery, order.Id, order.TotalAmount, order.State, 
		order.CustomerName, order.CustomerEmail, order.ShippingAddress).Scan(&createdAt, &updatedAt)
	if err != nil {
		return nil, fmt.Errorf("failed to create order: %w", err)
	}

	for _, item := range order.Items {
		itemQuery := `
			INSERT INTO order_items (order_id, product_id, product_name, product_description, product_image_data, quantity, price_at_purchase)
			VALUES ($1, $2, $3, $4, $5, $6, $7)
		`

		var description *string
		if item.Product.Description != "" {
			description = &item.Product.Description
		}

		var imageData []byte
		if len(item.Product.ImageData) > 0 {
			imageData = item.Product.ImageData
		}

		_, err = tx.ExecContext(ctx, itemQuery,
			order.Id,
			item.Product.Id,
			item.Product.Name,
			description,
			imageData,
			item.Quantity,
			item.PriceAtPurchase,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to create order item: %w", err)
		}
	}

	order.CreatedAt = timestamppb.New(createdAt)
	order.UpdatedAt = timestamppb.New(updatedAt)

	if err = tx.Commit(); err != nil {
		return nil, fmt.Errorf("failed to commit transaction: %w", err)
	}

	return order, nil
}

func (r *PostgreSQLOrderRepository) UpdateOrder(ctx context.Context, order *pb.Order) (*pb.Order, error) {
	query := `
		UPDATE orders
		SET state = $2
		WHERE id = $1
		RETURNING updated_at
	`

	var updatedAt time.Time
	err := r.db.QueryRowContext(ctx, query, order.Id, order.State).Scan(&updatedAt)
	if err == sql.ErrNoRows {
		return nil, ErrOrderNotFound
	}
	if err != nil {
		return nil, fmt.Errorf("failed to update order: %w", err)
	}

	order.UpdatedAt = timestamppb.New(updatedAt)
	return order, nil
}

func (r *PostgreSQLOrderRepository) QueryOrders(ctx context.Context, stateFilter *pb.Order_State, customerEmail string, limit int, after string) ([]*pb.Order, int32, error) {
	var args []interface{}
	whereClause := ""
	argIndex := 1

	if stateFilter != nil {
		whereClause = fmt.Sprintf("WHERE state = $%d", argIndex)
		args = append(args, *stateFilter)
		argIndex++
	}

	if customerEmail != "" {
		if whereClause == "" {
			whereClause = fmt.Sprintf("WHERE customer_email = $%d", argIndex)
		} else {
			whereClause += fmt.Sprintf(" AND customer_email = $%d", argIndex)
		}
		args = append(args, customerEmail)
		argIndex++
	}

	countQuery := fmt.Sprintf("SELECT COUNT(*) FROM orders %s", whereClause)

	var totalCount int32
	err := r.db.QueryRowContext(ctx, countQuery, args...).Scan(&totalCount)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to count orders: %w", err)
	}

	query := fmt.Sprintf(`
		SELECT id, total_amount, state, customer_name, customer_email, shipping_address, created_at, updated_at
		FROM orders
		%s
		ORDER BY created_at DESC
		LIMIT $%d
	`, whereClause, argIndex)

	args = append(args, limit)

	if after != "" {
		// Validate cursor is a UUID
		if _, err := uuid.Parse(after); err != nil {
			return nil, 0, fmt.Errorf("invalid cursor format: %w", err)
		}

		if whereClause == "" {
			whereClause = "WHERE"
		} else {
			whereClause += " AND"
		}
		
		// Rebuild args from scratch for cursor query
		baseArgs := []interface{}{}
		cursorArgIndex := 1
		
		if stateFilter != nil {
			baseArgs = append(baseArgs, *stateFilter)
			cursorArgIndex++
		}
		
		if customerEmail != "" {
			baseArgs = append(baseArgs, customerEmail)
			cursorArgIndex++
		}
		
		query = fmt.Sprintf(`
			SELECT id, total_amount, state, customer_name, customer_email, shipping_address, created_at, updated_at
			FROM orders
			%s created_at < (SELECT created_at FROM orders WHERE id = $%d::uuid)
			ORDER BY created_at DESC
			LIMIT $%d
		`, whereClause, cursorArgIndex, cursorArgIndex+1)
		
		args = append(baseArgs, after, limit)
	}

	rows, err := r.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to query orders: %w", err)
	}
	defer rows.Close()

	var orders []*pb.Order
	for rows.Next() {
		var order pb.Order
		var createdAt, updatedAt time.Time

		err := rows.Scan(
			&order.Id,
			&order.TotalAmount,
			&order.State,
			&order.CustomerName,
			&order.CustomerEmail,
			&order.ShippingAddress,
			&createdAt,
			&updatedAt,
		)
		if err != nil {
			return nil, 0, fmt.Errorf("failed to scan order: %w", err)
		}

		order.CreatedAt = timestamppb.New(createdAt)
		order.UpdatedAt = timestamppb.New(updatedAt)

		orders = append(orders, &order)
	}

	if err = rows.Err(); err != nil {
		return nil, 0, fmt.Errorf("failed to iterate orders: %w", err)
	}

	return orders, totalCount, nil
}

var ErrOrderNotFound = fmt.Errorf("order not found")
