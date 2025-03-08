package repository

import (
	"Users/models"
	"github.com/jmoiron/sqlx"
	logr "github.com/sirupsen/logrus"
)

type ProductRepo struct {
	db *sqlx.DB
}

func NewProductRepo(db *sqlx.DB) *ProductRepo {
	return &ProductRepo{
		db: db,
	}
}

func (r *ProductRepo) GetAll() ([]models.Product, error) {
	var products []models.Product
	err := r.db.Select(&products, `
		SELECT p.id, p.name, p.description, p.price, p.seller_id, 
		       p.category, p.clicks, p.in_stock, 
		       s.id as "seller.id", s.name as "seller.name"
		FROM t_products p
		LEFT JOIN t_sellers s ON p.seller_id = s.id
	`)
	if err != nil {
		logr.Errorf("Error fetching all products: %v", err)
		return nil, err
	}
	return products, nil
}

func (r *ProductRepo) GetById(id string) (*models.Product, error) {
	var product models.Product
	err := r.db.Get(&product, `
		SELECT p.id, p.name, p.description, p.price, p.seller_id, 
		       p.category, p.clicks, p.in_stock, 
		       s.id as "seller.id", s.name as "seller.name"
		FROM t_products p
		LEFT JOIN t_sellers s ON p.seller_id = s.id
		WHERE p.id=$1
	`, id)
	if err != nil {
		logr.Errorf("Error fetching product by ID %s: %v", id, err)
		return nil, err
	}
	return &product, nil
}

func (r *ProductRepo) GetByCategory(category string) ([]models.Product, error) {
	var products []models.Product
	err := r.db.Select(&products, `
		SELECT p.id, p.name, p.description, p.price, p.seller_id, 
		       p.category, p.clicks, p.in_stock, 
		       s.id as "seller.id", s.name as "seller.name"
		FROM t_products p
		LEFT JOIN t_sellers s ON p.seller_id = s.id
		WHERE p.category=$1
	`, category)
	if err != nil {
		logr.Errorf("Error fetching products by category %s: %v", category, err)
		return nil, err
	}
	return products, nil
}

func (r *ProductRepo) GetBySeller(sellerID string) ([]models.Product, error) {
	var products []models.Product
	err := r.db.Select(&products, `
		SELECT p.id, p.name, p.description, p.price, p.seller_id, 
		       p.category, p.clicks, p.in_stock, 
		       s.id as "seller.id", s.name as "seller.name"
		FROM t_products p
		LEFT JOIN t_sellers s ON p.seller_id = s.id
		WHERE p.seller_id=$1
	`, sellerID)
	if err != nil {
		logr.Errorf("Error fetching products by seller ID %s: %v", sellerID, err)
		return nil, err
	}
	return products, nil
}

func (r *ProductRepo) Create(product *models.Product) error {
	query := `
		INSERT INTO t_products (name, description, price, seller_id, category, in_stock)
		VALUES ($1, $2, $3, $4, $5, $6) RETURNING id
	`
	var id uint
	err := r.db.QueryRow(query, product.Name, product.Description, product.Price,
		product.SellerID, product.Category, product.InStock).Scan(&id)
	if err != nil {
		logr.Errorf("Error creating product: %v", err)
		return err
	}
	product.ID = id
	return nil
}

func (r *ProductRepo) Update(product *models.Product) error {
	query := `
		UPDATE t_products
		SET name = $1, description = $2, price = $3, category = $4, in_stock = $5
		WHERE id = $6
	`
	_, err := r.db.Exec(query, product.Name, product.Description, product.Price,
		product.Category, product.InStock, product.ID)
	if err != nil {
		logr.Errorf("Error updating product with ID %d: %v", product.ID, err)
		return err
	}
	return nil
}

func (r *ProductRepo) IncrementClicks(id string) error {
	_, err := r.db.Exec("UPDATE t_products SET clicks = clicks + 1 WHERE id = $1", id)
	if err != nil {
		logr.Errorf("Error incrementing clicks for product ID %s: %v", id, err)
		return err
	}
	return nil
}

func (r *ProductRepo) Delete(id string) error {
	_, err := r.db.Exec("DELETE FROM t_products WHERE id = $1", id)
	if err != nil {
		logr.Errorf("Error deleting product with ID %s: %v", id, err)
		return err
	}
	return nil
}
