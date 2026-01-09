package main

import (
	"context"
	"flag"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"demoshop/pkg/frontend"
	"demoshop/pkg/frontend/server"
)

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func main() {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Parse command line flags with environment variable defaults
	customerPort := flag.String("customer-port", getEnv("CUSTOMER_PORT", "8080"),
		"Port for customer GraphQL API (env: CUSTOMER_PORT)")
	adminPort := flag.String("admin-port", getEnv("ADMIN_PORT", "8081"),
		"Port for admin GraphQL API (env: ADMIN_PORT)")
	transactionService := flag.String("transaction-service", getEnv("TRANSACTION_SERVICE", "localhost:9000"),
		"Address of transaction service (env: TRANSACTION_SERVICE)")
	sessionSecret := flag.String("session-secret", getEnv("SESSION_COOKIE_SECRET", "default-secret-change-in-production"),
		"Secret for session cookie signing (env: SESSION_COOKIE_SECRET)")

	flag.Parse()

	cfg := &frontend.Config{
		CustomerPort:        *customerPort,
		AdminPort:           *adminPort,
		TransactionService:  *transactionService,
		SessionCookieSecret: *sessionSecret,
	}

	app, err := frontend.NewApp(cfg)
	if err != nil {
		log.Fatalf("Failed to create app: %v", err)
	}
	defer app.Close()

	srv, err := server.New(cfg, app)
	if err != nil {
		log.Fatalf("Failed to create server: %v", err)
	}

	// Start customer server
	go func() {
		log.Printf("Starting customer frontend service on port %s", cfg.CustomerPort)
		if err := srv.StartCustomer(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Customer server failed to start: %v", err)
		}
	}()

	// Start admin server
	go func() {
		log.Printf("Starting admin frontend service on port %s", cfg.AdminPort)
		if err := srv.StartAdmin(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Admin server failed to start: %v", err)
		}
	}()

	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)

	<-c
	log.Println("Shutting down servers...")

	ctx, cancel = context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Printf("Server shutdown error: %v", err)
	}

	log.Println("Servers exited")
}