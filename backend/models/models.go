package models

type Role string

const (
	UserRole   Role = "user"
	SellerRole Role = "seller"
	AdminRole  Role = "admin"
)

type User struct {
	ID                       uint   `json:"id" gorm:"primaryKey"`
	Name                     string `json:"name"`
	Email                    string `json:"email" gorm:"unique"`
	Password                 string `json:"-"` // Password won't be included in JSON responses
	Role                     Role   `json:"role" gorm:"default:user"`
	ReviewCount              int    `json:"review_count" gorm:"default:0"`
	TotalPurchases           int    `json:"total_purchase"`
	ChallengeProgess         int    `json:"challenge_progress"`
	TotalChallengesCompleted int    `json:"total_challenges_completed"`
}

type Seller struct {
	ID           uint      `json:"id" gorm:"primaryKey"`
	UserID       uint      `json:"user_id"`
	User         User      `json:"user" gorm:"foreignKey:UserID"`
	Description  string    `json:"description"`
	Rating       float64   `json:"rating" gorm:"default:0"`
	ProductsList []uint    `json:"products_list" gorm:"-"`       // Won't be stored directly in the database
	Products     []Product `json:"-" gorm:"foreignKey:SellerID"` // Relationship for ORM, but not included in JSON
}

type Product struct {
	ID          uint    `json:"id" gorm:"primaryKey"`
	Name        string  `json:"name"`
	Description string  `json:"description"`
	Price       float64 `json:"price"`
	SellerID    uint    `json:"seller_id"`
	Seller      Seller  `json:"seller" gorm:"foreignKey:SellerID"`
	Category    string  `json:"category"`
	Clicks      int     `json:"clicks" gorm:"default:0"`
	InStock     bool    `json:"in_stock" gorm:"default:true"`
}
