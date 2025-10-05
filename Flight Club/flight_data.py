# flight_data.py

class FlightData:
    """
    A class to structure the flight data obtained from the API.
    """
    def __init__(self, price, origin_airport, destination_airport, out_date, return_date, stops):
        """
        Constructor for initializing a new flight data instance with specific travel details.

        Parameters:
        - price (float): The cost of the flight.
        - origin_airport (str): The IATA code for the flight's origin airport.
        - destination_airport (str): The IATA code for the flight's destination airport.
        - out_date (str): The departure date for the flight (YYYY-MM-DD).
        - return_date (str): The return date for the flight (YYYY-MM-DD).
        - stops (int): The number of stops for the outbound flight (0 for direct).
        """
        self.price = price
        self.origin_airport = origin_airport
        self.destination_airport = destination_airport
        self.out_date = out_date
        self.return_date = return_date
        self.stops = stops

def find_cheapest_flight(data):
    """
    Parses flight data from the Amadeus API to find the cheapest flight option.

    Args:
        data (dict): The JSON data containing flight information from the API.

    Returns:
        FlightData: An instance of FlightData for the cheapest flight found.
        Returns a FlightData instance with 'N/A' fields if no flights are available.
    """
    # Return a placeholder object if the API response is empty or invalid.
    if data is None or not data.get('data'):
        print("No flight data found.")
        return FlightData(
            price="N/A",
            origin_airport="N/A",
            destination_airport="N/A",
            out_date="N/A",
            return_date="N/A",
            stops="N/A"
        )

    # Initialize variables to track the cheapest flight found so far.
    lowest_price = float('inf')
    cheapest_flight_data = None

    # Iterate through all flight offers to find the one with the lowest price.
    for flight in data['data']:
        price = float(flight["price"]["grandTotal"])
        if price < lowest_price:
            lowest_price = price
            cheapest_flight_data = flight

    # If no cheapest flight was found (e.g., initial data was valid but empty), return the placeholder.
    if cheapest_flight_data is None:
        return FlightData(
            price="N/A",
            origin_airport="N/A",
            destination_airport="N/A",
            out_date="N/A",
            return_date="N/A",
            stops="N/A"
        )
        
    # --- Correctly parse details from the actual cheapest flight ---
    
    # The outbound journey is the first itinerary.
    outbound_itinerary = cheapest_flight_data["itineraries"][0]
    # The return journey is the second itinerary.
    return_itinerary = cheapest_flight_data["itineraries"][1]
    
    # Calculate the number of stops. A flight with 2 segments has 1 stop.
    num_stops = len(outbound_itinerary["segments"]) - 1
    
    # Extract flight details.
    origin = outbound_itinerary["segments"][0]["departure"]["iataCode"]
    # The final destination is the arrival airport of the last segment in the outbound journey.
    destination = outbound_itinerary["segments"][-1]["arrival"]["iataCode"]
    
    # Extract dates and split to remove the time part.
    out_date = outbound_itinerary["segments"][0]["departure"]["at"].split("T")[0]
    return_date = return_itinerary["segments"][0]["departure"]["at"].split("T")[0]
    
    # Create and return the FlightData object with the correct details.
    cheapest_flight = FlightData(
        price=lowest_price,
        origin_airport=origin,
        destination_airport=destination,
        out_date=out_date,
        return_date=return_date,
        stops=num_stops
    )
    
    print(f"Lowest price to {destination} is £{lowest_price} with {num_stops} stop(s).")
    return cheapest_flight