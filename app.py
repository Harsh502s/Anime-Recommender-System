import streamlit as st
from st_pages import Page, show_pages
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

# Configuring Pages

show_pages(
    [
        Page(r"app.py", "Homepage", "🏠"),
        Page(r"Pages/Recommender App.py", "Anime Recommender", "📺"),
        Page(r"Pages/About.py", "About", "👋"),
    ]
)


# Home Page
def home_page():
    style_for_page = """
    <style>
    div.st-emotion-cache-1v0mbdj.e115fcil1>img {
    border-radius: 50px;
    }
    </style>
    """
    st.markdown(style_for_page, unsafe_allow_html=True)

    st.title("Welcome to Anime Recommender! :ninja:")
    st.subheader("Discover Your Next Favorite Anime")

    # Add unique content to the home page
    st.write(
        "Explore a world of anime and find personalized recommendations based on your anime preferences."
    )
    img = Image.open(r"animes.jpg")
    with st.container():
        st.image(img, width=950, caption="Anime Characters")
    st.write(
        "Get started by selecting your favorite anime and let the recommendation system do the rest!"
    )


# Web Application
if __name__ == "__main__":
    home_page()
