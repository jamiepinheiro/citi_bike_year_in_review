import argparse
import os
from receipt_parser import Receipt, load_station_data
from route_ingestor import extract_route, draw_route_ascii
import numpy as np
import folium

def draw_route_on_map(coordinates, zoom_start=12):
    # Calculate the center of the route
    center_lat = sum(coord[0] for coord in coordinates) / len(coordinates)
    center_lon = sum(coord[1] for coord in coordinates) / len(coordinates)
    
    # Create a map centered on the route
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start)
    
    # Add the route to the map
    folium.PolyLine(locations=coordinates, weight=5, color='blue').add_to(m)
   
    return m

def pixel_to_gps_coordinates(route, start_gps, end_gps):
    # Convert route coordinates to numpy array
    pixel_coords = np.array(route.route_coords)
    
    # Extract start and end points from the Route object
    start_pixel = np.array(route.start_point)
    end_pixel = np.array(route.end_point)
    
    # Calculate the pixel differences
    pixel_diff = end_pixel - start_pixel
    
    # Normalize coordinates based on start and end points
    normalized_coords = (pixel_coords - start_pixel) / pixel_diff
    
    # Calculate the latitude and longitude differences
    lat_diff = end_gps[0] - start_gps[0]
    lon_diff = end_gps[1] - start_gps[1]
    
    # Convert normalized coordinates to GPS coordinates
    gps_coords = np.array(start_gps) + normalized_coords[:, [1, 0]] * np.array([lat_diff, lon_diff])
    
    return gps_coords.tolist()

def _pixel_to_gps_coordinates(route, start_gps, end_gps):
    # Convert route coordinates to numpy array
    pixel_coords = np.array(route.route_coords)
    
    # Extract start and end points from the Route object
    start_pixel = np.array(route.start_point)
    end_pixel = np.array(route.end_point)
    
    # Calculate the pixel differences
    pixel_diff = end_pixel - start_pixel
    
    # Normalize coordinates based on start and end points
    normalized_coords = (pixel_coords - start_pixel) / pixel_diff
    
    # Calculate the latitude and longitude differences
    lat_diff = end_gps[0] - start_gps[0]
    lon_diff = end_gps[1] - start_gps[1]
    
    # Convert normalized coordinates to GPS coordinates
    gps_coords = start_gps + normalized_coords * [lat_diff, lon_diff]
    
    return [start_gps] + gps_coords.tolist()

def main():
    parser = argparse.ArgumentParser(description='Process Citi Bike receipt and route image.')
    parser.add_argument('email_file', type=str, help='Path to the email file (.eml)')
    parser.add_argument('image_file', type=str, help='Path to the route image file (.png)')
    args = parser.parse_args()

    # Load station data
    station_data = load_station_data('data/stations.json')

    # Process receipt
    receipt = Receipt(args.email_file, station_data)
    print(receipt)

    # Process route image
    route = extract_route(args.image_file)
    print(f"Start point: {route.start_point}")
    print(f"End point: {route.end_point}")
    print(f"Route coordinates (first 5): {route.route_coords[:5]}")
    ascii_map = draw_route_ascii(route)
    print(ascii_map)

    # Convert route coordinates to GPS coordinates
    gps_coords = pixel_to_gps_coordinates(route, receipt.start_location_coordinates, receipt.end_location_coordinates)
    print(f"GPS coordinates (first 5): {gps_coords[:5]}")

    route_map = draw_route_on_map(gps_coords)
    
    # Save the map to an HTML file
    route_map.save("route_map.html")

if __name__ == "__main__":
    main()
