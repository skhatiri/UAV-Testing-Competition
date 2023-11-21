# Developing Your Own Test Generator

You can integrate Aerialist's python package in your own code and directly define and execute UAV test cases with it.
This can be speccifically useful when you are working on test generation approaches for UAVs. An example of such usage of Aerialist can be found in [Surrealist](https://github.com/skhatiri/Surrealist).

1. `pip3 install git+https://github.com/skhatiri/Aerialist.git`
2. We suggest you first experiment with the Docker Agent
    - Make sure you are able to run test cases inside docker [using your client CLI](https://github.com/skhatiri/Aerialist#using-hosts-cli)
3. Check [TestCase](testcase.py) class for a simple implementation for defining and executing test cases.
4. Check [RandomGenerator](random_generator.py) class for a simple test generator that puts an obstacle with random size and position inside a givent case study mission.
5. Check [CLI](cli.py) for a sample Command Line Interface to invoke your code.
6. Check [Dockerfile](Dockerfile) for a proper way to dockerize your code.
7. Develop your own test genrator based on the above samples. You can clone this repository and re-use all classes and case studies.
8. Feel free to use the [discussion section]((https://github.com/skhatiri/UAV-Testing-Competition/discussions)) or contact the organizers to ask your questions.
