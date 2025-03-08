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

func (r *UserRepo) GetAll() ([]models.User, error) {
	var users []models.User
	err := r.db.Select(&users, "SELECT id, name, email, role, password, review_count FROM t_users")
	if err != nil {
		logr.Errorf("Error fetching all users: %v", err)
		return nil, err
	}
	return users, nil
}

func (r *UserRepo) GetById(id string) (*models.User, error) {
	var user models.User
	err := r.db.Get(&user, "SELECT id, name, email, role, password, review_count FROM t_users WHERE id=$1", id)
	if err != nil {
		logr.Errorf("Error fetching user by ID %s: %v", id, err)
		return nil, err
	}
	return &user, nil
}

func (r *UserRepo) GetByEmail(email string) (*models.User, error) {
	var user models.User
	err := r.db.Get(&user, "SELECT id, name, email, password, role, review_count FROM t_users WHERE email=$1", email)
	if err != nil {
		logr.Errorf("Error fetching user by email %s: %v", email, err)
		return nil, err
	}
	return &user, nil
}

func (r *UserRepo) AddUser(user *models.User) error {
	tx := r.db.MustBegin()
	defer func() {
		if r := recover(); r != nil {
			tx.Rollback()
		}
	}()
	query := `INSERT INTO t_users (name, email, password, role) 
              VALUES ($1, $2, $3, $4) RETURNING id`

	err := tx.QueryRow(query, user.Name, user.Email, user.Password, user.Role).Scan(&user.ID)
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
              SET name=$1, email=$2, role=$3, review_count=$4 
              WHERE id=$5`

	_, err := tx.Exec(query, user.Name, user.Email, user.Role, user.ReviewCount, user.ID)
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
