#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-17

Printing for shell.
"""


def print_battle_probs(battle_probs):
    print('territory | attack | defense | exact probability')
    battle_prob_list = sorted(battle_probs.items())
    for (t, a, d), p in battle_prob_list:
        print(f'{t + 1:>9} | {a:>6} |{d:>8} | {p}')


def print_cum_probs(atk, dfn):
    for index in range(2):
        player_text = ['attack', 'defense'][index] + ' (cumulative)'
        cum_probs = [atk, dfn][index]
        print(f'{player_text.center(66, ".")}')
        print(f'territory | troops on territory | troops remaining | cum. prob.')
        for (t, rem, n), p in cum_probs:
            print(f'{t + 1:>9} | {n:>19} | {rem:>16} | {p}')
        if index == 0:
            print()


def print_win_probs(win_probs):
    print('territory | attack win probability')
    for t, p in enumerate(win_probs):
        print(f'{t + 1:>9} | {p}')


def print_all(battle_probs, atk, dfn, win_probs):
    print_battle_probs(battle_probs)
    print()
    print_cum_probs(atk, dfn)
    print()
    print_win_probs(win_probs)
