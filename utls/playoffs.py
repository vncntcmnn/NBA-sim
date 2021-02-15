import pandas as pd
import numpy as np
import scipy as sc


def get_wins_by_team(df):
    """From a games DataFrame calendar with results, compute the total number of
    wins by team.

    Args:
        df (pd.DataFrame): DataFrame calendar with results, ylabel = 1 if home wins,
        else 0.

    Returns:
        pd.DataFrame: Number of wins by team.
    """
    df = df.copy()
    home_wins = df.loc[df["ylabel"] == 1, :]
    away_wins = df.loc[df["ylabel"] == 0, :]
    teams_home_wins = home_wins.groupby(["home_name"]).size().reset_index(name="counts")
    teams_away_wins = away_wins.groupby(["away_name"]).size().reset_index(name="counts")
    teams_home_wins.columns = ["team", "counts"]
    teams_away_wins.columns = ["team", "counts"]
    teams_win = pd.concat([teams_home_wins, teams_away_wins])
    teams_win = teams_win.groupby(["team"], as_index=False).sum("counts")
    return teams_win


def better_winning_pctg_tied_teams(games_calendar, tie_teams):
    """Filter the tie_teams to keep only the highest winning percentages between the
    tie teams if possible, otherwise return the original tie_teams.

    Args:
        games_calendar (pd.DataFrame): Calendar with games results of the regular season.
        tie_teams (list(str)): List of the tied teams

    Returns:
        list(str): Top teams among the tied ones if some have a higher result than other.
        Otherwise, return the original tie_teams.
    """
    scores = []
    for team in tie_teams:
        wins = games_calendar.loc[
            (games_calendar["home_name"] == team) & (games_calendar["ylabel"] == 1)
        ].shape[0]
        wins += games_calendar.loc[
            (games_calendar["away_name"] == team) & (games_calendar["ylabel"] == 0)
        ].shape[0]
        if games_calendar.shape[0] > 0:
            scores.append([team, round(wins / games_calendar.shape[0], 2)])
        else:
            scores.append([team, round(wins, 2)])
    max_pctg = max([x[1] for x in scores])
    filtered = [x[0] for x in scores if x[1] == max_pctg]
    return filtered


def division_winners(df_conference, games_calendar, tie_teams):
    """Filter the tie_teams to keep only the division winners in games_calender, if
    possible, otherwise return the original tie_teams.

    Args:
        df_conference (pd.DataFrame): DataFrame of wins by teams.
        games_calendar (pd.DataFrame): Calendar with games results of the regular season.
        tie_teams (list(str)): List of the tied teams

    Returns:
        list(str): Top teams among the tied ones if at least one but not all teams, is
        a division winner. Otherwise, return the original tie_teams.
    """
    div_winners = [False for _ in tie_teams]
    for i, team in enumerate(tie_teams):
        division = df_conference.loc[df_conference["team"] == team, "division"].values[
            0
        ]
        division = df_conference.loc[
            df_conference["division"] == division, :
        ].sort_values(by=["counts"], ascending=False)
        div_win = division["team"].values[0] == team
        div_winners[i] = div_win
    fitlered = [tie_teams[i] for i, win in enumerate(div_winners) if win]
    if (sum(div_winners) == len(tie_teams)) or (sum(div_winners) == 0):
        return tie_teams
    else:
        return fitlered


