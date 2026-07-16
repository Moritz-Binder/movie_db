import os
import random
import json
import pandas as pd
import requests
from dotenv import load_dotenv
from requests.exceptions import RequestException
import movie_storage_sql as storage

load_dotenv()


def load_credentials():
    """Load the OMDb API key from the .env file or environment variables."""
    api_key = os.environ.get("OMDb_API_key")
    if not api_key:
        raise ValueError(
            "OMDb_API_key not found. Create a .env file with OMDb_API_key=<your key> "
            "or set the environment variable."
        )

    return {"OMDb_API_key": api_key}


def get_movie_from_api(title, api_key):
    """Retrieve detailed movie data from the OMDb API."""
    url = "http://www.omdbapi.com/"
    params = {"apikey": api_key, "t": title, "type": "movie"}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "Error" in data:
            print(f"API Error: {data['Error']}")
            return None

        return data

    except requests.exceptions.Timeout:
        print("Error: The request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Check your internet connection.")
    except RequestException as e:
        print(f"An unexpected error occurred: {e}")

    return None


def command_list_movies():
    """List all movies stored in the local database."""
    movies = storage.get_list_movies()
    if not movies:
        print("No movies found.")
        return

    print(f"{len(movies)} movies in total")
    for movie, data in movies.items():
        print(f"{movie} ({data['year']}): {data['rating']}")


def command_add_movie():
    """Add a movie to the local database using OMDb data."""
    title = input("Movie title: ").strip()
    if not title:
        print("Movie title cannot be empty.")
        return

    try:
        config = load_credentials()
    except (FileNotFoundError, ValueError) as error:
        print(error)
        return

    api_key = config["OMDb_API_key"]
    data = get_movie_from_api(title, api_key)
    if data is None:
        return

    movie_title = data.get("Title")
    year = data.get("Year")
    rating = data.get("imdbRating")
    url = data.get("Poster") or ""

    if not movie_title or not year or not rating:
        print("Incomplete movie data received from OMDb. Movie was not added.")
        return

    success = storage.add_movie(movie_title, year, rating, url)
    if success:
        print(f"Movie '{movie_title}' added successfully.")
    else:
        print(f"Could not add '{movie_title}'. It may already exist.")


def command_delete_movie():
    """Delete a movie from the local database."""
    title = input("Movie title to delete from records: ").strip()
    if not title:
        print("Movie title cannot be empty.")
        return

    movie = storage.get_movie_by_title(title)
    if not movie:
        print(f"Movie '{title}' not found in the database.")
        return

    choice = input(f"Are you sure you want to delete '{movie[0]}' from the records? (y/n) ").strip().lower()
    if choice != "y":
        print("Delete cancelled.")
        return

    deleted = storage.delete_movie(movie[0])
    if deleted:
        print(f"Movie '{movie[0]}' deleted successfully.")
    else:
        print(f"Movie '{movie[0]}' could not be deleted.")


def command_update_movie():
    """Update the rating of an existing movie."""
    title = input("Movie title to update the rating in the records: ").strip()
    if not title:
        print("Movie title cannot be empty.")
        return

    movie = storage.get_movie_by_title(title)
    if not movie:
        print(f"Movie '{title}' not found in the database.")
        return

    rating_text = input("New movie rating: ").strip()
    try:
        rating = float(rating_text)
    except ValueError:
        print("Please enter a valid numeric rating.")
        return

    choice = input(f"Are you sure you want to update '{movie[0]}' rating to {rating}? (y/n) ").strip().lower()
    if choice != "y":
        print("Update cancelled.")
        return

    updated = storage.update_movie(movie[0], rating)
    if updated:
        print(f"Movie '{movie[0]}' updated successfully.")
    else:
        print(f"Movie '{movie[0]}' could not be updated.")


