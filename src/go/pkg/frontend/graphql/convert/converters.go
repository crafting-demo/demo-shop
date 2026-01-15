package convert

import (
	"encoding/base64"
	"fmt"

	demoshopv1 "demoshop/gen/proto/demoshop/v1"
	"demoshop/pkg/frontend/graphql/types"
)

// ProductStateToProto converts GraphQL ProductState to proto Product_State
func ProductStateToProto(state types.ProductState) demoshopv1.Product_State {
	switch state {
	case types.ProductStateAvailable:
		return demoshopv1.Product_AVAILABLE
	case types.ProductStateOffShelf:
		return demoshopv1.Product_OFF_SHELF
	default:
		return demoshopv1.Product_UNSPECIFIED
	}
}

// ProductStateFromProto converts proto Product_State to GraphQL ProductState
func ProductStateFromProto(state demoshopv1.Product_State) types.ProductState {
	switch state {
	case demoshopv1.Product_AVAILABLE:
		return types.ProductStateAvailable
	case demoshopv1.Product_OFF_SHELF:
		return types.ProductStateOffShelf
	default:
		return types.ProductStateAvailable
	}
}

// OrderStateToProto converts GraphQL OrderState to proto Order_State
func OrderStateToProto(state types.OrderState) demoshopv1.Order_State {
	switch state {
	case types.OrderStateProcessing:
		return demoshopv1.Order_PROCESSING
	case types.OrderStateShipped:
		return demoshopv1.Order_SHIPPED
	case types.OrderStateCompleted:
		return demoshopv1.Order_COMPLETED
	case types.OrderStateCanceled:
		return demoshopv1.Order_CANCELED
	default:
		return demoshopv1.Order_UNSPECIFIED
	}
}

// OrderStateFromProto converts proto Order_State to GraphQL OrderState
func OrderStateFromProto(state demoshopv1.Order_State) types.OrderState {
	switch state {
	case demoshopv1.Order_PROCESSING:
		return types.OrderStateProcessing
	case demoshopv1.Order_SHIPPED:
		return types.OrderStateShipped
	case demoshopv1.Order_COMPLETED:
		return types.OrderStateCompleted
	case demoshopv1.Order_CANCELED:
		return types.OrderStateCanceled
	default:
		return types.OrderStateProcessing
	}
}

// ImageDataToDataURI converts image bytes to a data URI string
func ImageDataToDataURI(imageData []byte) *string {
	if len(imageData) == 0 {
		return nil
	}
	// For simplicity, assume PNG format. In production, you'd want to detect the actual format
	encoded := base64.StdEncoding.EncodeToString(imageData)
	dataURI := fmt.Sprintf("data:image/png;base64,%s", encoded)
	return &dataURI
}

// DataURIToImageData converts a data URI string to image bytes
func DataURIToImageData(dataURI *string) []byte {
	if dataURI == nil || *dataURI == "" {
		return nil
	}
	// Parse data URI (e.g., "data:image/png;base64,...")
	// Simple implementation - in production you'd want more robust parsing
	prefix := "data:image/"
	if len(*dataURI) < len(prefix) {
		return nil
	}

	// Find the base64 data after the comma
	for i := len(prefix); i < len(*dataURI); i++ {
		if (*dataURI)[i] == ',' {
			encoded := (*dataURI)[i+1:]
			decoded, err := base64.StdEncoding.DecodeString(encoded)
			if err != nil {
				return nil
			}
			return decoded
		}
	}
	return nil
}

// ProductFromProto converts proto Product to GraphQL Product
func ProductFromProto(p *demoshopv1.Product) *types.Product {
	if p == nil {
		return nil
	}

	return &types.Product{
		ID:           p.Id,
		Name:         p.Name,
		Description:  stringPtr(p.Description),
		ImageData:    ImageDataToDataURI(p.ImageData),
		PricePerUnit: int(p.PricePerUnit),
		CountInStock: int(p.CountInStock),
		State:        ProductStateFromProto(p.State),
		CreatedAt:    p.CreatedAt.AsTime(),
		UpdatedAt:    p.UpdatedAt.AsTime(),
	}
}

// CartItemFromProto converts proto CartItem to GraphQL CartItem
func CartItemFromProto(ci *demoshopv1.CartItem) *types.CartItem {
	if ci == nil {
		return nil
	}

	product := ProductFromProto(ci.Product)
	totalPrice := int(product.PricePerUnit) * int(ci.Quantity)

	return &types.CartItem{
		Product:    product,
		Quantity:   int(ci.Quantity),
		TotalPrice: totalPrice,
	}
}

// CartFromProto converts proto Cart to GraphQL Cart
func CartFromProto(c *demoshopv1.Cart) *types.Cart {
	if c == nil {
		return nil
	}

	items := make([]*types.CartItem, len(c.Items))
	totalPrice := 0
	for i, item := range c.Items {
		items[i] = CartItemFromProto(item)
		totalPrice += items[i].TotalPrice
	}

	return &types.Cart{
		ID:         c.Id,
		Items:      items,
		TotalPrice: totalPrice,
	}
}

// OrderItemFromProto converts proto OrderItem to GraphQL OrderItem
func OrderItemFromProto(oi *demoshopv1.OrderItem) *types.OrderItem {
	if oi == nil {
		return nil
	}

	return &types.OrderItem{
		Product:    ProductFromProto(oi.Product),
		Quantity:   int(oi.Quantity),
		TotalPrice: int(oi.PriceAtPurchase) * int(oi.Quantity),
	}
}

// OrderFromProto converts proto Order to GraphQL Order with customer info
func OrderFromProto(o *demoshopv1.Order, customerName, customerEmail, shippingAddress string) *types.Order {
	if o == nil {
		return nil
	}

	items := make([]*types.OrderItem, len(o.Items))
	for i, item := range o.Items {
		items[i] = OrderItemFromProto(item)
	}

	// Use proto fields if available, otherwise fall back to parameters (for compatibility)
	name := o.CustomerName
	if name == "" {
		name = customerName
	}
	email := o.CustomerEmail
	if email == "" {
		email = customerEmail
	}
	address := o.ShippingAddress
	if address == "" {
		address = shippingAddress
	}

	return &types.Order{
		ID:              o.Id,
		CustomerName:    name,
		CustomerEmail:   email,
		ShippingAddress: address,
		Items:           items,
		TotalPrice:      int(o.TotalAmount),
		State:           OrderStateFromProto(o.State),
		CreatedAt:       o.CreatedAt.AsTime(),
		UpdatedAt:       o.UpdatedAt.AsTime(),
	}
}

func stringPtr(s string) *string {
	if s == "" {
		return nil
	}
	return &s
}