def tie_two_teams(
    df_conference_full, df_conference_filtered, games_calendar, conference, tie_teams
):
    """Tie three teams or more using NBA playoffs bracket tie breaker rules.

    Args:
        df_conference_full (pd.DataFrame): DataFrame of wins by teams, full conference.
        df_conference_filtered (pd.DataFrame): DataFrame of wins by teams, only the tied teams.
        games_calendar (pd.DataFrame): Calendar with games results of the regular season.
        conference (str): Conference of the teams.
        tie_teams (list(str)): List of the tied teams

    Returns:
        str: Top team among the tied ones.
    """
    # Better winning percentage in games against each other.
    tie_calendar = games_calendar.loc[
        (
            games_calendar["home_name"].isin(tie_teams)
            & games_calendar["away_name"].isin(tie_teams)
        ),
        :,
    ]
    filtered = better_winning_pctg_tied_teams(tie_calendar, tie_teams)
    if len(filtered) == 1:
        return filtered[0]
    else:
        tie_teams = filtered
    # Division winner (this criterion is applied regardless of whether the tied teams are in the same division).
    filtered = division_winners(df_conference_full, games_calendar, tie_teams)
    if len(filtered) == 1:
        return filtered[0]
    else:
        tie_teams = filtered
    # Better winning percentage against teams in own division (only if tied teams are in same division).
    # Check same division
    divs = []
    for team in tie_teams:
        div = df_conference_filtered.loc[
            df_conference_filtered["team"] == tie_teams[0], "division"
        ].values[0]
        divs.append(div)
    if divs:
        if all([x == divs[0] for x in divs]):
            div_teams = df_conference_filtered.loc[
                df_conference_filtered["division"] == divs[0], "team"
            ].values
            tie_calendar = games_calendar.loc[
                (
                    games_calendar["home_name"].isin(div_teams)
                    & games_calendar["away_name"].isin(div_teams)
                ),
                :,
            ]
            filtered = better_winning_pctg_tied_teams(tie_calendar, tie_teams)
            if len(filtered) == 1:
                return filtered[0]
            else:
                tie_teams = filtered
    # Better winning percentage against teams in own conference.
    conf_teams = df_conference_filtered.loc[
        df_conference_filtered["division"] == conference, "team"
    ].values
    tie_calendar = games_calendar.loc[
        (
            games_calendar["home_name"].isin(conf_teams)
            & games_calendar["away_name"].isin(conf_teams)
        ),
        :,
    ]
    filtered = better_winning_pctg_tied_teams(tie_calendar, tie_teams)
    if len(filtered) == 1:
        return filtered[0]
    else:
        tie_teams = filtered
    # Not implemented: Shuffle
    np.random.shuffle(tie_teams)
    tie_teams = list(tie_teams)
    return tie_teams[0]


def tie_three_teams(
    df_conference_full, df_conference_filtered, games_calendar, conference, tie_teams
):
    """Tie three teams or more using NBA playoffs bracket tie breaker rules.

    Args:
        df_conference_full (pd.DataFrame): DataFrame of wins by teams, full conference.
        df_conference_filtered (pd.DataFrame): DataFrame of wins by teams, only the tied teams.
        games_calendar (pd.DataFrame): Calendar with games results of the regular season.
        conference (str): Conference of the teams.
        tie_teams (list(str)): List of the tied teams

    Returns:
        str: Top team among the tied ones.
    """
    # Division winner (this criterion is applied regardless of whether the tied teams are in the same division).
    filtered = division_winners(df_conference_full, games_calendar, tie_teams)
    if len(filtered) == 2:
        tie_two_teams(
            df_conference_full,
            df_conference_filtered,
            games_calendar,
            conference,
            filtered,
        )
    if len(filtered) == 1:
        return filtered[0]
    else:
        tie_teams = filtered
    # Better winning percentage in all games among the tied teams.
    tie_calendar = games_calendar.loc[
        (
            games_calendar["home_name"].isin(tie_teams)
            & games_calendar["away_name"].isin(tie_teams)
        ),
        :,
    ]
    filtered = better_winning_pctg_tied_teams(tie_calendar, tie_teams)
    if len(filtered) == 2:
        tie_two_teams(
            df_conference_full,
            df_conference_filtered,
            games_calendar,
            conference,
            filtered,
        )
    if len(filtered) == 1:
        return filtered[0]
    else:
        tie_teams = filtered
    # Better winning percentage against teams in own division (only if all tied teams are in same division).
    # Check same division
    divs = []
    for team in tie_teams:
        div = df_conference_filtered.loc[
            df_conference_filtered["team"] == tie_teams[0], "division"
        ].values[0]
        divs.append(div)
    if all([x == divs[0] for x in divs]):
        div_teams = df_conference_filtered.loc[
            df_conference_filtered["division"] == div, "team"
        ].values
        tie_calendar = games_calendar.loc[
            (
                games_calendar["home_name"].isin(div_teams)
                & games_calendar["away_name"].isin(div_teams)
            ),
            :,
        ]
        filtered = better_winning_pctg_tied_teams(tie_calendar, tie_teams)
        if len(filtered) == 2:
            tie_two_teams(
                df_conference_full,
                df_conference_filtered,
                games_calendar,
                conference,
                filtered,
            )
        if len(filtered) == 1:
            return filtered[0]
        else:
            tie_teams = filtered
    # Better winning percentage against teams in own conference.
    conf_teams = df_conference_filtered.loc[
        df_conference_filtered["division"] == conference, "team"
    ].values
    tie_calendar = games_calendar.loc[
        (
            games_calendar["home_name"].isin(conf_teams)
            & games_calendar["away_name"].isin(conf_teams)
        ),
        :,
    ]
    filtered = better_winning_pctg_tied_teams(tie_calendar, tie_teams)
    if len(filtered) == 2:
        tie_two_teams(
            df_conference_full,
            df_conference_filtered,
            games_calendar,
            conference,
            filtered,
        )
    if len(filtered) == 1:
        return filtered[0]
    else:
        tie_teams = filtered
    # Not implemented: Shuffle
    np.random.shuffle(tie_teams)
    tie_teams = list(tie_teams)
    return tie_teams[0]


