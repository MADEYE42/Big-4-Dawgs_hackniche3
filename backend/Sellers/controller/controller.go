package controller

import (
	"Users/Sellers/repository"
	repo "Users/Users/repository"
	"Users/models"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	logr "github.com/sirupsen/logrus"
)

type SellerController struct {
	sellerRepo *repository.SellerRepo
	userRepo   *repo.UserRepo // May need to validate user exists
}

func NewSellerController(sellerRepo *repository.SellerRepo, userRepo *repo.UserRepo) *SellerController {
	return &SellerController{
		sellerRepo: sellerRepo,
		userRepo:   userRepo,
	}
}

// SetupRoutes registers all the seller routes
func (c *SellerController) SetupRoutes(router *gin.RouterGroup) {
	sellerRoutes := router.Group("/sellers")
	{
		sellerRoutes.GET("", c.GetAllSellers)
		sellerRoutes.GET("/:id", c.GetSellerById)
		sellerRoutes.GET("/user/:userId", c.GetSellerByUserId)
		sellerRoutes.POST("", c.CreateSeller)
		sellerRoutes.PUT("/:id", c.UpdateSeller)
		sellerRoutes.DELETE("/:id", c.DeleteSeller)
		sellerRoutes.PATCH("/:id/rating", c.UpdateSellerRating)
	}
}

// GetAllSellers returns all sellers
func (c *SellerController) GetAllSellers(ctx *gin.Context) {
	sellers, err := c.sellerRepo.GetAll()
	if err != nil {
		logr.Errorf("Failed to get all sellers: %v", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch sellers"})
		return
	}

	ctx.JSON(http.StatusOK, sellers)
}

// GetSellerById returns a seller by ID
func (c *SellerController) GetSellerById(ctx *gin.Context) {
	id := ctx.Param("id")

	seller, err := c.sellerRepo.GetById(id)
	if err != nil {
		logr.Errorf("Failed to get seller with ID %s: %v", id, err)
		ctx.JSON(http.StatusNotFound, gin.H{"error": "Seller not found"})
		return
	}

	ctx.JSON(http.StatusOK, seller)
}

// GetSellerByUserId returns a seller by user ID
func (c *SellerController) GetSellerByUserId(ctx *gin.Context) {
	userId := ctx.Param("userId")

	seller, err := c.sellerRepo.GetByUserId(userId)
	if err != nil {
		logr.Errorf("Failed to get seller with user ID %s: %v", userId, err)
		ctx.JSON(http.StatusNotFound, gin.H{"error": "Seller not found"})
		return
	}

	ctx.JSON(http.StatusOK, seller)
}

// CreateSeller creates a new seller
func (c *SellerController) CreateSeller(ctx *gin.Context) {
	var seller models.Seller

	if err := ctx.ShouldBindJSON(&seller); err != nil {
		logr.Errorf("Invalid request body: %v", err)
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
		return
	}

	// Validate that user exists
	userIdStr := strconv.FormatUint(uint64(seller.UserID), 10)
	_, err := c.userRepo.GetById(userIdStr)
	if err != nil {
		logr.Errorf("User with ID %d not found: %v", seller.UserID, err)
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "User not found"})
		return
	}

	// Set default rating if not provided
	if seller.Rating == 0 {
		seller.Rating = 0.0
	}

	err = c.sellerRepo.Create(&seller)
	if err != nil {
		logr.Errorf("Failed to create seller: %v", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create seller"})
		return
	}

	// Fetch the complete seller with user information
	completeSellerIdStr := strconv.FormatUint(uint64(seller.ID), 10)
	completeSeller, err := c.sellerRepo.GetById(completeSellerIdStr)
	if err != nil {
		logr.Warnf("Created seller but couldn't fetch complete details: %v", err)
		ctx.JSON(http.StatusCreated, seller)
		return
	}

	ctx.JSON(http.StatusCreated, completeSeller)
}

// UpdateSeller updates an existing seller
func (c *SellerController) UpdateSeller(ctx *gin.Context) {
	id := ctx.Param("id")

	// Verify seller exists
	existingSeller, err := c.sellerRepo.GetById(id)
	if err != nil {
		logr.Errorf("Seller with ID %s not found: %v", id, err)
		ctx.JSON(http.StatusNotFound, gin.H{"error": "Seller not found"})
		return
	}

	var updatedSeller models.Seller
	if err := ctx.ShouldBindJSON(&updatedSeller); err != nil {
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
	updatedSeller.ID = uint(idUint)

	// Preserve the user ID - can't change which user the seller is linked to
	updatedSeller.UserID = existingSeller.UserID

	err = c.sellerRepo.Update(&updatedSeller)
	if err != nil {
		logr.Errorf("Failed to update seller with ID %s: %v", id, err)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update seller"})
		return
	}

	// Fetch the complete updated seller
	completeSeller, err := c.sellerRepo.GetById(id)
	if err != nil {
		logr.Warnf("Updated seller but couldn't fetch complete details: %v", err)
		ctx.JSON(http.StatusOK, updatedSeller)
		return
	}

	ctx.JSON(http.StatusOK, completeSeller)
}

// DeleteSeller deletes a seller
func (c *SellerController) DeleteSeller(ctx *gin.Context) {
	id := ctx.Param("id")

	// Verify seller exists
	_, err := c.sellerRepo.GetById(id)
	if err != nil {
		logr.Errorf("Seller with ID %s not found: %v", id, err)
		ctx.JSON(http.StatusNotFound, gin.H{"error": "Seller not found"})
		return
	}

	err = c.sellerRepo.Delete(id)
	if err != nil {
		logr.Errorf("Failed to delete seller with ID %s: %v", id, err)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete seller"})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{"message": "Seller deleted successfully"})
}

// UpdateSellerRating updates just the rating field of a seller
func (c *SellerController) UpdateSellerRating(ctx *gin.Context) {
	id := ctx.Param("id")

	// Verify seller exists
	_, err := c.sellerRepo.GetById(id)
	if err != nil {
		logr.Errorf("Seller with ID %s not found: %v", id, err)
		ctx.JSON(http.StatusNotFound, gin.H{"error": "Seller not found"})
		return
	}

	var ratingData struct {
		Rating float64 `json:"rating"`
	}

	if err := ctx.ShouldBindJSON(&ratingData); err != nil {
		logr.Errorf("Invalid rating data: %v", err)
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid rating data"})
		return
	}

	// Validate rating
	if ratingData.Rating < 0 || ratingData.Rating > 5 {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Rating must be between 0 and 5"})
		return
	}

	idUint, err := strconv.ParseUint(id, 10, 32)
	if err != nil {
		logr.Errorf("Invalid ID format: %v", err)
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID format"})
		return
	}

	err = c.sellerRepo.UpdateRating(uint(idUint), ratingData.Rating)
	if err != nil {
		logr.Errorf("Failed to update rating for seller with ID %s: %v", id, err)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update rating"})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{"message": "Rating updated successfully"})
}
