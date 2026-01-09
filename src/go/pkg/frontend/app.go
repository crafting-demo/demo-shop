package frontend

import (
	"log"

	"demoshop/pkg/frontend/grpc"
	"demoshop/pkg/frontend/session"
)

type Config struct {
	CustomerPort        string
	AdminPort           string
	TransactionService  string
	SessionCookieSecret string
}

type App struct {
	cfg             *Config
	sessionManager  *session.Manager
	transactionConn *grpc.TransactionClient
}

func NewApp(cfg *Config) (*App, error) {
	sessionManager := session.NewManager(cfg.SessionCookieSecret)

	transactionConn, err := grpc.NewTransactionClient(cfg.TransactionService)
	if err != nil {
		return nil, err
	}

	return &App{
		cfg:             cfg,
		sessionManager:  sessionManager,
		transactionConn: transactionConn,
	}, nil
}

func (a *App) SessionManager() *session.Manager {
	return a.sessionManager
}

func (a *App) TransactionClient() *grpc.TransactionClient {
	return a.transactionConn
}

func (a *App) Close() {
	if a.transactionConn != nil {
		if err := a.transactionConn.Close(); err != nil {
			log.Printf("Error closing transaction client: %v", err)
		}
	}
}