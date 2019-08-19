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
