package interceptor

import (
	"context"
	"log"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/status"
)

// UnaryServerLoggingInterceptor logs all incoming unary gRPC calls (server-side)
func UnaryServerLoggingInterceptor(
	ctx context.Context,
	req interface{},
	info *grpc.UnaryServerInfo,
	handler grpc.UnaryHandler,
) (interface{}, error) {
	start := time.Now()

	traceID := extractTraceID(ctx)
	
	log.Printf("[TRACE:%s] --> gRPC Call: %s", traceID, info.FullMethod)
	log.Printf("[TRACE:%s]     Request: %+v", traceID, req)

	resp, err := handler(ctx, req)

	duration := time.Since(start)
	statusCode := codes.OK
	statusMsg := "OK"
	
	if err != nil {
		st, ok := status.FromError(err)
		if ok {
			statusCode = st.Code()
			statusMsg = st.Message()
		}
		log.Printf("[TRACE:%s] <-- gRPC Call: %s [FAILED]", traceID, info.FullMethod)
		log.Printf("[TRACE:%s]     Duration: %v", traceID, duration)
		log.Printf("[TRACE:%s]     Status: %s (%s)", traceID, statusCode, statusMsg)
		log.Printf("[TRACE:%s]     Error: %v", traceID, err)
	} else {
		log.Printf("[TRACE:%s] <-- gRPC Call: %s [SUCCESS]", traceID, info.FullMethod)
		log.Printf("[TRACE:%s]     Duration: %v", traceID, duration)
		log.Printf("[TRACE:%s]     Status: %s", traceID, statusCode)
		log.Printf("[TRACE:%s]     Response: %+v", traceID, resp)
	}

	return resp, err
}

// UnaryClientLoggingInterceptor logs all outgoing unary gRPC calls (client-side)
func UnaryClientLoggingInterceptor(
	ctx context.Context,
	method string,
	req interface{},
	reply interface{},
	cc *grpc.ClientConn,
	invoker grpc.UnaryInvoker,
	opts ...grpc.CallOption,
) error {
	start := time.Now()

	traceID := extractOrGenerateTraceID(ctx)
	
	// Add trace ID to outgoing metadata
	ctx = metadata.AppendToOutgoingContext(ctx, "x-trace-id", traceID)

	log.Printf("[TRACE:%s] ==> Outgoing gRPC Call: %s", traceID, method)
	log.Printf("[TRACE:%s]     Target: %s", traceID, cc.Target())
	log.Printf("[TRACE:%s]     Request: %+v", traceID, req)

	err := invoker(ctx, method, req, reply, cc, opts...)

	duration := time.Since(start)
	
	if err != nil {
		st, ok := status.FromError(err)
		statusCode := "Unknown"
		statusMsg := err.Error()
		if ok {
			statusCode = st.Code().String()
			statusMsg = st.Message()
		}
		log.Printf("[TRACE:%s] <== Outgoing gRPC Call: %s [FAILED]", traceID, method)
		log.Printf("[TRACE:%s]     Duration: %v", traceID, duration)
		log.Printf("[TRACE:%s]     Status: %s (%s)", traceID, statusCode, statusMsg)
		log.Printf("[TRACE:%s]     Error: %v", traceID, err)
	} else {
		log.Printf("[TRACE:%s] <== Outgoing gRPC Call: %s [SUCCESS]", traceID, method)
		log.Printf("[TRACE:%s]     Duration: %v", traceID, duration)
		log.Printf("[TRACE:%s]     Response: %+v", traceID, reply)
	}

	return err
}

// extractTraceID extracts trace ID from incoming context metadata (server-side)
func extractTraceID(ctx context.Context) string {
	md, ok := metadata.FromIncomingContext(ctx)
	if !ok {
		return generateTraceID()
	}

	traceIDs := md.Get("x-trace-id")
	if len(traceIDs) > 0 && traceIDs[0] != "" {
		return traceIDs[0]
	}

	requestIDs := md.Get("x-request-id")
	if len(requestIDs) > 0 && requestIDs[0] != "" {
		return requestIDs[0]
	}

	return generateTraceID()
}

// extractOrGenerateTraceID extracts trace ID from context or generates a new one (client-side)
func extractOrGenerateTraceID(ctx context.Context) string {
	// Try to get from incoming metadata (in case of chained calls)
	if md, ok := metadata.FromIncomingContext(ctx); ok {
		if traceIDs := md.Get("x-trace-id"); len(traceIDs) > 0 && traceIDs[0] != "" {
			return traceIDs[0]
		}
		if requestIDs := md.Get("x-request-id"); len(requestIDs) > 0 && requestIDs[0] != "" {
			return requestIDs[0]
		}
	}

	// Try to get from outgoing metadata
	if md, ok := metadata.FromOutgoingContext(ctx); ok {
		if traceIDs := md.Get("x-trace-id"); len(traceIDs) > 0 && traceIDs[0] != "" {
			return traceIDs[0]
		}
	}

	// Try to get from context value (set by GraphQL layer)
	if traceID, ok := ctx.Value("traceID").(string); ok && traceID != "" {
		return traceID
	}

	// Generate new trace ID
	return generateTraceID()
}

// generateTraceID generates a simple trace ID
func generateTraceID() string {
	return time.Now().Format("20060102150405.000000")
}
