import os
import streamlit as st

linkedin_jacques = "https://www.linkedin.com/in/jacques-drouvroy-65044765/"
linkedin_joffrey = "https://www.linkedin.com/in/joffrey-lemery-b740a5112/"
linkedin_nicolas = "https://www.linkedin.com/in/nicolascarayon/"
github_jacques = "https://github.com/Baloux79"
github_joffrey = "https://github.com/JoffreyLemery"
github_nicolas = "https://github.com/nicolascarayon/"


def set_page_config():
    st.set_page_config(
        page_title="Hello Vineyard operator",
        page_icon="🍇",
        layout="wide")


def get_env_var(env_name):
    return os.environ.get(env_name)


def get_images_path():
    paths = ["streamlit/images/", "images/"]
    for path in paths:
        if os.path.exists(path):
            return path
    return ""


def display_linkedin_github_pics():
    images_path = get_images_path()
    st.image(images_path + 'LinkedIn_Logo_blank.png',
             channels="RGB", output_format="auto")
    st.image(images_path + 'github_blank.png',
             channels="RGB", output_format="auto")


def display_linkedin_github_links(linkedin_lnk, github_lnk):
    st.write("")
    st.write("")
    st.write(f"[Linkedin]({linkedin_lnk})")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write(f"[GitHub]({github_lnk})")


def display_side_bar():
    with st.sidebar:
        with st.expander("Joffrey Lemery"):
            col1, col2, col3 = st.columns([1, 0.5, 1])
            with col1:
                display_linkedin_github_pics()
            with col3:
                display_linkedin_github_links(linkedin_joffrey, github_joffrey)

        with st.expander("Nicolas Carayon"):
            col1, col2, col3 = st.columns([1, 0.5, 1])
            with col1:
                display_linkedin_github_pics()
            with col3:
                display_linkedin_github_links(linkedin_nicolas, github_nicolas)

        with st.expander("Jacques Douvroy"):
            col1, col2, col3 = st.columns([1, 0.5, 1])
            with col1:
                display_linkedin_github_pics()
            with col3:
                display_linkedin_github_links(linkedin_jacques, github_jacques)
