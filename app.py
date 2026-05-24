import streamlit as st
import pickle
import pandas as pd
import requests




def fetch_poster(movie_id):

    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=74fbc12e39284a6df924842591bd4992'
    )

    data = response.json()

    # check if poster exists
    if data.get('poster_path') is not None:

        return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

    else:
        # default image if poster missing
        return "https://via.placeholder.com/500x750?text=No+Poster"


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

    for i in movies_list:

        movie_id = movies.iloc[i[0]].movie_id

        recommended_movies.append(
            movies.iloc[i[0]].title
        )

        recommended_movies_poster.append(
            fetch_poster(movie_id)
        )

    return recommended_movies, recommended_movies_poster


movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))

movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))


st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie',
    movies['title'].values
)

if st.button('Show Recommendation'):

    recommended_movie_names, recommended_movie_posters = recommend(selected_movie_name)

    # Display 20 movies in rows of 5 columns

    for i in range(0, 20, 5):

        cols = st.columns(5)

        for j in range(5):

            movie_index = i + j

            with cols[j]:
                st.text(recommended_movie_names[movie_index])
                st.image(recommended_movie_posters[movie_index])