import copy
from typing import List
from aerialist.px4.drone_test import DroneTest
from aerialist.px4.obstacle import Obstacle
from aerialist.px4.docker_agent import DockerAgent
from aerialist.px4.trajectory import Trajectory


class TestCase(object):
    def __init__(self, casestudy: DroneTest, obstacles: List[Obstacle]):
        self.test = copy.deepcopy(casestudy)
        self.test.simulation.obstacles = obstacles

    def execute(self) -> Trajectory:
        docker_agent = DockerAgent(self.test)
        self.test_results = docker_agent.run()
        self.trajectory = self.test_results[0].record
        return self.trajectory

    def get_distances(self) -> List[float]:
        return [
            self.trajectory.min_distance_to_obstacles([obst])
            for obst in self.test.simulation.obstacles
        ]

    def plot(self):
        DroneTest.plot(self.test, self.test_results)

    def save_yaml(self, path):
        self.test.to_yaml(path)
