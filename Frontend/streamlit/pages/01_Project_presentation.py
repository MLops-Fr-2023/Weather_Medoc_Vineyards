import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import base64
import s3fs
import io
import os


######## CONFIGURATION #######

st.set_page_config(
    page_title="Hello Vineyard operator",
    page_icon="🍇",
    layout="wide")

##############################


########## VARIABLES #########

fs = s3fs.S3FileSystem(anon=False)
image_path_team = os.environ.get("IMAGE_PATH_TEAM")

##############################


########## FUNCTIONS #########

@st.cache_data(ttl=600)
def read_image_bucket(filename):
    return Image.open(fs.open(filename))

@st.cache_data(ttl=600)
def read_file(filename):
    with fs.open(filename, 'rb') as f:
        return f.read()

##############################


########### TEXT  ############


def main():
      
    st.markdown("<h3 style='text-align: center; color: violet;'>This is our team. We are glad to host you!</h3>", unsafe_allow_html=True)


    st.markdown("""---""")
    c1, c2, c3 = st.columns(3, gap="large")


    with c1 : 
        st.subheader('Joffrey Lemery')
    with c2 : 
        st.subheader('Nicolas Carayon') 
    with c3 : 
        st.subheader('Jacques Douvroy') 

    c1, c2, c3 = st.columns(3, gap="large")

    with c1 : 
        st.image(read_image_bucket( image_path_team + 'joffrey_lemery.jpg'),channels="RGB", output_format="JPEG", use_column_width= "auto")
    with c2 : 
        st.image(read_image_bucket( image_path_team + 'nicolas_carayon.jpg'),channels="RGB", output_format="JPEG", use_column_width="auto")
    with c3 : 
        st.image(read_image_bucket( image_path_team + 'jacques_douvroy.jpg'),channels="RGB", output_format="JPEG", use_column_width="auto")

        


    c1, c2, c3 = st.columns(3, gap="large")
    with c1 : 
        st.write("Joffrey is a graduate engineer from France and Quebec.\nHis energy, his technical skills as a MLE and his infinite thirst for knowledge bring people together around technical and challenging projects. ")
    with c2 : 
        st.write("Nicolas is the eye for rigour. \nHis strong technical background in deployment and his functional skills make him a strong asset as well on the Ops side than the functionnal side")
    with c3 : 
        st.write("Jacques is the team's spirit of discovery and science. \nHis skills in DS and his quick understanding of the issues at stake are invaluable assets for IA and MLE project")

    st.markdown("""---""")

##############################

if __name__ == '__main__':
    main()

########### SIDEBAR ##########

with st.sidebar:
    with st.expander("Joffrey Lemery"):
        col1, col2, col3 = st.columns([1,0.5,1])  
        with col1: 
            st.image(read_image_bucket( image_path_team + 'LinkedIn_Logo_blank.png'),channels="RGB", output_format="auto") 
            st.image(read_image_bucket( image_path_team + 'github_blank.png'),channels="RGB", output_format="auto")
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
        col1, col2, col3 = st.columns([1,0.5,1])  
        with col1: 
            st.image(read_image_bucket( image_path_team + 'LinkedIn_Logo_blank.png'),channels="RGB", output_format="auto") 
            st.image(read_image_bucket( image_path_team + 'github_blank.png'),channels="RGB", output_format="auto")
        with col3:
            st.write("")
            st.write("")
            st.write("[Linkedin](https://www.linkedin.com/in/nicolascarayon/)")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("[GitHub](https://github.com/nicolascarayon/)")

    with st.expander("Jacques Douvroy"):
        col1, col2, col3 = st.columns([1,0.5,1])  
        with col1: 
            st.image(read_image_bucket( image_path_team + 'LinkedIn_Logo_blank.png'),channels="RGB", output_format="auto") 
            st.image(read_image_bucket( image_path_team + 'github_blank.png'),channels="RGB", output_format="auto")
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

