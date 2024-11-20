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

        # Reading mission plan content
        self.case_study = DroneTest.from_yaml(case_study_file)
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
        self.test_counter = 1
        self.budget = 0
        self.history_mutant = set()
        self.candidate_points = self.obstacle_generator.filtered_spiral.copy()
        self.threshold = config.THRESHOLD_DISTANCE
        self.candidate_points_used = set()
        

    def generate(self, budget: int) -> List[TestCase]: 
        print("------------------------------------")
        print("Generation")
        print("------------------------------------")

        # Total budget
        self.budget = budget

        # Initialize parent
        parent_config = self.initialize_parent()
        parent_obsts = self.obstacle_generator.get_obstacles_from_parameters(parent_config)
        is_valid = self.obstacle_generator.is_valid(parent_obsts)
        
        # Mutate parent until it is valid
        if(not is_valid):
            parent_config = self.mutate(parent_config, config.MAX_ATTEMPTS_GENERATION)
            if(parent_config==None):
                raise ValueError("No valid configuration found")
            parent_obsts = self.obstacle_generator.get_obstacles_from_parameters(parent_config)
        else:
            self.history_mutant.add(tuple(parent_config)) # Add to history

        print(f"Parent config: {parent_config}")

        # Execute
        parent_fitness = self.execution(parent_obsts)
        print(f"Parent fitness: {parent_fitness}")
        
        performance_attemps = 0
        while(self.test_counter <= self.budget):
            
            if(performance_attemps < config.MAX_ATTEMPTS_PERFORMANCE):
                child_config = self.mutate(parent_config, config.MAX_ATTEMPTS_GENERATION)
                child_obsts = self.obstacle_generator.get_obstacles_from_parameters(child_config)
                child_fitness = self.execution(child_obsts)

                # Selection
                if child_fitness <= parent_fitness:
                    parent_config = child_config
                    parent_fitness = child_fitness
                    self.history_mutant.add(tuple(parent_config)) # Add to history
                else:
                    performance_attemps += 1
                
                # Output 
                print(f"Generation {self.test_counter-1}: Best fitness = {parent_fitness:.4f}")
            
            else: # Local minimum
                print(f"Local minimum reached")
                parent_config = self.initialize_parent()
                parent_obsts = self.obstacle_generator.get_obstacles_from_parameters(parent_config)
                is_valid = self.obstacle_generator.is_valid(parent_obsts)
                performance_attemps = 0

                # Mutate parent until it is valid
                if(not is_valid):
                    parent_config = self.mutate(parent_config, config.MAX_ATTEMPTS_GENERATION)
                else:
                    self.history_mutant.add(tuple(parent_config)) # Add to history

        print("------------------------------------")
        print(f"Budget ended - Best fitness = {parent_fitness:.4f}")

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
                print("Running ros. . .")
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
        else:
            self.test_counter += 1
        

    def mutate(self, parameters, max_attempts):

        mutated_parameters = parameters.copy()

        for attempt in range(max_attempts):

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
            
            # Add hyperparameters to check validity
            obstacles = self.obstacle_generator.get_obstacles_from_parameters(mutated_parameters)

            # Check if the mutated parameters are valid
            if(self.obstacle_generator.is_valid(obstacles) and tuple(mutated_parameters) not in self.history_mutant):
                self.history_mutant.add(tuple(mutated_parameters))
                return mutated_parameters
        
        #after max attempts, change the parent and mutate again
        print(f"Max attempts reached, initialization new parent")
        parent_config = self.initialize_parent()
        return self.mutate(parent_config, max_attempts)

    def simulate_execute(self):
        distance = round(random.uniform(0.10, 40), 3)        
        print(f"Simulating execution (random)")
        return distance        
    
    def initialize_parent(self):

        # Check if there are any candidate points left
        cand_len = len(self.candidate_points)

        if cand_len == 0:
            self.candidate_points = self.obstacle_generator.recalculate_filter_spiral(self.threshold + 1)
            cand_len = len(self.candidate_points)
        
        # Shuffle the candidate points
        random.shuffle(self.candidate_points)
        
        selected_point = None

        # Iterate through the candidate points to find an unused one
        for point in self.candidate_points:
            if tuple(point) not in self.candidate_points_used:
                selected_point = point
                break

        # If no unused point is found, recalculate and restart
        if selected_point is None:
            self.candidate_points = self.obstacle_generator.recalculate_filter_spiral(self.threshold + 1)
            return self.initialize_parent() 

        # Create parent parameters using the selected point
        parent_parameters = [
            selected_point[0], 
            selected_point[1],  
            np.random.choice(np.arange(0, 91, config.ANGLE_STEP)),  # Random rotation between 0 and 90 degrees (N degree steps)
            selected_point[0],  
            selected_point[1],  
            np.random.choice(np.arange(0, 91, config.ANGLE_STEP))  # Random rotation between 0 and 90 degrees (N degree steps)
        ]

        # Mark the point as used
        self.candidate_points_used.add(tuple(selected_point))

        print(f"Initialization Parent: {parent_parameters}")
        return parent_parameters

if __name__ == "__main__":
    # Testing
    generator = EvolutionaryStrategy("case_studies/mission3.yaml")
    generator.generate(200) # Budget