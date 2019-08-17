#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-15

Functions for computing battle outcome probabilities in the board game Risk.
"""
from collections import Counter, defaultdict, OrderedDict
from functools import lru_cache
from itertools import product
import argparse
import random

import utils


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
        d (int): Number of troops on defending territory
        stop (int): When attack has this many troops or fewer, stop

    Returns:
        (dict) Key is tuple of final attack and defense troops, and
        values are probabilites of those outcomes
    """
    fixed = utils.fix_risk_args(a, d, a_sides, d_sides, stop)
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
            new = {(t, a, d): p * p2 for (t, a, d), p in new.items()}
            probs_list.append(new)

        combined = utils.combine_dict_probs(probs_list)
        return combined

    return recur_helper(0, a, d_list[0])


# def calc_win_probs(battle_probs):
#     """Calculate win probabilities for each territory."""
#     win_probs = defaultdict(int)
#     cum_prob = 0
#     print(sorted(battle_probs.items(), reverse=True))
#     for (t, a, d), p in sorted(battle_probs.items(), reverse=True):
#         cum_prob += p
#         win_probs[t] = cum_prob
#     return [p for k, p in sorted(win_probs.items())]


def calc_win_probs(battle_probs):
    """Calculate win probabilities for each territory."""
    win_probs = defaultdict(int)
    for (t, a, d), p in battle_probs.items():
        for t_before in range(0, t):
            win_probs[t_before] += p
        if d == 0:
            win_probs[t] += p
    return [p for k, p in sorted(win_probs.items())]


def calc_cum_probs(battle_probs, attack):
    """Calculate cumulative probs for attack or defense."""
    player_index = 1 if attack else 2

    # Sort for cumulative probability calculation.
    def key_func(tup):
        switcher = -1 if attack else 1
        return switcher * tup[0][0], -tup[0][player_index]
    battle_prob_list = sorted(battle_probs.items(), key=key_func)

    # Calculate cumulative probability.
    probs = dict()
    cum_prob = 0
    for tup, p in battle_prob_list:
        cum_prob += p
        probs[(tup[0], tup[player_index])] = cum_prob

    # Just sort descending by cumulative probability. Otherwise it gets a
    # little hairy with the indexing for defense.
    return OrderedDict(sorted(probs.items(), key=lambda x: -x[1]))


def simulate_battles(a, d, a_sides=6, d_sides=6, stop=1, iters=10000):
    """Simulate battles (for sanity-checking)."""
    fixed = utils.fix_risk_args(a, d, a_sides, d_sides, stop)
    d_list, a_sides_list, d_sides_list = fixed

    def simulate_one(a, d_list):
        d = d_list[0]
        t = 0
        while a > stop and d > 0:
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
    res = {k: v / iters for k, v in res.items()}
    return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('a',
                        type=int,
                        help='number of troops on attacking territory')
    parser.add_argument('d',
                        nargs='+',
                        type=int,
                        help=('number of troops on defending territory; '
                              'use multiple values for multiple territories'))
    parser.add_argument('--asides',
                        nargs='*',
                        type=int,
                        default=6,
                        help=('number of sides on attack dice; use multiple '
                              'values for multiple territories or single '
                              'value to represent all territories'))
    parser.add_argument('--dsides',
                        nargs='*',
                        type=int,
                        default=6,
                        help=('number of sides on defense dice; use multiple '
                              'values for multiple territories or single '
                              'value to represent all territories'))
    parser.add_argument('--stop',
                        default=1,
                        type=int,
                        help='when attack has this many troops or fewer, stop')
    args = parser.parse_args()

    # Clean arguments.
    if len(args.d) == 1:
        args.d = args.d[0]
    if isinstance(args.asides, list) and len(args.asides) == 1:
        args.asides = args.asides[0]
    if isinstance(args.dsides, list) and len(args.dsides) == 1:
        args.dsides = args.dsides[0]

    battle_probs = calc_battle_probs(args.a, args.d,
                                     args.asides, args.dsides,
                                     args.stop)

    # Print results.
    separator = '.' * 64
    utils.print_battle_probs(battle_probs)
    print(separator)
    utils.print_cum_probs(battle_probs, attack=True)
    print(separator)
    utils.print_cum_probs(battle_probs, attack=False)
    print(separator)
    utils.print_win_probs(battle_probs)


if __name__ == '__main__':
    main()
