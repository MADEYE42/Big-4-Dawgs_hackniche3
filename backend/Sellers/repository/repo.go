package repository

import (
	"Users/models"
	"github.com/jmoiron/sqlx"
	logr "github.com/sirupsen/logrus"
)

type SellerRepo struct {
	db *sqlx.DB
}

func NewSellerRepo(db *sqlx.DB) *SellerRepo {
	return &SellerRepo{
		db: db,
	}
}

// GetAll returns all sellers with their linked user information
func (r *SellerRepo) GetAll() ([]models.Seller, error) {
	var sellers []models.Seller

	query := `
		SELECT s.id, s.user_id, s.description, s.rating,
			   u.id as "user.id", u.name as "user.name", u.email as "user.email", 
			   u.role as "user.role", u.review_count as "user.review_count"
		FROM t_sellers s
		JOIN t_users u ON s.user_id = u.id
	`

	err := r.db.Select(&sellers, query)
	if err != nil {
		logr.Errorf("Error fetching all sellers: %v", err)
		return nil, err
	}

	// For each seller, fetch their products
	for i := range sellers {
		products, err := r.getProductsBySellerID(sellers[i].ID)
		if err != nil {
			logr.Warnf("Failed to fetch products for seller %d: %v", sellers[i].ID, err)
			continue
		}

		// Extract product IDs for the ProductsList field
		productIDs := make([]uint, len(products))
		for j, product := range products {
			productIDs[j] = product.ID
		}
		sellers[i].ProductsList = productIDs
	}

	return sellers, nil
}

// GetById returns a seller by ID with all related information
func (r *SellerRepo) GetById(id string) (*models.Seller, error) {
	var seller models.Seller

	query := `
		SELECT s.id, s.user_id, s.description, s.rating,
			   u.id as "user.id", u.name as "user.name", u.email as "user.email", 
			   u.role as "user.role", u.review_count as "user.review_count"
		FROM t_sellers s
		JOIN t_users u ON s.user_id = u.id
		WHERE s.id = $1
	`

	err := r.db.Get(&seller, query, id)
	if err != nil {
		logr.Errorf("Error fetching seller by ID %s: %v", id, err)
		return nil, err
	}

	// Fetch products for this seller
	products, err := r.getProductsBySellerID(seller.ID)
	if err != nil {
		logr.Warnf("Failed to fetch products for seller %d: %v", seller.ID, err)
	} else {
		// Extract product IDs for the ProductsList field
		productIDs := make([]uint, len(products))
		for i, product := range products {
			productIDs[i] = product.ID
		}
		seller.ProductsList = productIDs
	}

	return &seller, nil
}

// GetByUserId returns a seller by the associated user ID
func (r *SellerRepo) GetByUserId(userId string) (*models.Seller, error) {
	var seller models.Seller

	query := `
		SELECT s.id, s.user_id, s.description, s.rating,
			   u.id as "user.id", u.name as "user.name", u.email as "user.email", 
			   u.role as "user.role", u.review_count as "user.review_count"
		FROM t_sellers s
		JOIN t_users u ON s.user_id = u.id
		WHERE s.user_id = $1
	`

	err := r.db.Get(&seller, query, userId)
	if err != nil {
		logr.Errorf("Error fetching seller by user ID %s: %v", userId, err)
		return nil, err
	}

	// Fetch products for this seller
	products, err := r.getProductsBySellerID(seller.ID)
	if err != nil {
		logr.Warnf("Failed to fetch products for seller %d: %v", seller.ID, err)
	} else {
		// Extract product IDs for the ProductsList field
		productIDs := make([]uint, len(products))
		for i, product := range products {
			productIDs[i] = product.ID
		}
		seller.ProductsList = productIDs
	}

	return &seller, nil
}

// Create adds a new seller
func (r *SellerRepo) Create(seller *models.Seller) error {
	tx, err := r.db.Beginx()
	if err != nil {
		logr.Errorf("Failed to begin transaction: %v", err)
		return err
	}

	// Insert the seller
	query := `
		INSERT INTO t_sellers (user_id, description, rating)
		VALUES ($1, $2, $3)
		RETURNING id
	`

	var id uint
	err = tx.QueryRowx(query, seller.UserID, seller.Description, seller.Rating).Scan(&id)
	if err != nil {
		tx.Rollback()
		logr.Errorf("Failed to insert seller: %v", err)
		return err
	}

	seller.ID = id

	// Commit the transaction
	if err := tx.Commit(); err != nil {
		logr.Errorf("Failed to commit transaction: %v", err)
		return err
	}

	return nil
}

// Update updates an existing seller
func (r *SellerRepo) Update(seller *models.Seller) error {
	query := `
		UPDATE t_sellers
		SET description = $1, rating = $2
		WHERE id = $3
	`

	_, err := r.db.Exec(query, seller.Description, seller.Rating, seller.ID)
	if err != nil {
		logr.Errorf("Failed to update seller with ID %d: %v", seller.ID, err)
		return err
	}

	return nil
}

// Delete removes a seller
func (r *SellerRepo) Delete(id string) error {
	query := "DELETE FROM t_sellers WHERE id = $1"

	_, err := r.db.Exec(query, id)
	if err != nil {
		logr.Errorf("Failed to delete seller with ID %s: %v", id, err)
		return err
	}

	return nil
}

// UpdateRating updates only the rating field of a seller
func (r *SellerRepo) UpdateRating(id uint, rating float64) error {
	query := "UPDATE t_sellers SET rating = $1 WHERE id = $2"

	_, err := r.db.Exec(query, rating, id)
	if err != nil {
		logr.Errorf("Failed to update rating for seller with ID %d: %v", id, err)
		return err
	}

	return nil
}

// Helper method to get products for a seller
func (r *SellerRepo) getProductsBySellerID(sellerID uint) ([]models.Product, error) {
	var products []models.Product

	query := "SELECT id, name, description, price, seller_id FROM t_products WHERE seller_id = $1"

	err := r.db.Select(&products, query, sellerID)
	if err != nil {
		return nil, err
	}

	return products, nil
}
