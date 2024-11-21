import random
from typing import List
from math import sin, pi
import yaml
import numpy as np
import config
from aerialist.px4.drone_test import DroneTest  # type: ignore
from aerialist.px4.obstacle import Obstacle # type: ignore

from config import X_RANGE, Y_RANGE
from testcase import TestCase
from mission_plan import DroneMissionPlan
import signal
from datetime import datetime
import os
import shutil
from json import *
from obstacle_generator import ObstacleGenerator
import json

class EvolutionaryStrategy(object):

    def __init__(self, case_study_file):
        """
        Initializes the Evolutionary Strategy class, including reading the mission plan 
        and preparing the environment for testing.

        Parameters:
        case_study_file (str): Path to the YAML file containing the case study configuration.
        
        Return:
        None
        """
        
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

        # Initialize variables
        self.test_counter = 1
        self.budget = 0
        self.history_mutant = set()
        self.candidate_points = self.obstacle_generator.filtered_spiral.copy()
        self.candidate_pairs_used = set()
        self.threshold = config.THRESHOLD_DISTANCE
        self.total_score = 0
        self.valid_test_cases = 0
        
    def generate(self, budget): 
        """
        Executes an evolutionary strategy to optimize obstacle configurations within a given budget.

        Parameters:
        budget (int): The total number of test iterations allowed for the optimization process.

        Returns:
        None
        """
        
        print("------------------------------------")
        print("Generation")
        print("------------------------------------")

        # Total budget of tests
        self.budget = budget

        # Initialize parent configuration
        parent_config = self.restart()
        parent_obsts = self.obstacle_generator.get_obstacles_from_parameters(parent_config)
        print(f"Parent config: {parent_config}")

        # Execute
        parent_fitness = self.execution(parent_obsts)
        print(f"Parent fitness: {parent_fitness}")
        
        # Counter to check local minimum    
        performance_attemps = 0 

        # Main loop
        while(self.test_counter <= self.budget):
            
            # Check precence of local minimum
            if(performance_attemps < config.MAX_ATTEMPTS_PERFORMANCE):
                
                # Mutate
                child_config = self.mutate_child(parent_config, config.MAX_ATTEMPTS_GENERATION)
                child_obsts = self.obstacle_generator.get_obstacles_from_parameters(child_config)
                child_fitness = self.execution(child_obsts)

                # Selection
                if child_fitness <= parent_fitness:
                    parent_config = child_config
                    parent_fitness = child_fitness
                    self.history_mutant.add(tuple(parent_config)) # Add to history
                else:
                    performance_attemps += 1
                
                # Print generation results
                print(f"Generation {self.test_counter-1}: Best fitness = {parent_fitness:.4f}")
            
            else: # Local minimum reached
                
                # Restart
                parent_config = self.restart()
                performance_attemps = 0

        print("------------------------------------")
        print(f"Budget ended - Best fitness = {parent_fitness:.4f}")

    def execution(self, obstacles):
        """
        Executes a test case with the given obstacle configuration and manages the test results.

        Parameters:
        obstacles (list): A list of dictionaries representing obstacles, where each dictionary contains:
            - 'x', 'y', 'z': Position coordinates.
            - 'rotation': Rotation angle.
            - 'length', 'width', 'height': Size dimensions.

        Returns:
        float: The minimum distance recorded during the test execution, if the test is valid.
        """
        
        print("------------------------------------")
        print(f"Execution {self.test_counter}/{self.budget}")
        print("------------------------------------")

        list_obstacles = []

        # Create obstacles from the input
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
            
            obstacle = Obstacle(size, position)
            list_obstacles.append(obstacle)

        # Execute the test case
        test = TestCase(self.case_study, list_obstacles)
        distances = []
        try:
            
            if(config.TESTING == True):
                distances = [self.simulate_execute()]
            else:
                # Set timeout for test execution
                signal.signal(signal.SIGALRM, timeout_handler)
                timeout_duration = 60 * 10
                signal.alarm(timeout_duration)
                print("Running ros. . .")
                
                # Execute the test
                test.execute()
                
                # Plot the test results
                test.plot()
                
                # Get the distances
                distances = test.get_distances()

            print(f"Minimum distance: {min(distances)}")
        except Exception as e:
            print("Exception during test execution, skipping the test")
            print(e)
        
        if(distances == []):
            distances = [9999]
        
        # Save the results
        if(min(distances) < config.MINIMUM_DISTANCE_EXECUTION):

            self.total_score += self.calculate_score(min(distances))
            self.valid_test_cases += 1

            if(config.TESTING == False):
                test.save_yaml(f"{self.tests_fld}test_{self.test_counter}.yaml")
                shutil.copy2(test.log_file, f"{self.tests_fld}test_{self.test_counter}.ulg")
                shutil.copy2(test.plot_file, f"{self.tests_fld}test_{self.test_counter}.png")

            # Add minimum distance and obstacles to json
            parameters = self.obstacle_generator.getParameters()
            print(obstacles)
            parameters["obstacles"] = obstacles
            parameters["minimum_distance"] = float(min(distances))
            
            # Save the parameters to json
            parameters_file = f"{self.tests_fld}parameters_{self.test_counter}.json"
            with open(parameters_file, "w") as json_file:
                json.dump(parameters, json_file, indent=4, ensure_ascii=False)
            
            print(f"Test saved to {self.tests_fld}")
        
        # Update the test counter
        self.test_counter += 1
        return min(distances)       
                
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
        parent_config = self.initialize_parent()
        return self.mutate(parent_config, max_attempts)

    def simulate_execute(self):
        """
        Simulates the execution of a test by generating a random distance value.

        Returns:
        float: A randomly generated distance value, rounded to 3 decimal places.
        """
        
        # Generate a random distance value
        distance = round(random.uniform(0.10, config.MINIMUM_DISTANCE_EXECUTION + 10), 3)        
        print(f"Simulating execution (random)")
        
        return distance        
    
    def initialize_parent(self):
        """
        Initializes a new parent configuration by selecting a pair of candidate points
        and generating their parameters (positions and angles).

        Returns:
        list: A list of parent parameters, including positions (x, y) and rotations (r) for two points.
        """
        
        cand_len = len(self.candidate_points)

        if cand_len < 2:
            self.candidate_points = self.obstacle_generator.recalculate_filter_spiral(self.threshold + 1)
            self.threshold += 1 # Increase threshold
            return self.initialize_parent()
        
        # Shuffle the candidate points
        random.shuffle(self.candidate_points)
        
        selected_pair = None

        # Iterate through candidate points to find an unused pair
        for i, point1 in enumerate(self.candidate_points):
            for j, point2 in enumerate(self.candidate_points):
                
                 # Ensure the two points are distinct
                if i != j:  
                    
                    # Check if the pair is already used
                    pair = (tuple(point1), tuple(point2))
                    if pair not in self.candidate_pairs_used and tuple(reversed(pair)) not in self.candidate_pairs_used:
                        selected_pair = pair
                        
                        break
            if selected_pair:
                break

        # If no unused pair is found, recalculate and restart
        if selected_pair is None:
            self.candidate_points = self.obstacle_generator.recalculate_filter_spiral(self.threshold + 1)
            self.threshold += 1 # Increase threshold
            return self.initialize_parent()

        # Create parent parameters
        parent_parameters = [
            selected_pair[0][0], # x1
            selected_pair[0][1], # y1 
            np.random.choice(np.arange(0, 91, config.ANGLE_STEP)),  # r1
            selected_pair[1][0], # x2
            selected_pair[1][1], # y2
            np.random.choice(np.arange(0, 91, config.ANGLE_STEP))  # r2
        ]

        # Add the selected pair to the used pairs
        self.candidate_pairs_used.add(selected_pair)
        return parent_parameters

    def mutate_child(self, parameters, max_attempts):
        """
        Mutates the child
        :param parameters:
        :param max_attempts:
        :return:
        """

        for attempt in range(max_attempts):

            # create a copy of the father and mutate i
            mutated_parameters = parameters.copy()

            # Choose a random parameter to mutate
            choice = np.random.uniform(0.0, 1.0)
            # print(f"{choice}")
            if choice < 0.3:  # Move block 1
                new_x1 = mutated_parameters[0] + np.random.choice(X_RANGE)
                new_y1 = mutated_parameters[1] + np.random.choice(Y_RANGE)
                mutated_parameters[0] = new_x1
                mutated_parameters[1] = new_y1

            elif choice < 0.5:  # Rotate block 1
                new_r1 = np.random.choice(np.arange(0, 91, config.ANGLE_STEP))
                mutated_parameters[2] = new_r1

            elif choice < 0.8:  # Move block 2
                new_x2 = mutated_parameters[3] + np.random.choice(X_RANGE)
                new_y2 = mutated_parameters[4] + np.random.choice(Y_RANGE)
                mutated_parameters[3] = new_x2
                mutated_parameters[4] = new_y2

            elif choice <= 1:  # Rotate block 2
                new_r2 = np.random.choice(np.arange(0, 91, config.ANGLE_STEP))
                mutated_parameters[5] = new_r2

            # Add hyperparameters to check validity
            obstacles = self.obstacle_generator.get_obstacles_from_parameters(mutated_parameters)

            # Check if the mutated parameters are valid
            if (self.obstacle_generator.is_valid(obstacles) and tuple(mutated_parameters) not in self.history_mutant):
                self.history_mutant.add(tuple(mutated_parameters))
                return mutated_parameters

        # after max attempts, change the parent and mutate again
        parent_config = self.initialize_parent()
        return self.mutate(parent_config, max_attempts)
    
    def mutate_parent(self, parameters, max_attempts):
        """
        Mutates the given parent parameters by randomly modifying one parameter at a time
        and checks for validity after each mutation. If a valid mutation is not found within
        the maximum number of attempts, a new parent is initialized and mutation continues.

        Parameters:
        parameters (list): [x1, y1, r1, x2, y2, r2]
        max_attempts (int): The maximum number of mutation attempts allowed.

        Returns:
        list: A new valid set of mutated parameters
        
        """
        # Mutate parent
        mutated_parameters = parameters.copy()

        for attempt in range(max_attempts):
            # Choose a random parameter to mutate
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
            if(self.obstacle_generator.is_valid(obstacles)):
                return mutated_parameters
        
        # After max attempts, change the parent and mutate again
        parent_config = self.initialize_parent()
        
        return self.mutate_parent(parent_config, max_attempts)
            
    def restart(self):
        """
        Restarts the evolutionary strategy by initializing a new parent configuration.

        Returns:
        parameters: new valid parent configuration
        """
        
        parent_config = self.initialize_parent()
        parent_obsts = self.obstacle_generator.get_obstacles_from_parameters(parent_config)
        is_valid = self.obstacle_generator.is_valid(parent_obsts)
        
        # Mutate parent until it is valid
        if(not is_valid):
            parent_config = self.mutate_parent(parent_config, config.MAX_ATTEMPTS_GENERATION)
        else:
            self.history_mutant.add(tuple(parent_config)) # Add to history
        
        return parent_config
    
    def save_results(self):
        
        # Data to save in JSON
        data = {
            "Global Variables": {
                "NUM_SPIRAL_POINTS": config.NUM_SPIRAL_POINTS,
                "SPIRAL_GOLDEN_ANGLE": config.SPIRAL_GOLDEN_ANGLE,
                "SPIRAL_RADIUS_INCREMENT": config.SPIRAL_RADIUS_INCREMENT,
                "GENERATION_AREA_MIN_POS": [config.GENERATION_AREA_MIN_POS[0], config.GENERATION_AREA_MIN_POS[1]],
                "GENERATION_AREA_MAX_POS": [config.GENERATION_AREA_MAX_POS[0], config.GENERATION_AREA_MAX_POS[1]],
                "THRESHOLD_DISTANCE": config.THRESHOLD_DISTANCE,
                "ROUND_PARAMETER": config.ROUND_PARAMETER,
                "X_RANGE": config.X_RANGE,
                "Y_RANGE": config.Y_RANGE,
                "OBST_LENGTH": config.OBST_LENGTH,
                "OBST_WIDTH": config.OBST_WIDTH,
                "OBSTACLE_HEIGHT": config.OBSTACLE_HEIGHT,
                "OBST_Z": config.OBST_Z,
                "ANGLE_STEP": config.ANGLE_STEP,
                "MAX_ATTEMPTS_GENERATION": config.MAX_ATTEMPTS_GENERATION,
                "MAX_ATTEMPTS_PERFORMANCE": config.MAX_ATTEMPTS_PERFORMANCE,
                "MINIMUM_DISTANCE_EXECUTION": config.MINIMUM_DISTANCE_EXECUTION,
                "LOCAL_MINIMUM": config.LOCAL_MINIMUM,
                "DIR_GENERATED_PLOTS": config.DIR_GENERATED_PLOTS,
                "DIR_GENERATED_TESTS": config.DIR_GENERATED_TESTS,
                "TESTING": config.TESTING,
                "NUM_OBSTS": config.NUM_OBSTS
                },
                "Competition": {
                    "Score": self.total_score,
                    "Failures": round((self.valid_test_cases / self.budget) * 100, 2),
                }
            }
        
        try:
            with open(f"{self.tests_fld}setup.json", 'w') as json_file:
                json.dump(data, json_file, indent=4)
            print(f"Result file saved successfully.")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            
    def calculate_score(self, min_dist):
        """
        Calculates the score based on the minimum distance.

        Args:
            min_dist (float): The minimum distance in meters.

        Returns:
            int: The calculated score.
        """
        
        # Calculate score based on the minimum distance
        if min_dist < 0.25:
            return 5
        elif 0.25 <= min_dist < 1.0:
            return 2
        elif 1.0 <= min_dist < 1.5:
            return 1
        else:
            return 0
    
def timeout_handler(signum, frame):
    """
    Utility function: handles timeout signals by raising an exception.

    Parameters:
    signum (int): The signal number.
    frame (frame): The current stack frame.

    Raises:
    Exception: An exception to indicate a timeout occurred.
    """
    raise Exception("Timeout")

if __name__ == "__main__":
    # Testing
    generator = EvolutionaryStrategy("case_studies/mission3.yaml")
    generator.generate(20) # Budget
    generator.save_results()