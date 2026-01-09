package server

import (
	"context"
	"fmt"
	"net/http"

	"demoshop/pkg/frontend"
	"demoshop/pkg/frontend/graphql"
)

type Server struct {
	cfg              *frontend.Config
	app              *frontend.App
	customerServer   *http.Server
	adminServer      *http.Server
}

func New(cfg *frontend.Config, app *frontend.App) (*Server, error) {
	// Create customer GraphQL handler
	customerGQLHandler, err := graphql.NewCustomerHandler(app)
	if err != nil {
		return nil, fmt.Errorf("failed to create customer GraphQL handler: %w", err)
	}

	// Create admin GraphQL handler
	adminGQLHandler, err := graphql.NewAdminHandler(app)
	if err != nil {
		return nil, fmt.Errorf("failed to create admin GraphQL handler: %w", err)
	}

	// Setup customer mux
	customerMux := http.NewServeMux()
	customerMux.Handle("/graphql", customerGQLHandler)
	customerMux.Handle("/playground", graphql.NewCustomerPlaygroundHandler())
	customerMux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("OK"))
	})

	// Setup admin mux
	adminMux := http.NewServeMux()
	adminMux.Handle("/graphql", adminGQLHandler)
	adminMux.Handle("/playground", graphql.NewAdminPlaygroundHandler())
	adminMux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("OK"))
	})

	customerServer := &http.Server{
		Addr:    ":" + cfg.CustomerPort,
		Handler: customerMux,
	}

	adminServer := &http.Server{
		Addr:    ":" + cfg.AdminPort,
		Handler: adminMux,
	}

	return &Server{
		cfg:            cfg,
		app:            app,
		customerServer: customerServer,
		adminServer:    adminServer,
	}, nil
}

func (s *Server) StartCustomer() error {
	return s.customerServer.ListenAndServe()
}

func (s *Server) StartAdmin() error {
	return s.adminServer.ListenAndServe()
}

func (s *Server) Shutdown(ctx context.Context) error {
	// Shutdown both servers
	customerErr := s.customerServer.Shutdown(ctx)
	adminErr := s.adminServer.Shutdown(ctx)

	if customerErr != nil {
		return fmt.Errorf("customer server shutdown error: %w", customerErr)
	}
	if adminErr != nil {
		return fmt.Errorf("admin server shutdown error: %w", adminErr)
	}

	return nil
}
