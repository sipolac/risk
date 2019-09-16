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
from typing import Dict, List, Tuple
import argparse
import random


# Key for dict defining distribution of outcome probabilities. terr_idx is
# territory index, where 0 is the first defense territory, 1 is the second,
# etc. {x}_troops is the number of attack or defense troops on that
# territory.
Outcome = namedtuple('Outcome', 'terr_idx a_troops d_troops')

# Holds two CumulOutcome objects.
CumulStats = namedtuple('CumulStats', 'attack defense')

# Key for cumulative outcome dictionary. Specific to either attack or defense.
# troops_total is the number of troops for that player still in play across
# all territories relevant to the engagement. E.g., for defense, it's the
# number of troops still left on the territory specified by terr_idx plus the
# number of troops in territories that haven't been attacked.
CumulOutcome = namedtuple('CumulOutcome', 'terr_idx troops_total troops')


class BattleConfig(object):
    """Battle configuration: the parameters that define an interaction."""
    def __init__(self, a, d, a_sides, d_sides, stop):
        # Original inputs into the function that computes outcome probs.
        self.a = a
        self.d = d
        self.a_sides = a_sides
        self.d_sides = d_sides
        self.stop = stop

        # Derived or standardized inputs.
        self.num_terr = 1 if isinstance(d, int) else len(d)
        self.d_list = broadcast(d, self.num_terr)
        self.a_sides_list = broadcast(a_sides, self.num_terr)
        self.d_sides_list = broadcast(d_sides, self.num_terr)
        self.args = dict(a=a, d=d, a_sides=a_sides, d_sides=d_sides, stop=stop)

        self.check_args()

    def check_args(self):
        assert self.a > 1
        assert all([d > 0 for d in self.d_list])
        assert all([a_sides > 0 for a_sides in self.a_sides_list])
        assert all([d_sides > 0 for d_sides in self.d_sides_list])
        assert self.stop > 0


class BattleProbs(object):
    """Packet of information describing output probabilities."""
    def __init__(self, dist: Dict[Outcome, float], cfg: BattleConfig):
        self.dist = dist
        self.cfg = cfg
        self.cumul = self._calc_cumul_probs()
        self.win = self._calc_win_probs()

    def _calc_cumul_probs(self) -> CumulStats:
        """Calculates cumulative probabilities for attack and defense."""
        def one_player(player: str) -> List[Tuple[CumulOutcome, float]]:
            player_idx = ['attack', 'defense'].index(player)

            # Sum probs to create dict keyed on *cumulative* outcomes. But
            # note that probs aren't cumulative yet.
            rem_probs = defaultdict(int)
            for (t, a, d), p in self.dist.items():
                rems = self._calc_remaining_troops(t, a, d, self.cfg.d_list)
                cumout = CumulOutcome(t, rems[player_idx], (a, d)[player_idx])
                rem_probs[cumout] += p

            # Compute cumulative probabilities. First sort by total (i.e.,
            # remaining) troops for the player.
            probs_list = sorted(rem_probs.items(),
                                key=lambda x: -x[0].troops_total)
            csum = cumsum([x[1] for x in probs_list])
            cumul_probs = list(zip([x[0] for x in probs_list], csum))
            return cumul_probs

        return CumulStats(one_player('attack'), one_player('defense'))

    def _calc_win_probs(self) -> List:
        """Calculates attack's probability of conquering each territory."""
        # Get probability of defeat of each defense territory. Reverse
        # to prepare for cumsum.
        terr_probs = defaultdict(int)
        for (t, a, d), p in sorted(self.dist.items(), reverse=True):
            if d == 0:
                t += 1  # dummy territory to make calcs easier
            terr_probs[t] += p

        # Take cumsum, cut off dummy territory, and "un"-reverse.
        win_probs = cumsum(terr_probs.values())[:-1][::-1]
        win_probs += [0] * (self.cfg.num_terr - len(win_probs))
        return win_probs

    @staticmethod
    def _calc_remaining_troops(t, a, d, d_list) -> Tuple[int, int]:
        """Calculates remaining troops on specified engagement.

        t is territory index, a is # of attack troops, d is # of defense.
        """
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
def calc_loss_probs(a_sides, d_sides) -> Dict[Tuple, Dict[Tuple, float]]:
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

        # Enumerate all possible roll results.
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


