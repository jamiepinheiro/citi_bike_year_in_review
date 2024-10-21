import os
import folium
from folium.plugins import HeatMap
import numpy as np
from receipt_parser import Receipt, load_station_data
from normalized_route import NormalizedRoute
import argparse

def create_heatmap(directory_path, output_file='heatmap.html', verbose=False):
    station_data = load_station_data('data/stations.json')
    all_gps_coords = []

    for filename in os.listdir(directory_path):
        if filename.endswith('.eml'):
            file_path = os.path.join(directory_path, filename)

            try:
                normalized_route = NormalizedRoute(file_path, station_data)
                if verbose:
                    normalized_route.print_details()
                all_gps_coords.extend(normalized_route.gps_coords)
            except Exception as e:
                print(f"Skipping {filename}: {str(e)}")

    if not all_gps_coords:
        print("No GPS coordinates found in the processed files.")
        return

    center_lat = sum(coord[0] for coord in all_gps_coords) / len(all_gps_coords)
    center_lon = sum(coord[1] for coord in all_gps_coords) / len(all_gps_coords)

    heatmap = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    HeatMap(all_gps_coords, radius=10, blur=9, max_zoom=1).add_to(heatmap)
    heatmap.save(output_file)
    print(f"Heatmap saved to {output_file}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Create a heatmap from .eml files in a directory.')
    parser.add_argument('directory', type=str, help='Path to the directory containing .eml files')
    parser.add_argument('--output', type=str, default='heatmap.html', help='Output file name for the heatmap (default: heatmap.html)')
    parser.add_argument('--verbose', action='store_true', help='Print details of each receipt')
    args = parser.parse_args()

    create_heatmap(args.directory, args.output, verbose=args.verbose)
