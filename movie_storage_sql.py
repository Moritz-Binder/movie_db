import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

DB_URL = os.environ.get("MOVIE_DB_URL", "sqlite:///movies.db")
engine = create_engine(DB_URL, echo=False, future=True)

with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster_image_url TEXT NOT NULL
        )
    """))
    connection.commit()


def get_raw_list_movies():
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT title, year, rating, poster_image_url FROM movies ORDER BY title"))
        return result.fetchall()


def get_list_movies():
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT title, year, rating, poster_image_url FROM movies ORDER BY title"))
        movies = result.fetchall()

    return {row[0]: {"year": row[1], "rating": row[2], "url": row[3]} for row in movies}


def get_movie_by_title(title):
    """Find a movie by exact title, case-insensitive."""
    with engine.connect() as connection:
        result = connection.execute(
            text(
                "SELECT title, year, rating, poster_image_url FROM movies WHERE LOWER(title) = :title"
            ),
            {"title": title.lower()},
        )
        return result.fetchone()


def find_movies_by_title(search):
    """Search for movies by partial title, case-insensitive."""
    query = f"%{search.lower()}%"
    with engine.connect() as connection:
        result = connection.execute(
            text(
                "SELECT title, year, rating, poster_image_url FROM movies"
                " WHERE LOWER(title) LIKE :query ORDER BY title"
            ),
            {"query": query},
        )
        return result.fetchall()


def add_movie(title, year, rating, url):
    """Add a new movie to the database."""
    with engine.connect() as connection:
        try:
            connection.execute(
                text(
                    "INSERT INTO movies (title, year, rating, poster_image_url)"
                    " VALUES (:title, :year, :rating, :poster_image_url)"
                ),
                {
                    "title": title,
                    "year": year,
                    "rating": rating,
                    "poster_image_url": url,
                },
            )
            connection.commit()
            return True
        except IntegrityError:
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False


def delete_movie(title):
    """Delete a movie from the database."""
    with engine.connect() as connection:
        result = connection.execute(text("DELETE FROM movies WHERE title = :title"), {"title": title})
        connection.commit()
        return result.rowcount > 0


def update_movie(title, rating):
    """Update a movie's rating in the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text("UPDATE movies SET rating = :rating WHERE title = :title"),
            {"title": title, "rating": rating},
        )
        connection.commit()
        return result.rowcount > 0
