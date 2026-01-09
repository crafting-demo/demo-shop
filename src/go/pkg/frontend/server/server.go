package server

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"path/filepath"

	"demoshop/pkg/frontend"
	"demoshop/pkg/frontend/graphql"
)

type Server struct {
	cfg              *frontend.Config
	app              *frontend.App
	customerServer   *http.Server
	adminServer      *http.Server
}

// serveHTMLFile creates a handler that serves a specific HTML file
func serveHTMLFile(webRoot, filename string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if webRoot == "" {
			http.Error(w, "Web root not configured", http.StatusServiceUnavailable)
			return
		}

		htmlPath := filepath.Join(webRoot, filename)
		if _, err := os.Stat(htmlPath); os.IsNotExist(err) {
			http.Error(w, fmt.Sprintf("File not found: %s", filename), http.StatusNotFound)
			return
		}

		http.ServeFile(w, r, htmlPath)
	}
}

// serveStaticFiles creates a handler that serves static assets
func serveStaticFiles(webRoot string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if webRoot == "" {
			http.Error(w, "Web root not configured", http.StatusServiceUnavailable)
			return
		}

		// Serve files from the web root
		http.FileServer(http.Dir(webRoot)).ServeHTTP(w, r)
	}
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

	// Serve index.html for customer endpoint at root path
	customerMux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/" {
			serveHTMLFile(cfg.WebRoot, "index.html")(w, r)
		} else {
			serveStaticFiles(cfg.WebRoot)(w, r)
		}
	})

	// Setup admin mux
	adminMux := http.NewServeMux()
	adminMux.Handle("/graphql", adminGQLHandler)
	adminMux.Handle("/playground", graphql.NewAdminPlaygroundHandler())
	adminMux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("OK"))
	})

	// Serve admin.html for admin endpoint at root path
	adminMux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/" {
			serveHTMLFile(cfg.WebRoot, "admin.html")(w, r)
		} else {
			serveStaticFiles(cfg.WebRoot)(w, r)
		}
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
