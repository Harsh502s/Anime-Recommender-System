# Making an anime recommendation app using streamlit

# Importing libraries

import streamlit as st
import pandas as pd
import pickle
from PIL import Image

# Make the page full width
im = Image.open(r"ninja.png")
st.set_page_config(
    page_title="Anime Recommender App",
    page_icon=im,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "This Anime Recommender App is made by Harshit Singh."},
)

# Importing the dataset
try:
    anime_data = pd.read_csv(r"anime_rec.csv")
    anime_posters = pd.read_csv(r"anime_data_cleaned.csv")
except:
    pass

def fetch_anime_url(anime_id):
    url = anime_posters[anime_posters["anime_id"] == anime_id].urls.values[0]
    return url


def fetch_poster(anime_id):
    poster = anime_posters[anime_posters["anime_id"] == anime_id].poster.values[0]
    return poster


def recommend(anime):
    index = anime_data[anime_data["title"] == anime].index[0]
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


# Importing the similarity matrix
try:
    similarity = pickle.load(open(r"similarity_matrix.pkl", "rb"))
except:
    pass

def home_page():
    st.title("Welcome to Anime Recommender! :ninja:")
    st.subheader("Discover Your Next Favorite Anime")

    # Add unique content to the home page
    st.write(
        "Explore a world of anime and find personalized recommendations based on your anime preferences."
    )
    img = Image.open(r"animes.jpg")
    st.image(img, use_column_width=True, caption="Anime Characters")
    st.write(
        "Get started by selecting your favorite anime and let the recommendation system do the rest!"
    )

    # Add any additional content or instructions


# Define the home page
def recommender_page():
    st.title("Anime Recommendation System")

    anime_list = anime_data["title"].tolist()
    anime_list.sort()
    anime_list.insert(0, "Select")
    anime_select = st.selectbox("Select an Anime", anime_list)

    if st.button("Recommendation"):
        if anime_select == "Select":
            st.write("Please select an anime.")
        else:
            (
                recommended_anime_names,
                recommended_anime_posters,
                recommended_anime_urls,
            ) = recommend(anime_select)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write(f"[{recommended_anime_names[0]}]({recommended_anime_urls[0]})")
                st.image(recommended_anime_posters[0])
            with col2:
                st.write(f"[{recommended_anime_names[1]}]({recommended_anime_urls[1]})")
                st.image(recommended_anime_posters[1])
            with col3:
                st.write(f"[{recommended_anime_names[2]}]({recommended_anime_urls[2]})")
                st.image(recommended_anime_posters[2])
            with col4:
                st.write(f"[{recommended_anime_names[3]}]({recommended_anime_urls[3]})")
                st.image(recommended_anime_posters[3])

            col5, col6, col7, col8 = st.columns(4)
            with col5:
                st.write(f"[{recommended_anime_names[4]}]({recommended_anime_urls[4]})")
                st.image(recommended_anime_posters[4])
            with col6:
                st.write(f"[{recommended_anime_names[5]}]({recommended_anime_urls[5]})")
                st.image(recommended_anime_posters[5])
            with col7:
                st.write(f"[{recommended_anime_names[6]}]({recommended_anime_urls[6]})")
                st.image(recommended_anime_posters[6])
            with col8:
                st.write(f"[{recommended_anime_names[7]}]({recommended_anime_urls[7]})")
                st.image(recommended_anime_posters[7])


# Define the about page
def about_page():
    st.title("About")
    st.divider()
    st.subheader(
        "This is a content based recommender system that recommends animes similar to the animes you like."
    )
    st.write("\n")
    st.write("\n")
    st.write(
        "This Anime Recommender App is made by [Harshit Singh](https://Harsh502s.github.io/). :ninja:"
    )


def feedback_page():
    st.title("Feedback")
    st.write("Leave your feedback below:")

    feedback_text = st.text_input("Feedback", "")
    submit_button = st.button("Submit")

    if submit_button and feedback_text:
        # Store the feedback in a CSV file
        feedback_data = pd.DataFrame({"Feedback": [feedback_text]})
        feedback_data.to_csv("feedback.csv", mode="a", header=False, index=False)
        st.success("Thank you for your feedback!")


# Run the app
if __name__ == "__main__":
    st.sidebar.title("Navigation :mag_right:")
    selected_page = st.sidebar.radio(
        ":radio:", ("Home", "Recommender", "About", "Feedback")
    )

    if selected_page == "Home":
        home_page()
    elif selected_page == "Recommender":
        recommender_page()
    elif selected_page == "About":
        about_page()
    elif selected_page == "Feedback":
        feedback_page()
