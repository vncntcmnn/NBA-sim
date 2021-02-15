import pandas as pd
import numpy as np


def add_pts(pts, new):
    return np.concatenate((pts[1:], [new]))


class TeamNaive:
    """Team object to store the scores of the past season.

    Args:
        name (str): Name of the team.
        pts (list(int)): Points scored by the team.
        opp_pts (list(int)): Points scored by the opponents of the team.
    """

    def __init__(self, name, pts, opp_pts):

        self.name = name
        self.pts = pts
        self.opp_pts = opp_pts
        self.get_features()

    def get_features(self):
        """Compute the features of the team from its scores."""
        self.features = {
            "pts_avg": np.mean(self.pts),
            "pts_std": np.std(self.pts),
            "opp_avg": np.mean(self.opp_pts),
            "opp_std": np.std(self.opp_pts),
        }

    def update_last_game(self, pts, opp_pts):
        """Update the teams scores with the ones from the last game.

        Args:
            pts (int): Points scored.
            opp_pts (int): Points scored by the opponent.
        """
        self.pts = add_pts(self.pts, pts)
        self.opp_pts = add_pts(self.opp_pts, opp_pts)
        self.get_features()


class TeamsNaive:
    """Object to store all the teams who will play a season or playoffs.

    Args:
        data_path (str): Path to the data folder.
        season_to_play (int): Season to play.
        season_data (int): Season data to use as past scores.
        playoffs_only (bool, optional): If they play only the playoffs. Defaults to False.
    """

    def __init__(self, data_path, season_to_play, season_data, playoffs_only=False):
        self.data_path = data_path
        self.season_to_play = season_to_play
        self.season_data = season_data
        self.playoffs_only = playoffs_only
        self.games_results = pd.read_parquet(
            f"{self.data_path}/BasketRefGames.snappy.parquet"
        )
        self.teams_info = pd.read_csv(f"{self.data_path}/teams_info.csv")
        self.teams_names = self._get_teams_from_season(self.season_to_play)
        self.teams_names_previous = self._get_teams_from_season(self.season_data)
        self.construct_teams()

    def _get_teams_from_season(self, season):
        """Extract teams name from a specific season.

        Args:
            season ([type]): Season from which to extract the teams.

        Returns:
            np.array(str): Teams name.
        """
        return self.games_results.loc[
            self.games_results["season"] == season, "away_name"
        ].unique()

    def check_in_both_seasons(self, verbose=False):
        check_teams_in_both = all(
            [x in self.teams_names_previous for x in self.teams_names]
        )
        self.check_teams_in_both = check_teams_in_both
        if verbose:
            if self.check_teams_in_both:
                print("Teams in actual and previous seasons as expected.")
            else:
                print("Teams in actual not all in previous seasons, not handled.")

    def _team_season_scores(self, season, team):
        """Extract points scored by a team and its opponents.

        Args:
            season (int): Season from which to extract the data.
            team (str): Team to process.

        Returns:
            tuple(int, int): Points scored by the team, points scored by its opponents
        """
        if self.playoffs_only and (self.season_to_play == self.season_data):
            games_results = self.games_results.loc[
                self.games_results["season"] == self.season_to_play
            ]
            if self.season_to_play != 2011:
                games_results = games_results.iloc[:1230]
            else:
                games_results = games_results.iloc[:990]
        season_filter = self.games_results["season"] == season
        team_away_filter = self.games_results["away_name"] == team
        team_home_filter = self.games_results["home_name"] == team
        df_away = self.games_results.loc[season_filter & team_away_filter, :]
        df_home = self.games_results.loc[season_filter & team_home_filter, :]
        away_pts = df_away["away_ftscore"].values
        home_pts = df_home["home_ftscore"].values
        away_ptsr = df_away["home_ftscore"].values
        home_ptsr = df_home["away_ftscore"].values
        return np.concatenate((away_pts, home_pts)), np.concatenate(
            (away_ptsr, home_ptsr)
        )

    def _teams_data(self, season):
        """From a df of all games, extract for each team its pts scored and pts against them"""
        season_scores = {}
        for t in self.teams_names:
            pts = self._team_season_scores(season, t)
            season_scores[t] = pts
        return season_scores

    def construct_teams(self):
        """Construct the teams and store them in self.dteams"""
        past_season_scores = self._teams_data(self.season_to_play)
        self.dteams = {
            t: TeamNaive(t, *past_season_scores[t]) for t in self.teams_names
        }
