#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-17

Testing and spot checking Risk functions.
"""
import risk


def main():
    """Spot check exact and simulation output."""
    a = 5
    d = [4, 3]
    a_sides = [6, 6]
    d_sides = [6, 6]
    stop = 1

    print('simulation')
    battle_probs = risk.simulate_battles(a, d, a_sides, d_sides, stop)
    for k, v in sorted(battle_probs.items()):
        print(k, v)

    print('\nexact')
    battle_probs = risk.calc_battle_probs(a, d, a_sides, d_sides, stop)
    for k, v in sorted(battle_probs.items()):
        print(k, v)


if __name__ == '__main__':
    main()
