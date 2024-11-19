import random
from typing import List
from math import cos, sin, pi
import yaml
import numpy as np
import config
from aerialist.px4.drone_test import DroneTest
from aerialist.px4.obstacle import Obstacle
from testcase import TestCase
from mission_plan import DroneMissionPlan
import signal
from datetime import datetime
import os
import shutil
from json import *
from obstacle_generator import ObstacleGenerator
import json

class DataEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
    
def timeout_handler(signum, frame):
        raise Exception("Timeout")

class EvolutionaryStrategy(object):

    def __init__(self, case_study_file: str) -> None:
        
        print("------------------------------------")
        print("Evolutionary Strategy Setup")
        print("------------------------------------")

        self.case_study = DroneTest.from_yaml(case_study_file)
        
        # Reading mission plan content
        self.case_study_file = case_study_file
        with open(self.case_study_file, 'r') as file:
            yaml_content = yaml.safe_load(file)
        
        mission_file = yaml_content.get("drone", {}).get("mission_file")
        self.mission_plan = DroneMissionPlan(mission_file)

        # Create obstacle Generator based on mission plan
        self.obstacle_generator = ObstacleGenerator(self.mission_plan, case_study_file)

        # Create a folder to store the tests
        self.tests_fld = f'{config.DIR_GENERATED_TESTS}{datetime.now().strftime("%d-%m-%H-%M-%S")}/'
        os.makedirs(self.tests_fld, exist_ok=True)
        print(f"Output folder: {self.tests_fld}")

        #Counter for the tests
        self.test_counter = 0
        self.budget = 0

    def simulate_execute(self):
        distance = round(random.uniform(0.10, 40), 3)        
        print(f"Simulating execution (random)")
        return distance        
    
    def initialize_parent(self):
        candidate_points = self.obstacle_generator.getCandidatePoints()
        cand_len = len(candidate_points)
        
        # Choose random points from the candidate points
        i = random.randint(0, cand_len-1)

        parent_parameters = [
            candidate_points[i][0], 
            candidate_points[i][1],  
            np.random.choice(np.arange(0, 91, config.ANGLE_STEP)), # Random rotation between 0 and 90 degrees (N degree steps)
            candidate_points[i][0],  
            candidate_points[i][1],  
            np.random.choice(np.arange(0, 91, config.ANGLE_STEP)) # Random rotation between 0 and 90 degrees (N degree steps)
        ]

        return parent_parameters

    def generate(self, budget: int) -> List[TestCase]: 
        print("------------------------------------")
        print("Generation")
        print("------------------------------------")

        self.budget = budget
        parent_config = self.initialize_parent()
        parent_config = self.obstacle_generator.generate(parent_config)
        print(f"Parent config: {parent_config}")
        parent_obsts = self.obstacle_generator.get_obstacles_from_parameters(parent_config)
        parent_fitness = self.execution(parent_obsts)
        print(f"Parent fitness: {parent_fitness}")
        
        minimum_local = 0
        history_mutant = []
        
        for i in range(self.budget):

            if(minimum_local < config.LOCAL_MINIMUM): # Avoid local minimum
                child_config = self.obstacle_generator.mutate(parent_config, history_mutant)
                history_mutant.append(child_config)
                child_obsts = self.obstacle_generator.get_obstacles_from_parameters(child_config)
                child_fitness = self.execution(child_obsts)

                # Selection
                if child_fitness <= parent_fitness:
                    parent_config = child_config
                    parent_fitness = child_fitness
                    minimum_local = 0
                    history_mutant = []
                else:
                    minimum_local += 1

                # Output 
                print(f"Generation {self.test_counter}: Best fitness = {parent_fitness:.4f}")
            else:
                parent_parameters = self.initialize_parent()
                parent_config = self.obstacle_generator.generate(parent_parameters)
                minimum_local = 0
                history_mutant = []

    def execution(self, obstacles):
        
        print("------------------------------------")
        print(f"Execution {self.test_counter}/{self.budget}")
        print("------------------------------------")

        list_obstacles = []

        for obst in obstacles:
            
            position = Obstacle.Position(
                x=obst['x'], 
                y=obst['y'], 
                z=obst['z'],
                r=obst['rotation'],
            )

            size = Obstacle.Size(
                l=obst['length'], 
                w=obst['width'], 
                h=obst['height'],
            )
            
            # Create an obstacle with size and position
            obstacle = Obstacle(size, position)
            list_obstacles.append(obstacle)

        test = TestCase(self.case_study, list_obstacles)
        try:
            
            if(config.TESTING == True):
                distances = [self.simulate_execute()]
            else:
                signal.signal(signal.SIGALRM, timeout_handler)
                timeout_duration = 60 * 10
                signal.alarm(timeout_duration)

                test.execute()
                test.plot()
                distances = test.get_distances()


            print(f"Minimum distance:{min(distances)}")
        except Exception as e:
            print("Exception during test execution, skipping the test")
            print(e)
        
        # Save the results
        if(min(distances) < config.MINIMUM_DISTANCE_EXECUTION):


            if(config.TESTING == False):
                test.save_yaml(f"{self.tests_fld}test_{self.test_counter}.yaml")
                shutil.copy2(test.log_file, f"{self.tests_fld}test_{self.test_counter}.ulg")
                shutil.copy2(test.plot_file, f"{self.tests_fld}test_{self.test_counter}.png")

            # Add minimum distance and obstacles to json
            parameters = self.obstacle_generator.getParameters()
            parameters["obstacles"] = f"{obstacles}"
            parameters["minimum_distance"] = f"{min(distances)}"
            
            # Save the parameters to json
            parameters_file = f"{self.tests_fld}parameters_{self.test_counter}.json"
            with open(parameters_file, "w") as json_file:
                json.dump(parameters, json_file, indent=4, ensure_ascii=False)
            
            print(f"Test saved to {parameters_file}")
            self.test_counter += 1
            return min(distances)

if __name__ == "__main__":
    # Testing
    generator = EvolutionaryStrategy("case_studies/mission3.yaml")
    generator.generate(200) # Budget
