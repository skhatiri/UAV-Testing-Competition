import json
import matplotlib.pyplot as plt

class DroneMissionPlan:
    def __init__(self, json_data):
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
    
    def get_mission_items(self):
        items_details = []
        for item in self.items:
            # Check that latitude and longitude are not None
            lat = item["params"][4]
            lon = item["params"][5]
            alt = item.get("Altitude")
            
            if lat is not None and lon is not None:
                item_details = {
                    "Command": item.get("command"),
                    "Latitude": lat,
                    "Longitude": lon,
                    "Altitude": alt,
                    "Altitude Mode": item.get("AltitudeMode"),
                }
                items_details.append(item_details)
        return items_details

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
        for item in self.get_mission_items():
            print(f"- Command: {item['Command']}, Lat: {item['Latitude']}, Lon: {item['Longitude']}, Alt: {item['Altitude']}")


    def plot(self):
        # Extract lat/lon and altitude coordinates for each mission point, ignoring None values
        mission_items = self.get_mission_items()
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

if __name__ == "__main__":
    # Load the mission plan from a JSON file
    json_data = {}
    with open('case_studies/mission2.plan', 'r') as file:
        json_data = json.load(file)

    mission_plan = DroneMissionPlan(json_data)
    mission_plan.display_mission_summary()

    # Display the mission plan
    mission_plan.plot()
