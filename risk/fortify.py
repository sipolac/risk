#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-19

Functions for allocating troops for fortification.
"""
from copy import deepcopy
from functools import reduce
from operator import mul
from typing import Dict, List

from risk import battle


def fortify(troops_to_allocate: int, *args: List[Dict]):
    """Fortify position to minimize chance of attack winning *any* engagement.

    Args:
        troops_to_allocate (int): Number of troops to allocate to defensive
            territories
        args (dict): Dict of battle config arguments. Note that any value
            that could take multiple values, like d, must be represented as a
            list

    Returns:
        (dict or list of dicts) Battle args updated so that defensive positions
        have been fortified
    """
    arg_list = deepcopy(args)
    del args

    p_list = [battle.calc_probs(**args).win[-1] for args in arg_list]

    def _calc_p_any(args, terr_idx):
        new_args = deepcopy(args)
        new_args['d'][terr_idx] += 1
        p = battle.calc_probs(**new_args).win[-1]
        p_list_new = p_list[:]
        p_list_new[arg_idx] = p
        p_any = calc_any_win_prob(p_list_new)
        return p_any

    # Iteratively add troops to the weakest defensive positions.
    for _ in range(troops_to_allocate):
        best_arg_idx = None
        best_terr_idx = None
        best_p_any = 1
        for arg_idx, args in enumerate(arg_list):
            for terr_idx in range(len(args['d'])):
                p_any = _calc_p_any(args, terr_idx)
                if p_any < best_p_any:
                    best_p_any = p_any
                    best_arg_idx = arg_idx
                    best_terr_idx = terr_idx
        arg_list[best_arg_idx]['d'][best_terr_idx] += 1
        p_list[best_arg_idx] = battle.calc_probs(**arg_list[best_arg_idx]).win[-1]

    return arg_list[0] if len(arg_list) == 1 else arg_list


def calc_any_win_prob(prob_list):
    """Probably that attack wins *any* of the engagements."""
    return 1 - reduce(mul, [(1 - p) for p in prob_list])


def get_allocations(arg_list, arg_list_new):
    allocs = list()
    for orig, new in zip(arg_list, arg_list_new):
        alloc = [d_new - d_orig for d_orig, d_new in zip(orig['d'], new['d'])]
        allocs.append(alloc)
    return allocs


def main():
    """Sanity check."""
    def print_probs(arg_list):
        p_list = list()
        for args in arg_list:
            p = battle.calc_probs(**args).win[-1]
            p_list.append(p)
            print(args, p)
        print(f'any_win_prob: {calc_any_win_prob(p_list)}')

    # Always use lists for d values.
    arg_list = [dict(a=8, d=[4]),
                dict(a=8, d=[4], d_sides=[8]),
                dict(a=16, d=[8, 3, 2])]
    troops_to_allocate = 10

    print('current win probs')
    print_probs(arg_list)

    arg_list_new = fortify(troops_to_allocate, *arg_list)

    print('\nnew win probs')
    print_probs(arg_list_new)

    print('\nallocations')
    for alloc in get_allocations(arg_list, arg_list_new):
        print(alloc)


if __name__ == '__main__':
    main()
