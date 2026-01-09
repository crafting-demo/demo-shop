package db

import (
	"database/sql"
	"fmt"
	"log"
	"time"

	_ "github.com/lib/pq"
)

type Config struct {
	Host     string
	Port     int
	User     string
	Password string
	DBName   string
	SSLMode  string
}

func (c *Config) ConnectionString() string {
	connStr := fmt.Sprintf("host=%s port=%d user=%s dbname=%s sslmode=%s search_path=public",
		c.Host, c.Port, c.User, c.DBName, c.SSLMode)
	if c.Password != "" {
		connStr = fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=%s search_path=public",
			c.Host, c.Port, c.User, c.Password, c.DBName, c.SSLMode)
	}
	return connStr
}

func NewConnection(config *Config) (*sql.DB, error) {
	db, err := sql.Open("postgres", config.ConnectionString())
	if err != nil {
		return nil, fmt.Errorf("failed to open database connection: %w", err)
	}

	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(25)
	db.SetConnMaxLifetime(5 * time.Minute)

	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	log.Printf("Connected to PostgreSQL database: %s:%d/%s", config.Host, config.Port, config.DBName)
	return db, nil
}