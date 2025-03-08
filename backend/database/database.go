package database

import (
	"context"
	"fmt"
	"time"

	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq" // PostgreSQL driver
)

// Config holds database connection parameters
type Config struct {
	Host     string
	Port     string
	Password string
	User     string
	DBName   string
	SSLMode  string
}

// DB wraps the sqlx connection
type DB struct {
	Connection *sqlx.DB
}

// NewDB creates a new DB instance
func NewDB(sqlConn *sqlx.DB) *DB {
	return &DB{
		Connection: sqlConn,
	}
}

// CreateUsersTable creates the users table based on User struct
func CreateUsersTable(db *sqlx.DB) error {
	schema := `CREATE TABLE IF NOT EXISTS t_users(
		id SERIAL PRIMARY KEY,
		name VARCHAR(100) NOT NULL,
		email VARCHAR(100) UNIQUE NOT NULL,
		password TEXT NOT NULL,
		role VARCHAR(20) DEFAULT 'user',
		review_count INT DEFAULT 0
	)`
	_, err := db.Exec(schema)
	if err != nil {
		fmt.Printf("Error creating users table: %v\n", err)
		return err
	}
	return nil
}

// CreateSellersTable creates the sellers table based on Seller struct
func CreateSellersTable(db *sqlx.DB) error {
	schema := `CREATE TABLE IF NOT EXISTS t_sellers(
		id SERIAL PRIMARY KEY,
		user_id INT NOT NULL,
		description TEXT,
		rating FLOAT DEFAULT 0,
		FOREIGN KEY (user_id) REFERENCES t_users(id) ON DELETE CASCADE
	)`
	_, err := db.Exec(schema)
	if err != nil {
		fmt.Printf("Error creating sellers table: %v\n", err)
		return err
	}
	return nil
}

// CreateProductsTable creates the products table based on Product struct
func CreateProductsTable(db *sqlx.DB) error {
	schema := `CREATE TABLE IF NOT EXISTS t_products(
		id SERIAL PRIMARY KEY,
		name VARCHAR(255) NOT NULL,
		description TEXT,
		price DECIMAL(10,2) NOT NULL,
		seller_id INT NOT NULL,
		category VARCHAR(100) NOT NULL,
		clicks INT DEFAULT 0,
		in_stock BOOLEAN DEFAULT TRUE,
		FOREIGN KEY (seller_id) REFERENCES t_sellers(id) ON DELETE CASCADE
	)`
	_, err := db.Exec(schema)
	if err != nil {
		fmt.Printf("Error creating products table: %v\n", err)
		return err
	}
	return nil
}

// CreateSellerProductsMappingTable creates a mapping table for seller-products relationship
func CreateSellerProductsMappingTable(db *sqlx.DB) error {
	schema := `CREATE TABLE IF NOT EXISTS t_seller_products(
		seller_id INT NOT NULL,
		product_id INT NOT NULL,
		PRIMARY KEY (seller_id, product_id),
		FOREIGN KEY (seller_id) REFERENCES t_sellers(id) ON DELETE CASCADE,
		FOREIGN KEY (product_id) REFERENCES t_products(id) ON DELETE CASCADE
	)`
	_, err := db.Exec(schema)
	if err != nil {
		fmt.Printf("Error creating seller products mapping table: %v\n", err)
		return err
	}
	return nil
}

// SetupDatabase creates all required tables
func SetupDatabase(db *sqlx.DB) error {
	if err := CreateUsersTable(db); err != nil {
		return err
	}

	if err := CreateSellersTable(db); err != nil {
		return err
	}

	if err := CreateProductsTable(db); err != nil {
		return err
	}

	if err := CreateSellerProductsMappingTable(db); err != nil {
		return err
	}

	return nil
}

// ConnectToDb establishes a connection to the database
func (c *Config) ConnectToDb() (*sqlx.DB, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// PostgreSQL connection string
	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
		c.Host, c.Port, c.User, c.Password, c.DBName, c.SSLMode)

	fmt.Println("Connecting to PostgreSQL:", connStr)

	db, err := sqlx.Connect("postgres", connStr)
	if err != nil {
		return nil, err
	}

	if err := db.PingContext(ctx); err != nil {
		db.Close()
		return nil, err
	}

	// Setup all tables
	if err := SetupDatabase(db); err != nil {
		db.Close()
		return nil, err
	}

	return db, nil
}
