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
from utils import Position,fibonacci_spiral, calculate_inclination, is_left_of_trajectory


class ObstacleGenerator:
   
    def distance(self, pos1: Position, pos2: Position) -> float:
        return sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2)

    def filter_spiral(self, spiral_points: List[Position], traj_segment: List[Position], threshold_distance: float) -> List[Position]:
        filtered_points = []
        for traj_point in traj_segment:
            for point in spiral_points:
                if self.distance(point, traj_point) <= threshold_distance:
                    filtered_points.append(point)
                    
        filtered_points = list(set(filtered_points))
    
        return filtered_points

    def plot(self, spiral_points: List[Position], filtered_points: List[Position], trajectory: List[Position], center: Position, obstacles: List[Dict]) -> None:
        spiral_x = [pos.x for pos in spiral_points]
        spiral_y = [pos.y for pos in spiral_points]
        filtered_x = [pos.x for pos in filtered_points]
        filtered_y = [pos.y for pos in filtered_points]
        trajectory_x = [pos.x for pos in trajectory]
        trajectory_y = [pos.y for pos in trajectory]

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.plot(spiral_x, spiral_y, label="Fibonacci Spiral", marker='o', linestyle='-', color="blue")
        ax.scatter(filtered_x, filtered_y, color="red", s=100, marker="x", label="Filtered Points")
        ax.plot(trajectory_x, trajectory_y, label="Mission Trajectory", color="purple", linestyle="--")
        ax.scatter(center.x, center.y, color="green", s=100, marker="x", label="Spiral Center (Centroid)")

        # Draw rotated polygons for obstacles
        for obs in obstacles:
            # Calculate the four corners of the rotated rectangle
            cx, cy = obs["x"], obs["y"]
            half_length = obs["length"] / 2
            half_width = obs["width"] / 2
            angle_rad = math.radians(obs["rotation"])
            
            corners = [
                (cx + half_length * math.cos(angle_rad) - half_width * math.sin(angle_rad),
                cy + half_length * math.sin(angle_rad) + half_width * math.cos(angle_rad)),
                (cx - half_length * math.cos(angle_rad) - half_width * math.sin(angle_rad),
                cy - half_length * math.sin(angle_rad) + half_width * math.cos(angle_rad)),
                (cx - half_length * math.cos(angle_rad) + half_width * math.sin(angle_rad),
                cy - half_length * math.sin(angle_rad) - half_width * math.cos(angle_rad)),
                (cx + half_length * math.cos(angle_rad) + half_width * math.sin(angle_rad),
                cy + half_length * math.sin(angle_rad) - half_width * math.cos(angle_rad))
            ]
            
            # Create a Polygon patch with the rotated corners
            polygon = Polygon(corners, closed=True, color="black", alpha=0.5, label="Obstacle" if obstacles.index(obs) == 0 else "")
            ax.add_patch(polygon)
        
        plt.xlabel("X Position")
        plt.ylabel("Y Position")
        plt.legend()
        plt.grid(True)
        os.makedirs(config.DIR_GENERATED_PLOTS, exist_ok=True)
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        plt.savefig(f"{config.DIR_GENERATED_PLOTS}obst_{current_datetime}.png")

    def generate_obstacles(self, segment: List[Position], filtered_points: List[Position], drone_dimension: float) -> List[Dict]:

        num_obstacles = config.NUM_OBSTACLES 
        obstacles = []

        # Calculate inclination of the segment
        is_left_first, angle = calculate_inclination(segment[0], segment[-1])

        print("Inclination: ", angle)

        # Divide filtered points into left and right
        left_points = [p for p in filtered_points if is_left_of_trajectory(segment, p)]
        right_points = [p for p in filtered_points if not is_left_of_trajectory(segment, p)]

        if not left_points or not right_points:
            return []  # No valid points

        entry_point = None
        
        # Select the entry point based on the inclination
        if(is_left_first):
            entry_point = left_points[len(left_points) // config.OBST_POS_FACTOR] 
        else:
            entry_point = right_points[len(right_points) // config.OBST_POS_FACTOR]
        
        ##
        ## GATE COORDINATES
        ##
        
        gate_min_position = Position(entry_point.x-((drone_dimension/2)*config.DRONE_FACTOR), entry_point.y) 
        gate_max_position = Position(entry_point.x+((drone_dimension/2)*config.DRONE_FACTOR), entry_point.y)

        print("Gate Min Position:", gate_min_position.x, gate_min_position.y)
        print("Gate Max Position:", gate_max_position.x, gate_max_position.y)

        max_legth_left = 0
        max_width_left = 0

        max_legth_right = 0
        max_width_right = 0
        
        ##
        ## POSITIONING
        ##
        if is_left_first:
            
            ##
            ## LEFT OBSTACLE
            ##
            
            max_legth_left = self.distance(Position(config.GENERATION_AREA_MIN_POS.x, gate_min_position.y), gate_min_position)/2
            max_width_left = self.distance(Position(gate_min_position.x, config.GENERATION_AREA_MIN_POS.y), gate_min_position)/2

            if(max_legth_left > (config.OBST_MAX_LENGTH / 2)):
                max_legth_left = config.OBST_MAX_LENGTH / 2

            if(max_legth_left < (config.OBST_MIN_LENGTH / 2)):
                max_legth_left = config.OBST_MIN_LENGTH / 2

            if(max_width_left > (config.OBST_MAX_WIDTH / 2)):
                max_width_left = config.OBST_MAX_WIDTH / 2

            if(max_width_left < (config.OBST_MIN_WIDTH / 2)):
                max_width_left = config.OBST_MIN_WIDTH / 2
            
            ##
            ## RIGHT OBSTACLE
            ##

            max_legth_right = self.distance(Position(config.GENERATION_AREA_MAX_POS.x, gate_max_position.y), gate_max_position)/2
            max_width_right = self.distance(Position(gate_max_position.x, config.GENERATION_AREA_MAX_POS.y), gate_max_position)/2

            if(max_legth_right > (config.OBST_MAX_LENGTH / 2)):
                max_legth_right = config.OBST_MAX_LENGTH / 2

            if(max_width_right > (config.OBST_MAX_WIDTH / 2)):
                max_width_right = config.OBST_MAX_WIDTH / 2

            # `gate_min_position` is the top-right corner of the left block
            left_obstacle_x = gate_min_position.x - max_legth_left
            left_obstacle_y = gate_min_position.y - max_width_left

            # `gate_max_position` is the bottom-left corner of the right block
            right_obstacle_x = gate_max_position.x + max_legth_right
            right_obstacle_y = gate_max_position.y + max_width_right

            obstacles = [
                {
                    "x": left_obstacle_x,
                    "y": left_obstacle_y,
                    "z": 0,
                    "length": max_legth_left*2,
                    "width": max_width_left*2,
                    "rotation": config.OBST_ROTATION
                },
                {
                    "x": right_obstacle_x,
                    "y": right_obstacle_y,
                    "z": 0,
                    "length": max_legth_right*2,
                    "width": max_width_right*2,
                    "rotation": config.OBST_ROTATION
                }
            ]
        else:

            ##
            ## LEFT OBSTACLE
            ##
            
            max_legth_left = self.distance(Position(config.GENERATION_AREA_MIN_POS.x, gate_min_position.y), gate_min_position)/2
            max_width_left = self.distance(Position(gate_min_position.x, config.GENERATION_AREA_MAX_POS.y), gate_min_position)/2

            if(max_legth_left > (config.OBST_MAX_LENGTH / 2)):
                max_legth_left = config.OBST_MAX_LENGTH / 2

            if(max_legth_left < (config.OBST_MIN_LENGTH / 2)):
                max_legth_left = config.OBST_MIN_LENGTH / 2

            if(max_width_left > (config.OBST_MAX_WIDTH / 2)):
                max_width_left = config.OBST_MAX_WIDTH / 2

            if(max_width_left < (config.OBST_MIN_WIDTH / 2)):
                max_width_left = config.OBST_MIN_WIDTH / 2
            
            ##
            ## RIGHT OBSTACLE
            ##

            max_legth_right = self.distance(Position(config.GENERATION_AREA_MAX_POS.x, gate_max_position.y), gate_max_position)/2
            max_width_right = self.distance(Position(gate_max_position.x, config.GENERATION_AREA_MIN_POS.y), gate_max_position)/2

            if(max_legth_right > (config.OBST_MAX_LENGTH / 2)):
                max_legth_right = config.OBST_MAX_LENGTH / 2

            if(max_width_right > (config.OBST_MAX_WIDTH / 2)):
                max_width_right = config.OBST_MAX_WIDTH / 2

            # `gate_min_position` is the bottom-left corner of the left block
            left_obstacle_x = gate_min_position.x - max_legth_left
            left_obstacle_y = gate_min_position.y + max_width_left

            # `gate_max_position` is the top-right corner of the right block
            right_obstacle_x = gate_max_position.x + max_legth_right
            right_obstacle_y = gate_max_position.y - max_width_right

            obstacles = [
                {
                    "x": left_obstacle_x,
                    "y": left_obstacle_y,
                    "z": 0,
                    "length": max_legth_left*2,
                    "width": max_width_left*2,
                    "rotation": config.OBST_ROTATION
                },
                {
                    "x": right_obstacle_x,
                    "y": right_obstacle_y,
                    "z": 0,
                    "length": max_legth_right*2,
                    "width": max_width_left*2,
                    "rotation": config.OBST_ROTATION
                }
            ]

        return obstacles, [gate_min_position, gate_max_position]

    def get_obstacle_segment(self, trajectory, min_pos, max_pos) -> List[Position]:
        max_points_in_area = 0
        best_segment = None

        for segment in trajectory:
            
            in_area_points = [
                point for point in segment 
                if (min_pos.x <= point.x <= max_pos.x) and (min_pos.y <= point.y <= max_pos.y)
            ]
            
            # Update if the current segment has the most points within the area
            if len(in_area_points) > max_points_in_area:
                max_points_in_area = len(in_area_points)
                best_segment = in_area_points  # Store only the filtered points

        return best_segment

    def generate(self, case_study_file: str):
       
        # Extract plan file details
        with open(case_study_file, 'r') as file:
            yaml_content = yaml.safe_load(file)
        
        mission_file = yaml_content.get("drone", {}).get("mission_file")

        # Extract mission waypoints
        mission_plan = DroneMissionPlan(mission_file)
        waypoints2D = mission_plan.get_mission_items2D()

        # Calculate the centroid of the mission waypoints
        avg_x = sum(point['x'] for point in waypoints2D) / len(waypoints2D)
        avg_y = sum(point['y'] for point in waypoints2D) / len(waypoints2D)
        spiral_center = Position(avg_x, avg_y)

        # Generate Fibonacci spiral points
        spiral_points = fibonacci_spiral(config.NUM_SPIRAL_POINTS, spiral_center, config.GENERATION_AREA_MIN_POS, config.GENERATION_AREA_MAX_POS)

        # Trajectory segment between each pair of waypoints
        trajectory = mission_plan.get_trajectory()
        
        # Get the segment with the most points within the generation area
        obst_segment = self.get_obstacle_segment(trajectory, config.GENERATION_AREA_MIN_POS, config.GENERATION_AREA_MAX_POS)
        
        # Filter spiral points based on distance from obstacles segment
        filtered_points = self.filter_spiral(spiral_points, obst_segment, config.THRESHOLD_DISTANCE)
        
        # Generate obstacles
        obstacles, gate = self.generate_obstacles(obst_segment, filtered_points, config.DRONE_DIMENSIONS)
        
        parameters = {
            "obstacles": obstacles,
            "gate_pos1": gate[0],
            "gate_pos2": gate[1],
            "center_factor": config.OBST_POS_FACTOR,
            "obst_segment": obst_segment,
            "waypoints": waypoints2D,
            "drone_dimension": config.DRONE_DIMENSIONS,
            "drone_factor": config.DRONE_FACTOR,
            "mission": mission_file,
        }

        #Plot everything
        self.plot(spiral_points, filtered_points, obst_segment, spiral_center, obstacles)
        
        print("Generated Obstacles:", json.dumps(obstacles, indent=4))

        return obstacles, parameters

if __name__ == "__main__":
    print("--- Obstacle Generator ---")
    generator = ObstacleGenerator()
    obstacles = generator.generate("case_studies/mission5.yaml")
