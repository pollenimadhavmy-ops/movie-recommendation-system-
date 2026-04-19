import pickle
import streamlit as st
import requests
import speech_recognition as sr
from fuzzywuzzy import fuzz

# Set page config 
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
)

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    try:
        data = requests.get(url)
        data.raise_for_status()  # Raise an HTTPError for bad responses
        data = data.json()
        poster_path = data['poster_path']
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        return full_path
    except requests.exceptions.HTTPError as errh:
        st.error(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        st.error(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        st.error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        st.error(f"Request Error: {err}")
    return None


def recommend(movie):
    # Convert both the search term and movie titles to lowercase for case-insensitive comparison
    movie_lower = movie.lower()
    movies['title_lower'] = movies['title'].str.lower()

    # Use a fuzzy matching algorithm to find similar titles
    matched_movies = movies[movies['title_lower'].apply(lambda x: fuzz.ratio(x, movie_lower) > 70)]

    if not matched_movies.empty:
        index = matched_movies.index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_movie_names = []
        recommended_movie_posters = []

        for i in distances[1:6]:
            # fetch the movie poster
            movie_id = movies.iloc[i[0]].movie_id
            poster = fetch_poster(movie_id)

            if poster:
                recommended_movie_posters.append(poster)
                recommended_movie_names.append(movies.iloc[i[0]].title)

        return recommended_movie_names, recommended_movie_posters
    else:
        return [], []  # Return empty lists if no similar titles are found


# Speech Recognition function
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as mic:
        st.write("Listening... Say a movie name.")
        audio = recognizer.listen(mic)

    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.write("Sorry, could not understand audio.")
        return None

# Initialize session state
if 'listened_movie' not in st.session_state:
    st.session_state.listened_movie = ""
    selected_movie = ""

st.header('Movie Recommender')
movies = pickle.load(open('D:/Projects/Team Projects/Mini Project/movie-recommender-system/movie_list.pkl', 'rb'))
similarity = pickle.load(open('D:/Projects/Team Projects/Mini Project/movie-recommender-system/similarity.pkl', 'rb'))

# Button for Voice Recommendation
if st.button('Voice Recommendation'):
    spoken_text = recognize_speech()
    movie_list = movies['title'].values
    if spoken_text:
        st.write(f"Spoken Text: {spoken_text}")
        st.session_state.listened_movie = spoken_text
        selected_movie = st.session_state.listened_movie
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

        # Display recommendations
        for name, poster in zip(recommended_movie_names, recommended_movie_posters):
            st.text(name)
            st.image(poster, caption=name, use_column_width=True)

else:
    movie_list = movies['title'].values
    selected_movie = st.selectbox(
        "Type or select a movie from the dropdown",
        movie_list
    )

# Button for Show Recommendation
if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    # Display recommendations
    for name, poster in zip(recommended_movie_names, recommended_movie_posters):
        st.text(name)
        st.image(poster, caption=name, use_column_width=True)