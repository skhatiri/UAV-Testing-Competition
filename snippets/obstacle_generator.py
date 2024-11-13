import random
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

    def edge_distance(self, obstacle_edges: Dict, point: Position) -> float:
        # Calculate the shortest distance from point to the edges of the obstacle
        x_dist = min(abs(point.x - obstacle_edges["x_min"]), abs(point.x - obstacle_edges["x_max"]))
        y_dist = min(abs(point.y - obstacle_edges["y_min"]), abs(point.y - obstacle_edges["y_max"]))
        return (x_dist**2 + y_dist**2) ** 0.5  # Euclidean distance from point to the closest edge

    def generate_obstacles(self, budget: int, segment: List[Position], filtered_points: List[Position], speedDrone: float, drone_dimension: float) -> List[Dict]:

        num_obstacles = config.NUM_OBSTACLES 
        obstacles = []

        # Calcola l'angolo del segmento per orientare gli ostacoli
        left_first, angle = calculate_inclination(segment[0], segment[-1])

        # Divide i punti filtrati in sinistra e destra rispetto alla traiettoria
        left_points = [p for p in filtered_points if is_left_of_trajectory(segment, p)]
        right_points = [p for p in filtered_points if not is_left_of_trajectory(segment, p)]

        # Verifica se ci sono punti sufficienti per posizionare gli ostacoli
        if not left_points or not right_points:
            return []  # Nessun ostacolo se i punti sono insufficienti

        # Determina i punti medi a sinistra e a destra per posizionare gli ostacoli
        entry_point_left = left_points[len(left_points) // 2]  # Punto mediano della sinistra
        entry_point_right = right_points[len(right_points) // 2]  # Punto mediano della destra

        # Definisci le dimensioni e inclinazioni degli ostacoli
        obstacle_length = 10
        obstacle_width = 5
        internal_inclination = 25  # Gradi di inclinazione verso l'interno

        candidate_obstacles = {
            "x": entry_point_left.x,
            "y": entry_point_left.y,
            "z": 0,
            "length": obstacle_length,
            "width": obstacle_width,
            "rotation": angle - internal_inclination  # Inclinazione verso l'interno
        }

        # Verifica se l'ostacolo candidato supera la traiettoria, se supera sposta il centro
        candidate_obstacles = self.check_obstacle_position(candidate_obstacles, left_first)

        #Posizionamento secondo elemento:
        #parto dal punto mediano di destra e mi allontano finche non ho la distanza che voglio
        #posiziono il secondo ostacolo

        return obstacles

    # Helper methods

    def calculate_rotated_edges(self, obstacle: Dict) -> Dict:
        """Calculate the rotated edge coordinates of the obstacle."""
        cx, cy = obstacle["x"], obstacle["y"]
        half_length = obstacle["length"] / 2
        half_width = obstacle["width"] / 2
        angle_rad = math.radians(obstacle["rotation"])
        
        # Calculate corner points after rotation
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
        
        # Determine min and max x and y from rotated corners
        x_values, y_values = zip(*corners)
        return {
            "x_min": min(x_values),
            "x_max": max(x_values),
            "y_min": min(y_values),
            "y_max": max(y_values),
        }
    
    def get_obstacle_segment(self, trajectory, min_pos, max_pos) -> List[Position]:
        max_points_in_area = 0
        best_segment = None

        for segment in trajectory:
            
            in_area_points = [
                point for point in segment 
                if (min_pos.x <= point.x <= max_pos.x) and (min_pos.y <= point.y <= max_pos.y)
            ]
            print(len(in_area_points))
            # Update if the current segment has the most points within the area
            if len(in_area_points) > max_points_in_area:
                max_points_in_area = len(in_area_points)
                best_segment = in_area_points  # Store only the filtered points

        return best_segment



    def is_within_generation_area(self, edges: Dict) -> bool:
        """Check if the rotated obstacle edges are within the generation area."""
        return (config.GENERATION_AREA_MIN_POS.x <= edges["x_min"] <= config.GENERATION_AREA_MAX_POS.x and
                config.GENERATION_AREA_MIN_POS.x <= edges["x_max"] <= config.GENERATION_AREA_MAX_POS.x and
                config.GENERATION_AREA_MIN_POS.y <= edges["y_min"] <= config.GENERATION_AREA_MAX_POS.y and
                config.GENERATION_AREA_MIN_POS.y <= edges["y_max"] <= config.GENERATION_AREA_MAX_POS.y)

    def generate(self, case_study_file: str, budget:int):
       
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
        
        drone_speed = mission_plan.get_drone_speed()

        # Generate obstacles
        obstacles = self.generate_obstacles(budget, obst_segment, filtered_points, drone_speed, config.DRONE_DIMENSIONS)
        
        #Plot everything
        self.plot(spiral_points, filtered_points, obst_segment, spiral_center, obstacles)
        
        return obstacles

if __name__ == "__main__":
    print("Obstacle Generator")
    generator = ObstacleGenerator()
    obstacles = generator.generate("case_studies/mission3.yaml", 10)
    print("Generated Obstacles:", obstacles)
