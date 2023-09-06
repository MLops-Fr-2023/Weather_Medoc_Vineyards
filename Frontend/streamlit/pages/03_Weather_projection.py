import requests
import numpy as np
import pandas as pd
import streamlit as st
import libs.tools as tools
from datetime import datetime, timedelta
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
HISTORIC_DATA = tools.get_env_var('HISTORIC_DATA')

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


def call_historic_api(jwt_token, city, start_date, end_date):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    url = f"{API_BASE_URL}{HISTORIC_DATA}?start_date={start_date}&end_date={end_date}&name_city={city}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        st.error("Unauthorized. Please check your JWT Token.")
    else:
        st.error(f"Error: {response.status_code}")
        st.write(response.text)
    return None


def call_forecast_api(jwt_token, city):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    url = f"{API_BASE_URL}{FORECAST_DATA}?name_city={city}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        st.error("Unauthorized. Please check your JWT Token.")
    else:
        st.error(f"Error: {response.status_code}")
        st.write(response.text)
    return None


def dict_to_df(dict):
    return dict['success']


def plot_forecast_data(historic_data_dict, forecast_data_dict):
    """
    Display the variables of insterests for the 3 past days + the forecast graph for
    the 9 variables of interest along 3 columns
    """
    # Convert historic_data to DataFrame
    df_historic = pd.DataFrame(dict_to_df(historic_data_dict))
    df_historic = df_historic.sort_values(by=['DATE'], ascending=True)

    # Convert forecast_data to DataFrame
    df_forecast = pd.DataFrame(dict_to_df(forecast_data_dict))
    df_forecast = df_forecast.sort_values(by=['DATE'], ascending=True)

    # Get the time index
    time_index_historic = pd.to_datetime(df_historic['DATE'])
    time_index_forecast = pd.to_datetime(df_forecast['DATE'])

    # Exclude 'CITY' from the columns to plot
    columns_to_plot = [col for col in df_historic.columns[1:] if col != 'CITY']
    columns_to_plot = [col for col in df_forecast.columns[1:] if col != 'CITY']

    # Create 3 columns
    cols = st.columns(3)

    # Plot each signal as a separate subplot in one of the columns
    for idx, signal_name in enumerate(columns_to_plot):  # Assuming the first column is 'time'
        with cols[idx % 3]:
            fig, ax = plt.subplots(figsize=(10, 5))

            # Plot historic data in blue
            ax.plot(time_index_historic, df_historic[signal_name], label='Historic', color='blue')

            # Append the last historic value to the beginning of the forecast series
            first_forecast_value = df_historic[signal_name].iloc[-1]
            df_forecast_new = np.insert(df_forecast[signal_name].values, 0, first_forecast_value)

            # Similarly, append the last time of historic to the beginning of the forecast time index
            first_forecast_time = time_index_historic.iloc[-1]
            time_index_forecast_new = pd.to_datetime(np.insert(time_index_forecast.values, 0, first_forecast_time))

            # Plot forecast data in green
            ax.plot(time_index_forecast_new, df_forecast_new, label='Forecast', color='green')

            ax.set_xlabel('Time')
            ax.set_ylabel('Value')
            ax.axvline(datetime.now(), color='orange', linestyle='--')
            ax.set_title(signal_name)
            ax.legend(loc="upper left")
            plt.xticks(rotation=45)
            st.pyplot(fig)
            plt.close(fig)


# Function to print the dataframe for details
def show_dataframe_details(dataframe):
    """
    Display the dataframe content
    """
    st.dataframe(dict_to_df(dataframe))


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
                # Today
                today = datetime.now()
                end_date = today.strftime('%Y-%m-%d')

                # Today - 7 days
                three_days_ago = today - timedelta(days=7)
                start_date = three_days_ago.strftime('%Y-%m-%d')

                historic_data_dict = call_historic_api(jwt_token=st.session_state.jwt_token, city=city,
                                                       start_date=start_date, end_date=end_date)
                forecast_data_dict = call_forecast_api(st.session_state.jwt_token, city)

                if historic_data_dict and forecast_data_dict:
                    st.success("Historical and forecast data fetched successfully")
                    st.markdown("""---""")
                    plot_forecast_data(historic_data_dict, forecast_data_dict)
                    st.markdown("""---""")
                    # Show DataFrame details
                    st.subheader("Forecast Data Details")
                    show_dataframe_details(forecast_data_dict)

            else:
                st.warning("Please select a city for weather forecast.")
        else:
            st.warning("Please obtain the JWT token first.")


if __name__ == "__main__":
    main()

tools.display_side_bar()
