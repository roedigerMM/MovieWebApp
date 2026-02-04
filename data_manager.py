from models import db, User, Movie

class DataManager():
    # Define Crud operations as methods
    # --- Users ---
    def create_user(self, name):
        """Add a new user to the database and return it."""
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def get_users(self) -> list[User]:
        """Get all users from the database."""
        return User.query.order_by(User.id.asc()).all()

    # --- Movies ---
    def get_movies(self, user_id: int) -> list[Movie]:
        """Return a list of all movies for a specific user."""
        return Movie.query.filter_by(user_id=user_id).order_by(Movie.id.asc()).all()

    def add_movie(self, movie: Movie) -> Movie:
        """Add a movie to the database.

        Expected: `movie` is a Movie ORM object created in app.py (including user_id).
        """
        db.session.add(movie)
        db.session.commit()
        return movie

    def update_movie(self, movie_id: int, new_title: str) -> Movie:
        """Update the title of a specific movie and return the updated movie."""
        movie = Movie.query.get(movie_id)
        if movie is None:
            raise ValueError(f"Movie with id={movie_id} not found")

        movie.name = new_title
        db.session.commit()
        return movie

    def delete_movie(self, movie_id: int) -> None:
        """Delete a movie by id."""
        movie = Movie.query.get(movie_id)
        if movie is None:
            raise ValueError(f"Movie with id={movie_id} not found")

        db.session.delete(movie)
        db.session.commit()


