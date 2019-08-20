#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-19

Functions for allocating troops for fortification.
"""
from collections import namedtuple
from copy import deepcopy
from functools import reduce
from operator import mul
from typing import Dict, List

from risk import battle
from risk import utils


Fortified = namedtuple('Fortified',
                       'args_new args_old allocations p_min p_any method')


def fortify(*args: List[Dict],
            d_troops: int,
            a_troops: int = 0,
            method: str = 'any') -> Fortified:
    """Fortify position to minimize chance of defeat.

    Args:
        troops_to_allocate (int): Number of troops to allocate to defensive
            territories
        args (dict): Dict of battle config arguments. Note that any value
            that could take multiple values, like d, must be represented as a
            list
        new_attack_troops (int): TODO
        method (str): One of two options: "weakest" or "any".
            "weakest": Minimize the maximum probability that you lose across
                configurations. Works better if you assume that the attacker
                will only attack in one engagement
            "any": Minimize the probability that you lose in *at least one*
                configuration. Works better if the attacker will attack
                in all engagements

    Returns:
        (dict or list of dicts) Battle args updated so that defensive positions
        have been fortified
    """
    assert method in ['weakest', 'any']

    arg_list_new = deepcopy(args)
    arg_list_old = deepcopy(args)
    del args

    @utils.memoize  # can't use lru_cache b/c function args are not hashable
    def calc_desired_p(args, terr_idx, p_list):
        new_args = deepcopy(args)
        new_args['d'][terr_idx] += 1
        p = battle.calc_probs(**new_args).win[-1]
        p_list_new = p_list[:]
        p_list_new[arg_idx] = p
        if method == 'weakest':
            # Want to minimze the max probability.
            return max(p_list_new)
        else:
            # Want to minimize the chance of losing in one or more configs.
            return calc_any_win_prob(p_list_new)

    # Get list of attack defeating all territories in each battle config.
    p_list = [battle.calc_probs(**args).win[-1] for args in arg_list_new]

    # Iteratively add troops to the optimal positions.
    for _ in range(d_troops):
        best_arg_idx = None
        best_terr_idx = None
        best_p = 1
        for arg_idx, args in enumerate(arg_list_new):
            for terr_idx in range(len(args['d'])):
                p = calc_desired_p(args, terr_idx, p_list)
                if p < best_p:
                    best_p = p
                    best_arg_idx = arg_idx
                    best_terr_idx = terr_idx
        arg_list_new[best_arg_idx]['d'][best_terr_idx] += 1
        p_list[best_arg_idx] = \
            battle.calc_probs(**arg_list_new[best_arg_idx]).win[-1]

    fortified = Fortified(utils.unbroadcast(arg_list_new),
                          utils.unbroadcast(arg_list_old),
                          get_allocations(arg_list_old, arg_list_new),
                          max(p_list),
                          calc_any_win_prob(p_list),
                          method)

    return fortified


def calc_any_win_prob(prob_list):
    return 1 - reduce(mul, [(1 - p) for p in prob_list])


def get_allocations(arg_list, arg_list_new):
    allocs = list()
    for orig, new in zip(arg_list, arg_list_new):
        alloc = [d_new - d_orig for d_orig, d_new in zip(orig['d'], new['d'])]
        allocs.append(alloc)
    return allocs


def main():
    """Sanity check."""
    # Always use lists for d values.
    arg_list = [dict(a=8, d=[4]),
                dict(a=8, d=[4], d_sides=[8]),
                dict(a=16, d=[8, 3, 2])]
    d_troops = 10
    a_troops = 0

    for method in ['weakest', 'any']:
        print(method)
        print(fortify(*arg_list, d_troops, a_troops, method=method))


if __name__ == '__main__':
    main()
