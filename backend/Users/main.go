package main

import (
	"os"

	"Users/Users/controller"
	"Users/Users/repository"
	"Users/database"
	"github.com/gin-gonic/gin"
	logr "github.com/sirupsen/logrus"
)

func main() {
	// Set up logging
	logr.SetOutput(os.Stdout)
	logr.SetLevel(logr.InfoLevel)

	// Database configuration
	dbConfig := database.Config{
		Host:     getEnv("DB_HOST", "localhost"),
		Port:     getEnv("DB_PORT", "5432"),
		User:     getEnv("DB_USER", "postgres"),
		Password: getEnv("DB_PASSWORD", "postgres"),
		DBName:   getEnv("DB_NAME", "shopmart_db"),
		SSLMode:  getEnv("DB_SSLMODE", "disable"),
	}

	// Connect to database
	dbConn, err := dbConfig.ConnectToDb()
	if err != nil {
		logr.Fatalf("Failed to connect to database: %v", err)
	}
	defer dbConn.Close()
	logr.Info("Connected to database successfully")

	// Create database wrapper
	db := database.NewDB(dbConn)

	// Initialize repositories
	userRepo := repository.NewUserRepo(db.Connection)

	// Initialize controllers
	userController := controller.NewUserController(userRepo)

	// Create Gin router with default middleware (logger, recovery)
	router := gin.Default()

	// Setup API routes
	apiRouter := router.Group("/api")
	{
		// Register user routes
		userController.SetupRoutes(apiRouter)

		// Health check endpoint
		apiRouter.GET("/health", func(c *gin.Context) {
			c.JSON(200, gin.H{
				"status": "ok",
			})
		})
	}

	// Get server port from environment or use default
	port := getEnv("PORT", "8080")

	// Start the server
	logr.Infof("Starting server on port %s", port)
	if err := router.Run(":" + port); err != nil {
		logr.Fatalf("Failed to start server: %v", err)
	}
}

// getEnv retrieves environment variables with fallback values
func getEnv(key, fallback string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return fallback
}
