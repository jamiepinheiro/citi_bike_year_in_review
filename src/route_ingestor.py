import cv2
import numpy as np
import argparse

class Route:
    def __init__(self, route_coords, end_point):
        self.route_coords = route_coords
        self.end_point = end_point
        self.start_point = max(route_coords, key=lambda p: (p[0] - end_point[0])**2 + (p[1] - end_point[1])**2)

    def __str__(self):
        return f"Route(route_coords={self.route_coords[:5]}..., start_point={self.start_point}, end_point={self.end_point})"

def extract_route(image_path):
    img = cv2.imread(image_path)
    
    # Convert to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Define color ranges in HSV
    lower_purple = np.array([130,50,50])
    upper_purple = np.array([170,255,255])
    lower_pink = np.array([145,50,50])
    upper_pink = np.array([175,255,255])
    
    # Create masks
    purple_mask = cv2.inRange(hsv, lower_purple, upper_purple)
    pink_mask = cv2.inRange(hsv, lower_pink, upper_pink)
    
    # Find contours
    purple_contours, _ = cv2.findContours(purple_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    pink_contours, _ = cv2.findContours(pink_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    def find_circular_point(contours):
        for contour in sorted(contours, key=cv2.contourArea, reverse=True):
            # Compute circularity
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * (area / (perimeter * perimeter))
            
            # If the contour is sufficiently circular
            if circularity > 0.8:  # You might need to adjust this threshold
                (x, y), radius = cv2.minEnclosingCircle(contour)
                return (int(x), int(y))
        return None
    
    # Find end (pink) point
    end_point = find_circular_point(pink_contours)
    
    # Find the route (the largest purple contour that's not circular)
    route_contour = max(purple_contours, key=cv2.contourArea)
    route_coords = [tuple(point[0]) for point in route_contour]
    
    return Route(route_coords, end_point)

def draw_route_ascii(route, width=25, height=25):
    # Initialize the canvas
    route_coords = route.route_coords
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
    start_x, start_y = route.start_point
    end_x, end_y = route.end_point
    canvas[int((start_y - min_y) * scale_y)][int((start_x - min_x) * scale_x)] = 'S'
    canvas[int((end_y - min_y) * scale_y)][int((end_x - min_x) * scale_x)] = 'E'
    
    # Convert canvas to string
    return '\n'.join(''.join(row) for row in canvas)

def main():
    parser = argparse.ArgumentParser(description='Extract route from image and display ASCII map.')
    parser.add_argument('image_path', type=str, help='Path to the image file containing the route')
    args = parser.parse_args()
    route = extract_route_and_points(args.image_path)
    ascii_map = draw_route_ascii(route)
    print(ascii_map)
    print(route)

if __name__ == "__main__":
    main()
