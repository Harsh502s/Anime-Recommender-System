import streamlit as st
import pandas as pd
import pickle
from ast import literal_eval


# Importing the dataset
@st.cache_data
def load_data():
    try:
        anime_data = pd.read_csv(r"rec_data.csv")
    except:
        st.error("Dataset Not Found")
    return anime_data


anime_data = load_data()


def get_genres():
    genres = sorted(
        list(set([j for i in anime_data["genres"] for j in literal_eval(i)]))
    )
    genres.insert(0, "All Genres")
    genres.remove("NA")
    return genres


# Uncomment this if you want to load the model
@st.cache_resource
def load_model():
    try:
        similarity = pickle.load(open(r"similarity.pkl", "rb"))
    except:
        st.error("Model Not Found")
    return similarity


similarity = load_model()


# Fetching the poster and url of the anime
def fetch_anime_url(anime_id):
    url = anime_data[anime_data["anime_id"] == anime_id].anime_url.values[0]
    return url


def fetch_poster(anime_id):
    poster = anime_data[anime_data["anime_id"] == anime_id].poster.values[0]
    return poster


# Recommender System
def recommend(anime, genre=None):
    if genre == None:
        index = (
            anime_data[anime_data["title"] == anime]
            .sort_values("score", ascending=False)
            .index[0]
        )
    elif genre != None:
        index = (
            anime_data[
                (anime_data["title"] == anime)
                | (anime_data["genres"].str.contains(genre))
            ]
            .sort_values("score", ascending=False)
            .index[0]
        )
    # index = anime_data[anime_data["title"] == anime].index[0]
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1]
    )

    recommended_anime_names = []
    recommended_anime_posters = []
    recommended_anime_urls = []

    for i in distances[1:9]:
        # fetch the anime poster
        anime_id = anime_data.iloc[i[0]].anime_id
        recommended_anime_posters.append(fetch_poster(anime_id))
        recommended_anime_names.append(anime_data.iloc[i[0]].title)
        recommended_anime_urls.append(fetch_anime_url(anime_id))

    return recommended_anime_names, recommended_anime_posters, recommended_anime_urls


# Function to display the top 8 animes with the highest rating
def top_animes():
    style_for_page = """
    <style>
    div.st-emotion-cache-1v0mbdj.e115fcil1>img {
    border-radius: 20px;
    }
    a.st-emotion-cache-1lbx6hs.e16zdaao0 {
    border-radius: 15px;
    text-align: center;
    }
    a.st-emotion-cache-1lbx6hs.e16zdaao0>div>p {
    font-weight: 600;
    }
    a.st-emotion-cache-1lbx6hs.e16zdaao0:hover {
    scale: 1.05;
    transition-duration: 0.3s;
    }
    </style>
    """
    st.markdown(style_for_page, unsafe_allow_html=True)

    top8 = anime_data.sort_values("score", ascending=False).head(8)

    for i in range(0, 8, 4):
        with st.container():
            cols = st.columns(4)
            for j, col in enumerate(cols):
                index = i + j
                with col:
                    st.link_button(
                        f"{top8.iloc[index].title}",
                        f"{top8.iloc[index].anime_url}",
                        use_container_width=True,
                    )
                    st.image(top8.iloc[index].poster, use_column_width=True)

        if i == 0:
            st.divider()


# Function to display the top 8 animes for user given genre
def top_animes_genres(genre_select):
    style_for_page = """
    <style>
    div.st-emotion-cache-1v0mbdj.e115fcil1>img {
    border-radius: 20px;
    }
    a.st-emotion-cache-1lbx6hs.e16zdaao0 {
    border-radius: 15px;
    text-align: center;
    }
    a.st-emotion-cache-1lbx6hs.e16zdaao0>div>p {
    font-weight: 600;
    }    
    a.st-emotion-cache-1lbx6hs.e16zdaao0:hover {
    scale: 1.05;
    transition-duration: 0.3s;
    }
    </style>
    """
    st.markdown(style_for_page, unsafe_allow_html=True)

    top_8_genre = anime_data[
        anime_data["genres"].str.contains(genre_select)
    ].sort_values("score", ascending=False)[:8]

    for i in range(0, 8, 4):
        cols = st.columns(4)
        for j, col in enumerate(cols):
            index = i + j
            with col:
                st.link_button(
                    f"{top_8_genre.iloc[index].title}",
                    f"{top_8_genre.iloc[index].anime_url}",
                    use_container_width=True,
                )
                st.image(top_8_genre.iloc[index].poster, use_column_width=True)
        if i == 0:
            st.divider()


