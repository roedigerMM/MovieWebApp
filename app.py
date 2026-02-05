from flask import Flask, abort, redirect, render_template, request, url_for
from data_manager import DataManager
from models import db, Movie, User
import os
import json
import requests

def load_env(path: str = ".env") -> None:
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value

load_env()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("MOVIWEB_SECRET_KEY", "dev-secret-key")

basedir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(basedir, "data")
os.makedirs(data_dir, exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(data_dir, 'movies.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["OMDB_API_KEY"] = os.environ.get("OMDB_API_KEY")

db.init_app(app)

data_manager = DataManager()

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500

@app.route("/", methods=["GET"])
def index():
    users = data_manager.get_users()
    error = request.args.get("error")
    return render_template("index.html", users=users, error=error)

@app.route("/users", methods=["POST"])
def create_user():
    name = request.form.get("name", "").strip()
    if not name:
        return redirect(url_for("index"))

    created_user = data_manager.create_user(name)
    if created_user is None:
        return redirect(url_for("index", error="User already exists. Please choose a different name."))
    return redirect(url_for("index"))

@app.route("/users/<int:user_id>/movies", methods=["GET"])
def user_movies(user_id: int):
    user = data_manager.get_user(user_id)
    if user is None:
        abort(404)

    movies = data_manager.get_movies(user_id)
    error = request.args.get("error")
    return render_template("user_movies.html", user=user, movies=movies, error=error)

def fetch_movie_details(title: str):
    api_key = app.config.get("OMDB_API_KEY")
    if not api_key:
        return None, "OMDb API key is missing. Set OMDB_API_KEY in your environment."

    try:
        response = requests.get(
            "https://www.omdbapi.com/",
            params={"t": title, "apikey": api_key},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return None, "Unable to reach OMDb. Please try again."
    except json.JSONDecodeError:
        return None, "OMDb returned invalid data."

    if data.get("Response") != "True":
        return None, data.get("Error", "Movie not found.")

    year_raw = (data.get("Year") or "").strip()
    year_digits = "".join([c for c in year_raw if c.isdigit()])
    year = int(year_digits[:4]) if len(year_digits) >= 4 else None
    if year is None:
        return None, "OMDb did not provide a valid release year."

    poster_url = (data.get("Poster") or "").strip()
    if not poster_url or poster_url == "N/A":
        return None, "OMDb did not provide a poster URL."

    director = (data.get("Director") or "").strip()
    if not director or director == "N/A":
        return None, "OMDb did not provide a director."

    return {
        "title": (data.get("Title") or title).strip(),
        "director": director,
        "year": year,
        "poster_url": poster_url,
    }, None

def search_movies(title: str):
    api_key = app.config.get("OMDB_API_KEY")
    if not api_key:
        return None, "OMDb API key is missing. Set OMDB_API_KEY in your environment."

    try:
        response = requests.get(
            "https://www.omdbapi.com/",
            params={"s": title, "apikey": api_key},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return None, "Unable to reach OMDb. Please try again."
    except json.JSONDecodeError:
        return None, "OMDb returned invalid data."

    if data.get("Response") != "True":
        return None, data.get("Error", "Movie not found.")

    results = []
    for item in data.get("Search", []):
        imdb_id = (item.get("imdbID") or "").strip()
        if not imdb_id:
            continue
        results.append(
            {
                "imdb_id": imdb_id,
                "title": (item.get("Title") or "").strip(),
                "year": (item.get("Year") or "").strip(),
                "poster_url": (item.get("Poster") or "").strip(),
            }
        )

    if not results:
        return None, "Movie not found."

    return results, None

def fetch_movie_details_by_id(imdb_id: str):
    api_key = app.config.get("OMDB_API_KEY")
    if not api_key:
        return None, "OMDb API key is missing. Set OMDB_API_KEY in your environment."

    try:
        response = requests.get(
            "https://www.omdbapi.com/",
            params={"i": imdb_id, "apikey": api_key},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return None, "Unable to reach OMDb. Please try again."
    except json.JSONDecodeError:
        return None, "OMDb returned invalid data."

    if data.get("Response") != "True":
        return None, data.get("Error", "Movie not found.")

    year_raw = (data.get("Year") or "").strip()
    year_digits = "".join([c for c in year_raw if c.isdigit()])
    year = int(year_digits[:4]) if len(year_digits) >= 4 else None
    if year is None:
        return None, "OMDb did not provide a valid release year."

    poster_url = (data.get("Poster") or "").strip()
    if not poster_url or poster_url == "N/A":
        return None, "OMDb did not provide a poster URL."

    director = (data.get("Director") or "").strip()
    if not director or director == "N/A":
        return None, "OMDb did not provide a director."

    return {
        "title": (data.get("Title") or "").strip(),
        "director": director,
        "year": year,
        "poster_url": poster_url,
    }, None

@app.route("/users/<int:user_id>/movies", methods=["POST"])
def add_user_movie(user_id: int):
    user = data_manager.get_user(user_id)
    if user is None:
        abort(404)

    title = request.form.get("title", "").strip()
    imdb_id = request.form.get("imdb_id", "").strip()
    if not title:
        return redirect(url_for("user_movies", user_id=user_id, error="Please provide a movie title."))

    if imdb_id:
        details, error = fetch_movie_details_by_id(imdb_id)
        if error:
            return redirect(url_for("user_movies", user_id=user_id, error=error))
    else:
        results, error = search_movies(title)
        if error:
            return redirect(url_for("user_movies", user_id=user_id, error=error))

        if len(results) == 1:
            details, error = fetch_movie_details_by_id(results[0]["imdb_id"])
            if error:
                return redirect(url_for("user_movies", user_id=user_id, error=error))
        else:
            movies = data_manager.get_movies(user_id)
            return render_template(
                "user_movies.html",
                user=user,
                movies=movies,
                search_results=results,
                search_title=title,
                error=None,
            )

    movie = Movie(
        name=details["title"],
        director=details["director"],
        year=details["year"],
        poster_url=details["poster_url"],
        user_id=user_id,
    )
    data_manager.add_movie(movie)
    return redirect(url_for("user_movies", user_id=user_id))

@app.route("/users/<int:user_id>/movies/<int:movie_id>/update", methods=["POST"])
def update_user_movie(user_id: int, movie_id: int):
    user = data_manager.get_user(user_id)
    if user is None:
        abort(404)

    new_title = request.form.get("title", "").strip()
    if not new_title:
        return redirect(url_for("user_movies", user_id=user_id))

    try:
        movie = data_manager.get_movie(movie_id)
        if movie is None or movie.user_id != user_id:
            abort(404)
        data_manager.update_movie(movie_id, new_title)
    except ValueError:
        abort(404)

    return redirect(url_for("user_movies", user_id=user_id))

@app.route("/users/<int:user_id>/movies/<int:movie_id>/delete", methods=["POST"])
def delete_user_movie(user_id: int, movie_id: int):
    user = data_manager.get_user(user_id)
    if user is None:
        abort(404)

    try:
        movie = data_manager.get_movie(movie_id)
        if movie is None or movie.user_id != user_id:
            abort(404)
        data_manager.delete_movie(movie_id)
    except ValueError:
        abort(404)

    return redirect(url_for("user_movies", user_id=user_id))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5002, debug=True)
