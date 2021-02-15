K = 20
HOME_ADVANTAGE = 100


def elo_pred(elo1, elo2):
    return 1.0 / (10.0 ** (-(elo1 - elo2) / 400.0) + 1.0)


def expected_margin(elo_diff):
    return 7.5 + 0.006 * elo_diff


def elo_update(w_elo, l_elo, margin):
    elo_diff = w_elo - l_elo
    pred = elo_pred(w_elo, l_elo)
    mult = ((margin + 3.0) ** 0.8) / expected_margin(elo_diff)
    update = K * mult * (1 - pred)
    return (pred, update)
