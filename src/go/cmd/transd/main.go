package main

import (
	"flag"
	"fmt"
	"log"
	"net"
	"os"

	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"

	pb "demoshop/gen/proto/demoshop/v1"
	"demoshop/pkg/common/interceptor"
	"demoshop/pkg/transaction/db"
	"demoshop/pkg/transaction/repository"
	"demoshop/pkg/transaction/service"
)

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvAsInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		var result int
		if _, err := fmt.Sscanf(value, "%d", &result); err == nil {
			return result
		}
	}
	return defaultValue
}

func main() {
	// gRPC server flags
	listenAddr := flag.String("l", ":9000", "The gRPC server listening address")

	// Database flags
	dbHost := flag.String("db-host", getEnv("DB_HOST", "localhost"),
		"Database host (env: DB_HOST)")
	dbPort := flag.Int("db-port", getEnvAsInt("DB_PORT", 5432),
		"Database port (env: DB_PORT)")
	dbUser := flag.String("db-user", getEnv("DB_USER", "postgres"),
		"Database user (env: DB_USER)")
	dbPassword := flag.String("db-password", getEnv("DB_PASSWORD", ""),
		"Database password (env: DB_PASSWORD)")
	dbName := flag.String("db-name", getEnv("DB_NAME", "demoshop"),
		"Database name (env: DB_NAME)")
	dbSSLMode := flag.String("db-sslmode", getEnv("DB_SSLMODE", "disable"),
		"Database SSL mode (env: DB_SSLMODE)")

	flag.Parse()

	dbConfig := &db.Config{
		Host:     *dbHost,
		Port:     *dbPort,
		User:     *dbUser,
		Password: *dbPassword,
		DBName:   *dbName,
		SSLMode:  *dbSSLMode,
	}

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

	grpcServer := grpc.NewServer(
		grpc.UnaryInterceptor(interceptor.UnaryServerLoggingInterceptor),
	)

	pb.RegisterInventoryServiceServer(grpcServer, inventoryServer)
	pb.RegisterCartServiceServer(grpcServer, cartServer)
	pb.RegisterOrderServiceServer(grpcServer, orderServer)

	reflection.Register(grpcServer)

	listener, err := net.Listen("tcp", *listenAddr)
	if err != nil {
		log.Fatalf("Failed to listen on port %s: %v", *listenAddr, err)
	}

	fmt.Printf("Transaction service listening on port %s\n", *listenAddr)
	log.Println("gRPC request tracing and logging enabled")

	if err := grpcServer.Serve(listener); err != nil {
		log.Fatalf("Failed to serve gRPC: %v", err)
	}
}