def calc_probs_api(request) -> BattleProbs:
    """Calculates probability of all outcomes.

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
    print('running API')
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    print(request)
    print(request.get_json())
    print(type(request))
    print(dir(request))
    print(request.args)
    print(request.data)
    print(request.content_type)

    request_json = request.get_json()
    if request.args and 'a' in request.args:
        a = request.args.get('a')
        d = request.args.get('d')
    elif request_json and 'a' in request_json:
        a = request_json['a']
        d = request_json['d']
    else:
        print('something went wrong')
        return f'Something went wrong :-('

    a_sides, d_sides = 6, 6
    stop = 1

    cfg = BattleConfig(a, d, a_sides, d_sides, stop)

    def combine_dict_probs(dist_list):
        """Combine list of dicts into single dict, summing probabilies."""
        combined = defaultdict(int)
        for dct in dist_list:
            for outcome, p in dct.items():
                combined[outcome] += p
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
        dist_list = list()
        for (a_loss, d_loss), p_upstream in loss_probs.items():
            a_new, d_new = a - a_loss, d - d_loss

            if d_new == 0 and a_new > stop and t < cfg.num_terr - 1:
                # Move on to next territory. Need to leave one troop behind.
                new = recur_helper(t + 1, a_new - 1, cfg.d_list[t + 1])
            else:
                new = recur_helper(t, a_new, d_new)

            # Multiply by upstream probability.
            new = {outcome: p_upstream * p for outcome, p in new.items()}
            dist_list.append(new)

        dist = combine_dict_probs(dist_list)
        return dist

    dist = recur_helper(0, a, cfg.d_list[0])

    return (str(BattleProbs(dist, cfg).win), 200, headers)


def calc_probs_sim(a, d, a_sides=6, d_sides=6,
                   stop=1, iters=10000) -> BattleProbs:
    """Simulates battles (for sanity-checking).

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

    counts = Counter([simulate_one(a) for _ in range(iters)])
    dist = {outcome: count / iters for outcome, count in counts.items()}
    return BattleProbs(dist, cfg)


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-17

Utility functions.
"""
import functools


def clean_argparse(args):
    if len(args.d) == 1:
        args.d = args.d[0]
    if isinstance(args.asides, list) and len(args.asides) == 1:
        args.asides = args.asides[0]
    if isinstance(args.dsides, list) and len(args.dsides) == 1:
        args.dsides = args.dsides[0]


def broadcast(x, n):
    """Broadcasts into a list if not done already."""
    if not isinstance(x, (list, tuple)):
        x = [x] * n
    assert len(x) == n
    return x


def memoize(func):
    """Allows for memoization of functions that have non-hashable args."""
    cache = func.cache = {}
    @functools.wraps(func)
    def memoized_func(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return memoized_func


def cumsum(a):
    res = list()
    acc = 0
    for x in a:
        acc += x
        res.append(acc)
    return res



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-17

Printing for shell.
"""


def print_dist_probs(battle_probs):
    print('territory | attack | defense | probability')
    battle_prob_list = sorted(battle_probs.dist.items())
    for (t, a, d), p in battle_prob_list:
        print(f'{t + 1:>9} | {a:>6} |{d:>8} | {p}')


def print_cumul_probs(battle_probs):
    for index in range(2):
        player_text = ['attack', 'defense'][index] + ' (cumulative)'
        cumul_probs = battle_probs.cumul[index]
        print(f'{player_text.center(66, ".")}')
        print((f'territory | troops on territory | '
               f'troops remaining | cumulative prob.'))
        for (t, rem, n), p in cumul_probs:
            print(f'{t + 1:>9} | {n:>19} | {rem:>16} | {p}')
        if index == 0:
            print()


def print_win_probs(battle_probs):
    print('territory | attack win probability')
    for t, p in enumerate(battle_probs.win):
        print(f'{t + 1:>9} | {p}')


def print_all(battle_probs):
    print_dist_probs(battle_probs)
    print()
    print_cumul_probs(battle_probs)
    print()
    print_win_probs(battle_probs)
