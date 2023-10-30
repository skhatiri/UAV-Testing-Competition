import random
from aerialist.px4.drone_test import DroneTest
from aerialist.px4.obstacle import Obstacle
from testcase import TestCase


class RandomGenerator(object):
    min_size = Obstacle.Size(2, 2, 15)
    max_size = Obstacle.Size(20, 20, 25)
    min_position = Obstacle.Position(5, 5, 0, 0)
    max_position = Obstacle.Position(50, 50, 0, 90)

    def __init__(self, case_study_file: str) -> None:
        self.case_study = DroneTest.from_yaml(case_study_file)

    def generate(self, budget: int):
        for i in range(budget):
            size = Obstacle.Size(
                l=random.uniform(self.min_size.l, self.max_size.l),
                w=random.uniform(self.min_size.w, self.max_size.w),
                h=random.uniform(self.min_size.h, self.max_size.h),
            )
            position = Obstacle.Position(
                x=random.uniform(self.min_position.x, self.max_position.x),
                y=random.uniform(self.min_position.y, self.max_position.y),
                z=0,  # obstacles should always be place on the ground
                r=random.uniform(self.min_position.r, self.max_position.r),
            )
            obstacle = Obstacle(size, position)
            test = TestCase(self.case_study, [obstacle])
            test.execute()
            distances = test.get_distances()
            print(f"minimum_distance:{min(distances)}")
            test.plot()


if __name__ == "__main__":
    generator = RandomGenerator("case_studies/mission1.yaml")
    generator.generate(3)
