import json
import matplotlib.pyplot as plt
import utils
from scipy.interpolate import interp1d
import numpy as np

class DroneMissionPlan:
    def __init__(self, json_file):
        # Load JSON data from file
        json_data = {}
        with open(json_file, 'r') as file:
            json_data = json.load(file)

        # Load data from JSON
        self.file_type = json_data.get("fileType", "")
        self.geo_fence = json_data.get("geoFence", {})
        self.ground_station = json_data.get("groundStation", "")
        self.mission = json_data.get("mission", {})
        self.rally_points = json_data.get("rallyPoints", {})
        self.version = json_data.get("version", 0)
        
        # Extract specific mission information
        self.cruise_speed = self.mission.get("cruiseSpeed", 0)
        self.firmware_type = self.mission.get("firmwareType", 0)
        self.global_plan_altitude_mode = self.mission.get("globalPlanAltitudeMode", 0)
        self.hover_speed = self.mission.get("hoverSpeed", 0)
        self.items = self.mission.get("items", [])
        self.planned_home_position = self.mission.get("plannedHomePosition", [])
        self.vehicle_type = self.mission.get("vehicleType", 0)

    def get_mission_details(self):
        mission_details = {
            "File Type": self.file_type,
            "Ground Station": self.ground_station,
            "Cruise Speed": self.cruise_speed,
            "Hover Speed": self.hover_speed,
            "Firmware Type": self.firmware_type,
            "Vehicle Type": self.vehicle_type,
            "Planned Home Position": self.planned_home_position
        }
        return mission_details
    
    def get_mission_items3D(self):
        items_details = []
        for item in self.items:
            # Check that latitude and longitude are not None
            lat = item["params"][4]
            lon = item["params"][5]
            alt = item.get("Altitude")
            
            if lat is not None and lon is not None:
                item_details = {
                    "Latitude": lat,
                    "Longitude": lon,
                    "Altitude": alt,
                }
                items_details.append(item_details)
        return items_details
    
    def get_mission_items2D(self):
        cartesian_waypoints = []
        # Get the mission items in 3D
        waypoints = self.get_mission_items3D()
        origin_lat = waypoints[0]["Latitude"]
        origin_lon = waypoints[0]["Longitude"]

        for waypoint in waypoints:
            y, x = utils.latlon_to_cartesian(waypoint["Latitude"], waypoint["Longitude"], origin_lat, origin_lon)
            cartesian_waypoints.append({
                "x": x,
                "y": y,
            })

        return cartesian_waypoints

    def get_drone_speed(self):
        speed = self.cruise_speed
        return speed
       
    def get_trajectory(self, interval=0.10):
        mission_items = self.get_mission_items2D()        
        trajectory_segments = []
        
        for i in range(len(mission_items) - 1):
            start_point = mission_items[i]
            end_point = mission_items[i + 1]
            
            # Calculate Euclidean distance between the two points
            dist_x = end_point["x"] - start_point["x"]
            dist_y = end_point["y"] - start_point["y"]
            distance = np.sqrt(dist_x**2 + dist_y**2)
            
            # Calculate the number of intervals needed
            num_steps = int(distance // interval)
            
            # Interpolate points between start_point and end_point
            x_values = np.linspace(start_point["x"], end_point["x"], num_steps)
            y_values = np.linspace(start_point["y"], end_point["y"], num_steps)
            
            # Initialize a new list for the current segment
            segment_points = []
            
            for x, y in zip(x_values, y_values):
                segment_points.append(utils.Position(x, y))
            
            # Add the current segment to the main list of trajectory segments
            trajectory_segments.append(segment_points)
        
        return trajectory_segments


    def display_mission_summary(self):
        print("Mission Summary:")
        print(f"File Type: {self.file_type}")
        print(f"Ground Station: {self.ground_station}")
        print(f"Cruise Speed: {self.cruise_speed}")
        print(f"Hover Speed: {self.hover_speed}")
        print(f"Firmware Type: {self.firmware_type}")
        print(f"Vehicle Type: {self.vehicle_type}")
        print(f"Planned Home Position: {self.planned_home_position}")
        print("\nMission Items:")
        for item in self.get_mission_items3D():
            print(f"- Lat: {item['Latitude']}, Lon: {item['Longitude']}, Alt: {item['Altitude']}")


    def plot3D(self):
        # Extract lat/lon and altitude coordinates for each mission point, ignoring None values
        mission_items = self.get_mission_items3D()
        latitudes = [item["Latitude"] for item in mission_items]
        longitudes = [item["Longitude"] for item in mission_items]
        altitudes = [item["Altitude"] for item in mission_items]

        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.plot(longitudes, latitudes, linestyle='-', marker='o', color='blue')  # Line connecting the points
        
        # Add labels for each mission point
        for i, (lat, lon, alt) in enumerate(zip(latitudes, longitudes, altitudes)):
            plt.text(lon, lat, f"Alt: {alt}m" if alt is not None else "Alt: N/A", fontsize=9, ha='right')
        
        # Add labels and title
        plt.title("Drone Mission Plan")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.grid(True)
        plt.show()

    def plot2D(self):
        # Extract x and y coordinates for each mission point
        mission_items = self.get_mission_items2D()
        x_coords = [item["x"] for item in mission_items]
        y_coords = [item["y"] for item in mission_items]

        #Plot cartesian coordinates
        plt.figure(figsize=(8, 8))
        plt.plot(x_coords, y_coords, marker='o', linestyle='-', color='blue')
        plt.scatter(x_coords, y_coords, color='red', s=100, label="Waypoints")
        plt.xlabel("X (metri)")
        plt.ylabel("Y (metri)")
        plt.title("Waypoints in Coordinate Cartesiane")
        plt.legend()
        plt.grid(True)
        plt.axis("equal")
        plt.show()


if __name__ == "__main__":
    # Load the mission plan from a JSON file
    json_data = {}
    with open('case_studies/mission3.plan', 'r') as file:
        json_data = json.load(file)

    mission_plan = DroneMissionPlan(json_data)
    mission_plan.display_mission_summary()

    # Display the mission plan
    mission_plan.plot3D()
    mission_plan.plot2D()
