import requests
import streamlit as st
from datetime import datetime

class SpaceData:
    def __init__(self, api_key = "DEMO_KEY"):
        self.api_key = api_key
        self.base_url = "https://api.nasa.gov/neo/rest/v1/feed"

    def get_todays_asteroid(self):
        today = datetime.now().strftime("%Y-%m-%d")
        params = {"start_date": today, "end_date": today, "api_key": self.api_key}
        response = requests.get(self.base_url, params)

        if response.status_code == 200:
            return response.json()

        return None

    def get_apod(self):
        self.apod_base_url = "https://api.nasa.gov/planetary/apod"
        params = {"api_key": self.api_key}
        response = requests.get(self.apod_base_url, params)
        if response.status_code == 200:
            return response.json()
        return None

    def get_mars_photos(self, sol = 1000, camera = "fhaz"):
        mars_base_url = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos"
        params = {"sol": sol,
                  "camera": camera,
                  "api_key": self.api_key}

        response = requests.get(mars_base_url, params)

        if response.status_code == 200:
            return response.json()
        return None
secure_key = st.secrets.get("NASA_API_KEY", "DEMO_KEY")
ast = SpaceData(secure_key)
