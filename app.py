import requests
import streamlit as st

ors_key = st.secrets["ors_key"]

st.markdown('''
# NY taxi fare predictor
''')

pickup_date = st.date_input('Pickup date:')
pickup_time = st.time_input('Pickup time:')
pickup_longitude = st.number_input('Pickup longitude:', value=-74.006111)
pickup_latitude = st.number_input('Pickup latitude:', value=40.712778)
dropoff_longitude = st.number_input('Dropoff longitude:', value=-74.006111)
dropoff_latitude = st.number_input('Dropoff latitude:', value=40.712778)
passenger_count = st.number_input('How many passengers?', min_value=1, max_value=8, value='min')


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

st.markdown(f'''
#### **Predicted fare:**
#### ${round(response['fare'], 2)}
''')
