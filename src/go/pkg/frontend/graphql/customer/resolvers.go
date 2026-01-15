package customer

// THIS CODE WILL BE UPDATED WITH SCHEMA CHANGES. PREVIOUS IMPLEMENTATION FOR SCHEMA CHANGES WILL BE KEPT IN THE COMMENT SECTION. IMPLEMENTATION FOR UNCHANGED SCHEMA WILL BE KEPT.

import (
	"context"
	"fmt"
	"regexp"

	demoshopv1 "demoshop/gen/proto/demoshop/v1"
	"demoshop/pkg/frontend"
	"demoshop/pkg/frontend/graphql/convert"
	"demoshop/pkg/frontend/graphql/types"
)

// Email validation regex
// Matches standard email format: local-part@domain
// - Local part: alphanumeric, dots, hyphens, underscores
// - Must have @ symbol
// - Domain: alphanumeric, dots, hyphens
// - Must have at least one dot in domain
var emailRegex = regexp.MustCompile(`^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$`)

type Resolver struct {
	app *frontend.App
}

func NewResolver(app *frontend.App) *Resolver {
	return &Resolver{app: app}
}

// getCartID retrieves the cart ID from context (set by middleware)
func (r *Resolver) getCartID(ctx context.Context) string {
	cartID, ok := ctx.Value("cartID").(string)
	if !ok || cartID == "" {
		// Return empty string if not found - caller should handle this
		return ""
	}
	return cartID
}

// AddToCart is the resolver for the addToCart field.
func (r *mutationResolver) AddToCart(ctx context.Context, input AddToCartInput) (*types.Cart, error) {
	cartID := r.getCartID(ctx)
	if cartID == "" {
		return nil, fmt.Errorf("no cart session found")
	}

	quantity := 1
	if input.Quantity != nil {
		quantity = *input.Quantity
	}

	resp, err := r.app.TransactionClient().CartService().AddProductToCart(ctx, &demoshopv1.AddProductToCartRequest{
		CartId:    cartID,
		ProductId: input.ProductID,
		Quantity:  int32(quantity),
	})
	if err != nil {
		return nil, fmt.Errorf("failed to add product to cart: %w", err)
	}

	return convert.CartFromProto(resp.Cart), nil
}

// UpdateCartItem is the resolver for the updateCartItem field.
func (r *mutationResolver) UpdateCartItem(ctx context.Context, input UpdateCartItemInput) (*types.Cart, error) {
	cartID := r.getCartID(ctx)
	if cartID == "" {
		return nil, fmt.Errorf("no cart session found")
	}

	resp, err := r.app.TransactionClient().CartService().UpdateProductInCart(ctx, &demoshopv1.UpdateProductInCartRequest{
		CartId:    cartID,
		ProductId: input.ProductID,
		Quantity:  int32(input.Quantity),
	})
	if err != nil {
		return nil, fmt.Errorf("failed to update cart item: %w", err)
	}

	return convert.CartFromProto(resp.Cart), nil
}

// RemoveFromCart is the resolver for the removeFromCart field.
func (r *mutationResolver) RemoveFromCart(ctx context.Context, productID string) (*types.Cart, error) {
	cartID := r.getCartID(ctx)
	if cartID == "" {
		return nil, fmt.Errorf("no cart session found")
	}

	// Remove by setting quantity to 0
	resp, err := r.app.TransactionClient().CartService().UpdateProductInCart(ctx, &demoshopv1.UpdateProductInCartRequest{
		CartId:    cartID,
		ProductId: productID,
		Quantity:  0,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to remove product from cart: %w", err)
	}

	return convert.CartFromProto(resp.Cart), nil
}

// ClearCart is the resolver for the clearCart field.
func (r *mutationResolver) ClearCart(ctx context.Context) (*types.Cart, error) {
	cartID := r.getCartID(ctx)
	if cartID == "" {
		return nil, fmt.Errorf("no cart session found")
	}

	_, err := r.app.TransactionClient().CartService().ClearCart(ctx, &demoshopv1.ClearCartRequest{
		CartId: cartID,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to clear cart: %w", err)
	}

	// Return empty cart
	return &types.Cart{
		ID:         cartID,
		Items:      []*types.CartItem{},
		TotalPrice: 0,
	}, nil
}

// PlaceOrder is the resolver for the placeOrder field.
func (r *mutationResolver) PlaceOrder(ctx context.Context, input PlaceOrderInput) (*types.Order, error) {
	// Validate input
	if input.CustomerName == "" {
		return nil, fmt.Errorf("customer name is required")
	}
	if input.CustomerEmail == "" {
		return nil, fmt.Errorf("customer email is required")
	}
	// Validate email format using regex
	if !emailRegex.MatchString(input.CustomerEmail) {
		return nil, fmt.Errorf("invalid email format")
	}
	if input.ShippingAddress == "" {
		return nil, fmt.Errorf("shipping address is required")
	}

	cartID := r.getCartID(ctx)
	if cartID == "" {
		return nil, fmt.Errorf("no cart session found")
	}

	resp, err := r.app.TransactionClient().OrderService().CreateOrder(ctx, &demoshopv1.CreateOrderRequest{
		CartId:          cartID,
		CustomerName:    input.CustomerName,
		CustomerEmail:   input.CustomerEmail,
		ShippingAddress: input.ShippingAddress,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create order: %w", err)
	}

	// Clear the cart after placing order
	_, _ = r.app.TransactionClient().CartService().ClearCart(ctx, &demoshopv1.ClearCartRequest{
		CartId: cartID,
	})

	return convert.OrderFromProto(resp.Order, input.CustomerName, input.CustomerEmail, input.ShippingAddress), nil
}

// Products is the resolver for the products field.
func (r *queryResolver) Products(ctx context.Context, first *int, after *string) (*types.ProductConnection, error) {
	limit := 20
	if first != nil {
		limit = *first
	}

	cursor := ""
	if after != nil {
		cursor = *after
	}

	// Query only AVAILABLE products
	resp, err := r.app.TransactionClient().InventoryService().QueryProducts(ctx, &demoshopv1.QueryProductsRequest{
		Pagination: &demoshopv1.PaginationRequest{
			First: int32(limit),
			After: cursor,
		},
		StateFilter: demoshopv1.Product_AVAILABLE,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to query products: %w", err)
	}

	edges := make([]*types.ProductEdge, 0, len(resp.Products))
	for _, product := range resp.Products {
		// Filter out products with no stock
		if product.CountInStock > 0 {
			edges = append(edges, &types.ProductEdge{
				Node:   convert.ProductFromProto(product),
				Cursor: product.Id,
			})
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

// Cart is the resolver for the cart field.
func (r *queryResolver) Cart(ctx context.Context) (*types.Cart, error) {
	cartID := r.getCartID(ctx)
	if cartID == "" {
		return nil, fmt.Errorf("no cart session found")
	}

	resp, err := r.app.TransactionClient().CartService().GetCart(ctx, &demoshopv1.GetCartRequest{
		CartId: cartID,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to get cart: %w", err)
	}

	return convert.CartFromProto(resp.Cart), nil
}

// Mutation returns MutationResolver implementation.
func (r *Resolver) Mutation() MutationResolver { return &mutationResolver{r} }

// Query returns QueryResolver implementation.
func (r *Resolver) Query() QueryResolver { return &queryResolver{r} }

type mutationResolver struct{ *Resolver }
type queryResolver struct{ *Resolver }
