import random
from typing import List, Dict
from math import cos, sin, sqrt
import matplotlib.pyplot as plt
import config
import os
import yaml
from datetime import datetime
from matplotlib.patches import Rectangle
from mission_plan import DroneMissionPlan
from utils import Position,fibonacci_spiral


class ObstacleGenerator:
   
    def distance(self, pos1: Position, pos2: Position) -> float:
        return sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2)

    def filter_spiral(self, spiral_points: List[Position], trajectory: List[Position], threshold_distance: float) -> List[Position]:
        return [
            point for point in spiral_points 
            if any(self.distance(point, traj_point) <= threshold_distance for traj_point in trajectory)
        ]

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

        # Draw rectangles for obstacles
        for obs in obstacles:
            rect = Rectangle(
                (obs['x'] - obs['length'] / 2, obs['y'] - obs['width'] / 2),  # Bottom-left corner
                obs['length'],
                obs['width'],
                color="black",
                alpha=0.5,
                label="Obstacle" if obstacles.index(obs) == 0 else ""
            )
            ax.add_patch(rect)
        
        
        plt.xlabel("X Position")
        plt.ylabel("Y Position")
        plt.legend()
        plt.grid(True)
        os.makedirs(config.DIR_GENERATED_PLOTS, exist_ok=True)
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")        
        plt.savefig(f"{config.DIR_GENERATED_PLOTS}obst_{current_datetime}.png")

    def check_overlap(self, new_obstacle: Dict, obstacles: List[Dict]) -> bool:
        for obs in obstacles:
            # Calculate AABB corners of the existing and new obstacles
            x1_min = obs['x'] - obs['length'] / 2
            x1_max = obs['x'] + obs['length'] / 2
            y1_min = obs['y'] - obs['width'] / 2
            y1_max = obs['y'] + obs['width'] / 2

            x2_min = new_obstacle['x'] - new_obstacle['length'] / 2
            x2_max = new_obstacle['x'] + new_obstacle['length'] / 2
            y2_min = new_obstacle['y'] - new_obstacle['width'] / 2
            y2_max = new_obstacle['y'] + new_obstacle['width'] / 2

            # Check for overlap (no gap in both x and y directions)
            if x1_max > x2_min and x1_min < x2_max and y1_max > y2_min and y1_min < y2_max:
                return True
        return False

    def generate_obstacles(self, filtered_points: List[Position]) -> List[Dict]:
        num_obstacles = 2
        obstacles = []
        
        for obstacle_index in range(num_obstacles):
            while True:
                if obstacle_index == 0:
                    # First obstacle can be any point from filtered_points
                    center_point = random.choice(filtered_points)
                    filtered_points.remove(center_point)
                else:
                    # For the second obstacle, find a point close to the first obstacle
                    first_obstacle = obstacles[0]
                    # Find points close to the first obstacle (within a reasonable distance, e.g., < THRESHOLD_DISTANCE)
                    nearby_points = [
                        point for point in filtered_points 
                        if self.distance(Position(first_obstacle['x'], first_obstacle['y']), point) <= config.THRESHOLD_DISTANCE
                    ]
                    
                    if not nearby_points:
                        print("No nearby points found for the second obstacle.")
                        break
                    
                    center_point = random.choice(nearby_points)
                    filtered_points.remove(center_point)

                length = random.uniform(config.OBST_MIN_LENGTH, config.OBST_MAX_LENGTH)
                width = random.uniform(config.OBST_MIN_WIDTH, config.OBST_MAX_WIDTH)
                
                new_obstacle = {
                    "x": center_point.x,
                    "y": center_point.y,
                    "z": 0,
                    "length": length,
                    "width": width,
                    "height": random.uniform(config.OBST_MIN_HEIGHT, config.OBST_MAX_HEIGHT),
                    "rotation": 0  # No rotation for simplicity
                }
                
                x_min = new_obstacle["x"] - (new_obstacle["length"] / 2)
                x_max = new_obstacle["x"] + (new_obstacle["length"] / 2)
                y_min = new_obstacle["y"] - (new_obstacle["width"] / 2)
                y_max = new_obstacle["y"] + (new_obstacle["width"] / 2)
                
                if not (config.GENERATION_AREA_MIN_POS.x <= x_min <= config.GENERATION_AREA_MAX_POS.x and config.GENERATION_AREA_MIN_POS.x <= x_max <= config.GENERATION_AREA_MAX_POS.x and
                        config.GENERATION_AREA_MIN_POS.y <= y_min <= config.GENERATION_AREA_MAX_POS.y and config.GENERATION_AREA_MIN_POS.y <= y_max <= config.GENERATION_AREA_MAX_POS.y):
                    continue  # Skip if out of bounds
                
                if not self.check_overlap(new_obstacle, obstacles):
                    obstacles.append(new_obstacle)
                    break  # Exit the loop if obstacle placed successfully
        
        return obstacles

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

        # Convert mission waypoints to Position objects
        trajectory = [Position(point['x'], point['y']) for point in waypoints2D]
        
        #Filter spiral points based on distance from trajectory
        filtered_points = self.filter_spiral(spiral_points, trajectory, config.THRESHOLD_DISTANCE)
        
        # Generate obstacles based on filtered points
        obstacles = self.generate_obstacles(filtered_points)
        
        # Plot everything
        self.plot(spiral_points, filtered_points, trajectory, spiral_center, obstacles)
        
        return obstacles

if __name__ == "__main__":
    print("Obstacle Generator")
    generator = ObstacleGenerator()
    obstacles = generator.generate("case_studies/mission3.yaml")
    print("Generated Obstacles:", obstacles)
