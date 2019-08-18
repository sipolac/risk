#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-17

Utility functions.
"""
from collections import defaultdict


def broadcast_arg(val, n):
    """Fix arguments so that single values get broadcasted into a list."""
    if isinstance(val, int):
        val = [val] * n
    assert len(val) == n
    return val


def broadcast_args(*vals, n):
    return tuple(broadcast_arg(val, n) for val in vals)


def fix_args(a, d, a_sides, d_sides, stop):
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


def cumsum(a):
    res = list()
    cum = 0
    for x in a:
        cum += x
        res.append(cum)
    return res
