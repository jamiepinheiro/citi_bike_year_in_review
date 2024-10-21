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

class NormalizedRoute:
    def __init__(self, email_file, station_data):
        self.receipt = Receipt(email_file, station_data)
        self.route = extract_route(self.receipt.map_image_file)
        self.gps_coords = pixel_to_gps_coordinates(self.route, self.receipt.start_location_coordinates, self.receipt.end_location_coordinates)
    

    def print_details(self):
        print(self.receipt)

        print(f"Start point: {self.route.start_point}")
        print(f"End point: {self.route.end_point}")
        print(f"Route coordinates (first 5): {self.route.route_coords[:5]}")
        print(f"GPS coordinates (first 5): {self.gps_coords[:5]}")
        draw_route_ascii(self.route)
        route_map = draw_route_on_map(self.gps_coords)
        # Get the directory and filename of the receipt
        receipt_dir = os.path.dirname(self.receipt.map_image_file)
        receipt_filename = os.path.splitext(os.path.basename(self.receipt.map_image_file))[0]
        
        # Create the route map filename with the same suffix as the receipt
        route_map_filename = f"{receipt_filename}_route_map.html"
        
        # Save the route map in the same directory as the receipt
        route_map_path = os.path.join(receipt_dir, route_map_filename)
        route_map.save(route_map_path)
        print(f"Route map saved as: {route_map_path}")

def main():
    parser = argparse.ArgumentParser(description='Process Citi Bike receipt and route image.')
    parser.add_argument('email_file', type=str, help='Path to the email file (.eml)')
    args = parser.parse_args()

    # Load station data
    station_data = load_station_data('data/stations.json')
     
    normalized_route = NormalizedRoute(args.email_file, station_data)
    normalized_route.print_details()

if __name__ == "__main__":
    main()
