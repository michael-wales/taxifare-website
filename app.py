import streamlit as st
import folium
import geopy
import requests

st.title("NY taxi fare predictor")

pickup_date = st.date_input('Pickup date:')
pickup_time = st.time_input('Pickup time:')

pickup_type = st.radio("Choose pickup input method:", ("Address", "Coordinates"))

if pickup_type == "Address":
    pickup_address = st.text_input("Enter pickup address")
    pickup_latitude = None
    pickup_longitude = None
else:
    pickup_address = None
    pickup_latitude = st.number_input("Enter pickup latitude", value=None)
    pickup_longitude = st.number_input("Enter pickup longitude", value=None)

dropoff_type = st.radio("Choose dropoff input method:", ("Address", "Coordinates"))

if dropoff_type == "Address":
    dropoff_address = st.text_input("Enter dropoff address")
    dropoff_latitude = None
    dropoff_longitude = None
else:
    dropoff_address = None
    dropoff_latitude = st.number_input("Enter dropoff latitude", value=None)
    dropoff_longitude = st.number_input("Enter dropoff longitude", value=None)

geolocator = geopy.geocoders.Nominatim(user_agent="taxifare-map-app")

def create_map(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude):

    m = folium.Map(location=[(pickup_latitude + dropoff_latitude) / 2, (pickup_longitude + dropoff_longitude) / 2], zoom_start=6)

    folium.Marker([pickup_latitude, pickup_longitude], popup="Pickup", icon=folium.Icon(color='blue')).add_to(m)
    folium.Marker([dropoff_latitude, dropoff_longitude], popup="Dropoff", icon=folium.Icon(color='red')).add_to(m)

    m.fit_bounds([[pickup_latitude, pickup_longitude], [dropoff_latitude, dropoff_longitude]])

    # Return the map HTML to embed in Streamlit
    return m._repr_html_()

# Geocode the addresses with retries in case of failure
def geocode_with_retry(address, retries=3):
    for _ in range(retries):
        lat, lon = None, None
        try:
            location = geolocator.geocode(address)
            if location:
                lat, lon = location.latitude, location.longitude
        except Exception as e:
            st.error(f"Error geocoding address: {e}")
        if lat is not None and lon is not None:
            return lat, lon
    return None, None

if pickup_type == "Address" and pickup_address:
    pickup_latitude, pickup_longitude = geocode_with_retry(pickup_address)
    if pickup_latitude is None or pickup_longitude is None:
        st.error("Unable to geocode pickup address.")

elif pickup_type == "Coordinates" and pickup_latitude and pickup_longitude:
    pass  # Use the provided coordinates directly
else:
    st.error("Please provide either an address or coordinates for pickup location.")

if dropoff_type == "Address" and dropoff_address:
    dropoff_latitude, dropoff_longitude = geocode_with_retry(dropoff_address)
    if dropoff_latitude is None or dropoff_longitude is None:
        st.error("Unable to geocode dropoff address.")

elif dropoff_type == "Coordinates" and dropoff_latitude and dropoff_longitude:
    pass  # Use the provided coordinates directly
else:
    st.error("Please provide either an address or coordinates for dropoff location.")

passenger_count = st.number_input('How many passengers?', min_value=1, max_value=8, value=1)

url = 'https://taxifare-805490564375.europe-west1.run.app/predict'

params =  {
    "pickup_datetime": str(pickup_date) + ' ' + str(pickup_time),
    "pickup_longitude": pickup_longitude,
    "pickup_latitude": pickup_latitude,
    "dropoff_longitude": dropoff_longitude,
    "dropoff_latitude": dropoff_latitude,
    "passenger_count": int(passenger_count)
}

response = requests.get(url, params=params).json()

if 'fare' in response:
    st.markdown(f'#### **Predicted fare:** ${round(response["fare"], 2)}')

if pickup_latitude is not None and dropoff_latitude is not None:
    map_html = create_map(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude)
    st.components.v1.html(map_html, height=500)
else:
    st.error("Both pickup and dropoff locations need to be provided.")
