from typing import List, Dict
from math import cos, sin, sqrt
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import config
import numpy as np
import os, math
import yaml
from datetime import datetime
from matplotlib.patches import Rectangle
from mission_plan import DroneMissionPlan
from fibonacci_spiral import FibonacciSpiral
from aerialist.px4.drone_test import DroneTest # type: ignore
from shapely.geometry import Polygon
import utils
import random


class ObstacleGenerator:

    def __init__(self, mission_plan: DroneMissionPlan, case_study_file: str):
        """
        Initializes the class with the given mission plan
        
        Parameters:
        mission_plan (DroneMissionPlan): The mission plan containing waypoint and trajectory information.
        case_study_file (str): The file path to the case study data.
        
        Returns:
        None
        """     
        
        self.mission_plan = mission_plan
        self.case_study_file = case_study_file

        # Trajectory segment between each pair of waypoints
        self.trajectory = self.mission_plan.get_trajectory_segments()
        print("Trajectory Segments: ", self.trajectory)
        
        # Get longest segment of the trajectory that intersects with the generation area
        self.obst_segment = utils.get_obstacle_segment((config.GENERATION_AREA_MIN_POS, config.GENERATION_AREA_MAX_POS), self.trajectory)
        print("Best Segment: ", self.obst_segment)

        # Center of the obstacle segment
        self.segment_center = (None, None)
        start, end = self.obst_segment
        self.segment_center = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)

        # Generate Fibonacci spiral
        self.fibonacci_spiral = FibonacciSpiral(self.segment_center, config.GENERATION_AREA_MIN_POS, config.GENERATION_AREA_MAX_POS)
        print("Fibonacci Spiral Points: ", len(self.fibonacci_spiral.points)) 
       
        # Filter spiral points based on distance from obstacles segment
        self.filtered_spiral = self.fibonacci_spiral.filter_spiral(self.obst_segment, config.THRESHOLD_DISTANCE, config.GENERATION_AREA_MIN_POS, config.GENERATION_AREA_MAX_POS)
        print("Filtered Spiral Points: ",len(self.filtered_spiral))
        
        self.plot()

    def plot(self):
        """
        Visualizes the Fibonacci spiral and filtered points, and also the trajectory segment on a 2D plot.

        Parameters:
        None

        Returns:
        None
        """
        
        # Fibonacci Spiral Points
        spiral_x = []
        spiral_y = []

        for point in self.fibonacci_spiral.points:
            spiral_x.append(point[0])
            spiral_y.append(point[1])
       
        # Filtered Spiral Points
        filtered_x = []
        filtered_y = []

        for point in self.filtered_spiral:
            filtered_x.append(point[0])
            filtered_y.append(point[1])

        # Trajectory Segment
        segment_x = []
        segment_y = []

        for point in self.obst_segment:
            segment_x.append(point[0])
            segment_y.append(point[1])

        # Plot
        plt.figure(figsize=(10, 8))
        plt.scatter(spiral_x, spiral_y, color='blue', label='Fibonacci Spiral Points', s=10)
        plt.scatter(filtered_x, filtered_y, color='green', label='Filtered Spiral Points', s=20)
        plt.plot(segment_x, segment_y, color='red', label='Trajectory Segment', linewidth=2)

        plt.xlabel("X Position")
        plt.ylabel("Y Position")
        plt.title("Obstacle Generation Visualization")
        plt.legend()
        plt.grid(True)

        # Save plot to file
        os.makedirs(config.DIR_GENERATED_PLOTS, exist_ok=True)
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = f"{config.DIR_GENERATED_PLOTS}obst_{current_datetime}.png"
        plt.savefig(file_path)
        print(f"Plot saved to: {file_path}")
    
    def getParameters(self):
        """
        Collects and returns the key parameters of simulation

        Parameters:
        None

        Returns:
        dict:
            - "mission": The case study file associated with the mission.
            - "segment": The best obstacle segment (trajectory segment intersecting the generation area).
            - "fibonacci_param": A list containing:
                - Center of the obstacle segment.
                - Number of points in the Fibonacci spiral.
                - Golden angle used in spiral generation.
                - Radius increment for the spiral.
            - "threshold_distance": The distance threshold for filtering spiral points.
        """
        
        # Parameters for the simulation
        parameters = {
            "mission": self.case_study_file,
            "segment": [self.obst_segment],
            "center": self.segment_center,
            "num_spiral_points": config.NUM_SPIRAL_POINTS,
            "golden_angle": config.SPIRAL_GOLDEN_ANGLE,
            "radius_increment": config.SPIRAL_RADIUS_INCREMENT,
            "thresold_distance": config.THRESHOLD_DISTANCE,
        }

        return parameters
    
    def get_obstacles_from_parameters(self, parameters):
        """
        Generates a list of obstacle dictionaries using the provided parameters.

        Parameters:
        parameters (list): A list containing the following parameters:
            - parameters[0]: X-coordinate of the first obstacle.
            - parameters[1]: Y-coordinate of the first obstacle.
            - parameters[2]: Rotation angle of the first obstacle.
            - parameters[3]: X-coordinate of the second obstacle.
            - parameters[4]: Y-coordinate of the second obstacle.
            - parameters[5]: Rotation angle of the second obstacle.

        Returns:
        list (obstacles): 
            - "x": X-coordinate of the obstacle center.
            - "y": Y-coordinate of the obstacle center .
            - "z": Z-coordinate (height) of the obstacle, determined by `config.OBST_Z`.
            - "rotation": Rotation angle of the obstacle.
            - "length": Length of the obstacle, determined by `config.OBST_LENGTH`.
            - "width": Width of the obstacle, determined by `config.OBST_WIDTH`.
            - "height": Height of the obstacle, determined by `config.OBSTACLE_HEIGHT`.
        """
        
        obstacles = [{
            "x": float(parameters[0]),
            "y": float(parameters[1]),
            "z": float(config.OBST_Z),
            "rotation": float(parameters[2]),
            "length": float(config.OBST_LENGTH),
            "width": float(config.OBST_WIDTH),
            "height": float(config.OBSTACLE_HEIGHT),
        },
        {
            "x": float(parameters[3]),
            "y": float(parameters[4]),
            "z": float(config.OBST_Z),
            "rotation": float(parameters[5]),
            "length": float(config.OBST_LENGTH),
            "width": float(config.OBST_WIDTH),
            "height": float(config.OBSTACLE_HEIGHT),
        }]

        return obstacles
    
    def check_inside_area(self, obstacles, generation_area_min_pos, generation_area_max_pos):
        """
        Checks if all obstacles are entirely within the specified generation area.

        Parameters:
        obstacles (list):
            - "x": X-coordinate of the obstacle center.
            - "y": Y-coordinate of the obstacle center.
            - "rotation": Rotation angle of the obstacle in degrees.
        generation_area_min_pos (tuple): Minimum (x, y) coordinates of the generation area.
        generation_area_max_pos (tuple): Maximum (x, y) coordinates of the generation area.

        Returns:
        bool: True if all obstacles are fully inside the generation area; False otherwise.
        """
        
        all_inside = True

        # Obstacle dimensions
        length = config.OBST_LENGTH
        width = config.OBST_WIDTH
        half_length = length / 2
        half_width = width / 2

        # Corners of the obstacle
        corners = [
            (half_length, half_width),
            (-half_length, half_width),
            (-half_length, -half_width),
            (half_length, -half_width)
        ]

        # Iterate over each obstacle
        for obst in obstacles:
            is_inside = True

            center_x = obst["x"]
            center_y = obst["y"]
            rotation = obst["rotation"]

            rad = math.radians(rotation)

            rotated_corners = []
            # Rotate each corner of the obstacle
            for corner in corners:
                x_rot = center_x + corner[0] * math.cos(rad) - corner[1] * math.sin(rad)
                y_rot = center_y + corner[0] * math.sin(rad) + corner[1] * math.cos(rad)
                rotated_corners.append((x_rot, y_rot))

            # Check if all corners are inside the generation area
            for vertex in rotated_corners:
                if not (generation_area_min_pos[0] <= vertex[0] <= generation_area_max_pos[0] and
                        generation_area_min_pos[1] <= vertex[1] <= generation_area_max_pos[1]):
                    is_inside = is_inside and False
            
            # Update overall result
            all_inside = all_inside and is_inside
    
        return all_inside 

    def check_overlap(self, obstacles):
        """
        Checks whether two obstacles overlap in their placement.

        Parameters:
        obstacles (list):
            - "x": X-coordinate of the obstacle center.
            - "y": Y-coordinate of the obstacle center.
            - "length": Length of the obstacle.
            - "width": Width of the obstacle.
            - "rotation": Rotation angle of the obstacle in degrees.

        Returns:
        bool: 
            - False if the two obstacles overlap.
            - True if the two obstacles do not overlap.
        """
        def get_polygon(obstacle):
            """
            Creates a Shapely polygon for an obstacle based on its dimensions, position, and rotation.

            Parameters:
            obstacle (dict): A dictionary with keys "x", "y", "length", "width", and "rotation".

            Returns:
            Polygon: A Shapely Polygon object representing the obstacle.
            """
            
            # Get obstacle parameters
            cx, cy = obstacle["x"], obstacle["y"]
            l, w = obstacle["length"] / 2, obstacle["width"] / 2
            angle = obstacle["rotation"]

            # Calculate the corners of the rectangle
            corners = [
                (cx - l, cy - w),  # Bottom-left
                (cx + l, cy - w),  # Bottom-right
                (cx + l, cy + w),  # Top-right
                (cx - l, cy + w),  # Top-left
            ]
            
            # Rotate the corners based on the angle
            rad = math.radians(angle)
            rotated_corners = [
                (
                    math.cos(rad) * (x - cx) - math.sin(rad) * (y - cy) + cx,
                    math.sin(rad) * (x - cx) + math.cos(rad) * (y - cy) + cy
                )
                for x, y in corners
            ]

            # Create a polygon from the rotated corners
            return Polygon(rotated_corners)

        # Create polygons from obstacles
        poly1 = get_polygon(obstacles[0])
        poly2 = get_polygon(obstacles[1])
        
        # Check if polygons intersect
        if poly1.intersects(poly2):
            return False # Overlapping
        else:
            return True # Not Overlapping
        
    def is_valid(self, obstacles):
        """
        Validates whether the given obstacles satisfy the following conditions:
        1. The obstacles do not overlap.
        2. The obstacles are entirely within the specified generation area.

        Parameters:
        obstacles (list): A list of obstacle dictionaries.

        Returns:
        bool: True if the obstacles are valid (no overlap and within bounds); False otherwise.
        """
        # Check both conditions
        return self.check_overlap(obstacles) and self.check_inside_area(
            obstacles, config.GENERATION_AREA_MIN_POS, 
            config.GENERATION_AREA_MAX_POS
        )
    
    def recalculate_filter_spiral(self, threshold):
        """
        Recalculates the filtered Fibonacci spiral points based on a new distance threshold.

        Parameters:
        threshold (float): The new threshold distance to filter spiral points 

        Returns:
        None
        """
        
        # New filtered spiral
        self.filtered_spiral = self.fibonacci_spiral.filter_spiral(
            self.obst_segment, 
            threshold, 
            config.GENERATION_AREA_MIN_POS, 
            config.GENERATION_AREA_MAX_POS
        )
        
if __name__ == "__main__":
    
    # Testing 
    print("--- Obstacle Generator ---")

    case_study_file = "case_studies/mission5.yaml"
    with open(case_study_file, 'r') as file:
        yaml_content = yaml.safe_load(file)
    
    case_study = DroneTest.from_yaml(case_study_file)
    case_study_file = case_study_file

    mission_file = yaml_content.get("drone", {}).get("mission_file")
    mission_plan = DroneMissionPlan(mission_file)

    obstacle_generator = ObstacleGenerator(mission_plan)
