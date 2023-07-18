import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import requests
import os
import s3fs

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
   ALLOWED_CITIES = ALLOWED_CITIES_STRING.split(",")

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
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        st.error("Unauthorized. Please check your JWT Token.")
    else:
        st.error(f"Error: {response.status_code}")
        st.write(response.text)
    return None

# Function to plot the forecast data
def plot_forecast_data(forecast_data):
    # Convert forecast_data to DataFrame (optional, if it's not already a DataFrame)
    df = pd.DataFrame(forecast_data)

    # Get the time index (assuming the time index is in a column named 'time', adjust accordingly)
    time_index = pd.to_datetime(df['time'])

    # Plot each signal as a separate subplot
    for signal_name in df.columns[1:]:  # Assuming the first column is 'time'
        plt.figure(figsize=(10, 5))
        plt.plot(time_index, df[signal_name], label=signal_name)
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.title(f'{signal_name} Forecast')
        plt.legend()
        st.pyplot(plt)

# Function to print the dataframe for details
def show_dataframe_details(dataframe):
    st.dataframe(dataframe)


def main():
    st.title(":violet[Weather Prediction]")
    st.subheader("Credentials")
    st.write("Please enter your credentials before to be allowed to use our IA application. \nEvery Token is available for 2h.")

    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    if st.button("Get JWT Token"):
        if username and password:
            jwt_token = get_jwt_token(username, password)
            if jwt_token:
                st.success("JWT Token successfully obtained!")
                st.write(f"Your JWT Token: {jwt_token}")
                #weather_forecast(jwt_token)  # Call the forecast function after getting the token
        else:
            st.warning("Please enter correct username and password.")

    # Display the Select City button unconditionally
    st.subheader("Weather Forecast")
    city = st.selectbox("Select a city for weather forecast:", ALLOWED_CITIES)

    # Add Streamlit button to trigger API call for weather forecast
    if st.button("Get Forecast"):
        if city:
            forecast_data = call_forecast_api(jwt_token, city)
            if forecast_data:
                st.success("Forecast data obtained successfully!")
                st.markdown("""---""")
                st.markdown("""---""")
                # st.write(forecast_data)

                st.subheader("Plots Forecast")
                plot_forecast_data(forecast_data)

                st.markdown("""---""")
                st.markdown("""---""")

                # Show DataFrame details
                st.subheader("Forecast Data Details")
                show_dataframe_details(forecast_data)

        else:
            st.warning("Please select a city for weather forecast.")

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
