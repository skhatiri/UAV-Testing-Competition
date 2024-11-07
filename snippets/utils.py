from math import cos, radians

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
