# UAV-Testing-Competition
## SBFT Tool Comepetion on Testing Unmanned Aerial Vehicles

The [SBFT workshop](https://sbft24.github.io/) organizes a testing tool competition for various tracks including
tool competition for Unmanned Aerial Vehicles(UAVs).

## Overview:

In the tool competition, it is required that each participant presents a robust test generator capable of creating 
a diverse array of tests. The primary objective of these generated tests is to find potential vulnerabilities within
the PX4 avoidance system. This exploration involves manipulating obstacle sizes and placements within the tests, 
with the ultimate goal of either causing the UAV to crash or significantly diverting from its intended flight path.

The efficacy of these generated tests will be assessed based on two crucial metrics: the number of failed cases
and the diversity of the test scenarios. The first metric, the number of failed cases, serves as a straightforward
indicator of the test's ability to uncover system weaknesses. A higher number of failures signifies a more effective 
test in this context.

However, it is equally essential to consider the second metric, which revolves around the diversity of test cases.
Diversifying the test scenarios is critical as it helps ensure that a wide spectrum of potential vulnerabilities is
explored. The more varied the test cases, the greater the likelihood of identifying hidden flaws and edge cases that
might otherwise go undetected.

## Goal

The goals of the tool competition are stated below:

* The objective is to develop a test generator capable of creating diverse and effective tests to uncover
vulnerabilities within the PX4 avoidance system. 
* The generated test will be for a predefined UAV firmware, model, and mission.
* The generated test will create a challenging environment by manipulating object sizes and placements to cause
either UAV crashes or significant deviations in its flight path. 

The effectiveness of these generated tests will be measured based on the number of failed cases and the diversity of
test scenarios. The goal is to identify potential system weaknesses comprehensively and establish a baseline for 
evaluation using the Surrealist tool.

## Software Under Test

* **[PX4](https://px4.io/)** : PX4 is an open-source autopilot software stack primarily used for controlling unmanned aerial vehicles
(UAVs), also known as drones. It provides a flexible and customizable platform for designing and controlling the flight 
of drones, including capabilities for navigation, stabilization, and mission planning. PX4 is compatible with various 
hardware platforms and is widely used in both academic and commercial drone applications. It supports a range of UAV 
types, from small quadcopters to fixed-wing aircraft and even VTOL (Vertical Take-Off and Landing) vehicles. Developers
and researchers often use PX4 as a foundation for creating and testing new drone capabilities and applications.

* **[Gazebo](https://gazebosim.org/home)** : Gazebo is an open-source, 3D robot simulation software framework. It is commonly used in the field of 
robotics for simulating the behavior and interactions of robots and their environments. Gazebo provides a realistic and
flexible simulation environment that allows developers to model and test various aspects of robotic systems without the 
need for physical hardware.

* **[PX4 Avoidance](https://github.com/PX4/PX4-Avoidance)** :  PX4 avoidance provides ROS nodes for obstacle detection and avoidance. It enables the 
autonomously flying UAVs to detect and avoid the obstacles in their flight path during their navigation. PX4 
communicates with another computer which is running ROS nodes and executing the computer vision modules to detect
and avoid obstacles.

## UAV Test Cases
A set of parameters is specified in the YAML file to define a UAV test case, encompassing software configuration,
environmental setup, and a series of runtime commands. These parameters are used to describe a test comprehensively:

* **UAV** : This encapsulates both the physical and software configurations of the UAV model, encompassing all Autopilot
parameters and configuration files.
*  **Environment** : It provides simulation settings, including details about the simulator in use and the world file. 
The world file contains information about surface materials and sets the initial position of the UAV.
* **Commands** : It consists of timestamped commands, specifying vital information such as flight mode and flight 
direction, which are conveyed to the UAV during the course of the flight either from Ground Control Station(GCS) or
Remote Control(RC).

Below is the sample YAML file:

```yaml
# template-test.yaml
drone:
  port: ros # type of the drone to conect to {sitl, ros, cf}
  #params: #PX4 parameters : https://docs.px4.io/main/en/advanced_config/parameter_reference.html
    # {parameter_name}: {parameter_value} #(keep datatype -> e.g, 1.0 for float, 1 for int)
    # CP_DIST: 1.0
    # POS_MOD: 2.5
  params_file: samples/flights/mission1-params.csv #csv file with the same structure as above 
  mission_file: samples/flights/mission1.plan # input mission file address

simulation:
  simulator: ros # the simulator environment to run {gazebo,jmavsim,ros} 
  speed: 1 # the simulator speed relative to real time
  headless: true # whether to run the simulator headless
  obstacles:
  - size: # Object 1 size in l,w,h
      l: 5
      w: 5
      h: 5
    position: # Object 1 position in x,y,z and it's rotation
      x: 10
      y: 5
      z: 0
      angle: 0
  - size: # Object 2 size in l,w,h
      l: 5
      w: 5
      h: 5
    position:  # Object 2 position in x,y,z and it's rotation
      x: -10
      y: 5
      z: 0
      angle: 0
  # home_position: # home position to place the drone [lat,lon,alt]  
test:
  commands_file: samples/flights/mission1-commands.csv # runtime commands file address
  speed: 1 # the commands speed relative to real time

assertion:
  log_file: samples/flights/mission1.ulg # reference log file address
  variable: trajectory # reference variables to compare 

agent:
  engine: docker # where to run the tests {k8s, docker, local}
  count: 1 # no. of parallel runs (only for k8s)
```

Below image shows the graph generated after the run:

![Screenshot from 2023-09-13 12-56-31.png](..%2F..%2FPictures%2FScreenshot%20from%202023-09-13%2012-56-31.png)

## UAV Test Generators

***Samples***:

## Competition Platform

* ***[Aerialist](https://github.com/skhatiri/Aerialist)*** : Aerialist is a modular and extensible test bench for UAV
software, supporting both simulated and physical UAVs. It is developed on the top of PX4. It is capable of executing
simulation-based test cases in your local setup, docker, or even in the Kubernetes cluster. It has a very simple test 
definition model which is very easy to configure.
* ***[Surrealist](https://github.com/skhatiri/Surrealist)*** : It is a tool that provides a search-based Test 
generation approach for UAV software. It provides an implementation for different testing goals like replication of 
real-world tests in simulation, generating non-deterministic test cases, and generating more challenging test cases
based on a given test. This tool internally uses Aerialist to evaluate the test cases.

## Case Studies
The few sample cases provided will contain a param file which will be responsible for delivering necessary commands to 
the UAV during flight and the mission file will be responsible for delivering the waypoints and flight altitudes. 

## Competition rules

The below rules apply to the competition:

* The UAV must finish its mission successfully.
* The test will be considered valid only if the UAV takes off from the specified point, visits all the waypoints, and
lands at the designated place. 
* The test will be considered a hard fail if there is a collision with the obstacle in the environment. So for a
valid test, the UAV must not collide with any obstacles.
* The UAV should also maintain a minimum safe distance of 1.5 m to the obstacles. Otherwise, this will be considered a
soft fail.

## Submission: 

* ***Tool Submission***:
* ***Benchmark results communicated to authors:***

## Evaluation and Ranking: 

To establish a baseline for evaluating these test generators, the Surrealist tool will be employed.
The test cases generated by the competitors will be evaluated against the test generated by 
Surrealist.


Surrealist, serving as the benchmark test generator, will provide a reference point against which the competitors' test
cases can be compared. This ensures a fair and comprehensive evaluation of the generated tests, allowing for a 
well-informed assessment of their quality and effectiveness in identifying vulnerabilities within the PX4 avoidance 
system.

### Evaluation: 

* Tools are allocated a predetermined budget for test execution. This budget represents the overall count of simulated
test executions.

* When a single test case is concurrently simulated 5 or 10 times, it draws upon 5 or 10 executions from the budget.

* Developers hold the responsibility for optimizing their utilization of this allocated budget.

### Evaluation Metrics and Ranking: 
Below evaluation metric will be used to evaluate the tests generated by the tools developed:

* Fault Detection (Test Failure): The test cases will be evaluated for fault detection.
* Testing Budget: A testing budget will be allocated for generating the test cases.
* Test Diversity: Diversity in the test will be valued more. 
* Simplicity: Faults found in less complicated environments will be valued more.

***In order to rank the generated tests, We will run 10 times the final test for evaluation
Fault Detection Probability.***
