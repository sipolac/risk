#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-17

Testing and spot checking Risk functions.
"""
from math import isclose

import pytest

from risk import min_troops
from risk import outcomes
from risk import utils


PROB_REL_TOL = 1e-6  # for comparison of "exact" probabilities
PROB_REL_TOL_APPROX = 1e-1  # for comparison of approx probabilities


@pytest.fixture
def params():
    a = 5
    d = [3, 2]
    a_sides = [6, 6]
    d_sides = [6, 6]
    stop = 1
    return a, d, a_sides, d_sides, stop


@pytest.fixture
def battle_probs(params):
    return outcomes.calc_battle_probs(*params)


@pytest.fixture
def battle_probs_sim(params):
    return outcomes.simulate(*params, 50000)


@pytest.fixture
def win_probs(battle_probs):
    return outcomes.calc_win_probs(battle_probs)


def test_calc_loss_probs():
    def test(a_sides, d_sides, loss_key, outcome, expected):
        actual = outcomes.calc_loss_probs(a_sides, d_sides)[loss_key][outcome]
        isclose(actual, expected)
    test(6, 6, (3, 2), (0, 2), 2890 / 7776)
    test(3, 3, (3, 1), (1, 0), 4 / 9)


def test_calc_battle_probs(battle_probs_sim, battle_probs):
    assert isinstance(battle_probs, dict)
    assert len(battle_probs) == 8
    assert len(battle_probs) == len(battle_probs_sim)
    battle_probs = sorted(battle_probs.items())
    battle_probs_sim = sorted(battle_probs_sim.items())
    for (tup1, p1), (tup2, p2) in zip(battle_probs, battle_probs_sim):
        assert tup1 == tup2
        assert isclose(p1, p2, rel_tol=PROB_REL_TOL_APPROX)


def test_calc_win_probs(win_probs):
    expected = [0.6416229, 0.2500009]
    for p1, p2 in zip(win_probs, expected):
        assert isclose(p1, p2, rel_tol=PROB_REL_TOL)


def test_calc_remaining_troops(params):
    def test(tup, d_list, expected):
        actual = utils.calc_remaining_troops(*tup, d_list)
        assert actual == expected
    a, d, a_sides, d_sides, stop = params
    test((0, 1, 1), d, (1, 3))
    test((1, 1, 1), d, (2, 1))


def test_calc_cum_probs(battle_probs, params):
    a, d, a_sides, d_sides, stop = params
    atk_expected = [0.0911264, 0.1861678, 0.2500009,
                    0.6416229, 1.0000000]
    dfn_expected = [0.1311585, 0.2750526, 0.3583771,
                    0.6606328, 0.7499991, 1.0000000]
    atk, dfn = outcomes.calc_cum_probs(battle_probs, d)
    for act, exp in zip([atk, dfn], [atk_expected, dfn_expected]):
        for p1, p2 in zip([p for tup, p in act], exp):
            assert isclose(p1, p2, rel_tol=PROB_REL_TOL)


def test_find_min_troops():
    def test(target, battle_args, a_expected, p_expected):
        a, p = min_troops.find_min_troops(target, battle_args)
        assert a == a_expected
        assert isclose(p, p_expected, rel_tol=PROB_REL_TOL)

    test(0.5, dict(d=11), 12, 0.5762944972440298)
    test(0.95, dict(d=11), 21, 0.9616912565871958)
    test(0.5, dict(d=11, d_sides=8), 19, 0.5070879747303201)


def main(battle_probs, battle_probs_sim):
    """Spot check."""
    params_dict = dict(a=5,
                       d=[3, 2],
                       a_sides=[6, 6],
                       d_sides=[6, 6],
                       stop=1)
    battle_probs = outcomes.calc_battle_probs(**params_dict)
    params_dict['iters'] = 50000
    battle_probs_sim = outcomes.simulate(**params_dict)

    def print_probs(probs):
        for k, v in sorted(probs.items()):
            print(k, v)

    print('\nexact')
    print_probs(battle_probs)

    print('\nsimulated')
    print_probs(battle_probs_sim)

    print('\ncumulative probs')
    outcomes.calc_cum_probs(battle_probs, params_dict['d'])


if __name__ == '__main__':
    main(battle_probs, battle_probs_sim)
