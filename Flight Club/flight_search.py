# flight_search.py

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Amadeus API Endpoints
IATA_ENDPOINT = "https://test.api.amadeus.com/v1/reference-data/locations/cities"
FLIGHT_ENDPOINT = "https://test.api.amadeus.com/v2/shopping/flight-offers"
TOKEN_ENDPOINT = "https://test.api.amadeus.com/v1/security/oauth2/token"

class FlightSearch:
    """
    This class is responsible for talking to the Amadeus Flight Search API.
    """
    def __init__(self):
        """
        Initializes the FlightSearch client by obtaining an API access token.
        """
        self._api_key = os.environ["AMADEUS_API_KEY"]
        self._api_secret = os.environ["AMADEUS_SECRET"]
        # A new token is obtained each time the program runs.
        self._token = self._get_new_token()

    def _get_new_token(self):
        """
        Generates and returns a new authentication token from the Amadeus API.

        Returns:
            str: The access token, or None if the request fails.
        """
        header = {'Content-Type': 'application/x-www-form-urlencoded'}
        body = {
            'grant_type': 'client_credentials',
            'client_id': self._api_key,
            'client_secret': self._api_secret
        }
        try:
            response = requests.post(url=TOKEN_ENDPOINT, headers=header, data=body)
            response.raise_for_status()
            print("Successfully obtained new Amadeus API token.")
            return response.json()['access_token']
        except requests.exceptions.RequestException as e:
            print(f"Error getting Amadeus API token: {e}")
            return None

    def get_destination_code(self, city_name):
        """
        Retrieves the IATA code for a given city name.

        Args:
            city_name (str): The name of the city.

        Returns:
            str: The IATA code for the city, or "N/A" if not found.
        """
        if not self._token:
            print("Cannot get destination code, authentication token is missing.")
            return "N/A"
            
        headers = {"Authorization": f"Bearer {self._token}"}
        query = {
            "keyword": city_name,
            "max": "2",
            "include": "AIRPORTS",
        }
        try:
            response = requests.get(url=IATA_ENDPOINT, headers=headers, params=query)
            response.raise_for_status()
            # Extract IATA code from the first result
            code = response.json()["data"][0]['iataCode']
            return code
        except requests.exceptions.RequestException as e:
            print(f"API request error for {city_name}: {e}")
            return "N/A"
        except (IndexError, KeyError):
            print(f"No airport IATA code found for {city_name}.")
            return "N/A"

    def check_flights(self, origin_city_code, destination_city_code, from_time, to_time, is_direct=True):
        """
        Searches for flights using the Amadeus API.

        Args:
            origin_city_code (str): IATA code for the origin city.
            destination_city_code (str): IATA code for the destination city.
            from_time (datetime): The start date for the search.
            to_time (datetime): The end date for the search.
            is_direct (bool): Whether to search for non-stop flights only.

        Returns:
            dict or None: Flight data as a dictionary if successful, otherwise None.
        """
        if not self._token:
            print("Cannot check flights, authentication token is missing.")
            return None
            
        headers = {"Authorization": f"Bearer {self._token}"}
        # The 'nonStop' parameter must be a string "true" or "false".
        query = {
            "originLocationCode": origin_city_code,
            "destinationLocationCode": destination_city_code,
            "departureDate": from_time.strftime("%Y-%m-%d"),
            "returnDate": to_time.strftime("%Y-%m-%d"),
            "adults": 1,
            "nonStop": "true" if is_direct else "false",
            "currencyCode": "GBP",
            "max": "10",
        }

        try:
            response = requests.get(url=FLIGHT_ENDPOINT, headers=headers, params=query)
            # A 400 Bad Request can occur if no flights are found, which is not a critical error.
            if response.status_code == 400:
                print(f"No flights found for {destination_city_code}. Status: 400.")
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"There was a problem with the flight search request: {e}")
            return None