#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-17

Utility functions.
"""
from collections import defaultdict

import risk


def broadcast_arg(val, n):
    """Fix arguments so that single values get broadcasted into a list."""
    if isinstance(val, int):
        val = [val] * n
    assert len(val) == n
    return val


def broadcast_args(*vals, n):
    return tuple(broadcast_arg(val, n) for val in vals)


def fix_risk_args(a, d, a_sides, d_sides, stop):
    n = 1 if isinstance(d, int) else len(d)
    d_list, a_sides_list, d_sides_list = broadcast_args(d, a_sides, d_sides, n=n)
    assert a > 1
    assert all([d > 0 for d in d_list])
    assert all([a_sides > 0 for a_sides in a_sides_list])
    assert all([d_sides > 0 for d_sides in d_sides_list])
    assert stop > 0
    return d_list, a_sides_list, d_sides_list


def combine_dict_probs(dict_list):
    """Combine list dicts into single dict, summing probabilies."""
    combined = defaultdict(int)
    for dct in dict_list:
        for key, prob in dct.items():
            combined[key] += prob
    return dict(combined)


def print_battle_probs(battle_probs):
    print('territory | attack | defense | probability')
    battle_prob_list = sorted(battle_probs.items())
    for (t, a, d), p in battle_prob_list:
        print(f'{t + 1:>9} | {a:>6} |{d:>8} | {p}')


def print_cum_probs(battle_probs, attack):
    player_text = ' attack' if attack else 'defense'
    print(f'territory | {player_text} | cumulative probability (at least)')
    cum_probs = risk.calc_cum_probs(battle_probs, attack)
    for (t, num), p in cum_probs.items():
        print(f'{t + 1:>9} | {num:>7} | {p}')


def print_win_probs(battle_probs):
    win_probs = risk.calc_win_probs(battle_probs)
    print('territory | win probability')
    for t, p in enumerate(win_probs):
        print(f'{t + 1:>9} | {p}')
