from flask import Flask, abort, redirect, render_template, request, url_for
from data_manager import DataManager
from models import db, Movie, User
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("MOVIWEB_SECRET_KEY", "dev-secret-key")

basedir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(basedir, "data")
os.makedirs(data_dir, exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(data_dir, 'movies.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

data_manager = DataManager()

@app.route("/", methods=["GET"])
def home():
    users = data_manager.get_users()
    error = request.args.get("error")
    return render_template("home.html", users=users, error=error)

@app.route("/users", methods=["POST"])
def create_user():
    name = request.form.get("name", "").strip()
    if not name:
        return redirect(url_for("home"))

    created_user = data_manager.create_user(name)
    if created_user is None:
        return redirect(url_for("home", error="User already exists. Please choose a different name."))
    return redirect(url_for("home"))

@app.route("/users/<int:user_id>/movies", methods=["GET"])
def user_movies(user_id: int):
    user = User.query.get(user_id)
    if user is None:
        abort(404)

    movies = data_manager.get_movies(user_id)
    return render_template("user_movies.html", user=user, movies=movies)

@app.route("/users/<int:user_id>/movies", methods=["POST"])
def add_user_movie(user_id: int):
    user = User.query.get(user_id)
    if user is None:
        abort(404)

    title = request.form.get("title", "").strip()
    director = request.form.get("director", "").strip()
    year_raw = request.form.get("year", "").strip()
    poster_url = request.form.get("poster_url", "").strip()

    if not title or not director or not year_raw or not poster_url:
        return redirect(url_for("user_movies", user_id=user_id))

    try:
        year = int(year_raw)
    except ValueError:
        return redirect(url_for("user_movies", user_id=user_id))

    movie = Movie(
        name=title,
        director=director,
        year=year,
        poster_url=poster_url,
        user_id=user_id,
    )
    data_manager.add_movie(movie)
    return redirect(url_for("user_movies", user_id=user_id))

@app.route("/users/<int:user_id>/movies/<int:movie_id>/update", methods=["POST"])
def update_user_movie(user_id: int, movie_id: int):
    user = User.query.get(user_id)
    if user is None:
        abort(404)

    new_title = request.form.get("title", "").strip()
    if not new_title:
        return redirect(url_for("user_movies", user_id=user_id))

    try:
        data_manager.update_movie(movie_id, new_title)
    except ValueError:
        abort(404)

    return redirect(url_for("user_movies", user_id=user_id))

@app.route("/users/<int:user_id>/movies/<int:movie_id>/delete", methods=["POST"])
def delete_user_movie(user_id: int, movie_id: int):
    user = User.query.get(user_id)
    if user is None:
        abort(404)

    try:
        data_manager.delete_movie(movie_id)
    except ValueError:
        abort(404)

    return redirect(url_for("user_movies", user_id=user_id))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5002, debug=True)
