#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-15

Functions for computing battle outcome probabilities in the board game Risk.
"""
from collections import defaultdict, OrderedDict
from functools import lru_cache
from itertools import product
from operator import itemgetter
import argparse


STOP_DEFAULT = 1


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


@lru_cache(maxsize=128)
def get_loss_probs(a_sides, d_sides):
    """Returns probability of various loss combinations.

    Args:
        a_sides: Int for number of sides on attacking dice
        d_sides: Int for number of sides on defending dice

    Returns:
        Dict of probailities of loss combinations. Keys are (# attack dice,
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
        combos = [list(tup) for tup in product(*iters)]

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


def calc_battle_probs(a, d, a_sides=6, d_sides=6, stop=STOP_DEFAULT):
    """Get probability of all outcomes.

    Args:
        a (int): Number of troops on attacking territory
        d (int): Number of troops on defending territory
        stop (int): When attack has this many troops or fewer, stop

    Returns:
        Dict where key is tuple of final attack and defense troops, and
        values are probabilites of those outcomes
    """
    assert a > 1 and d > 0
    assert stop > 0
    assert a_sides > 0 and d_sides > 0
    return calc_battle_probs_recur(a, d, a_sides, d_sides, stop, dict())


def calc_battle_probs_recur(a, d, a_sides, d_sides, stop, memo):
    """Recursive helper."""
    if a <= stop or d == 0:
        return {(a, d): 1}  # outcome has prob = 1 in absorbing state
    if (a, d) in memo:
        return memo[(a, d)]

    # Compute probabilities of next roll outcomes.
    next_loss_probs = get_loss_probs(a_sides, d_sides)[(min(3, a - 1), min(2, d))]
    probs_list = list()
    for (a_loss, d_loss), p2 in next_loss_probs.items():
        a2, d2 = a - a_loss, d - d_loss  # new attack and defense counts
        if (a2, d2) in memo:
            new = memo[(a2, d2)]
        else:
            new = calc_battle_probs_recur(a2, d2, a_sides, d_sides, stop, memo)
        # Multiply by upstream probability.
        new = {(a, d): p * p2 for (a, d), p in new.items()}
        probs_list.append(new)

    combined = combine_dict_probs(probs_list)

    memo[(a, d)] = combined
    return memo[(a, d)]


def combine_dict_probs(dict_list):
    """Combine list dicts into single dict, summing probabilies."""
    combined = defaultdict(int)
    for d in dict_list:
        for key, prob in d.items():
            combined[key] += prob
    return dict(combined)


def calc_win_prob(battle_probs):
    return sum([p for (a, d), p in battle_probs.items() if d == 0])


def calc_cum_probs(battle_probs, attack):
    """Calculate cumulative probs for attack or defense."""
    index = 0 if attack else 1
    battle_prob_list = sorted(battle_probs.items(),
                              key=lambda tup: tup[0][index],
                              reverse=True)
    probs = dict()
    cum_prob = 0
    for tup, p in battle_prob_list:
        cum_prob += p
        probs[tup[index]] = cum_prob
    return OrderedDict(sorted(probs.items()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('a',
                        type=int,
                        help='number of troops on attacking territory')
    parser.add_argument('d',
                        type=int,
                        help='number of troops on defending territory')
    parser.add_argument('--asides',
                        default=6,
                        type=int,
                        help='number of sides on attack dice')
    parser.add_argument('--dsides',
                        default=6,
                        type=int,
                        help='number of sides on defense dice')
    parser.add_argument('--stop',
                        default=STOP_DEFAULT,
                        type=int,
                        help='when attack has this many troops or fewer, stop')
    args = parser.parse_args()

    battle_probs = calc_battle_probs(args.a,
                                     args.d,
                                     args.asides,
                                     args.dsides,
                                     args.stop)
    win_prob = calc_win_prob(battle_probs)

    # Print all probabilities.
    print('(attack, defense): probability')
    battle_prob_list = sorted(battle_probs.items(), key=itemgetter(0))
    for (a, d), p in battle_prob_list:
        print(f'({a}, {d}): {p}')

    # Print cumulative probabilities.
    for attack in [False, True]:
        player_text = "attack" if attack else "defense"
        print(f'\n{player_text}: cumulative probability (at least)')
        cum_probs = calc_cum_probs(battle_probs, attack)
        for num, p in cum_probs.items():
            print(f'{num}: {p}')

    print(f'\nwin prob: {win_prob}')


if __name__ == '__main__':
    main()
