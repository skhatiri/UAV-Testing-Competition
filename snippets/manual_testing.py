import random
from typing import List
from aerialist.px4.drone_test import DroneTest
from aerialist.px4.obstacle import Obstacle
from testcase import TestCase
import os
import shutil
import sys
import signal

from decouple import config
from datetime import datetime
TESTS_FOLDER = config("TESTS_FOLDER", default="./generated_tests/")

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

class TestingGenerator(object):

    def __init__(self, case_study_file: str) -> None:
        self.case_study = DroneTest.from_yaml(case_study_file)

    def generate(self, budget: int) -> List[TestCase]:
        test_cases = []
        for i in range(budget):
            size1 = Obstacle.Size(
                l = 10,
                w = 20,
                h = 25,
            )
            position1 = Obstacle.Position(
                x= 3.2,
                y= 21.9,
                z= 0,
                r= 20,
            )
            obstacle1 = Obstacle(size1, position1)
            
            size2 = Obstacle.Size(
                l = 10,
                w = 20,
                h = 25,
            )
            position2 = Obstacle.Position(
                x= -13.1,
                y= 22.35,
                z= 0,
                r= 10,
            )
            obstacle2 = Obstacle(size2, position2)
            
            test = TestCase(self.case_study, [obstacle1, obstacle2])
            try:
                
                 # Set timeout for test execution
                signal.signal(signal.SIGALRM, timeout_handler)
                timeout_duration = 60 * 10
                signal.alarm(timeout_duration)
                print("Running ros. . .")
                
                test.execute()
                distances = test.get_distances()
                print(f"minimum_distance:{min(distances)}")
                test.plot()
                test_cases.append(test)
            except Exception as e:
                print("Exception during test execution, skipping the test")
                print(e)

        ### You should only return the test cases
        ### that are needed for evaluation (failing or challenging ones)
        return test_cases


if __name__ == "__main__":
    generator = TestingGenerator("case_studies/mission2.yaml")
    test_cases = generator.generate(1)
    
    ### copying the test cases to the output folder
    tests_fld = f'{TESTS_FOLDER}{datetime.now().strftime("%d-%m-%H-%M-%S")}/'
    os.mkdir(tests_fld)
    for i in range(len(test_cases)):
        test_cases[i].save_yaml(f"{tests_fld}/test_{i}.yaml")
        shutil.copy2(test_cases[i].log_file, f"{tests_fld}/test_{i}.ulg")
        shutil.copy2(test_cases[i].plot_file, f"{tests_fld}/test_{i}.png")
    print(f"{len(test_cases)} test cases generated")
    print(f"output folder: {tests_fld}")
