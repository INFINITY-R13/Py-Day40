# data_manager.py

import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DataManager:
    """
    This class is responsible for talking to the Google Sheet.
    It uses the Sheety API to get and update destination data.
    """
    def __init__(self):
        """
        Initializes the DataManager with authentication details from environment variables.
        """
        # Sheety API credentials and endpoints
        self._user = os.environ["SHEETY_USERNAME"]
        self._password = os.environ["SHEETY_PASSWORD"]
        self.prices_endpoint = os.environ["SHEETY_PRICES_ENDPOINT"]
        self.users_endpoint = os.environ["SHEETY_USERS_ENDPOINT"]
        self._authorization = HTTPBasicAuth(self._user, self._password)
        
        # Data attributes to be populated by API calls
        self.destination_data = {}
        self.customer_data = {}

    def get_destination_data(self):
        """
        Retrieves flight destination data from the Google Sheet via the Sheety API.
        
        Returns:
            list: A list of dictionaries, where each dictionary represents a row in the sheet.
                  Returns an empty list if the request fails.
        """
        try:
            response = requests.get(url=self.prices_endpoint)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            data = response.json()
            self.destination_data = data.get("prices", [])
            return self.destination_data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching destination data from Sheety: {e}")
            return []

    def update_destination_codes(self):
        """
        Updates the 'iataCode' in the Google Sheet for each city in self.destination_data.
        """
        print("Updating destination IATA codes in Google Sheet...")
        for city in self.destination_data:
            # Prepare the data payload for the PUT request
            new_data = {
                "price": {
                    "iataCode": city["iataCode"]
                }
            }
            try:
                # Make the PUT request to update the specific row
                response = requests.put(
                    url=f"{self.prices_endpoint}/{city['id']}",
                    json=new_data
                )
                response.raise_for_status()
                print(f"Successfully updated IATA code for {city['city']}.")
            except requests.exceptions.RequestException as e:
                print(f"Error updating IATA code for {city['city']}: {e}")

    def get_customer_emails(self):
        """
        Retrieves customer email data from the Google Sheet.
        
        Returns:
            list: A list of dictionaries containing user information.
                  Returns an empty list if the request fails.
        """
        try:
            response = requests.get(url=self.users_endpoint)
            response.raise_for_status()
            data = response.json()
            # The sheet tab name is expected to be 'users'
            self.customer_data = data.get("users", [])
            return self.customer_data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching customer emails from Sheety: {e}")
            return []