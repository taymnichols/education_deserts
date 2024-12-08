import concurrent.futures
import openrouteservice
import pandas as pd
import os

# Get the API key from environment variables
api_key = os.getenv('ORS_API_KEY')

# Initialize the client
client = openrouteservice.Client(key=api_key)

# Assuming you have a dataframe `colleges_lat_long` with columns for lat and lon
colleges_lat_long = pd.read_csv("static/addresses_clean.csv")

print(colleges_lat_long.columns)

def calculate_drive_time_polygon(lat, lon):
    # Make a request to ORS API to get the 30-minute drive time polygon
    routes = client.isochrones(
        locations=[(lon, lat)],
        profile='driving-car',  # or another profile like 'driving-hgv' depending on your needs
        range_type='time',  # specifies that it's a time-based range
        range=[30*60]  # 30-minute drive time in seconds
    )
    return routes

# Function to process multiple colleges in parallel
def process_colleges_in_parallel(colleges_lat_long):
    # Use ThreadPoolExecutor for parallel API calls
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Submit jobs to the executor for each college (lat, lon pair)
        futures = [
            executor.submit(calculate_drive_time_polygon, lat, lon)
            for lat, lon in zip(colleges_lat_long['Latitude'], colleges_lat_long['Longitude'])
        ]
        
        # Collect results from all futures
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    return results

# Process all colleges
drive_time_polygons = process_colleges_in_parallel(colleges_lat_long)
