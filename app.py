import streamlit as st
import pickle
import pandas as pd
import requests

API_KEY = '74fbc12e39284a6df924842591bd4992'

st.set_page_config(page_title="Movie Recommender", layout="wide")

MOOD_GENRE_MAP = {
    "😊 Happy": [35, 10751, 16],
    "😢 Sad": [18, 10749],
    "😱 Thrilling": [28, 53, 80],
    "😨 Scary": [27, 9648],
    "🚀 Adventurous": [12, 14, 878],
    "❤️ Romantic": [10749, 35],
    "🤔 Thoughtful": [99, 36, 10770],
}

def fetch_poster_and_rating(movie_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
    )
    data = response.json()
    poster = "https://image.tmdb.org/t/p/w500/" + data['poster_path'] if data.get('poster_path') else "https://via.placeholder.com/500x750?text=No+Poster"
    rating = round(data.get('vote_average', 0), 1)
    return poster, rating


def fetch_movie_details(movie_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
    )
    return response.json()


def fetch_movies_by_mood(genre_ids):
    genre_str = ",".join(str(g) for g in genre_ids)
    response = requests.get(
        f'https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_genres={genre_str}&sort_by=popularity.desc&page=1'
    )
    data = response.json()
    results = data.get('results', [])[:10]
    movies_out = []
    for m in results:
        poster = "https://image.tmdb.org/t/p/w500/" + m['poster_path'] if m.get('poster_path') else "https://via.placeholder.com/500x750?text=No+Poster"
        movies_out.append({
            'id': m['id'],
            'title': m['title'],
            'poster': poster,
            'rating': round(m.get('vote_average', 0), 1),
            'overview': m.get('overview', '')
        })
    return movies_out


def get_star_display(rating):
    stars = round(rating / 2)
    return "⭐" * stars + "☆" * (5 - stars)


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:21]

    recommended_movies = []
    recommended_movies_poster = []
    recommended_movie_ids = []
    recommended_movies_rating = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        poster, rating = fetch_poster_and_rating(movie_id)
        recommended_movies_poster.append(poster)
        recommended_movie_ids.append(movie_id)
        recommended_movies_rating.append(rating)

    return recommended_movies, recommended_movies_poster, recommended_movie_ids, recommended_movies_rating


def show_movie_details(movie_id, movie_title):
    details = fetch_movie_details(movie_id)
    poster, rating = fetch_poster_and_rating(movie_id)

    st.markdown("---")
    st.subheader(f"📽️ {movie_title}")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(poster, width=250)

    with col2:
        genres = ", ".join([g['name'] for g in details.get('genres', [])])
        release = details.get('release_date', 'N/A')
        runtime = details.get('runtime', 'N/A')
        overview = details.get('overview', 'No overview available.')
        tagline = details.get('tagline', '')
        votes = details.get('vote_count', 0)

        if tagline:
            st.markdown(f"*{tagline}*")

        st.markdown(f"⭐ **Rating:** {rating}/10  {get_star_display(rating)}")
        st.markdown(f"🗳️ **Votes:** {votes:,}")
        st.markdown(f"📅 **Release Date:** {release}")
        st.markdown(f"🎭 **Genres:** {genres}")
        st.markdown(f"🕒 **Runtime:** {runtime} mins")
        st.markdown(f"📝 **Overview:** {overview}")

    if st.button("❌ Close Details"):
        st.session_state.selected_movie_id = None
        st.session_state.selected_movie_title = None
        st.session_state.show_recommendations = False
        st.rerun()


# Load data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Session state init
if 'selected_movie_id' not in st.session_state:
    st.session_state.selected_movie_id = None
if 'selected_movie_title' not in st.session_state:
    st.session_state.selected_movie_title = None
if 'show_recommendations' not in st.session_state:
    st.session_state.show_recommendations = False
if 'recommended_movie_names' not in st.session_state:
    st.session_state.recommended_movie_names = []
if 'recommended_movie_posters' not in st.session_state:
    st.session_state.recommended_movie_posters = []
if 'recommended_movie_ids' not in st.session_state:
    st.session_state.recommended_movie_ids = []
if 'recommended_movie_ratings' not in st.session_state:
    st.session_state.recommended_movie_ratings = []

# UI
st.title('🎬 Movie Recommender System')

tab1, tab2 = st.tabs(["🎯 Recommend by Movie", "😊 Recommend by Mood"])

# ---- TAB 1: Normal Recommender ----
with tab1:
    selected_movie_name = st.selectbox(
        'Select a movie',
        movies['title'].values
    )

    if st.button('Show Recommendation'):
        st.session_state.selected_movie_id = None
        st.session_state.selected_movie_title = None

        with st.spinner('Finding best movies for you...'):
            names, posters, ids, ratings = recommend(selected_movie_name)
            st.session_state.recommended_movie_names = names
            st.session_state.recommended_movie_posters = posters
            st.session_state.recommended_movie_ids = ids
            st.session_state.recommended_movie_ratings = ratings
            st.session_state.show_recommendations = True

    # Always show recommendations if they exist in session
    if st.session_state.show_recommendations and st.session_state.recommended_movie_names:
        st.markdown("### Recommended Movies (click a title to see details)")

        for i in range(0, 20, 5):
            cols = st.columns(5)
            for j in range(5):
                movie_index = i + j
                with cols[j]:
                    st.image(st.session_state.recommended_movie_posters[movie_index])
                    rating = st.session_state.recommended_movie_ratings[movie_index]
                    st.markdown(f"⭐ **{rating}/10**")
                    st.markdown(get_star_display(rating))
                    if st.button(
                        st.session_state.recommended_movie_names[movie_index],
                        key=f"btn_{movie_index}"
                    ):
                        st.session_state.selected_movie_id = st.session_state.recommended_movie_ids[movie_index]
                        st.session_state.selected_movie_title = st.session_state.recommended_movie_names[movie_index]

        # Show details INSIDE tab1 so it stays visible
        if st.session_state.selected_movie_id:
            show_movie_details(
                st.session_state.selected_movie_id,
                st.session_state.selected_movie_title
            )

# ---- TAB 2: Mood Based ----
with tab2:
    st.markdown("### 🎭 What's your mood today?")
    st.markdown("Pick a mood and we'll suggest the best movies for you!")

    mood = st.selectbox("Select your mood", list(MOOD_GENRE_MAP.keys()))

    if st.button("Find Movies for my Mood 🎬"):
        genre_ids = MOOD_GENRE_MAP[mood]

        with st.spinner('Finding mood based movies...'):
            mood_movies = fetch_movies_by_mood(genre_ids)

        st.markdown(f"### Top movies for **{mood}** mood:")

        cols = st.columns(5)
        for idx, m in enumerate(mood_movies):
            with cols[idx % 5]:
                st.image(m['poster'])
                st.markdown(f"**{m['title']}**")
                st.markdown(f"⭐ **{m['rating']}/10**")
                st.markdown(get_star_display(m['rating']))
                with st.expander("Overview"):
                    st.write(m['overview'])