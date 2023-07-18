import streamlit as st
from PIL import Image
import base64
from PIL import Image
import pandas as pd
import numpy as np
import s3fs
import plotly.express as px
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

@st.cache_data
def read_csv_st(filename , sep_st):
        return pd.read_csv(fs.open(filename), sep= sep_st)
path = (df_path + 'GBIF_tax.csv')
df = read_csv_st(path ,sep_st='\t')
df2 = read_csv_st(df_path + "All_ranks_and_occurence.csv",sep_st=',')


##############################


########### TEXT  ############

def main():

    choice = st.sidebar.radio("Submenu", ["Introduction","Data", "Infrastructure", "Transformers"])
    if choice == 'Introduction':
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.title('Project report')
            c1, c2, c3, c4 = st.columns(4, gap="large")
        st.markdown("""---""")


        col1, col2, col3 = st.columns([0.5,8,0.5])
        with col2:   
            st.title('Context')
            st.markdown("---")
            st.write("""""")
            st.write("")
            st.write("")
            st.write("")
            st.write("""""")
            
    if choice == 'Data':
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.title('Project report')
            c1, c2, c3, c4 = st.columns(4, gap="large")
        st.markdown("""---""")



        col1, col2, col3 = st.columns([0.5,8,0.5])
        with col2:   
            st.title('Data')
            st.write("")
            st.write("""""")
            st.write("")
            st.write("")
            st.write("")
            expander = st.expander("")
            
            expander.dataframe(df)
            expander.write("""""")
        st.markdown("""---""")
        col1, col2, col3 = st.columns([0.5,8,0.5])
        with col2: 
            st.title("API")
            st.write("")
            st.write("""""")
            st.write("")
            st.write("")
            st.write("")
        col5, col6, col7, col8 = st.columns([0.5,4,4,0.5])
        with col6 : 
            #st.image(read_image_bucket( image_path + 'XXXXXX.png'),channels="RGB", output_format="auto")
        st.markdown("""---""")
        with col7: 
            st.write("""""")
        st.write("")
        st.write("")

        with c2: 
            st.plotly_chart(fig2 ,width= 900) 
            
        col1, col2, col3 = st.columns([0.5,8,0.5])
        with col2:
            

            st.write("")
                
        c1,c2,c3 = st.columns([0.5,1,0.5])
        with c2:

            st.write("")
        col1, col2, col3 = st.columns([0.5,8,0.5])
        with col2:
            st.write("""""")
        st.markdown("""---""")
        col1, col2, col3 = st.columns([0.5,8,0.5])
        with col2:  
            st.write("")
            st.write("")
            st.write("""""")
        st.write("")
        st.write("")
        col5, col6, col7 = st.columns([0.5,8,0.5])
        with col6 : 
        
        col1, col2, col3 = st.columns([0.5,8,0.5])
        with col2:
            st.write("""""")
            st.write("")
            st.write("")
            st.write("""""")
        st.write("")
        st.write("")
        
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.markdown("""---""")
        col1, col2, col3 = st.columns([0.5,8,0.5])
        with col2:
            st.write("""""")



    if choice == 'Infrastructure':
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.title('Project report')
        st.markdown("""---""")
        expander3 = st.expander("") 
        with st.expander("") :
            col1, col2, col3 = st.columns([0.5,2,0.5])
            with col2:
                #st.image(read_image_bucket( image_path + 'XXXXX.png'),channels="RGB", output_format="auto", use_column_width = 'auto')
                """
    """

        st.markdown("""---""")

        expander3 = st.expander("") 
        with st.expander("") :
            col1, col2, col3 = st.columns([0.5,2,0.5])
            with col2:
                #st.image(read_image_bucket( image_path + 'XXXX.png'),channels="RGB", output_format="auto", use_column_width = 'auto')
                """
    """

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
