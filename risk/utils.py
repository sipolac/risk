#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-17

Utility functions.
"""


def clean_argparse(args):
    if len(args.d) == 1:
        args.d = args.d[0]
    if isinstance(args.asides, list) and len(args.asides) == 1:
        args.asides = args.asides[0]
    if isinstance(args.dsides, list) and len(args.dsides) == 1:
        args.dsides = args.dsides[0]


def cumsum(a):
    res = list()
    acc = 0
    for x in a:
        acc += x
        res.append(acc)
    return res
