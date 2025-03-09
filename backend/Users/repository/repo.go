package repository

import (
	"Users/models"

	"github.com/jmoiron/sqlx"
	logr "github.com/sirupsen/logrus"
)

type UserRepo struct {
	db *sqlx.DB
}

func NewUserRepo(db *sqlx.DB) *UserRepo {
	return &UserRepo{
		db: db,
	}
}

func (r *UserRepo) AddUser(user *models.User) error {
	tx := r.db.MustBegin()
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()
	query := `INSERT INTO t_users (name, email, password, role, review_count, total_purchase, challenge_progress, total_challenges_completed) 
              VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING id`
	err := tx.QueryRow(query,
		user.Name,
		user.Email,
		user.Password,
		user.Role,
		0, // ReviewCount
		0, // TotalPurchases
		0, // ChallengeProgress
		0, // TotalChallengesCompleted
	).Scan(&user.ID)
	if err != nil {
		tx.Rollback()
		logr.Errorf("Error adding user: %v", err)
		return err
	}
	logr.Debugf("Added user: ID=%d, Name=%s, Role=%s, Email=%s", user.ID, user.Name, user.Role, user.Email)
	err = tx.Commit()
	if err != nil {
		logr.Errorf("Error committing transaction: %v", err)
		return err
	}
	return nil
}

func (r *UserRepo) GetAll() ([]models.User, error) {
	var users []models.User
	err := r.db.Select(&users, "SELECT id, name, email, role, password, review_count, total_purchase, challenge_progress, total_challenges_completed FROM t_users")
	if err != nil {
		logr.Errorf("Error fetching all users: %v", err)
		return nil, err
	}
	return users, nil
}

func (r *UserRepo) GetById(id string) (*models.User, error) {
	var user models.User
	err := r.db.Get(&user, "SELECT id, name, email, role, password, review_count, total_purchase, challenge_progress, total_challenges_completed FROM t_users WHERE id=$1", id)
	if err != nil {
		logr.Errorf("Error fetching user by ID %s: %v", id, err)
		return nil, err
	}
	return &user, nil
}

func (r *UserRepo) GetByEmail(email string) (*models.User, error) {
	var user models.User
	err := r.db.Get(&user, "SELECT id, name, email, password, role, review_count, total_purchase, challenge_progress, total_challenges_completed FROM t_users WHERE email=$1", email)
	if err != nil {
		logr.Errorf("Error fetching user by email %s: %v", email, err)
		return nil, err
	}
	return &user, nil
}

func (r *UserRepo) DeleteUser(id string) error {
	tx := r.db.MustBegin()
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()
	_, err := tx.Exec("DELETE FROM t_users WHERE id = $1", id)
	if err != nil {
		tx.Rollback()
		logr.Errorf("Error deleting user %s: %v", id, err)
		return err
	}
	logr.Debugf("Deleted user %s", id)
	err = tx.Commit()
	if err != nil {
		logr.Errorf("Error committing transaction: %v", err)
		return err
	}
	return nil
}

func (r *UserRepo) UpdateUser(user *models.User) error {
	tx := r.db.MustBegin()
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()
	query := `UPDATE t_users 
              SET name=$1, email=$2, role=$3, review_count=$4, total_purchase=$5, challenge_progress=$6, total_challenges_completed=$7 
              WHERE id=$8`
	_, err := tx.Exec(query,
		user.Name,
		user.Email,
		user.Role,
		user.ReviewCount,
		user.TotalPurchases,
		user.ChallengeProgess,
		user.TotalChallengesCompleted,
		user.ID)
	if err != nil {
		tx.Rollback()
		logr.Errorf("Error updating user %d: %v", user.ID, err)
		return err
	}
	logr.Debugf("Updated user ID=%d", user.ID)
	err = tx.Commit()
	if err != nil {
		logr.Errorf("Error committing transaction: %v", err)
		return err
	}
	return nil
}

func (r *UserRepo) IncrementReviewCount(id uint) error {
	tx := r.db.MustBegin()
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()
	_, err := tx.Exec("UPDATE t_users SET review_count = review_count + 1 WHERE id = $1", id)
	if err != nil {
		tx.Rollback()
		logr.Errorf("Error incrementing review count for user %d: %v", id, err)
		return err
	}
	err = tx.Commit()
	if err != nil {
		logr.Errorf("Error committing transaction: %v", err)
		return err
	}
	return nil
}

// New functions for challenge and purchase tracking
func (r *UserRepo) IncrementTotalPurchases(id uint) error {
	tx := r.db.MustBegin()
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()
	_, err := tx.Exec("UPDATE t_users SET total_purchase = total_purchase + 1 WHERE id = $1", id)
	if err != nil {
		tx.Rollback()
		logr.Errorf("Error incrementing purchase count for user %d: %v", id, err)
		return err
	}
	err = tx.Commit()
	if err != nil {
		logr.Errorf("Error committing transaction: %v", err)
		return err
	}
	return nil
}

func (r *UserRepo) UpdateChallengeProgress(id uint, progress int) error {
	tx := r.db.MustBegin()
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()
	_, err := tx.Exec("UPDATE t_users SET challenge_progress = $1 WHERE id = $2", progress, id)
	if err != nil {
		tx.Rollback()
		logr.Errorf("Error updating challenge progress for user %d: %v", id, err)
		return err
	}
	err = tx.Commit()
	if err != nil {
		logr.Errorf("Error committing transaction: %v", err)
		return err
	}
	return nil
}

func (r *UserRepo) IncrementTotalChallengesCompleted(id uint) error {
	tx := r.db.MustBegin()
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()
	_, err := tx.Exec("UPDATE t_users SET total_challenges_completed = total_challenges_completed + 1 WHERE id = $1", id)
	if err != nil {
		tx.Rollback()
		logr.Errorf("Error incrementing completed challenges for user %d: %v", id, err)
		return err
	}
	err = tx.Commit()
	if err != nil {
		logr.Errorf("Error committing transaction: %v", err)
		return err
	}
	return nil
}
