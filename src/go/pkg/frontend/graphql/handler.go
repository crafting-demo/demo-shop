package graphql

import (
	"context"
	"net/http"

	"demoshop/pkg/frontend"
	"demoshop/pkg/frontend/graphql/admin"
	"demoshop/pkg/frontend/graphql/customer"

	"github.com/99designs/gqlgen/graphql/handler"
	"github.com/99designs/gqlgen/graphql/playground"
)

// sessionMiddleware extracts session from request and adds cartID to context
func sessionMiddleware(app *frontend.App, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		session := app.SessionManager().GetSession(r)

		// Set session cookie if it's new
		app.SessionManager().SetSessionCookie(w, session)

		// Add cartID to context
		ctx := context.WithValue(r.Context(), "cartID", session.CartID)

		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

// NewCustomerHandler creates a new HTTP handler for the customer GraphQL API
func NewCustomerHandler(app *frontend.App) (http.Handler, error) {
	resolver := customer.NewResolver(app)
	schema := customer.NewExecutableSchema(customer.Config{Resolvers: resolver})

	srv := handler.NewDefaultServer(schema)

	// Wrap with session middleware
	return sessionMiddleware(app, srv), nil
}

// NewCustomerPlaygroundHandler creates a playground handler for the customer GraphQL API
func NewCustomerPlaygroundHandler() http.Handler {
	return playground.Handler("Customer GraphQL playground", "/graphql")
}

// NewAdminHandler creates a new HTTP handler for the admin GraphQL API
func NewAdminHandler(app *frontend.App) (http.Handler, error) {
	resolver := admin.NewResolver(app)
	schema := admin.NewExecutableSchema(admin.Config{Resolvers: resolver})

	srv := handler.NewDefaultServer(schema)

	return srv, nil
}

// NewAdminPlaygroundHandler creates a playground handler for the admin GraphQL API
func NewAdminPlaygroundHandler() http.Handler {
	return playground.Handler("Admin GraphQL playground", "/graphql")
}
