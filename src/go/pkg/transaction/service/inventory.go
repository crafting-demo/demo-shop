package service

import (
	"context"

	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	pb "demoshop/gen/proto/demoshop/v1"
	"demoshop/pkg/transaction/repository"
)

type InventoryServer struct {
	pb.UnimplementedInventoryServiceServer
	productRepo repository.ProductRepository
}

func NewInventoryServer(productRepo repository.ProductRepository) *InventoryServer {
	return &InventoryServer{
		productRepo: productRepo,
	}
}

func (s *InventoryServer) QueryProducts(ctx context.Context, req *pb.QueryProductsRequest) (*pb.QueryProductsResponse, error) {
	first := int(req.Pagination.First)
	if first <= 0 {
		first = 20
	}

	products, totalCount, err := s.productRepo.QueryProducts(ctx, req.StateFilter, first, req.Pagination.After)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to query products: %v", err)
	}

	pageInfo := &pb.PageInfo{
		HasNextPage:     len(products) == first,
		HasPreviousPage: req.Pagination.After != "",
	}

	if len(products) > 0 {
		pageInfo.StartCursor = products[0].Id
		pageInfo.EndCursor = products[len(products)-1].Id
	}

	return &pb.QueryProductsResponse{
		Products:   products,
		PageInfo:   pageInfo,
		TotalCount: totalCount,
	}, nil
}

func (s *InventoryServer) GetProduct(ctx context.Context, req *pb.GetProductRequest) (*pb.GetProductResponse, error) {
	product, err := s.productRepo.GetProduct(ctx, req.Id)
	if err == repository.ErrProductNotFound {
		return nil, status.Errorf(codes.NotFound, "product with id %s not found", req.Id)
	}
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to get product: %v", err)
	}

	return &pb.GetProductResponse{
		Product: product,
	}, nil
}

func (s *InventoryServer) CreateProduct(ctx context.Context, req *pb.CreateProductRequest) (*pb.CreateProductResponse, error) {
	product := &pb.Product{
		Name:         req.Name,
		Description:  req.Description,
		ImageData:    req.ImageData,
		PricePerUnit: req.PricePerUnit,
		CountInStock: req.CountInStock,
		State:        req.State,
	}

	createdProduct, err := s.productRepo.CreateProduct(ctx, product)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to create product: %v", err)
	}

	return &pb.CreateProductResponse{
		Product: createdProduct,
	}, nil
}

func (s *InventoryServer) UpdateProduct(ctx context.Context, req *pb.UpdateProductRequest) (*pb.UpdateProductResponse, error) {
	product, err := s.productRepo.GetProduct(ctx, req.Id)
	if err == repository.ErrProductNotFound {
		return nil, status.Errorf(codes.NotFound, "product with id %s not found", req.Id)
	}
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to get product: %v", err)
	}

	if req.Name != nil {
		product.Name = req.Name.Value
	}
	if req.Description != nil {
		product.Description = req.Description.Value
	}
	if req.ImageData != nil {
		product.ImageData = req.ImageData.Value
	}
	if req.PricePerUnit != nil {
		product.PricePerUnit = req.PricePerUnit.Value
	}
	if req.CountInStock != nil {
		product.CountInStock = req.CountInStock.Value
	}
	if req.State != nil {
		product.State = req.State.Value
	}

	updatedProduct, err := s.productRepo.UpdateProduct(ctx, product)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to update product: %v", err)
	}

	return &pb.UpdateProductResponse{
		Product: updatedProduct,
	}, nil
}

func (s *InventoryServer) DeleteProduct(ctx context.Context, req *pb.DeleteProductRequest) (*pb.DeleteProductResponse, error) {
	err := s.productRepo.DeleteProduct(ctx, req.Id)
	if err == repository.ErrProductNotFound {
		return nil, status.Errorf(codes.NotFound, "product with id %s not found", req.Id)
	}
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to delete product: %v", err)
	}

	return &pb.DeleteProductResponse{}, nil
}
