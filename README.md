# MoviWeb

A clean, minimal Flask app for managing users and their favorite movies. The app pulls movie details from the OMDb API and stores favorites locally using SQLite.

## Features

-   Create and list users
-   Search OMDb by title and select the correct match
-   Save movie details (title, director, year, poster)
-   Update a movie title locally
-   Delete movies from a user list
-   Responsive, modern UI with a shared base template

## Tech Stack

-   Python
-   Flask
-   SQLAlchemy (SQLite)
-   OMDb API

## Project Structure

```
MovieWebApp/
├─ app.py
├─ data_manager.py
├─ models.py
├─ templates/
├─ static/
├─ data/
├─ requirements.txt
└─ README.md
```

## Setup

1.  Clone the repo and create a virtual environment.
2.  Install dependencies:
    
    ```bash
    pip install -r requirements.txt
    ```
    
3.  Create a `.env` file in the project root:
    
    ```bash
    OMDB_API_KEY=your_api_key_here
    MOVIWEB_SECRET_KEY=your_long_random_secret
    ```
    
4.  Run the app:
    
    ```bash
    python app.py
    ```
    

By default the app runs at `http://localhost:5002`.

## Usage

-   Go to the home page to add and view users.
-   Click a user to view their movie list.
-   Add a movie by title; if multiple results match, select the correct one.
-   Update a movie title locally or delete it from the list.

## Routes

-   `GET /` — user list
-   `POST /users` — add a user
-   `GET /users/<user_id>/movies` — user movies
-   `POST /users/<user_id>/movies` — add a movie (OMDb search)
-   `POST /users/<user_id>/movies/<movie_id>/update` — update a title
-   `POST /users/<user_id>/movies/<movie_id>/delete` — delete a movie

## Environment Variables

-   `OMDB_API_KEY` (required for movie search)
-   `MOVIWEB_SECRET_KEY` (recommended)

## Notes

-   The SQLite database lives in `data/movies.db`.
-   To reset data locally, delete `data/movies.db`.
-   `.env` is ignored by git; use `.env.example` as a template.

##   

##