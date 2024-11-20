import config
from math import cos, sin
from utils import distance_point_segment

class FibonacciSpiral:

    def __init__(self, center:tuple, bottom_left:tuple, top_right:tuple):
        """
        Initializes a Fibonacci spiral object.

        Parameters:
        center (tuple): The center of the spiral as (x, y) coordinates.
        bottom_left (tuple): The bottom-left corner of the boundary area as (x, y) coordinates.
        top_right (tuple): The top-right corner of the boundary area as (x, y) coordinates.
        """
        
        # Center of the spiral
        self.x, self.y = center

        # Golden angle in radians
        self.angle = config.SPIRAL_GOLDEN_ANGLE
        self.radius = config.SPIRAL_RADIUS_INCREMENT
        self.num_points = config.NUM_SPIRAL_POINTS

        # Boundary coordinates
        self.bottom_left = bottom_left
        self.top_right = top_right

        # Spiral Points
        self.points = self.generate_points()

    def generate_points(self):
        """
        Generates Fibonacci spiral points within specified boundaries.

        Parameters:
        None

        Returns:
        list: A list of (x, y) tuples representing the coordinates of the spiral points that lie within the specified boundaries.
        """
        
        positions = []

        # Generate spiral points
        for i in range(self.num_points):
            radius = self.radius * (i + 1) 
            theta = i * self.angle 

            # Calculate Cartesian coordinates
            x = self.x + radius * cos(theta)
            y = self.y + radius * sin(theta)
            
            # Add point if within specified boundary
            if self.bottom_left[0] <= x <= self.top_right[0] and self.bottom_left[1] <= y <= self.top_right[1]:
                positions.append((x, y))

        return positions
    
    def filter_spiral(self, segment, threshold_distance, bottom_left:tuple, top_right:tuple):
        """
        Filters the Fibonacci spiral points based on their distance from a segment and boundaries.

        Parameters:
        segment (tuple): A pair of (x, y) tuples representing the start and end points of a segment.
        threshold_distance (float): The maximum allowable distance from the segment to include a point.
        bottom_left (tuple): The bottom-left corner of the boundary area as (x, y) coordinates.
        top_right (tuple): The top-right corner of the boundary area as (x, y) coordinates.

        Returns:
        list: A list of unique (x, y) tuples representing the filtered and boundary-constrained points.
        """
        
        filtered_points = []

        #Filter points based on distance from segment
        for point in self.points:
            if distance_point_segment(point, segment) < threshold_distance:
                
                # Round the point to the nearest config.round_parameter
                new_point = (
                    round(point[0] / config.ROUND_PARAMETER) * config.ROUND_PARAMETER,
                    round(point[1] / config.ROUND_PARAMETER) * config.ROUND_PARAMETER,
                )

            # Add point if within specified boundary
            if self.bottom_left[0] <= new_point[0] <= self.top_right[0] and self.bottom_left[1] <= new_point[1] <= self.top_right[1]:
                filtered_points.append(new_point)

        
        # Remove duplicates
        unique_points = list(set(filtered_points))
    
        return unique_points