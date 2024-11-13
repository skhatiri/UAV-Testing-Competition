from math import cos, sin, sqrt, radians, atan2, degrees
from typing import List, Dict
from config import SPIRAL_RADIUS_INCREMENT, SPIRAL_NUM_POINTS, SPIRAL_GOLDEN_ANGLE

class Position:
    """
    Represents a 3D position in Cartesian coordinates with an optional angle attribute.
    
    Attributes:
    x (float): X-coordinate in meters.
    y (float): Y-coordinate in meters.
    z (float): Z-coordinate in meters (default is 0).
    angle (int): Angle in degrees (default is 0).
    """
    def __init__(self, x: float, y: float, z: float = 0, angle: int = 0) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.angle = angle

def latlon_to_cartesian(lat: float, lon: float, origin_lat: float, origin_lon: float) -> tuple:
    """
    Converts latitude and longitude to Cartesian coordinates relative to a specified origin.
    
    Args:
    lat (float): Latitude of the target point.
    lon (float): Longitude of the target point.
    origin_lat (float): Latitude of the origin point.
    origin_lon (float): Longitude of the origin point.
    
    Returns:
    tuple: A tuple containing (x, y) Cartesian coordinates in meters.
    """
    # Conversion factors based on Earth's curvature
    lat_to_meters = 111000  # Approximate meters per degree of latitude
    lon_to_meters = 111000 * cos(radians(origin_lat))  # Meters per degree of longitude at the origin latitude

    # Calculate deltas in degrees
    delta_lat = lat - origin_lat
    delta_lon = lon - origin_lon

    # Convert deltas to meters
    x = delta_lon * lon_to_meters
    y = delta_lat * lat_to_meters

    return x, y

def fibonacci_spiral(n: int, center: Position, bottom_left: Position, top_right: Position) -> List[Position]:
    """
    Generates positions in a Fibonacci spiral pattern within specified bounds.
    
    Args:
    n (int): Number of main spiral points (each will generate multiple sub-points).
    center (Position): The center of the spiral.
    bottom_left (Position): Bottom-left boundary of the area.
    top_right (Position): Top-right boundary of the area.
    
    Returns:
    List[Position]: A list of Position objects that lie within the specified bounds.
    """
    # Golden angle in radians for Fibonacci spiral generation
    golden_angle = SPIRAL_GOLDEN_ANGLE
    positions = []
    
    # Generate points along the spiral, scaling the radius incrementally
    for i in range(n * SPIRAL_NUM_POINTS):
        # Radius grows linearly with the point index
        radius = SPIRAL_RADIUS_INCREMENT * (i + 1) 
        theta = i * golden_angle  # Angle for the current point

        # Calculate Cartesian coordinates
        x = center.x + radius * cos(theta)
        y = center.y + radius * sin(theta)
        
        # Add point if within specified rectangular boundary
        if bottom_left.x <= x <= top_right.x and bottom_left.y <= y <= top_right.y:
            positions.append(Position(x, y))  # Create Position instance and add to list
    
    return positions

def calculate_inclination(point1, point2):
    """
    Calculates the inclination angle between two points in a 2D plane relative to a vertical line (90 degrees).
    The result is the angle in degrees, with a positive or negative sign indicating direction relative to 90 degrees.
    
    Parameters:
    point1 (tuple): The first point as a tuple (x1, y1).
    point2 (tuple): The second point as a tuple (x2, y2).
    
    Returns:
    float: The angle in degrees, measured from 90 degrees, with a positive sign if the line leans to the right
           and a negative sign if it leans to the left.
    """
    
    
    # Calculate the difference in x and y coordinates between the two points
    dx = point2.x - point1.x
    dy = point2.y - point1.y
    
    # Calculate the angle (in radians) and convert to degrees
    angle_radians = atan2(dy, dx)
    angle_degrees = degrees(angle_radians)
    
    # Calculate deviation from 90 degrees
    deviation_from_90 =  90 - angle_degrees
    
    # Return the deviation with the correct sign (+ for right, - for left)
    return (deviation_from_90>= 0), angle_degrees

def is_left_of_trajectory(segment: List[Position], point: Position) -> bool:
        # Implement logic to check if the point is on the left of the trajectory based on the segment
        x1, y1 = segment[0].x, segment[0].y
        x2, y2 = segment[-1].x, segment[-1].y
        px, py = point.x, point.y
        return (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1) > 0  # True if point is on the left
