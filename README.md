# NBA season + playoffs simulator

This project aims to simulate a NBA season (or playoffs only) to generate probability of winning the championship for each team. A game is played between two teams with points scored for each one being sampled from past season data using a simple normal distribution.

## Usage

Project made with Python 3.8.5.

From the project directory:

1. Install the requirements:

    ```
    $ pip install -r requirements
    ```
2. Run a simulation:

    ```
    $ python main.py --save n_iter season_data season_to_play playoffs_only_bool
    ```

    * **--save** (option): Either or not to save the results in the data folder as a csv file.
    * **n_iter** (int): Number of times to play the simulation to get the probabilities. Default 1000.
    * **season_data** (int): Which past data to use to play the simulation. Choices: 2016, 2017, 2018.
    * **season_to_play** (int): Which season to play. Choices: 2016, 2017, 2018.
    * **playoffs_only** (bool): Play the full season or only the playoffs. If `True`, `season_data` and `season_to_play` can be the same (results should be better). In addition, if `True`, `n_iter` can be higher as there are less games to play.

    ### Examples:

    To get season 2018 probabilities before the start of the season:
    ```
    $ python main.py 10000 2017 2018 False
    ```

    To get season 2018 probabilities at the end of the regular season:
    ```
    $ python main.py 100000 2018 2018 True
    ```

## Output example

```
Team Name                 Number of wins    Probability of winning    Odd 100% RTP    Odd 85% RTP
----------------------  ----------------  ------------------------  --------------  -------------
portland trail blazers                 4                      0.04           25             21.25
chicago bulls                          0                      0
los angeles clippers                   2                      0.02           50             42.5
milwaukee bucks                        8                      0.08           12.5           10.62
brooklyn nets                          4                      0.04           25             21.25
```