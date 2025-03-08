package controller

import (
	"net/http"
	"strconv"

	"Users/Users/repository"
	"Users/models"
	"github.com/gin-gonic/gin"
	logr "github.com/sirupsen/logrus"
)

type UserController struct {
	userRepo *repository.UserRepo
}

func NewUserController(userRepo *repository.UserRepo) *UserController {
	return &UserController{
		userRepo: userRepo,
	}
}

// SetupRoutes registers all the user routes
func (c *UserController) SetupRoutes(router *gin.RouterGroup) {
	userRoutes := router.Group("/users")
	{
		userRoutes.GET("", c.GetAllUsers)
		userRoutes.GET("/:id", c.GetUserById)
		userRoutes.GET("/email/:email", c.GetUserByEmail)
		userRoutes.POST("", c.CreateUser)
		userRoutes.PUT("/:id", c.UpdateUser)
		userRoutes.DELETE("/:id", c.DeleteUser)
		userRoutes.PATCH("/:id/increment-reviews", c.IncrementReviewCount)
	}
}

// GetAllUsers returns all users
func (c *UserController) GetAllUsers(ctx *gin.Context) {
	users, err := c.userRepo.GetAll()
	if err != nil {
		logr.Errorf("Failed to get all users: %v", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch users"})
		return
	}

	ctx.JSON(http.StatusOK, users)
}

// GetUserById returns a user by ID
func (c *UserController) GetUserById(ctx *gin.Context) {
	id := ctx.Param("id")

	user, err := c.userRepo.GetById(id)
	if err != nil {
		logr.Errorf("Failed to get user with ID %s: %v", id, err)
		ctx.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}

	ctx.JSON(http.StatusOK, user)
}

// GetUserByEmail returns a user by email
func (c *UserController) GetUserByEmail(ctx *gin.Context) {
	email := ctx.Param("email")

	user, err := c.userRepo.GetByEmail(email)
	if err != nil {
		logr.Errorf("Failed to get user with email %s: %v", email, err)
		ctx.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}

	// Password is already omitted in the JSON output thanks to the model definition
	ctx.JSON(http.StatusOK, user)
}

// CreateUser creates a new user
func (c *UserController) CreateUser(ctx *gin.Context) {
	var user models.User

	if err := ctx.ShouldBindJSON(&user); err != nil {
		logr.Errorf("Invalid request body: %v", err)
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
		return
	}

	// Basic validation
	if user.Email == "" || user.Name == "" || user.Password == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"error": "Email, name and password are required",
		})
		return
	}

	// Set default role if not provided
	if user.Role == "" {
		user.Role = "user"
	}

	// Password should be hashed before storage in a real application
	// For example: user.Password = hashPassword(user.Password)

	err := c.userRepo.AddUser(&user)
	if err != nil {
		logr.Errorf("Failed to create user: %v", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create user"})
		return
	}

	ctx.JSON(http.StatusCreated, user)
}

// UpdateUser updates an existing user
func (c *UserController) UpdateUser(ctx *gin.Context) {
	id := ctx.Param("id")

	// Verify user exists
	_, err := c.userRepo.GetById(id)
	if err != nil {
		logr.Errorf("User with ID %s not found: %v", id, err)
		ctx.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}

	var updatedUser models.User
	if err := ctx.ShouldBindJSON(&updatedUser); err != nil {
		logr.Errorf("Invalid request body: %v", err)
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
		return
	}

	// Set ID from path parameter
	idUint, err := strconv.ParseUint(id, 10, 32)
	if err != nil {
		logr.Errorf("Invalid ID format: %v", err)
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID format"})
		return
	}
	updatedUser.ID = uint(idUint)

	// If there's a password, you might want to hash it here
	// For example: if updatedUser.Password != "" { updatedUser.Password = hashPassword(updatedUser.Password) }

	// Use the existing UpdateUser method for all updates
	err = c.userRepo.UpdateUser(&updatedUser)

	if err != nil {
		logr.Errorf("Failed to update user with ID %s: %v", id, err)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update user"})
		return
	}

	ctx.JSON(http.StatusOK, updatedUser)
} // DeleteUser deletes a user
func (c *UserController) DeleteUser(ctx *gin.Context) {
	id := ctx.Param("id")

	// Verify user exists
	_, err := c.userRepo.GetById(id)
	if err != nil {
		logr.Errorf("User with ID %s not found: %v", id, err)
		ctx.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}

	err = c.userRepo.DeleteUser(id)
	if err != nil {
		logr.Errorf("Failed to delete user with ID %s: %v", id, err)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete user"})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{"message": "User deleted successfully"})
}

// IncrementReviewCount increments the review count for a user
func (c *UserController) IncrementReviewCount(ctx *gin.Context) {
	id := ctx.Param("id")

	// Verify user exists
	_, err := c.userRepo.GetById(id)
	if err != nil {
		logr.Errorf("User with ID %s not found: %v", id, err)
		ctx.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}

	idUint, err := strconv.ParseUint(id, 10, 32)
	if err != nil {
		logr.Errorf("Invalid ID format: %v", err)
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID format"})
		return
	}

	err = c.userRepo.IncrementReviewCount(uint(idUint))
	if err != nil {
		logr.Errorf("Failed to increment review count for user with ID %s: %v", id, err)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to increment review count"})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{"message": "Review count incremented successfully"})
}
