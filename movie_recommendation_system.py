import streamlit as st
import requests

# Set Page Configuration
st.set_page_config(page_title="Movie Recommender", layout="wide")

# API Keys (Replace with your keys)
TMDB_API_KEY = "abfbc549ac67ff53bdfa216b9377b85f"
OPENWEATHER_API_KEY = "a9dff04f69a498780976ada3861f14f0"

# Base URLs
TMDB_BASE_URL = "https://api.themoviedb.org/3"
OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Helper Functions
def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch data. Please check your API keys or network connection.")
        return {}

def search_movie(query):
    url = f"{TMDB_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={query}"
    return fetch_data(url).get("results", [])

def get_movie_details(movie_id):
    url = f"{TMDB_BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}"
    return fetch_data(url)

def get_recommendations(movie_id):
    url = f"{TMDB_BASE_URL}/movie/{movie_id}/recommendations?api_key={TMDB_API_KEY}"
    return fetch_data(url).get("results", [])

def get_movies_by_genre(genre_id, page=1):
    url = f"{TMDB_BASE_URL}/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&page={page}"
    return fetch_data(url).get("results", [])

def get_weather(city):
    url = f"{OPENWEATHER_BASE_URL}?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    data = fetch_data(url)
    if data:
        temp = data["main"]["temp"]
        condition = data["weather"][0]["description"]
        return temp, condition
    return None, None

def get_weather_based_movies(condition):
    if "clear" in condition:
        return get_movies_by_genre(12)  # Adventure for sunny weather
    elif "rain" in condition or "cloud" in condition:
        return get_movies_by_genre(18)  # Drama for rainy weather
    elif "snow" in condition:
        return get_movies_by_genre(35)  # Comedy for snowy weather
    else:
        return get_movies_by_genre(28)  # Action as default

# Static Background
def set_static_background():
    st.markdown(
        """
        <style>
        .stApp {
            background: url("https://image.tmdb.org/t/p/original/xJWPZIYOEFIjZpBL7SVBGnzRYXp.jpg");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Set static background on page load
set_static_background()

# Sidebar Navigation
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Home", "Genres", "Weather-Based Recommendations", "Real-Time Updates"])

# Main Logic
if menu == "Home":
    st.title("🔍 Search for Movies")
    query = st.text_input("Enter movie name:")
    if query:
        results = search_movie(query)
        if results:
            # Display Most Rated Movie
            top_movie = max(results, key=lambda x: x.get("vote_average", 0))
            st.subheader("Main Result")
            st.image(f"https://image.tmdb.org/t/p/w500{top_movie['poster_path']}", width=200)
            st.write(f"**Title:** {top_movie['title']}")
            st.write(f"**Overview:** {top_movie['overview']}")
            st.write(f"**Release Date:** {top_movie['release_date']}")
            st.write(f"**Rating:** {top_movie['vote_average']} / 10")

            # Recommendations
            recommendations = get_recommendations(top_movie["id"])
            if recommendations:
                st.subheader("Recommended Movies")
                for movie in recommendations[:6]:
                    st.image(f"https://image.tmdb.org/t/p/w500{movie['poster_path']}", width=150)
                    if st.button(f"Details: {movie['title']}", key=movie["id"]):
                        details = get_movie_details(movie["id"])
                        st.image(f"https://image.tmdb.org/t/p/w500{details['poster_path']}")
                        st.write(f"**Overview:** {details['overview']}")

if menu == "Genres":
    st.title("🎭 Explore by Genre")
    genres = {
        "Action": 28,
        "Adventure": 12,
        "Comedy": 35,
        "Drama": 18,
        "Horror": 27,
        "Science Fiction": 878,
        "Romance": 10749
    }
    genre = st.selectbox("Select a Genre", list(genres.keys()))
    page = st.number_input("Page Number", min_value=1, value=1, step=1)
    if genre:
        movies = get_movies_by_genre(genres[genre], page=page)
        st.subheader(f"Movies in {genre} Genre")
        cols = st.columns(4)
        for idx, movie in enumerate(movies[:12]):
            with cols[idx % 4]:
                st.image(f"https://image.tmdb.org/t/p/w500{movie['poster_path']}", width=150)
                st.write(movie["title"])
                if st.button(f"Details {movie['title']}", key=movie["id"]):
                    details = get_movie_details(movie["id"])
                    st.write(f"**Overview:** {details['overview']}")

if menu == "Weather-Based Recommendations":
    st.title("🌤 Weather-Based Recommendations")
    city = st.text_input("Enter your city:")
    if city:
        temp, condition = get_weather(city)
        if temp and condition:
            st.success(f"{city}: {temp}°C, {condition.capitalize()}")
            weather_movies = get_weather_based_movies(condition)
            for movie in weather_movies[:8]:
                st.image(f"https://image.tmdb.org/t/p/w500{movie['poster_path']}", width=150)
                if st.button(f"Details {movie['title']}", key=movie["id"]):
                    details = get_movie_details(movie["id"])
                    st.write(f"**Overview:** {details['overview']}")

if menu == "Real-Time Updates":
    st.title("📅 Real-Time Movie Updates")
    # Get movies released in the past week (implement pagination if needed)
    # For now, it shows the latest 10 popular movies
    url = f"{TMDB_BASE_URL}/discover/movie?api_key={TMDB_API_KEY}&primary_release_date.gte=2024-12-01&sort_by=popularity.desc&page=1"
    real_time_movies = fetch_data(url).get("results", [])
    if real_time_movies:
        st.subheader("Newly Released Movies")
        for movie in real_time_movies[:10]:
            st.image(f"https://image.tmdb.org/t/p/w500{movie['poster_path']}", width=150)
            if st.button(f"Details {movie['title']}", key=movie["id"]):
                details = get_movie_details(movie["id"])
                st.write(f"**Overview:** {details['overview']}")
