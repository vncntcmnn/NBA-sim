import pandas as pd
import random as rnd
import numpy as np


class GameNaive:
    """Game class to play a game between two teams. Scores for each one are sampled
    from a normal distribution using their past season scores.

    Args:
        teams_update (bool): Either to update the teams scores after a game or not.
    """

    HADVG = 1

    def __init__(self, teams_update=True):
        self.teams_update = teams_update

    def play(self, team1, team2, return_pts=False):
        """Simulate a game between two teams, sampling scores from normal distribution.

        Args:
            team1 (Team): Home team object.
            team2 (Team): Away team object.
            return_pts (bool, optional): To return scores for each team. Defaults to False.

        Returns:
            int: 1 if first team wins else 0.
        """
        t1 = (
            rnd.gauss(team1.features["pts_avg"], team1.features["pts_std"])
            + rnd.gauss(team2.features["opp_avg"], team2.features["opp_std"])
        ) / 2
        t2 = (
            rnd.gauss(team2.features["pts_avg"], team2.features["pts_std"])
            + rnd.gauss(team1.features["opp_avg"], team1.features["opp_std"])
        ) / 2
        t1 = int(round(t1)) + self.HADVG
        t2 = int(round(t2))
        if t1 != t2:
            if self.teams_update:
                team1.update_last_game(t1, t2)
                team2.update_last_game(t2, t1)
            res = 1 if t1 > t2 else 0
            if return_pts:
                return res, t1, t2
            else:
                return res
        else:
            return self.play(team1, team2, return_pts=return_pts)
