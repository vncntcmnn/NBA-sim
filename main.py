import os
import argparse
import random as rnd
import numpy as np
from pathlib import Path
from simulation.nbasim import NBASim
from utls.results import process_results


SEED = 42


def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def boolean_string(s):
    if s not in {"False", "True"}:
        raise ValueError("Not a valid boolean string")
    return s == "True"


def check_parameters(n_iter, season_to_play, season_data, playoffs_only):
    ok = True
    if season_data > season_to_play:
        print(
            "Season data has to be less than season to play. It can be equals to season to"
            " play only if playoffs_only is True."
        )
        ok = False
    if (season_data == season_to_play) and (not playoffs_only):
        print(
            "When seasons are the same, playoffs_only has to be True. Then only the playoffs"
            " are run using current year regular season data."
        )
        ok = False
    return ok


if __name__ == "__main__":

    data_path = Path(__file__).parent / "data"

    parser = argparse.ArgumentParser(
        description="This performs simulation of NBA full season or playoffs only to generate "
        "probability of winning the championship. Teams scores are generated based on the "
        'season_data year and sampled from Normal distribution (hence the "naive" name).'
    )
    parser.add_argument(
        "n_iter",
        type=check_positive,
        default=100,
        help="Number of simulations run to get probabilities.",
    )
    parser.add_argument(
        "season_to_play",
        type=int,
        choices=[2016, 2017, 2018],
        default=2018,
        help="Season to simulate.",
    )
    parser.add_argument(
        "season_data",
        type=int,
        choices=[2016, 2017, 2018],
        default=2017,
        help="Season data to use to perform the simulations.",
    )
    parser.add_argument(
        "playoffs_only",
        type=boolean_string,
        default=False,
        help="Run only the playoffs. Season data and season to play can be the same if playoffs_only"
        "is True, only regular season data will be used.",
    )
    parser.add_argument(
        "--save", help="Save the results in the data folder.", action="store_true"
    )

    args = parser.parse_args()
    check = check_parameters(
        args.n_iter, args.season_to_play, args.season_data, args.playoffs_only
    )

    if check:
        rnd.seed(SEED)
        np.random.seed(SEED)
        print(
            f"Starting {args.n_iter} simulations to get probabilities of winning the championship:"
        )
        sim = NBASim(
            data_path,
            args.season_to_play,
            args.season_data,
            playoffs_only=args.playoffs_only,
        )
        results = sim.play_simulation(args.n_iter)
        if args.save:
            save_path = (
                data_path
                / f"n_iter_{args.n_iter}_season_to_play_{args.season_to_play}_season_data_"
                f"{args.season_data}_playoffs_only_{args.playoffs_only}.csv"
            )
        else:
            save_path = None
        process_results(results, args.n_iter, save_path=save_path)
