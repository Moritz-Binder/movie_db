from movie_storage_sql import add_movie, get_list_movies, delete_movie, update_movie

# Test adding a movie
add_movie("Inception", 2010, 8.8)

# Test listing movies
movies = get_list_movies()
print(movies)

# Test updating a movie's rating
update_movie("Inception", 9.0)
print(get_list_movies())

# Test deleting a movie
delete_movie("Inception")
print(get_list_movies())  # Should be empty if it was the only movie