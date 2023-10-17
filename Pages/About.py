import streamlit as st


# About page
def about_page():
    style_for_page = """
    <style>
    div.css-nahz7x.e16nr0p34>p {
        font-family: Poppins, sans-serif;
        font-size: 1.07rem;
    }
    </style>
    """
    st.markdown(style_for_page, unsafe_allow_html=True)
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


if __name__ == "__main__":
    about_page()
