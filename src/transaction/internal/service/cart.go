package service

import (
	"context"

	pb "demoshop/transaction/gen/proto/demoshop/v1"
	"demoshop/transaction/internal/repository"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type CartServer struct {
	pb.UnimplementedCartServiceServer
	cartRepo    repository.CartRepository
	productRepo repository.ProductRepository
}

func NewCartServer(cartRepo repository.CartRepository, productRepo repository.ProductRepository) *CartServer {
	return &CartServer{
		cartRepo:    cartRepo,
		productRepo: productRepo,
	}
}

func (s *CartServer) GetCart(ctx context.Context, req *pb.GetCartRequest) (*pb.GetCartResponse, error) {
	cart, err := s.cartRepo.GetCart(ctx, req.CartId)
	if err == repository.ErrCartNotFound {
		cart = &pb.Cart{Id: req.CartId}
		cart, err = s.cartRepo.CreateCart(ctx, cart)
		if err != nil {
			return nil, status.Errorf(codes.Internal, "failed to create cart: %v", err)
		}
	} else if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to get cart: %v", err)
	}

	return &pb.GetCartResponse{
		Cart: cart,
	}, nil
}

func (s *CartServer) AddProductToCart(ctx context.Context, req *pb.AddProductToCartRequest) (*pb.AddProductToCartResponse, error) {
	product, err := s.productRepo.GetProduct(ctx, req.ProductId)
	if err == repository.ErrProductNotFound {
		return nil, status.Errorf(codes.NotFound, "product with id %s not found", req.ProductId)
	}
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to get product: %v", err)
	}

	if product.State != pb.Product_AVAILABLE {
		return nil, status.Errorf(codes.FailedPrecondition, "product %s is not available", req.ProductId)
	}

	if product.CountInStock < req.Quantity {
		return nil, status.Errorf(codes.FailedPrecondition, "insufficient stock for product %s", req.ProductId)
	}

	cart, err := s.cartRepo.GetCart(ctx, req.CartId)
	if err == repository.ErrCartNotFound {
		cart = &pb.Cart{Id: req.CartId}
		cart, err = s.cartRepo.CreateCart(ctx, cart)
		if err != nil {
			return nil, status.Errorf(codes.Internal, "failed to create cart: %v", err)
		}
	} else if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to get cart: %v", err)
	}

	err = s.cartRepo.AddCartItem(ctx, req.CartId, product, req.Quantity)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to add product to cart: %v", err)
	}

	updatedCart, err := s.cartRepo.GetCart(ctx, req.CartId)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to get updated cart: %v", err)
	}

	return &pb.AddProductToCartResponse{
		Cart: updatedCart,
	}, nil
}

func (s *CartServer) UpdateProductInCart(ctx context.Context, req *pb.UpdateProductInCartRequest) (*pb.UpdateProductInCartResponse, error) {
	err := s.cartRepo.UpdateCartItem(ctx, req.CartId, req.ProductId, req.Quantity)
	if err == repository.ErrCartNotFound {
		return nil, status.Errorf(codes.NotFound, "cart with id %s not found", req.CartId)
	}
	if err == repository.ErrCartItemNotFound {
		return nil, status.Errorf(codes.NotFound, "product %s not found in cart %s", req.ProductId, req.CartId)
	}
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to update cart item: %v", err)
	}

	cart, err := s.cartRepo.GetCart(ctx, req.CartId)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to get updated cart: %v", err)
	}

	return &pb.UpdateProductInCartResponse{
		Cart: cart,
	}, nil
}

func (s *CartServer) ClearCart(ctx context.Context, req *pb.ClearCartRequest) (*pb.ClearCartResponse, error) {
	err := s.cartRepo.ClearCart(ctx, req.CartId)
	if err == repository.ErrCartNotFound {
		return nil, status.Errorf(codes.NotFound, "cart with id %s not found", req.CartId)
	}
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to clear cart: %v", err)
	}

	return &pb.ClearCartResponse{}, nil
}

