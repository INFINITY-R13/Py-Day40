# main.py

import time
from datetime import datetime, timedelta
from data_manager import DataManager
from flight_search import FlightSearch
from flight_data import find_cheapest_flight
from notification_manager import NotificationManager

# --- 1. SETUP ---
# Initialize the helper classes.
data_manager = DataManager()
flight_search = FlightSearch()
notification_manager = NotificationManager()

# Set the origin city for all flight searches.
ORIGIN_CITY_IATA = "LON"

# --- 2. GET & UPDATE DESTINATION DATA ---
# Fetch existing destination data from the Google Sheet.
sheet_data = data_manager.get_destination_data()

# Check if any destinations are missing an IATA code and update them.
for row in sheet_data:
    if row["iataCode"] == "":
        print(f"Finding IATA code for {row['city']}...")
        row["iataCode"] = flight_search.get_destination_code(row["city"])
        # Pause between requests to avoid hitting API rate limits.
        time.sleep(1)

# Update the destination_data in the DataManager and write changes to the Google Sheet.
data_manager.destination_data = sheet_data
data_manager.update_destination_codes()

# --- 3. GET CUSTOMER EMAILS ---
# Retrieve customer emails from the 'users' tab in the Google Sheet.
customer_data = data_manager.get_customer_emails()
# Ensure the column name matches your sheet exactly (e.g., "whatIsYourEmail?").
customer_email_list = [row["whatIsYourEmail?"] for row in customer_data]
print(f"Found {len(customer_email_list)} emails for notifications.")

# --- 4. SEARCH FOR FLIGHTS & NOTIFY ---
# Define the search period: from tomorrow to 6 months from now.
# Note: (6 * 30) is an approximation for 6 months.
tomorrow = datetime.now() + timedelta(days=1)
six_months_from_today = datetime.now() + timedelta(days=(6 * 30))

# Iterate through each destination in the Google Sheet.
for destination in sheet_data:
    print(f"--- Checking flights for {destination['city']} ---")
    
    # First, search for direct flights.
    flights = flight_search.check_flights(
        origin_city_code=ORIGIN_CITY_IATA,
        destination_city_code=destination["iataCode"],
        from_time=tomorrow,
        to_time=six_months_from_today,
        is_direct=True
    )
    cheapest_flight = find_cheapest_flight(flights)

    # If no direct flights are found, search for flights with one stop.
    if cheapest_flight.price == "N/A":
        print(f"No direct flights to {destination['city']}. Searching for indirect flights...")
        flights_with_stops = flight_search.check_flights(
            origin_city_code=ORIGIN_CITY_IATA,
            destination_city_code=destination["iataCode"],
            from_time=tomorrow,
            to_time=six_months_from_today,
            is_direct=False
        )
        cheapest_flight = find_cheapest_flight(flights_with_stops)
    
    # If a cheap flight is found (cheaper than the target price in the sheet), send notifications.
    if cheapest_flight.price != "N/A" and cheapest_flight.price < destination["lowestPrice"]:
        
        # Customize the message based on whether the flight is direct or has stops.
        if cheapest_flight.stops == 0:
            message = (f"Low price alert! Only £{cheapest_flight.price} to fly direct "
                       f"from {cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}, "
                       f"from {cheapest_flight.out_date} to {cheapest_flight.return_date}.")
        else:
            message = (f"Low price alert! Only £{cheapest_flight.price} to fly "
                       f"from {cheapest_flight.origin_airport} to {cheapest_flight.destination_airport}, "
                       f"with {cheapest_flight.stops} stop(s), "
                       f"from {cheapest_flight.out_date} to {cheapest_flight.return_date}.")
        
        print(message)
        
        # Send notifications via WhatsApp and Email.
        # notification_manager.send_sms(message_body=message)
        notification_manager.send_whatsapp(message_body=message)
        notification_manager.send_emails(email_list=customer_email_list, email_body=message)

    # Pause between checking each destination to respect API rate limits.
    time.sleep(1)