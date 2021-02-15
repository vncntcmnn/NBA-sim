import pandas as pd
import numpy as np
from tqdm import tqdm
from .teams import TeamsNaive
from .tournament import Playoffs
from .season import Season
from .game import GameNaive
from utls.playoffs import get_playoffs
from utls.regular_season_calendar import construct_calendar


class NBASim:
    """NBA simulation using simple sample of the teams scores from their points they
    scored during season_data. Scores are sampled using normal distribution.
    The full NBA season is played according to the real calendar

    Args:
        data_path (str): Path to the necessary data (Ref Games)
        season_to_play (int): Season to play.
        season_data (int): Season data to use as scores from which to sample
        (should be lower than season_to_play, or equal to if playoffs_only is True).
        method (str, optional): Sampling method to use (only naive atm.). Defaults to 'naive'.
        playoffs_only (bool, optional): Playing only the playoffs and use the real playoffs teams.
        Defaults to False.
    """

    def __init__(
        self,
        data_path,
        season_to_play,
        season_data,
        method="naive",
        playoffs_only=False,
    ):

        self.data_path = data_path
        self.season_to_play = season_to_play
        self.season_data = season_data
        self.method = method
        self.playoffs_only = playoffs_only
        df_games = pd.read_parquet(f"{data_path}/BasketRefGames.snappy.parquet")
        self.teams_info = pd.read_csv(f"{data_path}/teams_info.csv")
        self.season_calendar = construct_calendar(df_games, self.season_to_play)
        self.initialize()

    def initialize(self):
        """Initialize the teams and season according to the method and playoffs_only values."""
        if self.method == "naive":
            self.teams = TeamsNaive(
                self.data_path, self.season_to_play, self.season_data
            )
            self.gsim = GameNaive(False)
            if not self.playoffs_only:
                self.season = Season(self.season_calendar, self.teams_info, self.gsim)

    def play_simulation(self, n_iter=1000):
        """Run the simulation n_iter times to get probabilities of winning the championship.

        Args:
            n_iter (int, optional): Number of times to run the simulation. Defaults to 1000.
            verbose (bool, optional): Print the results if True, otherwise return it. Defaults to True.

        Returns:
            (dict): Dictionnary with team: number of time it won the championship.
        """
        final_wins = final_wins = {t: 0 for t in self.teams.dteams.keys()}
        season_teams_ranked, _ = get_playoffs(self.season_calendar, self.teams_info)
        for i in tqdm(range(n_iter)):
            if not self.playoffs_only:
                self.season.play_regular_season(self.teams)
                season_teams_ranked = self.season.playoffs_teams_ranked

            playoffs_sim = Playoffs(season_teams_ranked, self.gsim)
            winner_playoff = playoffs_sim.get_winner(self.teams)

            final_wins[winner_playoff] += 1

        return final_wins
