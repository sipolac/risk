#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-17

Utility functions.
"""
import functools


def clean_argparse(args):
    if len(args.d) == 1:
        args.d = args.d[0]
    if isinstance(args.asides, list) and len(args.asides) == 1:
        args.asides = args.asides[0]
    if isinstance(args.dsides, list) and len(args.dsides) == 1:
        args.dsides = args.dsides[0]


def broadcast(x, n):
    """Broadcasts into a list if not done already."""
    if not isinstance(x, (list, tuple)):
        x = [x] * n
    assert len(x) == n
    return x


def memoize(func):
    """Allows for memoization of functions that have non-hashable args."""
    cache = func.cache = {}
    @functools.wraps(func)
    def memoized_func(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return memoized_func


def cumsum(a):
    res = list()
    acc = 0
    for x in a:
        acc += x
        res.append(acc)
    return res
