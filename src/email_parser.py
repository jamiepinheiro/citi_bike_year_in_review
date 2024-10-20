import re
import email
from email import policy
from email.parser import BytesParser

def parse_citi_bike_receipt(email_file):
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

    return {
        'date': ride_date.group(1) if ride_date else None,
        'time': ride_date.group(2) if ride_date else None,
        'start_location': start_location.group(1).strip() if start_location else None,
        'end_location': end_location.group(1).strip() if end_location else None,
        'start_time': start_time.group(1) if start_time else None,
        'end_time': end_time.group(1) if end_time else None,
        'charges': [(charge[0].strip(), charge[1]) for charge in charges],
        'payment_method': f"{payment_method.group(1)} *{payment_method.group(2)}" if payment_method else None,
        'total': total.group(1) if total else None,
        'lyft_pink_savings': lyft_pink_savings.group(1) if lyft_pink_savings else None,
        'receipt_number': receipt_number.group(1) if receipt_number else None
    }

def main():
    email_file = 'examples/2.eml'  # Replace with the path to your email file
    parsed_data = parse_citi_bike_receipt(email_file)

    print("Citi Bike Ride Receipt:")
    print(f"Date: {parsed_data['date']}")
    print(f"Time: {parsed_data['time']}")
    print(f"Start Location: {parsed_data['start_location']}")
    print(f"End Location: {parsed_data['end_location']}")
    print(f"Start Time: {parsed_data['start_time']}")
    print(f"End Time: {parsed_data['end_time']}")
    print("\nCharges:")
    for charge in parsed_data['charges']:
        print(f"- {charge[0]}: ${charge[1]}")
    print(f"\nPayment Method: {parsed_data['payment_method']}")
    print(f"Total: ${parsed_data['total']}")
    print(f"Lyft Pink Savings: ${parsed_data['lyft_pink_savings']}")
    print(f"Receipt Number: {parsed_data['receipt_number']}")

if __name__ == "__main__":
    main()