def get_top_eight_conference(df_wins, games_calendar, conference):
    """Get the top eight teams of the conference, from a pd.DataFrame with the number
    of wins by team.

    Args:
        df_wins (pd.DataFrame): DataFrame of wins by team.
        games_calendar (pd.DataFrame): DataFrames of games with results during the regular season.
        conference (str): Conference to process

    Returns:
        list(str): List of the top eight ranked teams who will play the playoffs.
    """
    # for each conference we get the best teams according to win/loss
    # The tie-break criteria for playoff seeding and home-court advantage
    # have also changed; head-to-head results between the tied teams is the
    # first tie-breaker, and whether a team won its division championship is
    # the second tie-breaker.
    df_wins = df_wins.loc[df_wins["conference"] == conference]
    df_wins = df_wins.sort_values(by=["counts"], ascending=False).reset_index(drop=True)
    df_conference_full = df_wins.copy()  # Used to check division winners
    ranks = []
    while len(ranks) < 8:
        # Check if tie
        top_score = df_wins["counts"][0]
        tie_teams = df_wins.loc[df_wins["counts"] == top_score, "team"].values
        if len(tie_teams) == 1:
            team = df_wins["team"][0]
        elif len(tie_teams) == 2:
            team = tie_two_teams(
                df_conference_full, df_wins, games_calendar, conference, tie_teams
            )
        else:
            team = tie_three_teams(
                df_conference_full, df_wins, games_calendar, conference, tie_teams
            )
        ranks.append(team)
        df_wins = df_wins.loc[df_wins["team"] != team, :].reset_index(drop=True)
    return ranks


def get_playoffs(df_calendar_results, df_teams_info):
    """Get the teams who will play the playoffs from a regular season calendar with
    results.

    Args:
        df_calendar_results (pd.DataFrame): DataFrame of the results.
        df_teams_info (pd.DataFrame): Teams info for conference and division.

    Returns:
        dict: Dictionnary of k: v with k the conference and v the ranked teams list to
        play the playoffs.
    """
    team_wins = get_wins_by_team(df_calendar_results)
    team_wins = team_wins.merge(df_teams_info, left_on="team", right_on="team")
    playoffs = {}
    for conf in team_wins["conference"].unique():
        ranks = get_top_eight_conference(team_wins, df_calendar_results, conf)
        playoffs[conf] = ranks
    return playoffs, team_wins