# Function to display the top 8 animes with user given anime name for all genres
def top_animes_custom(anime_select):
    style_for_page = """
    <style>
    div.st-emotion-cache-1v0mbdj.e115fcil1>img {
    border-radius: 20px;
    }
    a.st-emotion-cache-1lbx6hs.e16zdaao0 {
    border-radius: 15px;
    text-align: center;
    }
    a.st-emotion-cache-1lbx6hs.e16zdaao0>div>p {
    font-weight: 600;
    }    
    a.st-emotion-cache-1lbx6hs.e16zdaao0:hover {
    scale: 1.05;
    transition-duration: 0.3s;
    }
    </style>
    """
    st.markdown(style_for_page, unsafe_allow_html=True)

    (
        recommended_anime_names,
        recommended_anime_posters,
        recommended_anime_urls,
    ) = recommend(anime_select)

    for i in range(0, 8, 4):
        with st.container():
            cols = st.columns(4)
            for j, col in enumerate(cols):
                index = i + j
                with col:
                    st.link_button(
                        f"{recommended_anime_names[index]}",
                        f"{recommended_anime_urls[index]}",
                        use_container_width=True,
                    )
                    st.image(recommended_anime_posters[index], use_column_width=True)
        if i == 0:
            st.divider()


# Function to display the top 8 animes with user given anime name and genre
def top_animes_custom_genres(anime_select, genre_select):
    style_for_page = """
    <style>
    div.st-emotion-cache-1v0mbdj.e115fcil1>img {
    border-radius: 20px;
    }
    a.st-emotion-cache-1lbx6hs.e16zdaao0 {
    border-radius: 15px;
    text-align: center;
    }
    a.st-emotion-cache-1lbx6hs.e16zdaao0>div>p {
    font-weight: 600;
    }
    a.st-emotion-cache-1lbx6hs.e16zdaao0:hover {
    scale: 1.05;
    transition-duration: 0.3s;
    }
    </style>
    """
    st.markdown(style_for_page, unsafe_allow_html=True)

    (
        recommended_anime_names,
        recommended_anime_posters,
        recommended_anime_urls,
    ) = recommend(anime_select, genre_select)

    for i in range(0, 8, 4):
        with st.container():
            cols = st.columns(4)
            for j, col in enumerate(cols):
                index = i + j
                with col:
                    st.link_button(
                        f"{recommended_anime_names[index]}",
                        f"{recommended_anime_urls[index]}",
                        use_container_width=True,
                    )
                    st.image(recommended_anime_posters[index], use_column_width=True)
        if i == 0:
            st.divider()


# Recommender Page
def recommender_page():
    style_for_page = """
    <style>
    button.st-emotion-cache-c766yy.ef3psqc11 {
    border-radius: 20px;    
    }

    button.st-emotion-cache-c766yy.ef3psqc11:hover {
    scale: 1.05;
    transition-duration: 0.3s;
    }
    </style>
    """
    st.markdown(style_for_page, unsafe_allow_html=True)

    st.title("Anime Recommendation System :ninja:")

    anime_list = anime_data["title"].tolist()
    anime_list.sort()
    anime_list.insert(0, "Top 8 Animes")
    anime_select = st.selectbox("Select an Anime", anime_list, key="anime_select")
    genre_select = st.selectbox("Select a Genre", get_genres(), key="genre_select")

    if st.button("Recommendation"):
        st.divider()
        if anime_select == "Top 8 Animes" and genre_select == "All Genres":
            top_animes()
            st.divider()
        elif anime_select == "Top 8 Animes" and genre_select != "All Genres":
            top_animes_genres(genre_select)
            st.divider()
        elif anime_select != "Top 8 Animes" and genre_select == "All Genres":
            top_animes_custom(anime_select)
            st.divider()
        elif anime_select != "Top 8 Animes" and genre_select != "All Genres":
            top_animes_custom_genres(anime_select, genre_select)
            st.divider()


if __name__ == "__main__":
    recommender_page()
