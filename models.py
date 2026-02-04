#models.py
"""
SQLAlchemy models for the Movie Library app.

Models:
- User: Stores basic User metadata.
- Movie: Stores movie metadata and references a user via a foreign key.

The `db` object is initialized in app.py via `db.init_app(app)`.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """User table.

        Columns:
            id: Integer primary key.
            name: Username (required).

        Relationships:
            pass
    """

    # Define all the User properties
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self) -> str:
        """Return a debug-friendly representation (useful in logs and the Python shell)."""
        return f"<User {self.name}>, ID: {self.id}"

    def __str__(self) -> str:
        """Return a human-friendly string representation (useful for UI output)."""
        return self.name

class Movie(db.Model):
    """Movie table.

        Columns:
            id: Integer primary key.
            name: Movie name string (required).
            director: Movie director string (required).
            year: Release year Integer (required).
            poster_url: URL for movie poster string (required).
            user_id: Foreign key referencing User.id (required).

        Relationships:
            user: The User instance associated with this book.
        """
    # Define all the Movie properties
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    poster_url = db.Column(db.String(255), nullable=False)

    # Link Movie to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self) -> str:
        """Return a debug-friendly representation (useful in logs and the Python shell)."""
        return f"<Movie {self.name}>, ID: {self.id}, Director: {self.director}, Year: {self.year}, Poster URL: {self.poster_url}"

    def __str__(self) -> str:
        """Return a human-friendly string representation (useful for UI output)."""
        return self.name
