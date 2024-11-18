import json
from typing import List, Dict
from math import cos, sin, sqrt
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import config
import os, math
import yaml
from datetime import datetime
from matplotlib.patches import Rectangle
from mission_plan import DroneMissionPlan
from fibonacci_spiral import FibonacciSpiral
from aerialist.px4.drone_test import DroneTest
import utils

class ObstacleGenerator:

    def __init__(self, mission_plan: DroneMissionPlan):        
        self.mission_plan = mission_plan

        # Trajectory segment between each pair of waypoints
        self.trajectory = self.mission_plan.get_trajectory_segments()
        print("Trajectory Segments:", self.trajectory)
        
        # Get longest segment of the trajectory that intersects with the generation area
        self.obst_segment = utils.get_obstacle_segment((config.GENERATION_AREA_MIN_POS, config.GENERATION_AREA_MAX_POS), self.trajectory)
        print("Best Segment:", self.obst_segment)

        # Center of the obstacle segment
        self.segment_center=None
        if self.obst_segment:
            start, end = self.obst_segment
            segment_center = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)

        # Generate Fibonacci spiral
        self.fibonacci_spiral = FibonacciSpiral(segment_center, config.GENERATION_AREA_MIN_POS, config.GENERATION_AREA_MAX_POS)
        print(len(self.fibonacci_spiral.points), "Fibonacci Spiral Points")
       
        # Filter spiral points based on distance from obstacles segment
        self.filtered_spiral = self.fibonacci_spiral.filter_spiral(self.obst_segment, config.THRESHOLD_DISTANCE)
        print(len(self.filtered_spiral), "Filtered Spiral Points")

        self.plot()

    def plot(self):
      
        spiral_x = []
        spiral_y = []

        for point in self.fibonacci_spiral.points:
            spiral_x.append(point[0])
            spiral_y.append(point[1])
       
        filtered_x = []
        filtered_y = []

        for point in self.filtered_spiral:
            filtered_x.append(point[0])
            filtered_y.append(point[1])

        segment_x = []
        segment_y = []

        for point in self.obst_segment:
            segment_x.append(point[0])
            segment_y.append(point[1])

        plt.figure(figsize=(10, 8))
        plt.scatter(spiral_x, spiral_y, color='blue', label='Fibonacci Spiral Points', s=10)
        plt.scatter(filtered_x, filtered_y, color='green', label='Filtered Spiral Points', s=20)
        plt.plot(segment_x, segment_y, color='red', label='Trajectory Segment', linewidth=2)

        plt.xlabel("X Position")
        plt.ylabel("Y Position")
        plt.title("Obstacle Generation Visualization")
        plt.legend()
        plt.grid(True)

        os.makedirs(config.DIR_GENERATED_PLOTS, exist_ok=True)

        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = f"{config.DIR_GENERATED_PLOTS}/obst_{current_datetime}.png"
        plt.savefig(file_path)
        print(f"Plot saved to {file_path}")

    def check_overlap(self, obstacles):
        overlap = False
        return overlap
    
    def check_area(self, obstacles):
        inside = False
        return inside

    def create_obstacles(self):
        return None
    
    def getParameters(self):

        parameters = {
            "mission": self.mission_plan.file_type,
            "segment": self.obst_segment,
            "fibonacci_param": [self.segment_center, config.NUM_SPIRAL_POINTS, config.SPIRAL_GOLDEN_ANGLE, config.SPIRAL_RADIUS_INCREMENT],
            "thresold_distance": config.THRESHOLD_DISTANCE,
        }

        return parameters
    
    def getCandidatePoints(self):
        return self.filtered_spiral

if __name__ == "__main__":
    print("--- Obstacle Generator ---")

    case_study_file = "case_studies/mission5.yaml"
    # Reading mission plan content
    with open(case_study_file, 'r') as file:
        yaml_content = yaml.safe_load(file)
    
    case_study = DroneTest.from_yaml(case_study_file)
    case_study_file = case_study_file

    mission_file = yaml_content.get("drone", {}).get("mission_file")
    mission_plan = DroneMissionPlan(mission_file)

    # Create obstacle Generator based on mission plan
    obstacle_generator = ObstacleGenerator(mission_plan)
