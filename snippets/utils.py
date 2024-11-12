from math import cos, sin, sqrt, radians
from typing import List, Dict
import config

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
    golden_angle = config.SPIRAL_GOLDEN_ANGLE
    positions = []
    
    # Generate points along the spiral, scaling the radius incrementally
    for i in range(n * config.SPIRAL_NUM_POINTS):
        # Radius grows linearly with the point index
        radius = config.SPIRAL_RADIUS_INCREMENT * (i + 1) 
        theta = i * golden_angle  # Angle for the current point

        # Calculate Cartesian coordinates
        x = center.x + radius * cos(theta)
        y = center.y + radius * sin(theta)
        
        # Add point if within specified rectangular boundary
        if bottom_left.x <= x <= top_right.x and bottom_left.y <= y <= top_right.y:
            positions.append(Position(x, y))  # Create Position instance and add to list
    
    return positions
