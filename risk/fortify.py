#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-19

Allocate troops defensively in a way that minimizes the maximum
probability of getting taken over across various battle configurations.
That is, allocate troops in a way that strengthens your weakest links
from a defensive position.
"""
from copy import deepcopy
from typing import Dict, List

from risk import battle


def minimax(troops_to_allocate: int, *args: List[Dict]):
    """Fortify position through efficient troop allocation.

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

    # Iteratively add troops to the weakest defensive positions.
    for _ in range(troops_to_allocate):

        # Find weakest position.
        worst_prob = 0  # higher is worse
        worst_arg_idx = None
        for arg_idx, args in enumerate(arg_list):
            p = battle.calc_probs(**args).win[-1]
            if p > worst_prob:
                worst_prob = p
                worst_arg_idx = arg_idx

        # Find out which territory to fortify.
        best_prob = 1  # lower is better
        best_terr = None
        worst_args = arg_list[worst_arg_idx]
        for terr_idx in range(len(worst_args['d'])):
            args = deepcopy(worst_args)
            args['d'][terr_idx] += 1
            p = battle.calc_probs(**args).win[-1]
            if p < best_prob:
                best_prob = p
                best_terr = terr_idx
        arg_list[worst_arg_idx]['d'][best_terr] += 1

    return arg_list[0] if len(arg_list) == 1 else arg_list


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
        print(f'weakest: {max(p_list)}')

    # Always use lists for d values.
    arg_list = [dict(a=8, d=[4]),
                dict(a=8, d=[4], d_sides=[8]),
                dict(a=16, d=[8, 3, 2])]
    troops_to_allocate = 10

    print('current win probs')
    print_probs(arg_list)

    arg_list_new = minimax(troops_to_allocate, *arg_list)

    print('\nnew win probs')
    print_probs(arg_list_new)

    print('\nallocations')
    for alloc in get_allocations(arg_list, arg_list_new):
        print(alloc)


if __name__ == '__main__':
    main()
