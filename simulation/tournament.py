import numpy as np


class Tournament:
    """Tournament class, play players two by two like in first three
    rounds of playoffs.

    Args:
        games_order (list(str)): List of the teams to play, ordered by games.
        For example ['0', '3', '1', '2'] means that the '0' player will face the '3'
        and '1' and '2' will be faced. Then winner of each one will play against
        each other.
                    0 \\
                        W1 \\
                    3 /     \\
                             W
                    1 \     /
                        W2 /
                    2 /
        game_sim (GameNaive): Game to make the teams play against each other.
    """

    def __init__(self, games_order, game_sim):
        self.games_order = games_order
        self.gsim = game_sim

    def _duel(self, i, teams):
        """Play a duel between two teams.

        Args:
            i (int): Index of the first name of the game to play, indices being
            processed two by two.
            teams (TeamsNaive): Object containing the teams.

        Returns:
            int: The loser of the game to be removed from the tournament.
        """
        first_name = self.games_order[i]
        second_name = self.games_order[i + 1]
        first = second = 0
        while (first < 4) and (second < 4):
            if first + second in [0, 1, 4, 6]:
                res = self.gsim.play(
                    teams.dteams[first_name], teams.dteams[second_name], return_pts=True
                )
            else:
                res = self.gsim.play(
                    teams.dteams[second_name], teams.dteams[first_name], return_pts=True
                )
            if res[0]:
                first += 1
            else:
                second += 1
        if first == 4:
            return i + 1
        else:
            return i

    def play(self, teams):
        """Play the tournament with the teams.

        Args:
            teams (TeamsNaive): Teams object containing the players of the tournament.

        Returns:
            str: Name of the winner.
        """
        while len(self.games_order) > 1:
            loser = []
            for i in range(0, len(self.games_order), 2):
                loses_duel = 0
                loses_duel = self._duel(i, teams)
                loser.append(loses_duel)
            for i in loser[::-1]:
                self.games_order.pop(i)
        return self.games_order[0]


class ConferenceTournament:
    """Conference tournament to simulate first three rounds of the playoffs.

    Args:
        lplayers (list(str)): List of the teams ranked by the end of the regular
        season. First one being the top one in conference.
        game_sim (GameNaive): Game to make the teams play against each other.
    """

    def __init__(self, lplayers, game_sim):
        self.start_games_order = [0, 7, 3, 4, 2, 5, 1, 6]
        # Reorder the team names according to playoffs games order.
        self.lplayers = [lplayers[x] for x in self.start_games_order]
        self.tournament = Tournament(self.lplayers, game_sim)

    def get_winner(self, teams):
        """Play the conference tournament with the teams.

        Args:
            teams (TeamsNaive): Teams object containing the players of the tournament.

        Returns:
            str: Name of the winner.
        """
        return self.tournament.play(teams)


class FinalTournament:
    """Conference tournament to simulate final round of the playoffs.

    Args:
        lplayers (list(str)): List of the teams 'ranked' by the end of the first three
        rounds. First one being the winner of the west conference playoffs.
        game_sim (GameNaive): Game to make the teams play against each other.
    """

    def __init__(self, lplayers, game_sim):
        self.start_games_order = [0, 1]
        self.lplayers = [lplayers[x] for x in self.start_games_order]
        self.tournament = Tournament(self.lplayers, game_sim)

    def get_winner(self, teams):
        """Play the conference tournament with the teams.

        Args:
            teams (TeamsNaive): Teams object containing the players of the tournament.

        Returns:
            str: Name of the winner.
        """
        return self.tournament.play(teams)


class Playoffs:
    """Playoffs tournament to simulate final phase of the NBA season.

    Args:
        season_team_ranked (dict): Dictionnary of k: v with k the conference and v the
        ranked teams list to play the playoffs. First one of a list being the top one
        of the conference playoffs.
        game_sim (GameNaive): Game to make the teams play against each other.
    """

    def __init__(self, season_teams_ranked, game_sim):
        self.season_teams_ranked = season_teams_ranked
        self.gsim = game_sim

    def get_winner(self, teams):
        """Play the playoffs tournament with the teams.

        Args:
            teams (TeamsNaive): Teams object containing the players of the tournament.

        Returns:
            str: Name of the winner.
        """
        # Play each conf playoffs
        playoff_ouest = ConferenceTournament(
            self.season_teams_ranked["ouest"], self.gsim
        )
        winner_ouest = playoff_ouest.get_winner(teams)
        playoff_est = ConferenceTournament(self.season_teams_ranked["est"], self.gsim)
        winner_est = playoff_est.get_winner(teams)
        # Play final
        final_players = [winner_ouest, winner_est]
        season_final = FinalTournament(final_players, self.gsim)
        winner_playoff = season_final.get_winner(teams)
        return winner_playoff
