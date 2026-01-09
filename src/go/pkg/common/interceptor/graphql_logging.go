package interceptor

import (
	"context"
	"log"
	"time"

	"github.com/99designs/gqlgen/graphql"
)

// GraphQLLoggingExtension logs all GraphQL operations
type GraphQLLoggingExtension struct{}

// ExtensionName returns the extension name
func (e GraphQLLoggingExtension) ExtensionName() string {
	return "GraphQLLoggingExtension"
}

// Validate validates the extension configuration
func (e GraphQLLoggingExtension) Validate(schema graphql.ExecutableSchema) error {
	return nil
}

// InterceptOperation logs GraphQL operations
func (e GraphQLLoggingExtension) InterceptOperation(ctx context.Context, next graphql.OperationHandler) graphql.ResponseHandler {
	oc := graphql.GetOperationContext(ctx)
	
	// Generate trace ID for this operation
	traceID := time.Now().Format("20060102150405.000000")
	
	// Add trace ID to context so gRPC calls can use it
	ctx = context.WithValue(ctx, "traceID", traceID)
	
	operationType := "query"
	if oc.Operation != nil && oc.Operation.Operation != "" {
		operationType = string(oc.Operation.Operation)
	}
	
	operationName := oc.OperationName
	if operationName == "" {
		operationName = "<anonymous>"
	}

	log.Printf("[TRACE:%s] >>> GraphQL %s: %s", traceID, operationType, operationName)
	if oc.Variables != nil && len(oc.Variables) > 0 {
		log.Printf("[TRACE:%s]     Variables: %+v", traceID, oc.Variables)
	}
	log.Printf("[TRACE:%s]     Query: %s", traceID, oc.RawQuery)
	
	return next(ctx)
}

// InterceptResponse logs GraphQL responses
func (e GraphQLLoggingExtension) InterceptResponse(ctx context.Context, next graphql.ResponseHandler) *graphql.Response {
	oc := graphql.GetOperationContext(ctx)
	
	// Get trace ID from context
	traceID, ok := ctx.Value("traceID").(string)
	if !ok {
		traceID = time.Now().Format("20060102150405.000000")
	}
	
	start := time.Now()
	resp := next(ctx)
	duration := time.Since(start)

	operationType := "query"
	if oc.Operation != nil && oc.Operation.Operation != "" {
		operationType = string(oc.Operation.Operation)
	}
	
	operationName := oc.OperationName
	if operationName == "" {
		operationName = "<anonymous>"
	}

	if resp.Errors != nil && len(resp.Errors) > 0 {
		log.Printf("[TRACE:%s] <<< GraphQL %s: %s [FAILED]", traceID, operationType, operationName)
		log.Printf("[TRACE:%s]     Duration: %v", traceID, duration)
		log.Printf("[TRACE:%s]     Errors: %v", traceID, resp.Errors)
	} else {
		log.Printf("[TRACE:%s] <<< GraphQL %s: %s [SUCCESS]", traceID, operationType, operationName)
		log.Printf("[TRACE:%s]     Duration: %v", traceID, duration)
		if resp.Data != nil {
			log.Printf("[TRACE:%s]     Response Data: %s", traceID, string(resp.Data))
		}
	}

	return resp
}

// InterceptField is not used for operation-level logging
func (e GraphQLLoggingExtension) InterceptField(ctx context.Context, next graphql.Resolver) (interface{}, error) {
	return next(ctx)
}
