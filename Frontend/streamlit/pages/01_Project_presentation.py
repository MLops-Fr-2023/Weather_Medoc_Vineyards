import streamlit as st
from PIL import Image
import s3fs
import os


# CONFIGURATION ##############

st.set_page_config(
    page_title="Hello Vineyard operator",
    page_icon="🍇",
    layout="wide")

# VARIABLES ##################

fs = s3fs.S3FileSystem(anon=False)
image_path_images = os.environ.get("IMAGE_PATH_IMAGES")
image_path_team = os.environ.get("IMAGE_PATH_TEAM")

# FUNCTIONS ##################


@st.cache_data(ttl=600)
def read_image_bucket(filename):
    return Image.open(fs.open(filename))


@st.cache_data(ttl=600)
def read_file(filename):
    with fs.open(filename, 'rb') as f:
        return f.read()

# TEXT  ######################


def main():

    st.markdown("<h3 style='text-align: center; color: violet;'>This is our team. We are glad to host you!</h3>",
                unsafe_allow_html=True)

    st.markdown("""---""")
    c1, c2, c3 = st.columns(3, gap="large")

    with c1:
        st.subheader('Joffrey Lemery')
        st.image(read_image_bucket(image_path_team + 'joffrey_lemery.jpg'),
                 channels="RGB", output_format="JPEG", width=300)
    with c2:
        st.subheader('Nicolas Carayon')
        st.image(read_image_bucket(image_path_team + 'nicolas_carayon.jpg'),
                 channels="RGB", output_format="JPEG", width=250)
    with c3:
        st.subheader('Jacques Drouvroy')
        st.image(read_image_bucket(image_path_team + 'jacques_douvroy.jpg'),
                 channels="RGB", output_format="JPEG", width=250)

    c1, c2, c3 = st.columns(3, gap="large")

    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        st.write("""
                 Joffrey is a graduate engineer from France and Quebec. His energy, his technical skills
                 as a MLE and his infinite thirst for knowledge bring people together around technical
                 and challenging projects.
                 """)
    with c2:
        st.write("""
                 Nicolas is the embodiment of rigour. His strong technical background in development
                 and his functional skills make him a strong asset both on the Ops side as well as the
                 functionnal side.
                 """)
    with c3:
        st.write("""
                 Jacques is the team's spirit of discovery and science.
                 His skills in DS and his quick understanding of the issues at stake are invaluable assets
                 for IA and MLE project.
                 """)

    st.markdown("""---""")

    pres_txt = """
        This site is dedicated to an innovative project that aims to predict the weather in the Médoc
        (France, Gironde), a week in advance. Utilizing state-of-the-art machine learning techniques,
        our approach leverages transformer models applied to time series data, paving a new way
        for weather prediction technologies.

        Médoc, renowned for its prestigious vineyards and rich wine culture, poses unique challenges
        for its vintners due to its variable weather patterns. Weather plays an essential role in viticulture,
        from vine growth to grape maturity, and ultimately, the quality of the wine produced. Therefore,
        reliable weather forecasting is of paramount importance to the vintners in Médoc.

        For vineyard managers, precise weather prediction helps inform daily decision-making, from
        adjusting watering schedules to choosing the optimal time for harvesting. Predicting weather patterns
        accurately can also provide early warnings about potential hazards like frost or drought, enabling
        preventive measures that can save an entire year's crop.

        Our project aims to enhance the precision of these weather predictions, improving the tools at the
        vintners' disposal to manage their vineyards more effectively. By harnessing the power of transformer
        models and machine learning, we aim to provide a forecast that can help secure the future of Médoc's
        wine industry and contribute to its ongoing success.

        In this repository, you will find the codes, data, and models used for this project. Your contributions,
        suggestions, and insights are warmly welcomed. We hope that our efforts will assist the vintners
        of Médoc in their noble pursuit of creating the world's finest wines. Join us on this journey of
        innovation, precision, and a shared passion for viticulture.
        """

    st.write(pres_txt)

##############################


if __name__ == '__main__':
    main()


# SIDEBAR ####################

with st.sidebar:
    with st.expander("Joffrey Lemery"):
        col1, col2, col3 = st.columns([1, 0.5, 1])
        with col1:
            st.image(read_image_bucket(image_path_images + 'LinkedIn_Logo_blank.png'),
                     channels="RGB", output_format="auto")
            st.image(read_image_bucket(image_path_images + 'github_blank.png'),
                     channels="RGB", output_format="auto")
        with col3:
            st.write("")
            st.write("")
            st.write("[Linkedin](https://www.linkedin.com/in/joffrey-lemery-b740a5112/)")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("[GitHub](https://github.com/JoffreyLemery)")

    with st.expander("Nicolas Carayon"):
        col1, col2, col3 = st.columns([1, 0.5, 1])
        with col1:
            st.image(read_image_bucket(image_path_images + 'LinkedIn_Logo_blank.png'),
                     channels="RGB", output_format="auto")
            st.image(read_image_bucket(image_path_images + 'github_blank.png'),
                     channels="RGB", output_format="auto")
        with col3:
            st.write("")
            st.write("")
            st.write("[Linkedin](https://www.linkedin.com/in/nicolascarayon/)")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("[GitHub](https://github.com/nicolascarayon/)")

    with st.expander("Jacques Drouvroy"):
        col1, col2, col3 = st.columns([1, 0.5, 1])
        with col1:
            st.image(read_image_bucket(image_path_images + 'LinkedIn_Logo_blank.png'),
                     channels="RGB", output_format="auto")
            st.image(read_image_bucket(image_path_images + 'github_blank.png'),
                     channels="RGB", output_format="auto")
        with col3:
            st.write("")
            st.write("")
            st.write("[Linkedin](https://www.linkedin.com/in/jacques-drouvroy-65044765/)")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("[GitHub](https://github.com/Baloux79)")

##############################
