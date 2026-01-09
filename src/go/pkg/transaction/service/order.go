package service

import (
	"context"

	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	pb "demoshop/gen/proto/demoshop/v1"
	"demoshop/pkg/transaction/repository"
)

type OrderServer struct {
	pb.UnimplementedOrderServiceServer
	orderRepo repository.OrderRepository
	cartRepo  repository.CartRepository
}

func NewOrderServer(orderRepo repository.OrderRepository, cartRepo repository.CartRepository) *OrderServer {
	return &OrderServer{
		orderRepo: orderRepo,
		cartRepo:  cartRepo,
	}
}

func (s *OrderServer) CreateOrder(ctx context.Context, req *pb.CreateOrderRequest) (*pb.CreateOrderResponse, error) {
	cart, err := s.cartRepo.GetCart(ctx, req.CartId)
	if err == repository.ErrCartNotFound {
		return nil, status.Errorf(codes.NotFound, "cart with id %s not found", req.CartId)
	}
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to get cart: %v", err)
	}

	if len(cart.Items) == 0 {
		return nil, status.Errorf(codes.FailedPrecondition, "cart %s is empty", req.CartId)
	}

	var orderItems []*pb.OrderItem
	var totalAmount int64

	for _, cartItem := range cart.Items {
		orderItem := &pb.OrderItem{
			Product:         cartItem.Product,
			Quantity:        cartItem.Quantity,
			PriceAtPurchase: cartItem.Product.PricePerUnit,
		}
		orderItems = append(orderItems, orderItem)
		totalAmount += cartItem.Product.PricePerUnit * int64(cartItem.Quantity)
	}

	order := &pb.Order{
		Items:       orderItems,
		TotalAmount: totalAmount,
		State:       pb.Order_PROCESSING,
	}

	createdOrder, err := s.orderRepo.CreateOrder(ctx, order)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to create order: %v", err)
	}

	err = s.cartRepo.ClearCart(ctx, req.CartId)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to clear cart: %v", err)
	}

	return &pb.CreateOrderResponse{
		Order: createdOrder,
	}, nil
}

func (s *OrderServer) QueryOrders(ctx context.Context, req *pb.QueryOrdersRequest) (*pb.QueryOrdersResponse, error) {
	first := int(req.Pagination.First)
	if first <= 0 {
		first = 20
	}

	var stateFilter *pb.Order_State
	if req.StateFilter != nil {
		stateFilter = &req.StateFilter.Value
	}

	orders, totalCount, err := s.orderRepo.QueryOrders(ctx, stateFilter, first, req.Pagination.After)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to query orders: %v", err)
	}

	pageInfo := &pb.PageInfo{
		HasNextPage:     len(orders) == first,
		HasPreviousPage: req.Pagination.After != "",
	}

	if len(orders) > 0 {
		pageInfo.StartCursor = orders[0].Id
		pageInfo.EndCursor = orders[len(orders)-1].Id
	}

	return &pb.QueryOrdersResponse{
		Orders:     orders,
		PageInfo:   pageInfo,
		TotalCount: totalCount,
	}, nil
}

func (s *OrderServer) GetOrder(ctx context.Context, req *pb.GetOrderRequest) (*pb.GetOrderResponse, error) {
	order, err := s.orderRepo.GetOrder(ctx, req.Id)
	if err == repository.ErrOrderNotFound {
		return nil, status.Errorf(codes.NotFound, "order with id %s not found", req.Id)
	}
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to get order: %v", err)
	}

	return &pb.GetOrderResponse{
		Order: order,
	}, nil
}

func (s *OrderServer) UpdateOrder(ctx context.Context, req *pb.UpdateOrderRequest) (*pb.UpdateOrderResponse, error) {
	order, err := s.orderRepo.GetOrder(ctx, req.Id)
	if err == repository.ErrOrderNotFound {
		return nil, status.Errorf(codes.NotFound, "order with id %s not found", req.Id)
	}
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to get order: %v", err)
	}

	if !s.isValidStateTransition(order.State, req.State) {
		return nil, status.Errorf(codes.FailedPrecondition,
			"invalid state transition from %s to %s", order.State, req.State)
	}

	order.State = req.State
	updatedOrder, err := s.orderRepo.UpdateOrder(ctx, order)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to update order: %v", err)
	}

	return &pb.UpdateOrderResponse{
		Order: updatedOrder,
	}, nil
}

func (s *OrderServer) isValidStateTransition(current, next pb.Order_State) bool {
	switch current {
	case pb.Order_PROCESSING:
		return next == pb.Order_SHIPPED || next == pb.Order_CANCELED
	case pb.Order_SHIPPED:
		return next == pb.Order_COMPLETED || next == pb.Order_CANCELED
	case pb.Order_COMPLETED, pb.Order_CANCELED:
		return false
	default:
		return false
	}
}
