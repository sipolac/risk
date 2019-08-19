#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-18

Definine common argparse arguments.
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
v = dict(
    action='count',
    default=0,
    help='verbosity'
)


def clean_args(args):
    if len(args.d) == 1:
        args.d = args.d[0]
    if isinstance(args.asides, list) and len(args.asides) == 1:
        args.asides = args.asides[0]
    if isinstance(args.dsides, list) and len(args.dsides) == 1:
        args.dsides = args.dsides[0]
