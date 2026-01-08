package main

import (
	"flag"
	"fmt"
	"log"
	"net"

	pb "demoshop/transaction/gen/proto/demoshop/v1"
	"demoshop/transaction/internal/db"
	"demoshop/transaction/internal/repository"
	"demoshop/transaction/internal/service"

	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

func main() {
	var listenAddr = flag.String("l", ":9000", "The gRPC server listening address")
	flag.Parse()

	dbConfig := db.NewConfig()
	database, err := db.NewConnection(dbConfig)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer database.Close()

	productRepo := repository.NewPostgreSQLProductRepository(database)
	cartRepo := repository.NewPostgreSQLCartRepository(database)
	orderRepo := repository.NewPostgreSQLOrderRepository(database)

	inventoryServer := service.NewInventoryServer(productRepo)
	cartServer := service.NewCartServer(cartRepo, productRepo)
	orderServer := service.NewOrderServer(orderRepo, cartRepo)

	grpcServer := grpc.NewServer()

	pb.RegisterInventoryServiceServer(grpcServer, inventoryServer)
	pb.RegisterCartServiceServer(grpcServer, cartServer)
	pb.RegisterOrderServiceServer(grpcServer, orderServer)

	reflection.Register(grpcServer)

	listener, err := net.Listen("tcp", *listenAddr)
	if err != nil {
		log.Fatalf("Failed to listen on port %s: %v", *listenAddr, err)
	}

	fmt.Printf("Transaction service listening on port %s\n", *listenAddr)

	if err := grpcServer.Serve(listener); err != nil {
		log.Fatalf("Failed to serve gRPC: %v", err)
	}
}
