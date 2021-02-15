import pandas as pd


def construct_calendar(df_games, season):
    """Construct/filter a calendar of games to get only the regular season games.

    Args:
        df_games (pd.DataFrame): Table of games.
        season (int): Season to use as filter.

    Returns:
        pd.DataFrame: Regular season games.
    """
    season_games = df_games.loc[df_games["season"] == season, :].sort_values(
        by=["game_id"]
    )
    if season != 2011:
        regular_season_calendar = season_games.iloc[:1230]
    else:
        regular_season_calendar = season_games.iloc[:1230]
    return regular_season_calendar
