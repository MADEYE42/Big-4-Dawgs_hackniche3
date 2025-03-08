package controllers

import (
	"Users/Products/repository"
	"Users/models"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	logr "github.com/sirupsen/logrus"
)

type ProductController struct {
	repo *repository.ProductRepo
}

func NewProductController(repo *repository.ProductRepo) *ProductController {
	return &ProductController{
		repo: repo,
	}
}

// GetAllProducts handles GET /products
func (c *ProductController) GetAllProducts(ctx *gin.Context) {
	products, err := c.repo.GetAll()
	if err != nil {
		logr.Errorf("Error fetching products: %v", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch products"})
		return
	}
	ctx.JSON(http.StatusOK, products)
}

// GetProductById handles GET /products/:id
func (c *ProductController) GetProductById(ctx *gin.Context) {
	id := ctx.Param("id")

	// Increment click counter
	if err := c.repo.IncrementClicks(id); err != nil {
		logr.Warnf("Failed to increment clicks: %v", err)
	}

	product, err := c.repo.GetById(id)
	if err != nil {
		logr.Errorf("Error fetching product: %v", err)
		ctx.JSON(http.StatusNotFound, gin.H{"error": "Product not found"})
		return
	}

	ctx.JSON(http.StatusOK, product)
}

// GetProductsByCategory handles GET /products/category/:category
func (c *ProductController) GetProductsByCategory(ctx *gin.Context) {
	category := ctx.Param("category")

	products, err := c.repo.GetByCategory(category)
	if err != nil {
		logr.Errorf("Error fetching products by category: %v", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch products"})
		return
	}

	ctx.JSON(http.StatusOK, products)
}

// GetProductsBySeller handles GET /products/seller/:seller_id
func (c *ProductController) GetProductsBySeller(ctx *gin.Context) {
	sellerID := ctx.Param("seller_id")

	products, err := c.repo.GetBySeller(sellerID)
	if err != nil {
		logr.Errorf("Error fetching products by seller: %v", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch products"})
		return
	}

	ctx.JSON(http.StatusOK, products)
}

// CreateProduct handles POST /products
func (c *ProductController) CreateProduct(ctx *gin.Context) {
	var product models.Product
	if err := ctx.ShouldBindJSON(&product); err != nil {
		logr.Errorf("Error decoding request body: %v", err)
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
		return
	}

	if err := c.repo.Create(&product); err != nil {
		logr.Errorf("Error creating product: %v", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create product"})
		return
	}

	ctx.JSON(http.StatusCreated, product)
}

// UpdateProduct handles PUT /products/:id
func (c *ProductController) UpdateProduct(ctx *gin.Context) {
	id := ctx.Param("id")

	var product models.Product
	if err := ctx.ShouldBindJSON(&product); err != nil {
		logr.Errorf("Error decoding request body: %v", err)
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
		return
	}

	idUint, err := strconv.ParseUint(id, 10, 32)
	if err != nil {
		logr.Errorf("Invalid ID format: %v", err)
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID format"})
		return
	}
	product.ID = uint(idUint)

	if err := c.repo.Update(&product); err != nil {
		logr.Errorf("Error updating product: %v", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update product"})
		return
	}

	ctx.JSON(http.StatusOK, product)
}

// DeleteProduct handles DELETE /products/:id
func (c *ProductController) DeleteProduct(ctx *gin.Context) {
	id := ctx.Param("id")

	if err := c.repo.Delete(id); err != nil {
		logr.Errorf("Error deleting product: %v", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete product"})
		return
	}

	ctx.Status(http.StatusNoContent)
}

// RegisterRoutes registers all the product routes
func (c *ProductController) RegisterRoutes(router *gin.RouterGroup) {
	productRoutes := router.Group("/products")
	{
		productRoutes.GET("", c.GetAllProducts)
		productRoutes.GET("/:id", c.GetProductById)
		productRoutes.GET("/category/:category", c.GetProductsByCategory)
		productRoutes.GET("/seller/:seller_id", c.GetProductsBySeller)
		productRoutes.POST("", c.CreateProduct)
		productRoutes.PUT("/:id", c.UpdateProduct)
		productRoutes.DELETE("/:id", c.DeleteProduct)
	}
}
