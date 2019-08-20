#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-18

Define common argparse arguments.
"""
a = dict(
    type=int,
    help='number of troops on attacking territory'
)
d = dict(
    nargs='+',
    type=int,
    help=('number of troops on defending territory; use multiple values for '
          'multiple territories')
)
asides = dict(
    nargs='*',
    type=int,
    default=6,
    help=('number of sides on attack dice; use multiple values for multiple '
          'territories or single value to represent all territories')
)
dsides = dict(
    nargs='*',
    type=int,
    default=6,
    help=('number of sides on defense dice; use multiple values for multiple '
          'territories or single value to represent all territories')
)
stop = dict(
    default=1,
    type=int,
    help='when attack has this many troops or fewer, stop'
)
_all = dict(
    action='store_true',
    default=False,
    help='show all probability values'
)
v = dict(
    action='count',
    default=0,
    help='verbosity'
)
