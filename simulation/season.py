import pandas as pd
import numpy as np
from utls.playoffs import get_playoffs


class Season:
    """Season object to play all games of a regular season.

    Args:
        games_calendar (pd.DataFrame): Games calendar, will be used to simulate the games.
        teams_info (pd.DataFrame): Contains teams information regarding division and conference.
        game_sim (GameNaive): A game object which will be used to performa a
        game simulation.
    """

    def __init__(self, games_calendar, teams_info, game_sim):
        self.regular_season_calendar = games_calendar
        self.teams_info = teams_info
        self.gsim = game_sim

    def _play_regular_season(self, teams):
        """Helper function to run the regular season simulation.

        Args:
            teams (Teams): Teams object storing the different teams of the season to play.
        """
        games_calendar = self.regular_season_calendar.copy()
        cols = [
            "game_id",
            "season",
            "away_id",
            "home_id",
            "away_name",
            "home_name",
            "away_ftscore",
            "home_ftscore",
            "ylabel",
        ]
        games_calendar = games_calendar[cols]
        games_calendar[["home_ftscore", "away_ftscore", "ylabel"]] = np.zeros(
            (games_calendar.shape[0], 3)
        )

        games_to_play = games_calendar[["home_name", "away_name"]].values
        games_results = []
        for g in games_to_play:
            res = self.gsim.play(
                teams.dteams[g[0]], teams.dteams[g[1]], return_pts=True
            )
            games_results.append(list(res))

        games_calendar[["ylabel", "home_ftscore", "away_ftscore"]] = np.array(
            games_results
        )
        self.sim_season_calendar = games_calendar

    def play_regular_season(self, teams):
        """Run the regular season simulation.

        Args:
            teams (Teams): Teams object storing the different teams of the season to play.
        """
        self._play_regular_season(teams)
        self.playoffs_teams_ranked, self.season_wins = get_playoffs(
            self.sim_season_calendar, self.teams_info
        )
