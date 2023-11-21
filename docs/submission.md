# Submission

## Test Generator Requirements

We ask all the competition participants to follow the following requiremnts and guidellines while developing their approach. This will make sure that we can run and evaluate your approach.

**Note that the sample code available [here](../snippets/) already fulfills these requirements. If you base your code on the same structure, you probably do not need any customization.**

### Command Line Interface

- All test generators MUST implement a Command Line Interface with the exact interface as [cli.py](../snippets/cli.py).
  - your test generator must be runnable with the following command given the case study file and budget:

    `python3 cli.py generate case_studies/mission1.yaml 100`

- The expected output of the test generators is a list of *challenging* test cases found during the gereration process stored in an specific folder.
  - You should only list the test cases that you want us to evaluate your approach with. e.g., you should not report the intermediate test cases that are safe and passing, which led your algorithm to the final failing scenarios.  
  - The test cases (YAML files), as well as their simulation flight logs (.ulg files) and flight plots should be copied to a new folder (e.g., results/generated-1/) and the address should be printed in the output of the CLI.
  - **Check [cli.py](../snippets/cli.py) for a sample implementation.** You are strongly advised to use it as reference, and just update it to use your own code instead of the sample test generator.

### Test Execution

- All test generators must be built on top of the functionalities available in the [TestCase](../snippets/testcase.py) class. This will make sure we can easily run your code in our evaluation infrastructure.
  - Speccifically, make sure to integrate the exact same options (see execute()) to change the test execution agent (local,docker,k8s) with an environment variable. We will use our own Kubernetes cluster to run the simulations.
  - **If you build on top of the given [TestCase](../snippets/testcase.py) class, you do not need to worry about the details.**
- It could be possible that some of the test executions are problematic and does not yield to a proper logfile (trajectory). You are required to handle such execptions within your code, as the sample [random generator](../snippets/random_generator.py).

### Docker Image

- All test generators MUST be dockerized with all the required dependencies.
  - We provide a sample [Dockerfile](../snippets/Dockerfile) that already implements all the required steps for easily creating a docker image for our sample test generator.
  - **This should already work for your custmized code as well if placed in the same folder.**
  - You can update [requirements.txt](../snippets/requirements.txt) to include your specific dependencies.

## Submission Guideline  

- You should fork this repository and integrate your code.
- Make sure the CLI is alligned with the above guideline.
- Make sure the Dockerfile works and your code behaves as expected using the built docker image.
- Update the [readme file](../snippets/README.md) with a short description of your code, running examples and list of authors (Name, Surname, Email, Affiliation).
- To submit your test generator, you should send a link to your fork in an email to the [competition organizers](../README.md#contacts). If it is a private repository, make sure to also invite [@skhatiri](https://github.com/skhatiri) to the repository.
- Alternatively, you can send us a compressed folder with the same structure.
- We will contact you if we need help running your code.

As always, feel free to use the [discussion section]((https://github.com/skhatiri/UAV-Testing-Competition/discussions)) or contact the organizers to ask your questions.
