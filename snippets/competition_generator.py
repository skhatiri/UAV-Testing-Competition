import random
from typing import List
from math import cos, sin, pi

import config
from aerialist.px4.drone_test import DroneTest
from aerialist.px4.obstacle import Obstacle
from testcase import TestCase

from obstacle_generator import ObstacleGenerator
import json

class CompetitionGenerator(object):

    def __init__(self, case_study_file: str) -> None:        
        self.case_study = DroneTest.from_yaml(case_study_file)
        self.case_study_file = case_study_file

    def generate(self, budget: int) -> List[TestCase]: 
        test_cases = []
        for _ in range(budget):
          
            obstacle_generator = ObstacleGenerator()
            obstacles = obstacle_generator.generate(self.case_study_file)
            print(json.dumps(obstacles, indent=4))

            list_obstacles = []
            for obst in obstacles:
                
                position = Obstacle.Position(
                    x=obst['x'], 
                    y=obst['y'], 
                    z=0,
                    r=0,
                )

                size = Obstacle.Size(
                    l=obst['length'], 
                    w=obst['width'], 
                    h= config.OBSTACLE_HEIGHT, # Fixed height of the obstacle
                )
                
                # Create an obstacle with size and position
                obstacle = Obstacle(size, position)
                list_obstacles.append(obstacle)

            test = TestCase(self.case_study, list_obstacles)
            try:
                # Execute test case
                test.execute()
                distances = test.get_distances()
                print(f"minimum_distance: {min(distances)}")
                test.plot()
                test_cases.append(test)
                 
            except Exception as e:
                print("Exception during test execution, skipping the test")
                print(e)
        
        return test_cases

if __name__ == "__main__":
    # Testing
    generator = CompetitionGenerator("case_studies/mission3.yaml")
    generator.generate(3) # Budget
