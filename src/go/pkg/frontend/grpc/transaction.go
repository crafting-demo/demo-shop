package grpc

import (
	demoshopv1 "demoshop/gen/proto/demoshop/v1"
	"demoshop/pkg/common/interceptor"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type TransactionClient struct {
	conn            *grpc.ClientConn
	inventoryClient demoshopv1.InventoryServiceClient
	cartClient      demoshopv1.CartServiceClient
	orderClient     demoshopv1.OrderServiceClient
}

func NewTransactionClient(address string) (*TransactionClient, error) {
	conn, err := grpc.NewClient(
		address,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithUnaryInterceptor(interceptor.UnaryClientLoggingInterceptor),
	)
	if err != nil {
		return nil, err
	}

	return &TransactionClient{
		conn:            conn,
		inventoryClient: demoshopv1.NewInventoryServiceClient(conn),
		cartClient:      demoshopv1.NewCartServiceClient(conn),
		orderClient:     demoshopv1.NewOrderServiceClient(conn),
	}, nil
}

func (c *TransactionClient) InventoryService() demoshopv1.InventoryServiceClient {
	return c.inventoryClient
}

func (c *TransactionClient) CartService() demoshopv1.CartServiceClient {
	return c.cartClient
}

func (c *TransactionClient) OrderService() demoshopv1.OrderServiceClient {
	return c.orderClient
}

func (c *TransactionClient) Close() error {
	return c.conn.Close()
}