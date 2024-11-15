# Announcements and Updates

## Evaluation Report and Ranking (3.03.2024)

The competition report and the ranking is out. Here is the overal ranking, while more details can be found in the competition report ([preprint](reports/UAV_Competition_SBFT_2024.pdf)).

| Tool Name                                                                             | #obst.     | CS2 |       | CS3 |       | CS4 |       | CS5 |       | CS6 |       | CS7 |       | Rank Sum  | Score Sum  | Final Rank  |
|---------------------------------------------------------------------------------------|------------|-----|-------|-----|-------|-----|-------|-----|-------|-----|-------|-----|-------|-----------|------------|-------------|
|                                                                                       |            | #   | score | #   | score | #   | score | #   | score | #   | score | #   | score |           |            |             |
| [WOGAN-UAV](https://gitlab.abo.fi/stc/experiments/wogan-uav)                          | 3          | 61  | 12,55 | 72  | 14,00 | 81  | 2,35  | 39  | 8,40  | 71  | 4,81  | 90  | 11,57 | 12        | 53,69      | 1           |
| [TUMB](https://github.com/MayDGT/UAV-Testing-Competition)                             | [1-4]      | 69  | 0,12  | 113 | 15,59 | 135 | 7,12  | 114 | 2,73  | 151 | 15,32 | 125 | 11,12 | 16        | 52,00      | 2           |
| [CAMBA](https://github.com/mdeliso97/CAMBA_CPS-UAV_at_the_SBFT_Tool_Competition_2024) | 2          | 36  | 11,84 | 30  | 8,50  | 33  | 0,00  | 11  | 3,16  | 102 | 12,92 | 22  | 4,69  | 18        | 41,11      | 3           |
| [DeepHyperion-UAV](https://github.com/zohdit/UAV-Testing-Competition)                 | 2          | 2   | 1,22  | 28  | 8,31  | 10  | 7,74  | 22  | 1,08  | 7   | 0,00  | 14  | 2,96  | 28        | 21,31      | 4           |
| [AmbiGen](https://github.com/swat-lab-optimization/UAV-Testing-Competition)           | [1-4]      | 30  | 2,82  | 46  | 2,00  | 36  | 0,86  | 65  | 1,22  | 151 | 10,07 | 30  | 1,51  | 26,00     | 18,47      | 5           |
| [Surrealist](https://github.com/skhatiri/Surrealist)                                  | 2          | 10  | 5,03  | 1   | 0,00  | 10  | 0,00  | 1   | 0,75  | 19  | 3,88  | 2   | 0,00  | 34        | 9,67       | 6           |
| [TAIiST](https://github.com/Trusted-AI-in-System-Test/UAV-Testing-Competition)        | [2-4]      | 7   | 0,81  | 13  | 0,00  | 6   | 0,43  | 11  | 1,57  | 29  | 1,67  | 22  | 1,33  | 33        | 5,81       | 7           |
| **SUM**                                                                               |            | 215 | 34,40 | 303 | 48,39 | 311 | 18,51 | 263 | 18,91 | 530 | 48,67 | 305 | 33,19 |           |            |             |

## Important Updates (8.12.2023)

- **Due to multiple requests, we are implementing a grace period. You can update your submissions until 10.12.2023 (AoE).**
- **In the meantime, we are checking if we can run and evaluate your submitted codes. We will let you know if we got problems and ask for an update if needed.**
- **A small update to [testcase.py](https://github.com/skhatiri/UAV-Testing-Competition/commit/50e3e983ef98f1be4a550922fc23b68b35740a4b) will also help some of you that had problems integrating latest changes.**
- **To easily set the simulation timeout, you can use the following command to run your test generator:**

  `SIMULATION_TIMEOUT=300 python3 cli.py generate case_studies/mission1.yaml 100`

## Important Updates (4.12.2023)

- **Recent [Aerialist update](https://github.com/skhatiri/Aerialist/pull/14) lets you set a timeout period for simulations. After timeout is reached, simulation is aborted and you can access the flight log and plot of the unfinished test.**
- **This can help with identifying the test cases that take too much time to finish, and before you were not able to check the logs to understand why.**

## Important Updates (28.11.2023)

- **Sumbmission Deadline is extended to 7.12.2023 (AoE).**
- **Make Sure to follow the below requirements in your submission.**

## Important Updates (21.11.2023)

- **Submission requirements and guideline is now available. [Check Here](./docs/submission.md).**
- **Make sure to review and integrate the recent updates to the [code samples](./snippets/) into your code where needed.**
- **Make sure to pull/install the latest version of [Aerialist](https://github.com/skhatiri/Aerialist).**
