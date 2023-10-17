import streamlit as st
from st_pages import Page, show_pages
from PIL import Image

# Configuring Pages

show_pages(
    [
        Page(r"app.py", "Homepage", "🏠"),
        Page(r"Pages/Recommender App.py", "Anime Recommender", "📺"),
        Page(r"Pages/About.py", "About", "👋"),
    ]
)


# Make the page full width
im = Image.open(r"ninja.png")
st.set_page_config(
    page_title="Anime Recommender App",
    page_icon=im,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "This Anime Recommender App is made by Harshit Singh."},
)


# Home Page
def home_page():
    style_for_page = """
    <style>
    div.css-1v0mbdj.etr89bj1>img {
    width: 100%;
    height: 100%;
    box-shadow: 0 0 0 1px rgba(0,0,0,.1);
    border-radius: 5rem;
    padding: 4rem;
    justify-content: left;}

    div.css-k7vsyb.e16nr0p31>h1 {
    font-family: Poppins, sans-serif;
    }

    div.css-14xtw13.e8zbici0 {
        margin-right: 2rem;
        scale: 1.15;
    }

    div.css-nahz7x.e16nr0p34>p {
        font-family: Poppins, sans-serif;
        font-size: 1.05rem;
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
    st.image(img, use_column_width=True, caption="Anime Characters")
    st.write(
        "Get started by selecting your favorite anime and let the recommendation system do the rest!"
    )


# Web Application
if __name__ == "__main__":
    home_page()
