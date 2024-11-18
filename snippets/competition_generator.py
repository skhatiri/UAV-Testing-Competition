import random
from typing import List
from math import cos, sin, pi

import config
from aerialist.px4.drone_test import DroneTest
from aerialist.px4.obstacle import Obstacle
from testcase import TestCase
import DroneMissionPlan

from obstacle_generator import ObstacleGenerator
import json

class CompetitionGenerator(object):

    def __init__(self, case_study_file: str) -> None:        
        self.case_study = DroneTest.from_yaml(case_study_file)
        self.case_study_file = case_study_file

    def simulate_execute():
        return random.uniform(0.10, 50)
    
    def generate(self, budget: int) -> List[TestCase]: 
        test_cases = []
        
        # Reading mission plan content
        with open(self.case_study_file, 'r') as file:
            yaml_content = yaml.safe_load(file)
        
        mission_file = yaml_content.get("drone", {}).get("mission_file")
        mission_plan = DroneMissionPlan(mission_file)

        # Create obstacle Generator based on mission plan
        obstacle_generator = ObstacleGenerator(mission_plan)
           
        for _ in range(budget):
            
            # Get candidate points
            candidate_points = obstacle_generator.getCandidatePoints()

            #TODO: Implement evolution algorithm
            obstacles, parameters = obstacle_generator.generate()

            list_obstacles = []
            for obst in obstacles:
                
                position = Obstacle.Position(
                    x=obst['x'], 
                    y=obst['y'], 
                    z=0,
                    r=obst['rotation'],
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
                
                # add minimum distance to parameters json
                parameters["minimum_distance"] = min(distances)
                print(parameters)

            except Exception as e:
                print("Exception during test execution, skipping the test")
                print(e)
        
        return test_cases

if __name__ == "__main__":
    # Testing
    generator = CompetitionGenerator("case_studies/mission3.yaml")
    generator.generate(3) # Budget
