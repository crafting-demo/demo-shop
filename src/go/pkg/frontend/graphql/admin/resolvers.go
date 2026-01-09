package admin

// THIS CODE WILL BE UPDATED WITH SCHEMA CHANGES. PREVIOUS IMPLEMENTATION FOR SCHEMA CHANGES WILL BE KEPT IN THE COMMENT SECTION. IMPLEMENTATION FOR UNCHANGED SCHEMA WILL BE KEPT.

import (
	"context"
	"fmt"

	demoshopv1 "demoshop/gen/proto/demoshop/v1"
	"demoshop/pkg/frontend"
	"demoshop/pkg/frontend/graphql/convert"
	"demoshop/pkg/frontend/graphql/types"
)

type Resolver struct {
	app *frontend.App
}

func NewResolver(app *frontend.App) *Resolver {
	return &Resolver{app: app}
}

// CreateProduct is the resolver for the createProduct field.
func (r *mutationResolver) CreateProduct(ctx context.Context, input CreateProductInput) (*types.Product, error) {
	state := demoshopv1.Product_AVAILABLE
	if input.State != nil {
		state = convert.ProductStateToProto(*input.State)
	}

	resp, err := r.app.TransactionClient().InventoryService().CreateProduct(ctx, &demoshopv1.CreateProductRequest{
		Name:         input.Name,
		Description:  stringValue(input.Description),
		ImageData:    convert.DataURIToImageData(input.ImageData),
		PricePerUnit: int64(input.PricePerUnit),
		CountInStock: int32(input.CountInStock),
		State:        state,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create product: %w", err)
	}

	return convert.ProductFromProto(resp.Product), nil
}

// UpdateProduct is the resolver for the updateProduct field.
func (r *mutationResolver) UpdateProduct(ctx context.Context, input UpdateProductInput) (*types.Product, error) {
	req := &demoshopv1.UpdateProductRequest{
		Id: input.ID,
	}

	if input.Name != nil {
		req.Name = &demoshopv1.UpdateProductRequest_NameUpdate{
			Value: *input.Name,
		}
	}

	if input.Description != nil {
		req.Description = &demoshopv1.UpdateProductRequest_DescriptionUpdate{
			Value: *input.Description,
		}
	}

	if input.ImageData != nil {
		req.ImageData = &demoshopv1.UpdateProductRequest_ImageDataUpdate{
			Value: convert.DataURIToImageData(input.ImageData),
		}
	}

	if input.PricePerUnit != nil {
		req.PricePerUnit = &demoshopv1.UpdateProductRequest_PricePerUnitUpdate{
			Value: int64(*input.PricePerUnit),
		}
	}

	if input.CountInStock != nil {
		req.CountInStock = &demoshopv1.UpdateProductRequest_CountInStockUpdate{
			Value: int32(*input.CountInStock),
		}
	}

	if input.State != nil {
		req.State = &demoshopv1.UpdateProductRequest_StateUpdate{
			Value: convert.ProductStateToProto(*input.State),
		}
	}

	resp, err := r.app.TransactionClient().InventoryService().UpdateProduct(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("failed to update product: %w", err)
	}

	return convert.ProductFromProto(resp.Product), nil
}

// PutProductOnShelf is the resolver for the putProductOnShelf field.
func (r *mutationResolver) PutProductOnShelf(ctx context.Context, id string) (*types.Product, error) {
	resp, err := r.app.TransactionClient().InventoryService().UpdateProduct(ctx, &demoshopv1.UpdateProductRequest{
		Id: id,
		State: &demoshopv1.UpdateProductRequest_StateUpdate{
			Value: demoshopv1.Product_AVAILABLE,
		},
	})
	if err != nil {
		return nil, fmt.Errorf("failed to put product on shelf: %w", err)
	}

	return convert.ProductFromProto(resp.Product), nil
}

// TakeProductOffShelf is the resolver for the takeProductOffShelf field.
func (r *mutationResolver) TakeProductOffShelf(ctx context.Context, id string) (*types.Product, error) {
	resp, err := r.app.TransactionClient().InventoryService().UpdateProduct(ctx, &demoshopv1.UpdateProductRequest{
		Id: id,
		State: &demoshopv1.UpdateProductRequest_StateUpdate{
			Value: demoshopv1.Product_OFF_SHELF,
		},
	})
	if err != nil {
		return nil, fmt.Errorf("failed to take product off shelf: %w", err)
	}

	return convert.ProductFromProto(resp.Product), nil
}

// RemoveProduct is the resolver for the removeProduct field.
func (r *mutationResolver) RemoveProduct(ctx context.Context, id string) (bool, error) {
	_, err := r.app.TransactionClient().InventoryService().DeleteProduct(ctx, &demoshopv1.DeleteProductRequest{
		Id: id,
	})
	if err != nil {
		return false, fmt.Errorf("failed to remove product: %w", err)
	}

	return true, nil
}

// ShipOrder is the resolver for the shipOrder field.
func (r *mutationResolver) ShipOrder(ctx context.Context, id string) (*types.Order, error) {
	resp, err := r.app.TransactionClient().OrderService().UpdateOrder(ctx, &demoshopv1.UpdateOrderRequest{
		Id:    id,
		State: demoshopv1.Order_SHIPPED,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to ship order: %w", err)
	}

	// Note: Order proto doesn't have customer info, we need to fetch it separately or store it
	// For now, we'll use placeholder values. In production, you'd store this info with the order.
	return convert.OrderFromProto(resp.Order, "", "", ""), nil
}

// CompleteOrder is the resolver for the completeOrder field.
func (r *mutationResolver) CompleteOrder(ctx context.Context, id string) (*types.Order, error) {
	resp, err := r.app.TransactionClient().OrderService().UpdateOrder(ctx, &demoshopv1.UpdateOrderRequest{
		Id:    id,
		State: demoshopv1.Order_COMPLETED,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to complete order: %w", err)
	}

	return convert.OrderFromProto(resp.Order, "", "", ""), nil
}

// CancelOrder is the resolver for the cancelOrder field.
func (r *mutationResolver) CancelOrder(ctx context.Context, id string) (*types.Order, error) {
	resp, err := r.app.TransactionClient().OrderService().UpdateOrder(ctx, &demoshopv1.UpdateOrderRequest{
		Id:    id,
		State: demoshopv1.Order_CANCELED,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to cancel order: %w", err)
	}

	return convert.OrderFromProto(resp.Order, "", "", ""), nil
}

// Products is the resolver for the products field.
func (r *queryResolver) Products(ctx context.Context, first *int, after *string, filter *ProductFilterInput) (*types.ProductConnection, error) {
	limit := 20
	if first != nil {
		limit = *first
	}

	cursor := ""
	if after != nil {
		cursor = *after
	}

	req := &demoshopv1.QueryProductsRequest{
		Pagination: &demoshopv1.PaginationRequest{
			First: int32(limit),
			After: cursor,
		},
	}

	// Apply filters
	if filter != nil && filter.State != nil {
		req.StateFilter = convert.ProductStateToProto(*filter.State)
	}

	resp, err := r.app.TransactionClient().InventoryService().QueryProducts(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("failed to query products: %w", err)
	}

	edges := make([]*types.ProductEdge, len(resp.Products))
	for i, product := range resp.Products {
		cursor := fmt.Sprintf("product_%d", i)
		edges[i] = &types.ProductEdge{
			Node:   convert.ProductFromProto(product),
			Cursor: cursor,
		}
	}

	var startCursor, endCursor *string
	if len(edges) > 0 {
		startCursor = &edges[0].Cursor
		endCursor = &edges[len(edges)-1].Cursor
	}

	return &types.ProductConnection{
		Edges: edges,
		PageInfo: &types.PageInfo{
			HasNextPage:     resp.PageInfo.HasNextPage,
			HasPreviousPage: resp.PageInfo.HasPreviousPage,
			StartCursor:     startCursor,
			EndCursor:       endCursor,
			TotalCount:      int(resp.TotalCount),
		},
	}, nil
}

// Product is the resolver for the product field.
func (r *queryResolver) Product(ctx context.Context, id string) (*types.Product, error) {
	resp, err := r.app.TransactionClient().InventoryService().GetProduct(ctx, &demoshopv1.GetProductRequest{
		Id: id,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to get product: %w", err)
	}

	return convert.ProductFromProto(resp.Product), nil
}

// Orders is the resolver for the orders field.
func (r *queryResolver) Orders(ctx context.Context, first *int, after *string, filter *OrderFilterInput) (*types.OrderConnection, error) {
	limit := 20
	if first != nil {
		limit = *first
	}

	cursor := ""
	if after != nil {
		cursor = *after
	}

	req := &demoshopv1.QueryOrdersRequest{
		Pagination: &demoshopv1.PaginationRequest{
			First: int32(limit),
			After: cursor,
		},
	}

	// Apply filters
	if filter != nil && filter.State != nil {
		req.StateFilter = &demoshopv1.QueryOrdersRequest_StateFilter{
			Value: convert.OrderStateToProto(*filter.State),
		}
	}

	resp, err := r.app.TransactionClient().OrderService().QueryOrders(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("failed to query orders: %w", err)
	}

	edges := make([]*types.OrderEdge, len(resp.Orders))
	for i, order := range resp.Orders {
		cursor := fmt.Sprintf("order_%d", i)
		edges[i] = &types.OrderEdge{
			Node:   convert.OrderFromProto(order, "", "", ""),
			Cursor: cursor,
		}
	}

	var startCursor, endCursor *string
	if len(edges) > 0 {
		startCursor = &edges[0].Cursor
		endCursor = &edges[len(edges)-1].Cursor
	}

	return &types.OrderConnection{
		Edges: edges,
		PageInfo: &types.PageInfo{
			HasNextPage:     resp.PageInfo.HasNextPage,
			HasPreviousPage: resp.PageInfo.HasPreviousPage,
			StartCursor:     startCursor,
			EndCursor:       endCursor,
			TotalCount:      int(resp.TotalCount),
		},
	}, nil
}

// Order is the resolver for the order field.
func (r *queryResolver) Order(ctx context.Context, id string) (*types.Order, error) {
	resp, err := r.app.TransactionClient().OrderService().GetOrder(ctx, &demoshopv1.GetOrderRequest{
		Id: id,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to get order: %w", err)
	}

	return convert.OrderFromProto(resp.Order, "", "", ""), nil
}

// Mutation returns MutationResolver implementation.
func (r *Resolver) Mutation() MutationResolver { return &mutationResolver{r} }

// Query returns QueryResolver implementation.
func (r *Resolver) Query() QueryResolver { return &queryResolver{r} }

type mutationResolver struct{ *Resolver }
type queryResolver struct{ *Resolver }

func stringValue(s *string) string {
	if s == nil {
		return ""
	}
	return *s
}
