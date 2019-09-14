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


fortified_argnames = 'args_new args_old allocation p_max p_any method'
Fortified = namedtuple('Fortified', fortified_argnames)


def fortify(arg_list: List[Dict],
            d_troops: int,
            a_troops: int = 0,
            method: str = 'any') -> Fortified:
    """Fortify position to minimize chance of defeat.

    Args:
        arg_list (list of dicts): Contains config arguments. Note that any
            value that could take multiple values, like d, must be represented
            as a list
        d_troops (int): Number of troops to allocate to defensive
            territories
        a_troops (int): TODO
        method (str): One of two options: "weakest" or "any".
            "weakest": Minimize the maximum probability that you lose across
                configurations. Works better if you assume that the attacker
                will only attack in one engagement
            "any": Minimize the probability that you lose in *at least one*
                configuration. Works better if the attacker will attack
                in all engagements

    Returns:
        (Fortified) Battle args updated so that defensive positions have been
        fortified, along with some other descriptive info
    """
    if a_troops > 0:
        raise NotImplementedError('argument `a_troops` not implemented')

    assert method in ['weakest', 'any']

    arg_list_old = deepcopy(arg_list)  # to include in output
    arg_list = deepcopy(arg_list)  # we'll modify this going forward

    # @utils.memoize  # can't use lru_cache b/c function args are not hashable
    def calc_prob(args, arg_idx, terr_idx, p_list):
        """Calculate the probability that will be minimized."""
        new_args = deepcopy(args)
        new_args['d'][terr_idx] += 1
        p = battle.calc_probs(**new_args).win[-1]
        p_list_new = p_list[:]
        p_list_new[arg_idx] = p
        if method == 'any':
            # Want to minimize the chance of losing in one or more configs.
            res = calc_any_win_prob(p_list_new)
        else:
            # Want to minimze the max probability.
            res = max(p_list_new)
        return res

    # Get list of attack winning in each battle config.
    p_list = [battle.calc_probs(**args).win[-1] for args in arg_list]

    # Iteratively add troops to the optimal positions.
    for _ in range(d_troops):
        best_arg_idx = None
        best_terr_idx = None
        best_p = 1
        for arg_idx, args in enumerate(arg_list):
            for terr_idx in range(len(args['d'])):
                p = calc_prob(args, arg_idx, terr_idx, p_list)
                if p < best_p:
                    best_p = p
                    best_arg_idx = arg_idx
                    best_terr_idx = terr_idx
        arg_list[best_arg_idx]['d'][best_terr_idx] += 1
        p_list[best_arg_idx] = \
            battle.calc_probs(**arg_list[best_arg_idx]).win[-1]

    fortified = Fortified(arg_list,
                          arg_list_old,
                          get_allocations(arg_list_old, arg_list),
                          max(p_list),
                          calc_any_win_prob(p_list),
                          method)
    return fortified


def calc_any_win_prob(prob_list):
    return 1 - reduce(mul, [(1 - p) for p in prob_list])


def get_allocations(arg_list_old, arg_list):
    allocs = list()
    for old, new in zip(arg_list_old, arg_list):
        alloc = [d_new - d_old for d_old, d_new in zip(old['d'], new['d'])]
        allocs.append(alloc)
    return allocs


def main():
    """Sanity check."""
    # Always use lists for d values.
    arg_list = [dict(a=8, d=[4]),
                dict(a=8, d=[4], d_sides=[8]),
                dict(a=16, d=[8, 3, 2])]
    d_troops = 10

    for method in ['weakest', 'any']:
        print(method)
        print(fortify(arg_list, d_troops, method=method))


if __name__ == '__main__':
    main()
