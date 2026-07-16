# Movie Database CLI Project

## Project Overview

This is a small Python movie database CLI application with SQLite storage (SQLAlchemy). The app:

- Integrates with the OMDb API to fetch movie metadata
- Persists movie records in SQLite via SQLAlchemy
- Provides CRUD commands (add, list, update, delete)
- Generates a static HTML site from a template located in `_static/`

## Repository Structure

- `movies.py` - Main CLI application and command dispatch logic
- `movie_storage_sql.py` - SQLite + SQLAlchemy database access functions
- `_static/` - Static site template and styles
  - `index_template.html` - HTML template containing the `__TEMPLATE_MOVIE_GRID__` placeholder
  - `style.css` - CSS used by the generated site
- `movies.db` - (optional) SQLite database file created in the project root by default
- `unit_tests.py` - Simple validation script for storage functions
- `.env.example` - Example environment file (copy to `.env` and add your OMDb key)

## Key Features

- Add movies using OMDb metadata
- List movies from the local database
- Delete and update movie records (with existence checks)
- Statistics: average, median, best and worst rated movies
- Random movie and sorted-by-rating views
- Generate a static website at `_static/movie_app.html`

## Installation

1. Install Python 3.10+ (or compatible).
2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and add your OMDb API key (see Configuration).

## Configuration (.env)

This project now uses environment variables for secrets. Create a `.env` file in the project root (do not commit it):

```
OMDb_API_key=your_real_api_key_here
# optional: change DB location
# MOVIE_DB_URL=sqlite:///data/movies.db
```

- The code uses `python-dotenv` to load `.env` automatically.
- If you prefer, you can set `OMDb_API_key` in your shell environment instead of using `.env`.
- Optionally set `MOVIE_DB_URL` to point to a different SQLite file or another database URL.

## Usage

Run the CLI from the project root:

```bash
python movies.py
```

Menu mapping (numbers shown in the CLI):

- `0` — Exit
- `1` — List movies
- `2` — Add movie (fetches metadata from OMDb)
- `3` — Delete movie
- `4` — Update movie rating
- `5` — Statistics (count, year range, average, median, best/worst)
- `6` — Random movie
- `7` — Search local DB by title (partial match)
- `8` — Movies sorted by rating
- `9` — Generate website (writes `_static/movie_app.html`)

The generated website is saved to `_static/movie_app.html` so that it can reference the stylesheet in the same folder.

## Database Notes

- By default the app uses `sqlite:///movies.db` (a file named `movies.db` in the project root).
- To change location set `MOVIE_DB_URL` in `.env` or the environment.
- The `movies` table columns are: `id`, `title`, `year`, `rating`, `poster_image_url`.

## Testing

Run the provided `unit_tests.py` script to exercise basic storage operations:

```bash
python unit_tests.py
```

This script performs a simple add/list/update/delete cycle using `movie_storage_sql.py` functions.

## Developer Notes

- `movie_storage_sql.py` now returns boolean success flags for write operations and provides case-insensitive search helpers (`get_movie_by_title`, `find_movies_by_title`).
- SQL logging is disabled by default (`echo=False`) to avoid leaking SQL during normal runs; set `echo=True` directly in the file while debugging if needed.
- The CLI performs existence checks for delete/update operations and reports failures rather than silently succeeding.

## .env.example

Copy `.env.example` to `.env` and set `OMDb_API_key`. Do not commit your `.env` file.

## Additional Recommendations

1. Add unit tests (pytest) for the CLI and storage layer.
2. Add input validation for years and ratings when adding/updating movies.
3. Consider packaging and a small web frontend if you want to serve the generated page dynamically.

---

If you'd like, I can also add a short `Makefile` with `setup`, `run` and `generate-site` targets to streamline local usage.
