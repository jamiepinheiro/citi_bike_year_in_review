import re
from email import policy
from email.parser import BytesParser
import json
from fuzzywuzzy import process
import html
import sys
import argparse

def load_station_data(station_fpath):
    with open(station_fpath, 'r') as f:
        data = json.load(f)
    return {station['name']: [station['lat'], station['lon']] for station in data['data']['stations']}

def find_coordinates(station_name, station_data):
    # Decode HTML entities
    station_name = html.unescape(station_name)
    
    # Find the best match using fuzzy string matching
    best_match = process.extractOne(station_name, station_data.keys())
    
    if best_match and best_match[1] >= 90:  # Adjust the threshold as needed
        coords = station_data[best_match[0]]
        # Data now has lat and long in the correct order
        return coords
    return None

class Receipt:
    def __init__(self, email_file, station_data):
        with open(email_file, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)

        html_content = msg.get_body(preferencelist=('html',)).get_content()

        # Extract ride details
        ride_date = re.search(r'(\w+ \d+, \d{4})\s+AT\s+(\d+:\d+ [AP]M)', html_content)
        start_location = re.search(r'<td[^>]*>([^<]+)</td>\s*<td[^>]*>\s*<span[^>]*>Start</span>', html_content)
        end_location = re.search(r'<td[^>]*>([^<]+)</td>\s*<td[^>]*>\s*<span[^>]*>End</span>', html_content)
        start_time = re.search(r'<span[^>]*>Start</span><br>\s*([\d:]+\s*[ap]m)', html_content, re.IGNORECASE)
        end_time = re.search(r'<span[^>]*>End</span><br>\s*([\d:]+\s*[ap]m)', html_content, re.IGNORECASE)

        # Extract charges
        charges = re.findall(r'<td[^>]*>((?:(?!</td>).)*?)</td>\s*<td[^>]*>\$([\d.]+)', html_content, re.DOTALL)

        # Extract payment method and total
        payment_method = re.search(r'(Mastercard|Visa|American Express)\s*\*(\d{4})', html_content)
        total = re.search(r'Total\s*</td>\s*<td[^>]*>\$([\d.]+)', html_content)

        # Extract Lyft Pink savings
        lyft_pink_savings = re.search(r'Saved this trip\s*</td>\s*<td[^>]*>\$([\d.]+)', html_content)

        # Extract receipt number
        receipt_number = re.search(r'Receipt #\s*(\d+)', html_content)

        # Extract Lyft API URL
        lyft_api_url = re.search(r'(https://api\.lyft\.com/v1/rides/\w+)', html_content)

        # Extract map image URL
        self.map_image_url = self.extractMapImageUrl(html_content)

        start_location_str = start_location.group(1).strip() if start_location else None
        end_location_str = end_location.group(1).strip() if end_location else None

        self.date = ride_date.group(1) if ride_date else None
        self.time = ride_date.group(2) if ride_date else None
        self.start_location = start_location.group(1).strip() if start_location else None
        self.end_location = end_location.group(1).strip() if end_location else None
        self.start_time = start_time.group(1) if start_time else None
        self.start_location_coordinates = find_coordinates(start_location_str, station_data)
        self.end_location_coordinates = find_coordinates(end_location_str, station_data)
        self.end_time = end_time.group(1) if end_time else None
        self.charges = [(charge[0].strip(), charge[1]) for charge in charges]
        self.payment_method = f"{payment_method.group(1)} *{payment_method.group(2)}" if payment_method else None
        self.total = total.group(1) if total else None
        self.lyft_pink_savings = lyft_pink_savings.group(1) if lyft_pink_savings else None
        self.receipt_number = receipt_number.group(1) if receipt_number else None
        self.lyft_api_url = lyft_api_url.group(1) if lyft_api_url else None

    def __str__(self):
        return (
            f"Receipt(\n"
            f"    date={self.date},\n"
            f"    time={self.time},\n"
            f"    start_location={self.start_location},\n"
            f"    end_location={self.end_location},\n"
            f"    start_time={self.start_time},\n"
            f"    start_location_coordinates={self.start_location_coordinates},\n"
            f"    end_location_coordinates={self.end_location_coordinates},\n"
            f"    end_time={self.end_time},\n"
            f"    charges={self.charges},\n"
            f"    payment_method={self.payment_method},\n"
            f"    total={self.total},\n"
            f"    lyft_pink_savings={self.lyft_pink_savings},\n"
            f"    receipt_number={self.receipt_number},\n"
            f"    map_image_url={self.map_image_url}\n"
            f")"
        )

    def extractMapImageUrl(self, html_content):
        regex = r'(https://api\.lyft\.com/v1/staticmap/general[^"\']+)'
        match = re.search(regex, html_content)
        if match:
            encoded_url = match.group(1)
            decoded_url = html.unescape(encoded_url)
            return decoded_url.replace('&amp;', '&')
        return None

def main():
    parser = argparse.ArgumentParser(description='Parse Lyft receipt from email file.')
    parser.add_argument('email_file', type=str, help='Path to the email file')
    args = parser.parse_args()

    email_file = args.email_file
    station_data = load_station_data('data/stations.json')
    # print(station_data)
    parsed_data = Receipt(email_file, station_data)

    print(parsed_data) 

if __name__ == "__main__":
    main()
