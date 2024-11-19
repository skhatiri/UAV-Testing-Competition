import random
from typing import List
from math import cos, sin, pi
import yaml
import numpy as np
import config
from aerialist.px4.drone_test import DroneTest
from aerialist.px4.obstacle import Obstacle
from testcase import TestCase
import DroneMissionPlan
import signal
import datetime
import os
import shutil

from obstacle_generator import ObstacleGenerator
import json

TESTS_FOLDER = config("TESTS_FOLDER", default="./generated_tests/")

def timeout_handler(signum, frame):
        raise Exception("Timeout")


class EvolutionaryStrategy(object):

    def __init__(self, case_study_file: str) -> None:        
        self.case_study = DroneTest.from_yaml(case_study_file)
        
        # Reading mission plan content
        self.case_study_file = case_study_file
        with open(self.case_study_file, 'r') as file:
            yaml_content = yaml.safe_load(file)
        
        mission_file = yaml_content.get("drone", {}).get("mission_file")
        self.mission_plan = DroneMissionPlan(mission_file)

        # Create obstacle Generator based on mission plan
        self.obstacle_generator = ObstacleGenerator(self.mission_plan)

        # Parameters for the evolution algorithm
        self.dimensions = 6
        self.sigma = 0.1
        self.num_generation = 50

        # Create a folder to store the tests
        self.tests_fld = f'{TESTS_FOLDER}{datetime.now().strftime("%d-%m-%H-%M-%S")}/'
        os.mkdir(self.tests_fld)
        print(f"Output folder: {self.tests_fld}")


    def simulate_execute():
        return random.uniform(0.10, 50)
    
    def generate(self, budget: int) -> List[TestCase]: 
        
        test_cases = []
        candidate_points = self.obstacle_generator.getCandidatePoints()

        parent_parameters = [
            candidate_points[0][0], 
            candidate_points[0][1],  
            np.random.choice(np.arange(0, 91, 10)), # Random rotation between 0 and 90 degrees (10 degree steps)
            candidate_points[1][0],  
            candidate_points[1][1],  
            np.random.choice(np.arange(0, 91, 10)) # Random rotation between 0 and 90 degrees (10 degree steps)
        ]
    
        parent_config = self.obstacle_generator.generate(parent_parameters)
        parent_fitness = self.execution(parent_config)
        
        minimum_local = 0
        history_mutant = []
        for i in range(budget):

            if(minimum_local < config.LOCAL_MINIMUM): # Avoid local minimum
                child_config = self.obstacle_generator.mutate(parent_config, history_mutant)
                history_mutant.append(child_config)
                child_fitness = self.execution(child_config)

                # Selection
                if child_fitness <= parent_fitness:
                    parent_config = child_config
                    parent_fitness = child_fitness
                    minimum_local = 0
                    history_mutant = []
                else:
                    minimum_local += 1

                # Output 
                print(f"Generation {i+1}: Miglior fitness = {parent_fitness:.4f}")
            else:
                parent_parameters = []
                parent_config = self.obstacle_generator.generate(parent_parameters)
                minimum_local = 0
                history_mutant = []

    def execution(self, config):
        test_cases = []
        list_obstacles = []
        for obst in config:
            
            position = Obstacle.Position(
                x=obst['x'], 
                y=obst['y'], 
                z=obst['z'],
                r=obst['rotation'],
            )

            size = Obstacle.Size(
                l=obst['length'], 
                w=obst['width'], 
                h=obst['heigth'],
            )
            
            # Create an obstacle with size and position
            obstacle = Obstacle(size, position)
            list_obstacles.append(obstacle)

        test = TestCase(self.case_study, list_obstacles)
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            timeout_duration = 60 * 10
            signal.alarm(timeout_duration)

            test.execute()

            distances = test.get_distances()
            print(f"Minimum distance:{min(distances)}")
            test.plot()
        except Exception as e:
            print("Exception during test execution, skipping the test")
            print(e)
        
        # Save the results
        if(min(distances) < config.MINIMUM_DISTANCE_EXECUTION):
            date_time = datetime.now().strftime("%d-%m-%H-%M-%S")
            test.save_yaml(f"{self.tests_fld}/test_{datetime}.yaml")
            shutil.copy2(test.log_file, f"{self.tests_fld}/test_{datetime}.ulg")
            shutil.copy2(test.plot_file, f"{self.tests_fld}/test_{datetime}.png")

            # Add minimum distance and obstacles to json
            parameters = self.obstacle_generator.getParameters()
            parameters["obstacles"] = config
            parameters["minimum_distance"] = min(distances)

            shutil.copy2(parameters, f"{self.tests_fld}/parameters{datetime}.json")
            print(f"Results saved to {self.tests_fld}")

        return min(distances)

if __name__ == "__main__":
    # Testing
    generator = CompetitionGenerator("case_studies/mission3.yaml")
    generator.generate(3) # Budget
