import requests
import pandas as pd
import streamlit as st
import libs.tools as tools
from datetime import datetime
import matplotlib.pyplot as plt

tools.set_page_config()

images_path = tools.get_images_path()

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


API_BASE_URL = tools.get_env_var('API_BASE_URL')
FORECAST_DATA = tools.get_env_var('FORECAST_DATA')
ALLOWED_CITIES = tools.get_env_var('ALLOWED_CITIES')

if ALLOWED_CITIES:
    ALLOWED_CITIES = ALLOWED_CITIES.split(";")


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
    url = f"{API_BASE_URL}{FORECAST_DATA}?name_city=" + str(city)
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
    df = df['success']
    return df


def plot_forecast_data(forecast_data):
    """
    Display the forecast graph for the 9 variables of interest along 3 columns
    """
    # Convert forecast_data to DataFrame
    df = pd.DataFrame(get_dataframe(forecast_data))
    df = df.sort_values(by=['DATE'], ascending=True)
    # Get the time index
    time_index = pd.to_datetime(df['DATE'])

    # Exclude 'CITY' from the columns to plot
    columns_to_plot = [col for col in df.columns[1:] if col != 'CITY']

    # Create 3 columns
    cols = st.columns(3)

    # Plot each signal as a separate subplot in one of the columns
    for idx, signal_name in enumerate(columns_to_plot):  # Assuming the first column is 'time'
        with cols[idx % 3]:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(time_index, df[signal_name])
            ax.set_xlabel('Time')
            ax.set_ylabel('Value')
            ax.axvline(datetime.now(), color='orange', linestyle='--')
            ax.set_title(signal_name)
            st.pyplot(fig)
            plt.close(fig)


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
             The token is usable for 2 hours
             """)

    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    if st.button("Get token"):
        if username and password:
            jwt_token = get_jwt_token(username, password)
            if jwt_token:
                st.success("JWT Token successfully obtained!")
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


if __name__ == "__main__":
    main()

tools.display_side_bar()
