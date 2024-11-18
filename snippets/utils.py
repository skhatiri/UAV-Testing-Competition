from math import *
from typing import List, Dict


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

def segment_length(x1, y1, x2, y2):
    """Calcola la lunghezza del segmento."""
    return sqrt((x2 - x1)**2 + (y2 - y1)**2)

def clip_segment_to_rectangle(rect, segment):
    """
    Taglia un segmento ai bordi del rettangolo (se interseca).
    rect: (x_min, y_min, x_max, y_max)
    segment: ((x1, y1), (x2, y2))
    Ritorna il segmento tagliato o None se non interseca.
    """
    from shapely.geometry import LineString, box

    rect_box = box(rect[0][0], rect[0][1], rect[1][0], rect[1][1])
    seg_line = LineString([segment[0], segment[1]])
    intersection = rect_box.intersection(seg_line)

    if intersection.is_empty:
        return None
    elif intersection.geom_type == 'LineString':
        x1, y1 = intersection.coords[0]
        x2, y2 = intersection.coords[1]
        return (x1, y1), (x2, y2)
    return None

def get_obstacle_segment(rect, segments):
    """
    Trova il segmento più lungo (dopo l'intersezione con il rettangolo).
    rect: (x_min, y_min, x_max, y_max)
    segments: [((x1, y1), (x2, y2)), ...]
    Ritorna il segmento più lungo e la sua lunghezza.
    """
    max_length = 0
    longest_segment = None

    for segment in segments:
        clipped = clip_segment_to_rectangle(rect, segment)
        if clipped:
            length = segment_length(clipped[0][0], clipped[0][1], clipped[1][0], clipped[1][1])
            if length > max_length:
                max_length = length
                longest_segment = clipped

    return longest_segment

def distance_point_segment(point, segment):
    x1, y1 = point
    x2, y2 = segment[0]
    x3, y3 = segment[1]
    
    # Calcolo dei coefficienti della retta ax + by + c = 0
    a = y3 - y2
    b = x2 - x3
    c = x3 * y2 - x2 * y3
    
    # Calcolo della distanza usando la formula
    n = abs(a * x1 + b * y1 + c)
    d = sqrt(a**2 + b**2)
    
    return n / d