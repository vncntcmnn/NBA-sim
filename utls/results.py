from tabulate import tabulate
import pandas as pd


def calculate_win_rate(wins, games):
    return wins / games


def calculate_odd(wr, return_to_player=0.85):
    if wr > 0:
        return round(1 / wr * return_to_player, 2)
    else:
        return None


def process_results(dres, n_iter, save_path=None):
    """Helper function to format the results of the simulations and print it.
    Additionnaly results can be saved in csv file.

    Args:
        dres (dict): Dictionnary of results with team_name: number_of_wins as k: v.
        n_iter (int): Number of iterations the simulation has ben run.
    """
    lres = [[k, v] for k, v in dres.items()]
    names = [x[0] for x in lres]
    wins = [x[1] for x in lres]
    wr = [calculate_win_rate(x[1], n_iter) for x in lres]
    odds = [calculate_odd(x, 1.0) for x in wr]
    odds_rtp = [calculate_odd(x, 0.85) for x in wr]
    table = list(zip(names, wins, wr, odds, odds_rtp))
    headers = [
        "Team Name",
        "Number of wins",
        "Probability of winning",
        "Odd 100% RTP",
        "Odd 85% RTP",
    ]
    print(tabulate(table, headers=headers))
    if save_path:
        df = pd.DataFrame(table, columns=headers)
        df.to_csv(save_path, index=False)
