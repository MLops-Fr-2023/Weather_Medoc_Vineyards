import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import requests
import os
import s3fs
import pandas as pd
from datetime import datetime, timedelta

######## CONFIGURATION #######

st.set_page_config(
    page_title="Hello Vineyard operator",
    page_icon="🍇",
    layout="wide")

m = st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #000099;
    color:#ffffff;
}
div.stButton > button:hover {
    background-color: #00FF00;
    color:#ff0000;
    }
</style>""", unsafe_allow_html=True)

##############################



########## VARIABLES #########

fs = s3fs.S3FileSystem(anon=False)
image_path_images = os.environ.get("IMAGE_PATH_IMAGES")

API_BASE_URL = os.environ.get('API_BASE_URL')
FORECAST_ENDPOINT = os.environ.get('FORECAST_CITY')
ALLOWED_CITIES_STRING = os.environ.get('ALLOWED_CITIES')

if ALLOWED_CITIES_STRING:
   ALLOWED_CITIES = ALLOWED_CITIES_STRING.split(";")

##############################





########## FUNCTIONS #########

@st.cache_data(ttl=600)
def read_image_bucket(filename):
    return Image.open(fs.open(filename))


def get_jwt_token(username, password):
    token_url = f"{API_BASE_URL}/token"
    payload = {
        "username": username,
        "password": password
    }
    response = requests.post(token_url, data=payload)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        st.error("Authentication failed. Please check your username and password.")
        return None


def call_forecast_api(jwt_token, city):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    url = f"{API_BASE_URL}{FORECAST_ENDPOINT}{city}"
   # url = 'http://api:8000//forecast_data/?name_city='+str(city)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        st.error("Unauthorized. Please check your JWT Token.")
    else:
        st.error(f"Error: {response.status_code}")
        st.write(response.text)
    return None

def get_dataframe(df):
    df=df['success']
    return df

# Function to plot the forecast data
def plot_forecast_data(forecast_data):
    # Convert forecast_data to DataFrame
    df = pd.DataFrame(get_dataframe(forecast_data))
    df = df.sort_values(by= ['DATE'], ascending=True)
    # Get the time index
    time_index = pd.to_datetime(df['DATE'])

    # Plot each signal as a separate subplot
    for signal_name in df.columns[1:]:  # Assuming the first column is 'time'
        plt.figure(figsize=(10, 5))
        plt.plot(time_index, df[signal_name])
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.axvline(datetime.now(), color='orange', linestyle='--')
        plt.title(signal_name)
        st.pyplot(plt)

# Function to print the dataframe for details
def show_dataframe_details(dataframe):
    st.dataframe(get_dataframe(dataframe))


def main():
    if 'jwt_token' not in st.session_state:
        st.session_state.jwt_token = None
    st.title(":violet[Weather Prediction]")
    st.subheader("Credentials")
    st.write("""
Please enter your credentials and choose the city to test our IA application.           
The token is usable for 2 hours""")

    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    if st.button("Get token"):
        if username and password:
            jwt_token = get_jwt_token(username, password)
            if jwt_token:
                st.success("JWT Token successfully obtained!")
#                st.write(f"Your JWT Token: {jwt_token}")
                st.session_state.jwt_token = jwt_token

        else:
            st.warning("Please enter correct username and password.")

    city = st.selectbox("Select a city for weather forecast:", ALLOWED_CITIES)
    if st.button("Weather forecast"):
        if st.session_state.jwt_token is not None:  # Check if the token is obtained before using it
            if city:
                forecast_data = call_forecast_api(st.session_state.jwt_token, city)
                if forecast_data:
                    st.success("Forecast data obtained successfully!")
                    st.markdown("""---""")
                    st.markdown("""---""")

                    st.subheader("Plots Forecast")
                    plot_forecast_data(forecast_data)

                    st.markdown("""---""")
                    st.markdown("""---""")

                    # Show DataFrame details
                    st.subheader("Forecast Data Details")
                    show_dataframe_details(forecast_data)

            else:
                st.warning("Please select a city for weather forecast.")
        else:
            st.warning("Please obtain the JWT token first.")





##############################

if __name__ == "__main__":
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
