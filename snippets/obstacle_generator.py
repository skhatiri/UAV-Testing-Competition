import json
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
from aerialist.px4.drone_test import DroneTest
from shapely.geometry import Polygon
import utils

class ObstacleGenerator:

    def __init__(self, mission_plan: DroneMissionPlan, case_study_file: str):     
        self.mission_plan = mission_plan
        self.case_study_file = case_study_file

        # Trajectory segment between each pair of waypoints
        self.trajectory = self.mission_plan.get_trajectory_segments()
        print("Trajectory Segments:", self.trajectory)
        
        # Get longest segment of the trajectory that intersects with the generation area
        self.obst_segment = utils.get_obstacle_segment((config.GENERATION_AREA_MIN_POS, config.GENERATION_AREA_MAX_POS), self.trajectory)
        print("Best Segment:", self.obst_segment)

        # Center of the obstacle segment
        self.segment_center=(None, None)
        start, end = self.obst_segment
        self.segment_center = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)

        # Generate Fibonacci spiral
        self.fibonacci_spiral = FibonacciSpiral(self.segment_center, config.GENERATION_AREA_MIN_POS, config.GENERATION_AREA_MAX_POS)
        print(len(self.fibonacci_spiral.points), "Fibonacci Spiral Points")
       
        # Filter spiral points based on distance from obstacles segment
        self.filtered_spiral = self.fibonacci_spiral.filter_spiral(self.obst_segment, config.THRESHOLD_DISTANCE, config.GENERATION_AREA_MIN_POS, config.GENERATION_AREA_MAX_POS)
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
    
    def create_obstacles(self):
        return None
    
    def getParameters(self):

        parameters = {
            "mission": f"{self.case_study_file}",
            "segment": f"{self.obst_segment}",
            "fibonacci_param": f"{[self.segment_center, config.NUM_SPIRAL_POINTS, config.SPIRAL_GOLDEN_ANGLE, config.SPIRAL_RADIUS_INCREMENT]}",
            "thresold_distance": f"{config.THRESHOLD_DISTANCE}",
        }

        return parameters
    
    def getCandidatePoints(self):
        return self.filtered_spiral
    
    def get_obstacles_from_parameters(self, parameters):
        obstacles = [{
            "x": parameters[0],
            "y": parameters[1],
            "z": config.OBST_Z,
            "rotation": parameters[2],
            "length": config.OBST_LENGTH,
            "width": config.OBST_WIDTH,
            "height": config.OBSTACLE_HEIGHT,
        },
        {
            "x": parameters[3],
            "y": parameters[4],
            "z": config.OBST_Z,
            "rotation": parameters[5],
            "length": config.OBST_LENGTH,
            "width": config.OBST_WIDTH,
            "height": config.OBSTACLE_HEIGHT,
        }]

        return obstacles

    def generate(self, parameters):
        parameters = parameters
        history_mutant = []
        history_mutant.append(parameters)

        is_overlapped = False
        is_inside_area = False
        is_unique = True

        while sum([is_unique, is_overlapped, is_inside_area]) < 3:

            obstacles = self.get_obstacles_from_parameters(parameters)
            is_overlapped = self.check_overlap(obstacles)
            is_inside_area = self.check_inside_area(obstacles, config.GENERATION_AREA_MIN_POS, config.GENERATION_AREA_MAX_POS)

            if(sum([is_overlapped, is_inside_area]) < 2):
                parameters = self.mutate(parameters, history_mutant)

                is_unique = False
                is_overlapped = False
                is_inside_area = False
           
            if parameters not in history_mutant:
                is_unique = True
                history_mutant.append(parameters)

        return parameters

    def mutate(self, parameters, history_mutant):
        is_unique = False
        is_overlapped = False
        is_inside_area = False

        mutated_parameters = parameters.copy()

        while sum([is_unique, is_overlapped, is_inside_area]) < 3:
            is_unique = False
            is_overlapped = False
            is_inside_area = False

            #Choose a random parameter to mutate
            choice = np.random.uniform(0, 6)

            if choice < 1:  # Mutation on x1
                new_x1 = mutated_parameters[0] + np.random.choice([-config.ROUND_PARAMETER, config.ROUND_PARAMETER])
                mutated_parameters[0] = new_x1

            elif choice < 2:  # Mutation on x1               
                new_y1 = mutated_parameters[1] + np.random.choice([-config.ROUND_PARAMETER, config.ROUND_PARAMETER])
                mutated_parameters[1] = new_y1

            elif choice < 3:  # Mutation on x1
                new_r1 = np.random.choice(np.arange(0, 91, config.ANGLE_STEP))
                mutated_parameters[2] = new_r1

            elif choice < 4:  # Mutation on x1
                new_x2 = mutated_parameters[3] + np.random.choice([-config.ROUND_PARAMETER, config.ROUND_PARAMETER])
                mutated_parameters[3] = new_x2

            elif choice < 5:  # Mutation on x1
                new_y2 = mutated_parameters[4] + np.random.choice([-config.ROUND_PARAMETER, config.ROUND_PARAMETER])
                mutated_parameters[4] = new_y2

            else:  # Mutation on x1
                new_r2 = np.random.choice(np.arange(0, 91, config.ANGLE_STEP))
                mutated_parameters[5] = new_r2

            # Check if mutated parameters are unique
            if mutated_parameters not in history_mutant:
                is_unique = True
            
            obstacles = self.get_obstacles_from_parameters(mutated_parameters)
            is_overlapped = self.check_overlap(obstacles)
            is_inside_area = self.check_inside_area(obstacles, config.GENERATION_AREA_MIN_POS, config.GENERATION_AREA_MAX_POS)

        return mutated_parameters

    def check_inside_area(self, obstacles, generation_area_min_pos, generation_area_max_pos):
        
        all_inside = True

        length = config.OBST_LENGTH
        width = config.OBST_WIDTH
        half_length = length / 2
        half_width = width / 2

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
            for corner in corners:
                x_rot = center_x + corner[0] * math.cos(rad) - corner[1] * math.sin(rad)
                y_rot = center_y + corner[0] * math.sin(rad) + corner[1] * math.cos(rad)
                rotated_corners.append((x_rot, y_rot))

            for vertex in rotated_corners:
                if not (generation_area_min_pos[0] <= vertex[0] <= generation_area_max_pos[0] and
                        generation_area_min_pos[1] <= vertex[1] <= generation_area_max_pos[1]):
                    is_inside = is_inside and False
        
            all_inside = all_inside and is_inside
    
        return all_inside 

    def check_overlap(self, obstacles):
        def get_polygon(obstacle):
            cx, cy = obstacle["x"], obstacle["y"]
            l, w = obstacle["length"] / 2, obstacle["width"] / 2
            angle = obstacle["rotation"]

            # Calcola i vertici non ruotati (rettangolo centrato su cx, cy)
            corners = [
                (cx - l, cy - w),  # Bottom-left
                (cx + l, cy - w),  # Bottom-right
                (cx + l, cy + w),  # Top-right
                (cx - l, cy + w),  # Top-left
            ]

            # Ruota i vertici attorno al centro
            rad = math.radians(angle)
            rotated_corners = [
                (
                    math.cos(rad) * (x - cx) - math.sin(rad) * (y - cy) + cx,
                    math.sin(rad) * (x - cx) + math.cos(rad) * (y - cy) + cy
                )
                for x, y in corners
            ]

            # Crea un poligono Shapely dai vertici
            return Polygon(rotated_corners)

        # Create polygons from obstacles
        poly1 = get_polygon(obstacles[0])
        poly2 = get_polygon(obstacles[1])
        
        # Check if polygons intersect
        if poly1.intersects(poly2):
            return False # Overlapping
        else:
            return True # Not Overlapping
        
        
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
