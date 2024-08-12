import streamlit as st
import requests_cache
import pandas as pd
from retry_requests import retry
import requests

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #134B70;
        font-family: Arial, sans-serif;
    }
    .sidebar .sidebar-content {
        background-color: #D2691E;
    }
    .stButton button {
        background-color: #D2691E;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
        position: fixed;
    }
    .stTitle {
        color: #D2691E;
    }
    .stDataFrame {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# HTML content
st.markdown("""
    <div style="background-color: #000035; padding: 20px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <h2 class="stTitle">Weather Dashboard</h2>
        <p> Choose your desired location, date range, latitude and longitude to get weather data </p>
    </div>
    """, unsafe_allow_html=True)

# Dictionary of locations with names, latitudes, and longitudes
locations = {
    "Berlin": (52.52, 13.41),
    "New York": (40.71, -74.01),
    "Tokyo": (35.68, 139.76),
    "Sydney": (-33.86, 151.21),
    "London": (51.51, -0.13),
    "Paris": (48.85, 2.35),
    "Rome": (41.90, 12.49),
    "Moscow": (55.76, 37.62),
    "Toronto": (43.65, -79.38),
    "Hong Kong": (22.31, 114.17),
    "Cape Town": (-33.92, 18.42),
    "Buenos Aires": (-34.61, -58.38),
    "Rio de Janeiro": (-22.91, -43.21),
    "Mumbai": (19.07, 72.87),
    "Singapore": (1.35, 103.82),
    "Dubai": (25.20, 55.27),
    "Istanbul": (41.01, 28.97),
    "Seoul": (37.56, 126.97),
    "Los Angeles": (34.05, -118.24),
    "San Francisco": (37.77, -122.42),
    "Chicago": (41.88, -87.63),
    "Mexico City": (19.43, -99.13),
    "Sao Paulo": (-23.55, -46.63)
}


def fetch_weather_data(latitude, longitude, start_date, end_date):
   
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m"
    }
    

    response = retry_session.get(url, params=params)
    data = response.json()
    
    return data

# Streamlit app layout
# st.title("Weather Dashboard")

# Sidebar inputs
# st.sidebar.header("Select Location, Date Range, and Coordinates")

# Location selection
selected_location = st.sidebar.selectbox("Select Location", options=list(locations.keys()))
latitude, longitude = locations[selected_location]

# Latitude and Longitude input
latitude_input = st.sidebar.number_input("Latitude", value=latitude, format="%.6f")
longitude_input = st.sidebar.number_input("Longitude", value=longitude, format="%.6f")

# Date range input
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2024-07-28"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-08-10"))

# Convert date inputs to strings for API request
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

# Fetch weather data
data = fetch_weather_data(latitude_input, longitude_input, start_date_str, end_date_str)

# Process data
hourly = data['hourly']
times = hourly['time']
temperatures = hourly['temperature_2m']

# Create DataFrame
hourly_data = {
    "Date": pd.to_datetime(times),
    "temperature_2m": temperatures
}
hourly_dataframe = pd.DataFrame(data=hourly_data)

# Display location and timezone information
st.write(f"Location: {selected_location} ({latitude_input}°N, {longitude_input}°E)")
st.write(f"Timezone: {data['timezone']}")
st.write(f"Data retrieved for {len(hourly_dataframe)} hours from {start_date_str} to {end_date_str}")

# Plot data
st.line_chart(hourly_dataframe.set_index("Date"))

# Map visualization
st.map(pd.DataFrame({'lat': [latitude_input], 'lon': [longitude_input]}))

# Create a two-column layout for DataFrame and download button
col1, col2 = st.columns([1.5,1])

with col1:
    # Display DataFrame
    st.write(hourly_dataframe)

with col2:
    

        # Summary Section
    st.subheader("Summary")
    st.write(f"Average Temperature: {hourly_dataframe['temperature_2m'].mean():.2f} °C")
    st.write(f"Maximum Temperature: {hourly_dataframe['temperature_2m'].max():.2f} °C")
    st.write(f"Minimum Temperature: {hourly_dataframe['temperature_2m'].min():.2f} °C")
    
# Download Data as CSV
    st.download_button(
        label="Download Data as CSV",
        data=hourly_dataframe.to_csv(index=False),
        file_name='weather_data.csv',
        mime='text/csv'
        )



