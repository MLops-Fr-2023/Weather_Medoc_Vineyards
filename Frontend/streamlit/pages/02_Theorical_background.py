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

@st.cache_data
def read_csv_st(filename , sep_st):
        return pd.read_csv(fs.open(filename), sep= sep_st)

# TODO : What is it?
# path = (df_path + 'GBIF_tax.csv')
# df = read_csv_st(path ,sep_st='\t')
# df2 = read_csv_st(df_path + "All_ranks_and_occurence.csv",sep_st=',')


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
            st.write("""
In today's rapidly evolving world of data science and machine learning, integrating MLOps (Machine Learning Operations) into projects has become essential to ensure efficiency, scalability, and reliability. In this context, the wine industry can greatly benefit from MLOps implementation to improve weather prediction in vineyards. By leveraging data science techniques, advanced machine learning models, and a robust MLOps pipeline, winemakers can gain valuable insights that optimize cultivation strategies and ultimately enhance wine quality and yields.

__Challenges in Wineyard Weather Prediction :__

Vineyard management heavily relies on weather conditions. Temperature, humidity, sunlight, and precipitation significantly impact grape growth, maturation, and disease susceptibility. However, predicting weather patterns in specific vineyard locations can be challenging due to the complexity of atmospheric processes and the inherent variability in regional climates.

__Data Collection and Preprocessing :__

The foundation of any successful data science project is the availability of high-quality data. In this wineyard weather prediction project, a diverse range of data sources is collected, including historical weather records, satellite imagery, soil composition data, and even information from IoT (Internet of Things) devices installed throughout the vineyard.

Data preprocessing is a crucial step in MLOps. The collected data needs to be cleaned, normalized, and transformed into a suitable format for model training and validation. Handling missing values and outliers is essential to ensure accurate and reliable predictions.

__Machine Learning Model Development :__

For wineyard weather prediction, sophisticated machine learning models, such as Long Short-Term Memory (LSTM) networks, can be employed. LSTMs are well-suited for time-series forecasting tasks, making them ideal for predicting weather patterns, which often exhibit temporal dependencies.

The model is trained on historical weather data with corresponding ground truth observations, ensuring it learns to capture the underlying patterns and relationships between various weather variables. The training process is iterative, with hyperparameter tuning to optimize model performance.

**MLops Implementation :**

MLOps refers to the set of practices and tools that streamline the development, deployment, and monitoring of machine learning models. In this project, MLOps principles are employed to build a reliable and scalable pipeline.

- Version Control: The codebase and model artifacts are stored in a version control system (e.g., Git) to track changes and facilitate collaboration among team members.
- Continuous Integration and Continuous Deployment (CI/CD): An automated CI/CD pipeline is established to ensure seamless integration of new code changes, automatic model retraining, and deployment of updated models to production.
- Monitoring and Logging: Metrics like model accuracy, prediction error, and data drift are continuously monitored to detect performance degradation and ensure the model's health.
- Model Governance: Strict model versioning and documentation are enforced to ensure reproducibility and compliance with industry regulations.
- Scalability: The MLOps pipeline is designed to scale efficiently, accommodating larger datasets and more complex models as the project evolves.

**Conclusion :**

By harnessing the power of data science, advanced machine learning models, and MLOps principles, the wine industry can make significant strides in weather prediction for vineyards. The ability to forecast weather conditions accurately empowers winemakers to make informed decisions, optimize cultivation strategies, and adapt to changing environmental factors. Ultimately, this project holds the potential to enhance wine quality and yields, contributing to the sustainable growth of the wine industry.""")

            st.write("<div style='text-align: right; color: white; height : 10px'>_Text generated by ChatGPT_</div>", unsafe_allow_html=True)
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
