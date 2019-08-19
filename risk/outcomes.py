#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-15

Functions for computing battle outcome probabilities in the board game Risk.
"""
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import product
import argparse
import random

from risk import argdefs
from risk import printing
from risk import utils


loss_probs_6_6 = {(3, 2): {(0, 2): 2890 / 7776,
                           (2, 0): 2275 / 7776,
                           (1, 1): 2611 / 7776},
                  (3, 1): {(0, 1): 855 / 1296,
                           (1, 0): 441 / 1296},
                  (2, 2): {(0, 2): 295 / 1296,
                           (2, 0): 581 / 1296,
                           (1, 1): 420 / 1296},
                  (2, 1): {(0, 1): 125 / 216,
                           (1, 0): 91 / 216},
                  (1, 2): {(0, 1): 55 / 216,
                           (1, 0): 161 / 216},
                  (1, 1): {(0, 1): 15 / 36,
                           (1, 0): 21 / 36}}


@lru_cache(maxsize=None)
def calc_loss_probs(a_sides, d_sides):
    """Returns probability of various loss combinations.

    Args:
        a_sides (int): Number of sides on attacking dice
        d_sides (int): Number of sides on defending dice

    Returns:
        (dict) Probabilities of loss combinations. Keys are (# attack dice,
        # defense dice). Values are dicts whose keys are (# attack losses, #
        # defense losses) and values are the probability of that outcome.
    """
    if a_sides == 6 and d_sides == 6:
        return loss_probs_6_6

    loss_probs = dict()
    for a_rolls, d_rolls in product(range(1, 4), range(1, 3)):
        loss_probs_rolls = defaultdict(int)

        # Generate all combos.
        a_roll_vals = list(range(1, a_sides + 1))
        d_roll_vals = list(range(1, d_sides + 1))
        iters = [a_roll_vals] * a_rolls + [d_roll_vals] * d_rolls
        combos = list(product(*iters))

        # Match highest rolls and determine losses.
        n = len(combos)
        total_losses = min(a_rolls, d_rolls)
        for combo in combos:
            a_vals = sorted(combo[:a_rolls], reverse=True)
            d_vals = sorted(combo[a_rolls:], reverse=True)
            a_losses = sum([1 for a, d in zip(a_vals, d_vals) if a <= d])
            loss_probs_rolls[(a_losses, total_losses - a_losses)] += 1 / n

        loss_probs[(a_rolls, d_rolls)] = loss_probs_rolls
    return loss_probs


def calc_battle_probs(a, d, a_sides=6, d_sides=6, stop=1):
    """Get probability of all outcomes.

    Args:
        a (int): Number of troops on attacking territory
        d (list or int): Number of troops on defending territory. Use multiple
            values for multiple territories
        a_sides (list or int): Number of sides on attack dice. Use list of
            values for multiple territories or single value to represent all
            territories
        d_sides (list or int): Number of sides on defense dice. Use list of
            values for multiple territories or single value to represent all
            territories
        stop (int): When attack has this many troops or fewer, stop

    Returns:
        (dict) Key is tuple of final attack and defense troops, and
        values are probabilites of those outcomes
    """
    fixed = utils.fix_args(a, d, a_sides, d_sides, stop)
    d_list, a_sides_list, d_sides_list = fixed

    @lru_cache(maxsize=None)
    def recur_helper(t, a, d):
        """New variable t keeps track of territory index."""
        if a <= stop or d == 0:
            return {(t, a, d): 1}  # outcome has prob = 1 in absorbing state

        # Compute probabilities of next roll outcomes.
        a_sides, d_sides = a_sides_list[t], d_sides_list[t]
        loss_key = min(3, a - 1), min(2, d)
        loss_probs = calc_loss_probs(a_sides, d_sides)[loss_key]
        probs_list = list()
        for (a_loss, d_loss), p2 in loss_probs.items():
            a2, d2 = a - a_loss, d - d_loss  # new attack and defense counts

            if d2 == 0 and a2 > stop and t < len(d_list) - 1:
                # Move on to next territory.
                t2 = t + 1
                a2, d2 = a2 - 1, d_list[t2]
            else:
                t2 = t
            new = recur_helper(t2, a2, d2)  # memoized from lru_cache

            # Multiply by upstream probability.
            new = {tup: p * p2 for tup, p in new.items()}
            probs_list.append(new)

        combined = utils.combine_dict_probs(probs_list)
        return combined

    return recur_helper(0, a, d_list[0])


def calc_win_probs(battle_probs, num_terr=None):
    """Calculate attack's probability of conquering each territory."""
    terr_probs = defaultdict(int)
    for (t, a, d), p in sorted(battle_probs.items(), reverse=True):
        if d == 0:
            t += 1  # pretend it's a new territory to make calcs easier
        terr_probs[t] += p
    # Take cumsum, cut off extra territory, and "un"-reverse.
    win_probs = utils.cumsum(terr_probs.values())[:-1][::-1]
    if num_terr is not None:
        assert num_terr >= len(win_probs)
        # Append values for impossible territories.
        win_probs += [0] * (num_terr - len(win_probs))
    return win_probs


def calc_cum_probs(battle_probs, d_list):
    """Calculate cumulative probabilities for attack and defense.

    Returns:
        (tuple) Two tuples (first for attack, second for defense) that consist
            of lists, which themselves have tuples of this form:
            ((territory index, num. remaining, num. on territory), cum. prob)
    """
    def one_player(index):
        """index is 0 for attack, 1 for defense."""
        dct = defaultdict(int)
        for (t, a, d), p in battle_probs.items():
            rems = utils.calc_remaining_troops(t, a, d, d_list)
            dct[(t, rems[index], (a, d)[index])] += p
        lst = sorted(dct.items(), key=lambda x: -x[0][1])  # sort on remaining
        csum = utils.cumsum([p for tup, p in lst])
        lst = list(zip([tup for tup, p in lst], csum))
        return lst

    atk = one_player(0)
    dfn = one_player(1)
    return atk, dfn


# -----------------------------------------------------------------------------
# Simulation, for sanity-checks
# -----------------------------------------------------------------------------


def simulate(a, d, a_sides=6, d_sides=6, stop=1, iters=10000):
    """Simulate battles (for sanity-checking).

    Should take same inputs and give same outputs as version that gives
    exact answers, with exception of additional arg for number of iterations.
    """
    fixed = utils.fix_args(a, d, a_sides, d_sides, stop)
    d_list, a_sides_list, d_sides_list = fixed

    def simulate_one(a, d_list):
        d = d_list[0]
        t = 0
        while a > stop and d > 0:
            # Get new attack and defense troop numbers.
            a_sides, d_sides = a_sides_list[t], d_sides_list[t]
            loss_key = min(3, a - 1), min(2, d)
            loss_probs = calc_loss_probs(a_sides, d_sides)[loss_key]
            vals, weights = zip(*loss_probs.items())
            a_loss, d_loss = random.choices(vals, weights)[0]
            a, d = a - a_loss, d - d_loss

            if d == 0 and a > stop and t < len(d_list) - 1:
                # Move on to next territory.
                t += 1
                a, d = a - 1, d_list[t]
        return t, a, d

    res = Counter([simulate_one(a, d_list) for _ in range(iters)])
    res = {tup: p / iters for tup, p in res.items()}  # turn into probs
    return res


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('a', **argdefs.a)
    parser.add_argument('d', **argdefs.d)
    parser.add_argument('--asides', **argdefs.asides)
    parser.add_argument('--dsides', **argdefs.dsides)
    parser.add_argument('--stop', **argdefs.stop)
    parser.add_argument('--all', **argdefs._all)
    args = parser.parse_args()

    argdefs.clean_args(args)

    battle_probs = calc_battle_probs(args.a, args.d,
                                     args.asides, args.dsides,
                                     args.stop)

    d_list = args.d if isinstance(args.d, list) else [args.d]
    win_probs = calc_win_probs(battle_probs, len(d_list))
    if args.all:
        cum_probs = calc_cum_probs(battle_probs, d_list)
        printing.print_all(battle_probs, *cum_probs, win_probs)
    else:
        printing.print_win_probs(win_probs)


if __name__ == '__main__':
    main()
