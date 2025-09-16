import copy
import logging
from typing import List
from decouple import config
from aerialist.px4.aerialist_test import AerialistTest, AgentConfig
from aerialist.px4.obstacle import Obstacle
from aerialist.px4.trajectory import Trajectory

AGENT = config("AGENT", default=AgentConfig.DOCKER)
if AGENT == AgentConfig.LOCAL:
    from aerialist.px4.local_agent import LocalAgent
if AGENT == AgentConfig.DOCKER:
    from aerialist.px4.docker_agent import DockerAgent
if AGENT == AgentConfig.K8S:
    from aerialist.px4.k8s_agent import K8sAgent

logger = logging.getLogger(__name__)


class TestCase(object):
    def __init__(self, casestudy: AerialistTest, obstacles: List[Obstacle]):
        self.test = copy.deepcopy(casestudy)
        self.test.simulation.obstacles = obstacles

    def execute(self) -> Trajectory:
        if AGENT == AgentConfig.LOCAL:
            agent = LocalAgent(self.test)
        if AGENT == AgentConfig.DOCKER:
            agent = DockerAgent(self.test)
        if AGENT == AgentConfig.K8S:
            agent = K8sAgent(self.test)
        logger.info("running the test...")
        self.test_results = agent.run()
        logger.info("test finished...")
        self.trajectory = self.test_results[0].record
        self.log_file = self.test_results[0].log_file
        return self.trajectory

    def get_distances(self) -> List[float]:
        return [
            self.trajectory.min_distance_to_obstacles([obst])
            for obst in self.test.simulation.obstacles
        ]

    def plot(self):
        self.plot_file = AerialistTest.plot(self.test, self.test_results)

    def save_yaml(self, path):
        self.test.to_yaml(path)
