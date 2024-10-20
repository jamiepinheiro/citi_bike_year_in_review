import cv2
import numpy as np
import argparse

def extract_route(image_path):
    # Load the image
    img = cv2.imread(image_path)
    
    # Convert to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Define range of purple color in HSV
    lower_purple = np.array([130,50,50])
    upper_purple = np.array([170,255,255])
    
    # Threshold the HSV image to get only purple colors
    mask = cv2.inRange(hsv, lower_purple, upper_purple)
    
    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Assuming the largest contour is our route
    route = max(contours, key=cv2.contourArea)
    
    # Convert route to list of coordinates
    route_coords = [tuple(point[0]) for point in route]
    
    return route_coords

def draw_route_ascii(route_coords, width=50, height=20):
    # Initialize the canvas
    canvas = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Find min and max coordinates to scale the route
    min_x = min(coord[0] for coord in route_coords)
    max_x = max(coord[0] for coord in route_coords)
    min_y = min(coord[1] for coord in route_coords)
    max_y = max(coord[1] for coord in route_coords)
    
    # Scale factor
    scale_x = (width - 1) / (max_x - min_x) if max_x != min_x else 1
    scale_y = (height - 1) / (max_y - min_y) if max_y != min_y else 1
    
    # Draw the route
    for i in range(len(route_coords) - 1):
        x1, y1 = route_coords[i]
        x2, y2 = route_coords[i+1]
        
        # Scale coordinates
        sx1 = int((x1 - min_x) * scale_x)
        sy1 = int((y1 - min_y) * scale_y)
        sx2 = int((x2 - min_x) * scale_x)
        sy2 = int((y2 - min_y) * scale_y)
        
        # Draw line
        if sx1 == sx2:
            for y in range(min(sy1, sy2), max(sy1, sy2) + 1):
                canvas[y][sx1] = '|'
        elif sy1 == sy2:
            for x in range(min(sx1, sx2), max(sx1, sx2) + 1):
                canvas[sy1][x] = '-'
        else:
            # Diagonal line (simplified)
            canvas[sy1][sx1] = '\\'
            canvas[sy2][sx2] = '\\'
    
    # Mark start and end points
    start_x, start_y = route_coords[0]
    end_x, end_y = route_coords[-1]
    canvas[int((start_y - min_y) * scale_y)][int((start_x - min_x) * scale_x)] = 'S'
    canvas[int((end_y - min_y) * scale_y)][int((end_x - min_x) * scale_x)] = 'E'
    
    # Convert canvas to string
    return '\n'.join(''.join(row) for row in canvas)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract route from an image.')
    parser.add_argument('image_path', type=str, help='Path to the image file')
    args = parser.parse_args()
    
    route = extract_route(args.image_path)
    ascii_map = draw_route_ascii(route)
    print(ascii_map)

# print(route)