def command_statistics():
    """Show movie statistics including average, median, best and worst movies."""
    raw_movies = storage.get_raw_list_movies()
    if not raw_movies:
        print("No movies found.")
        return

    movies_df = pd.DataFrame(raw_movies, columns=["title", "year", "rating", "url"])
    movies_df["rating"] = pd.to_numeric(movies_df["rating"], errors="coerce")
    movies_df["year"] = pd.to_numeric(movies_df["year"], errors="coerce")

    count = len(movies_df)
    min_year = int(movies_df["year"].min())
    max_year = int(movies_df["year"].max())
    average_rating = movies_df["rating"].mean()
    median_rating = movies_df["rating"].median()

    best_movies = movies_df.sort_values("rating", ascending=False).head(3)
    worst_movies = movies_df.sort_values("rating", ascending=True).head(3)

    print(f"The database has {count} movies saved,")
    print(f"with movies ranging from the year {min_year} until {max_year}.")
    print(f"Average rating: {average_rating:.2f}")
    print(f"Median rating: {median_rating:.2f}")
    print("Best-rated movies:")
    for _, row in best_movies.iterrows():
        print(f" - {row['title']} ({int(row['year'])}) rating {row['rating']}")
    print("Worst-rated movies:")
    for _, row in worst_movies.iterrows():
        print(f" - {row['title']} ({int(row['year'])}) rating {row['rating']}")


def command_random_movie():
    """Show a randomly selected movie from the local database."""
    movies = storage.get_list_movies()
    if not movies:
        print("No movies found.")
        return

    title, data = random.choice(list(movies.items()))
    print(f"Random movie: {title} ({data['year']}) - Rating: {data['rating']}")


def command_search_movie():
    """Search for a movie in the local database by title."""
    query = input("Movie title: ").strip()
    if not query:
        print("Search term cannot be empty.")
        return

    results = storage.find_movies_by_title(query)
    if not results:
        print(f"No movies found matching '{query}'.")
        return

    print(f"Found {len(results)} movie(s):")
    for row in results:
        print(f" - {row[0]} ({row[1]}) rating {row[2]}")


def command_movies_sorted_by_rating():
    """List movies sorted by rating from highest to lowest."""
    movies = storage.get_list_movies()
    if not movies:
        print("No movies found.")
        return

    sorted_movies = sorted(movies.items(), key=lambda item: float(item[1]["rating"]), reverse=True)
    for title, data in sorted_movies:
        print(f"{title} ({data['year']}): {data['rating']}")


def command_generate_webside():
    """Generate a static website for the current movie collection."""
    print("Generating website...")
    template_filename = os.path.join("_static", "index_template.html")
    if not os.path.exists(template_filename):
        print(f"Error: Template file '{template_filename}' not found.")
        return

    try:
        with open(template_filename, "r", encoding="utf-8") as file:
            html_template = file.read()
    except IOError as e:
        print(f"Error reading the template file: {e}")
        return

    movies = storage.get_list_movies()
    grid_items = ""
    for title, data in movies.items():
        year = data.get("year", "N/A")
        rating = data.get("rating", "N/A")
        poster_url = data.get("url") or "https://via.placeholder.com/300x450?text=No+Poster"

        grid_items += f"""
        <li class=\"movie-card\">
            <img src=\"{poster_url}\" alt=\"{title} poster\">
            <div class=\"movie-content\">
                <h3>{title}</h3>
                <p>Year: {year}</p>
                <p>Rating: {rating}</p>
            </div>
        </li>
        """

    if "__TEMPLATE_MOVIE_GRID__" not in html_template:
        print("Warning: The placeholder '__TEMPLATE_MOVIE_GRID__' was not found in the template.")

    final_html = html_template.replace("__TEMPLATE_MOVIE_GRID__", grid_items)
    output_filename = os.path.join("_static", "movie_app.html")

    try:
        with open(output_filename, "w", encoding="utf-8") as file:
            file.write(final_html)
        print(f"Success! Website generated as '{output_filename}'.")
    except IOError as e:
        print(f"Error writing the output HTML file: {e}")


def show_menu_and_get_input():
    """Show the menu and get user input."""
    print("Menu:")
    for key, value in FUNCTIONS.items():
        print(f"{key}. {value[1]}")

    while True:
        try:
            choice = int(input("Select an option: "))
            if choice in FUNCTIONS:
                return FUNCTIONS[choice][0]
        except ValueError:
            pass
        print("Try again...")

FUNCTIONS = {
    0: (quit, "Exit"),
    1: (command_list_movies, "List movies"),
    2: (command_add_movie, "Add movie"),
    3: (command_delete_movie, "Delete movie"),
    4: (command_update_movie, "Update movie"),
    5: (command_statistics, "Stats"),
    6: (command_random_movie, "Random movie"),
    7: (command_search_movie, "Search movie"),
    8: (command_movies_sorted_by_rating, "Movies sorted by rating"),
    9: (command_generate_webside, "Generate website"),
}


def main():
    while True:
        choice_func = show_menu_and_get_input()
        choice_func()


if __name__ == "__main__":
    main()
