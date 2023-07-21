import streamlit as st
from PIL import Image
import base64
from PIL import Image
from streamlit.components.v1 import html
import s3fs
import io
import os

######## CONFIGURATION #######

st.set_page_config(
    page_title="Hello Vineyard tenant",
    page_icon="🍇",
    layout="wide")

##############################


########## VARIABLES #########

fs = s3fs.S3FileSystem(anon=False)
image_path_team = os.environ.get("IMAGE_PATH_TEAM")
image_path_images = os.environ.get("IMAGE_PATH_IMAGES")

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

    c1,c2,c3 = st.columns([0.5,2,0.5])
    with c2: 

        st.title('Welcome to :violet[Weather Forecast] 🍷')
        st.title(" ")

    with st.container():
        col1, col2= st.columns([1,1])

        # with col1:
            # image_path = ("imagemobucket/Streamlit/Figure_project/")
            # st.image(read_image_bucket( image_path + 'word_mush.png'),channels="RGB", output_format="auto", use_column_width=True)

        with col2:
            st.markdown("""---""")
            st.subheader("Here you are on the main page of our Vineyard Weather Forecast app!")


            st.write("") 
            st.subheader("**Feel free to explore and use the capabilities of IA and transformers.**")
            st.write(' ')
            st.write(' ')
            st.subheader("Please feel free to thumbs up our [github](https://github.com/MLops-Fr-2023/Weather_Medoc_Vineyards)")
            

            st.markdown("""---""")

            col1, col2, col3= st.columns(3)

            with col2:
                file_ = (image_path_images + "wine.gif")
                contents = read_file(file_) 
                data_url = base64.b64encode(contents).decode("utf-8")
                st.markdown( f'<img src="data:image/gif;base64 , {data_url}" alt="Wine bottle gif" width="400" height="300">', unsafe_allow_html=True )

if __name__ == '__main__':
    main()

########### SIDEBAR ##########

with st.sidebar:
    with st.expander("Joffrey Lemery"):
        col1, col2, col3 = st.columns([1,0.5,1])  
        with col1: 
            st.image(read_image_bucket( image_path_images + 'LinkedIn_Logo_blank.png'),channels="RGB", output_format="auto") 
            st.image(read_image_bucket( image_path_images + 'github_blank.png'),channels="RGB", output_format="auto")
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
            st.image(read_image_bucket( image_path_images + 'LinkedIn_Logo_blank.png'),channels="RGB", output_format="auto") 
            st.image(read_image_bucket( image_path_images + 'github_blank.png'),channels="RGB", output_format="auto")
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
            st.image(read_image_bucket( image_path_images + 'LinkedIn_Logo_blank.png'),channels="RGB", output_format="auto") 
            st.image(read_image_bucket( image_path_images + 'github_blank.png'),channels="RGB", output_format="auto")
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


       