from math import cos, sin, sqrt, radians
from typing import List, Dict


class Position:
    def __init__(self, x: float, y: float, z: float = 0, angle: int = 0) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.angle = angle

# Function to convert lat/lon to Cartesian coordinates relative to the origin
def latlon_to_cartesian(lat, lon, origin_lat, origin_lon):
    # Conversion factors
    lat_to_meters = 111000  # 1 degree of latitude ≈ 111 km
    lon_to_meters = 111000 * cos(radians(origin_lat))  # Longitude conversion to meters

    # Delta relative to the origin
    delta_lat = lat - origin_lat
    delta_lon = lon - origin_lon

    # Cartesian coordinates in meters
    x = delta_lon * lon_to_meters
    y = delta_lat * lat_to_meters

    return x, y

def fibonacci_spiral(n: int, center, bottom_left: Position, top_right: Position) -> List[Position]:        
    golden_angle = 0.8
    positions = []
    
    for i in range(n):
        radius = 0.2 * (i + 1)
        theta = i * golden_angle
        
        # Calcola le coordinate del punto
        x = center.x + radius * cos(theta)
        y = center.y + radius * sin(theta)
        
        if bottom_left.x <= x <= top_right.x and bottom_left.y <= y <= top_right.y:
            positions.append(Position(x, y))
    
    return positions