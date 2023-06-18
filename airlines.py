import requests
import config

url = "https://flight-radar1.p.rapidapi.com/airlines/list"

headers = {
    "X-RapidAPI-Key": config.api_key,
    "X-RapidAPI-Host": config.host
}

response = requests.get(url, headers=headers)

data = response.json()

# Create an empty list to store the names of airlines
airline_names = []

# Iterate over the list of airlines
for airline in data['rows']:
    # Add the name of each airline to the list
    airline_names.append(airline['Name'])

# Return the list of airline names
def get_airline_names():
    return airline_names
