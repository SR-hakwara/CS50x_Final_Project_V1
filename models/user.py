from .database import db
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime


class User:
    @staticmethod
    def create_table():
        """
        Creates the 'users' table if it doesn't exist.
        The table includes columns for user details, authentication, and profile information.
        """
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                hash TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                inscription_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                profile_picture TEXT DEFAULT 'default-avatar.png',
                bio TEXT,
                last_login TIMESTAMP
            )
            """
        )

    @staticmethod
    def create(username, email, password):
        """
        Creates a new user with the provided username, email, and password.
        The password is hashed before being stored in the database.
        """
        hash_ = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (username, email, hash) VALUES (?, ?, ?)",
            username,
            email,
            hash_,
        )

    @staticmethod
    def update(user_id, username, email, password=None):
        """
        Updates the user's username, email, and optionally password.
        If a password is provided, it is hashed before being stored.
        """
        if password:
            hash_ = generate_password_hash(password)
            db.execute(
                "UPDATE users SET username = ?, email = ?, hash = ? WHERE id = ?",
                username,
                email,
                hash_,
                user_id,
            )
        else:
            db.execute(
                "UPDATE users SET username = ?, email = ? WHERE id = ?",
                username,
                email,
                user_id,
            )

    @staticmethod
    def get_by_username(username):
        """
        Retrieves a user by their username.
        """
        return db.execute("SELECT * FROM users WHERE username = ?", username)

    @staticmethod
    def get_by_email(email):
        """
        Retrieves a user by their email.
        """
        return db.execute("SELECT * FROM users WHERE email = ?", email)

    @staticmethod
    def update_last_login(user_id):
        """
        Updates the last login timestamp for the user.
        """
        db.execute(
            "UPDATE users SET last_login = ? WHERE id = ?", datetime.now(), user_id
        )

    @staticmethod
    def check_password(stored_hash, password):
        """
        Checks if the provided password matches the stored hash.
        """
        return check_password_hash(stored_hash, password)