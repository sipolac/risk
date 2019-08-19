#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-15

Functions for computing battle outcome probabilities in the board game Risk.
"""
from collections import Counter, defaultdict, namedtuple
from functools import lru_cache
from itertools import product
import argparse
import random

from risk import argdefs
from risk import printing
from risk import utils


Outcome = namedtuple('Dist', 'terr_idx a_troops d_troops')
CumulStats = namedtuple('CumulStats', 'attack defense')
CumulOutcome = namedtuple('Cumul', 'terr_idx troops_total troops')


class BattleConfig(object):
    """Battle configuration."""
    def __init__(self, a, d, a_sides, d_sides, stop):
        # Original inputs.
        self.a = a
        self.d = d
        self.a_sides = a_sides
        self.d_sides = d_sides
        self.stop = stop

        # Modified/inferred inputs.
        self.num_terr = 1 if isinstance(d, int) else len(d)
        self.d_list = self.broadcast_arg(d, self.num_terr)
        self.a_sides_list = self.broadcast_arg(a_sides, self.num_terr)
        self.d_sides_list = self.broadcast_arg(d_sides, self.num_terr)
        self.args = dict(a=a, d=d, a_sides=a_sides, d_sides=d_sides, stop=stop)

        self.check_args()

    @staticmethod
    def broadcast_arg(val, n):
        """Fix arguments so that single values get broadcasted into a list."""
        if isinstance(val, int):
            val = [val] * n
        assert len(val) == n
        return val

    def check_args(self):
        assert self.a > 1
        assert all([d > 0 for d in self.d_list])
        assert all([a_sides > 0 for a_sides in self.a_sides_list])
        assert all([d_sides > 0 for d_sides in self.d_sides_list])
        assert self.stop > 0


class BattleProbs(object):
    """Pack of information describing output probabilities."""
    def __init__(self, dist, cfg):
        self.cfg = cfg
        self.dist = dist
        self.cumul = self._calc_cum_probs()
        self.win = self._calc_win_probs()

    def _calc_cum_probs(self):
        """Calculate cumulative probabilities for attack and defense.

        Returns:
            (tuple) Two tuples (first for attack, second for defense) that
                consist of lists, which themselves have tuples of this form:
                ((territory index, num. remaining, num. on territory), cum.
                prob)
        """
        def one_player(index):
            """index is 0 for attack, 1 for defense."""
            dct = defaultdict(int)
            for (t, a, d), p in self.dist.items():
                rems = self._calc_remaining_troops(t, a, d, self.cfg.d_list)
                dct[(t, rems[index], (a, d)[index])] += p
            lst = sorted(dct.items(), key=lambda x: -x[0][1])  # sort on rem
            csum = utils.cumsum([p for tup, p in lst])
            lst = list(zip([CumulOutcome(*tup) for tup, p in lst], csum))
            return lst

        return CumulStats(one_player(0), one_player(1))

    def _calc_win_probs(self):
        """Calculate attack's probability of conquering each territory."""
        terr_probs = defaultdict(int)
        for (t, a, d), p in sorted(self.dist.items(), reverse=True):
            if d == 0:
                t += 1  # pretend it's a new territory to make calcs easier
            terr_probs[t] += p
        # Take cumsum, cut off extra territory, and "un"-reverse.
        win_probs = utils.cumsum(terr_probs.values())[:-1][::-1]
        win_probs += [0] * (self.cfg.num_terr - len(win_probs))
        return win_probs

    @staticmethod
    def _calc_remaining_troops(t, a, d, d_list):
        a_rem = a + t  # since 1 left on each conquered territory
        d_rem = d + sum(d_list[t + 1:])
        return a_rem, d_rem


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


def calc_probs(a, d, a_sides=6, d_sides=6, stop=1):
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
    cfg = BattleConfig(a, d, a_sides, d_sides, stop)

    def combine_dict_probs(dict_list):
        """Combine list dicts into single dict, summing probabilies."""
        combined = defaultdict(int)
        for dct in dict_list:
            for key, prob in dct.items():
                combined[key] += prob
        return dict(combined)

    @lru_cache(maxsize=None)
    def recur_helper(t, a, d):
        """New variable t keeps track of territory index."""
        if a <= stop or d == 0:
            return {Outcome(t, a, d): 1}  # absorbing, so prob = 1

        # Compute probabilities of next roll outcomes.
        a_sides, d_sides = cfg.a_sides_list[t], cfg.d_sides_list[t]
        loss_key = min(3, a - 1), min(2, d)
        loss_probs = calc_loss_probs(a_sides, d_sides)[loss_key]
        probs_list = list()
        for (a_loss, d_loss), p2 in loss_probs.items():
            a2, d2 = a - a_loss, d - d_loss  # new attack and defense counts

            if d2 == 0 and a2 > stop and t < cfg.num_terr - 1:
                # Move on to next territory.
                t2 = t + 1
                a2, d2 = a2 - 1, cfg.d_list[t2]
            else:
                t2 = t
            new = recur_helper(t2, a2, d2)  # memoized from lru_cache

            # Multiply by upstream probability.
            new = {tup: p * p2 for tup, p in new.items()}
            probs_list.append(new)

        dist = combine_dict_probs(probs_list)
        return dist

    dist = recur_helper(0, a, cfg.d_list[0])
    return BattleProbs(dist, cfg)


# -----------------------------------------------------------------------------
# Simulation, for sanity-checks
# -----------------------------------------------------------------------------


def calc_probs_sim(a, d, a_sides=6, d_sides=6, stop=1, iters=10000):
    """Simulate battles (for sanity-checking).

    Should take same inputs and give same outputs as version that gives
    exact answers, with exception of additional arg for number of iterations.
    """
    cfg = BattleConfig(a, d, a_sides, d_sides, stop)

    def simulate_one(a):
        d = cfg.d_list[0]
        t = 0
        while a > stop and d > 0:
            # Get new attack and defense troop numbers.
            a_sides, d_sides = cfg.a_sides_list[t], cfg.d_sides_list[t]
            loss_key = min(3, a - 1), min(2, d)
            loss_probs = calc_loss_probs(a_sides, d_sides)[loss_key]
            vals, weights = zip(*loss_probs.items())
            a_loss, d_loss = random.choices(vals, weights)[0]
            a, d = a - a_loss, d - d_loss

            if d == 0 and a > stop and t < cfg.num_terr - 1:
                # Move on to next territory.
                t += 1
                a, d = a - 1, cfg.d_list[t]
        return Outcome(t, a, d)

    dist = Counter([simulate_one(a) for _ in range(iters)])
    dist = {tup: p / iters for tup, p in dist.items()}  # turn into probs
    return BattleProbs(dist, cfg)


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

    utils.clean_argparse(args)
    cfg = BattleConfig(args.a, args.d, args.asides, args.dsides, args.stop)

    battle_probs = calc_probs(**cfg.args)

    if args.all:
        printing.print_all(battle_probs)
    else:
        printing.print_win_probs(battle_probs)


if __name__ == '__main__':
    main()
