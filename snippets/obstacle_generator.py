import random
from typing import List, Dict
from math import cos, sin, sqrt
import matplotlib.pyplot as plt
import json
from matplotlib.patches import Rectangle
from mission_plan import DroneMissionPlan
from utils import Position,fibonacci_spiral

MIN_POSITION = Position(-40,10)
MAX_POSITION = Position(30,40)

MIN_LENGTH = 2
MIN_WIDTH = 2
MAX_WIDTH = 20
MAX_LENGTH = 20
MIN_HEIGHT = 10
MAX_HEIGHT = 25

NUM_POINTS = 500
THRESHOLD_DISTANCE = 20

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
        plt.savefig('./obstacle_generator.png')

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
        
        for obstacle in range(num_obstacles):
            while True:  # Infinite loop until a valid obstacle is placed
                center_point = random.choice(filtered_points)
                filtered_points.remove(center_point)
                length = random.uniform(MIN_LENGTH, MAX_LENGTH)
                width = random.uniform(MIN_WIDTH, MAX_WIDTH)
                
                # Define the new obstacle with center as (x, y)
                new_obstacle = {
                    "x": center_point.x,
                    "y": center_point.y,
                    "z": 0,
                    "length": length,
                    "width": width,
                    "height": random.uniform(MIN_HEIGHT, MAX_HEIGHT),
                    "rotation": 0  # No rotation for simplicity
                }
                
                # Calculate bounds based on the center
                x_min = new_obstacle["x"] - (new_obstacle["length"] / 2)
                x_max = new_obstacle["x"] + (new_obstacle["length"] / 2)
                y_min = new_obstacle["y"] - (new_obstacle["width"] / 2)
                y_max = new_obstacle["y"] + (new_obstacle["width"] / 2)
                
                # Check if the obstacle is within the allowed boundaries
                if not (MIN_POSITION.x <= x_min <= MAX_POSITION.x and MIN_POSITION.x <= x_max <= MAX_POSITION.x and
                        MIN_POSITION.y <= y_min <= MAX_POSITION.y and MIN_POSITION.y <= y_max <= MAX_POSITION.y):
                    #print("Obstacle out of bounds")
                    continue  # Skip this obstacle if it is out of bounds
                
                # Check if the new obstacle overlaps with any existing obstacles
                if not self.check_overlap(new_obstacle, obstacles):
                    obstacles.append(new_obstacle)
                    break  # Break out of the loop if placed successfully
        
        return obstacles

    def generate(self, case_study_file: str):
       
        mission_plan = DroneMissionPlan(case_study_file)
        waypoints2D = mission_plan.get_mission_items2D()

        avg_x = sum(point['x'] for point in waypoints2D) / len(waypoints2D)
        avg_y = sum(point['y'] for point in waypoints2D) / len(waypoints2D)
        spiral_center = Position(avg_x, avg_y)

        # Generate Fibonacci spiral points
        spiral_points = fibonacci_spiral(NUM_POINTS, spiral_center, MIN_POSITION, MAX_POSITION)

        # Convert mission waypoints to Position objects
        trajectory = [Position(point['x'], point['y']) for point in waypoints2D]
        
        #Filter spiral points based on distance from trajectory
        filtered_points = self.filter_spiral(spiral_points, trajectory, THRESHOLD_DISTANCE)
        
        # Generate obstacles based on filtered points
        obstacles = self.generate_obstacles(filtered_points)
        
        # Plot everything
        self.plot(spiral_points, filtered_points, trajectory, spiral_center, obstacles)
        
        return obstacles

if __name__ == "__main__":
    print("Obstacle Generator")
    generator = ObstacleGenerator()
    obstacles = generator.generate("case_studies/mission3.plan")
    print("Generated Obstacles:", obstacles)
