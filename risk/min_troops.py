#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authors: Chris Sipola
Created: 2019-08-18

Functions that find the number of troops given a target win probability.
"""
import argparse
import logging

from risk import argdefs
from risk import battle
from risk import utils


def find_min_troops(target, battle_args, hi_start=8, logger=None):
    """Finds number of attack troops given a target probability of winning.

    The returned number is the smallest number of troops that would guarantee
    a win probability that is *at least* the target probability. The win
    probability is for conquering *all* defense territories.

    Before using binary search, the upper bound is tested for whether it's too
    low---and if it is, it's doubled until it's no longer too low. (And in each
    iteration, the lower bound is also increased to where the upper bound used
    to be.)

    Args:
        target (float): Win probability should be above this target
        battle_args (dict): Args to be passed to calc_probs
        hi_start (int): Starting upper bound on number of attack troops. If
            it's too low, it'll be increased
        logger (logger): Logger

    Returns:
        (tuple) Number of troops, and probability of winning.
    """
    assert 0 < target < 1
    logger = logger or logging.getLogger(__name__)

    def calc_prob(a):
        battle_args['a'] = a
        return battle.calc_probs(**battle_args).win[-1]

    lo, hi = 1, hi_start

    logger.info(f'testing upper bound {hi}...')
    p = calc_prob(hi)
    while p < target:
        lo = hi + 1
        hi *= 2
        logger.info(f'not high enough; trying range {lo} to {hi}...')
        p = calc_prob(hi)

    logger.info('searching for number of troops...')
    mid = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        p = calc_prob(mid)
        logger.info(f'{mid} (midpoint of {lo} and {hi}) gives {p}')
        if p < target:
            lo = mid + 1
        elif p > target:
            hi = mid - 1
        else:
            break

    # Since we want prob >= target, increment if that isn't true.
    if p < target:
        mid += 1
        p = calc_prob(mid)
        logger.info((f'incrementing to {mid}, putting {p} above {target}'))

    return mid, p  # mid is our number of attack troops


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('target',
                        type=float,
                        help='want at least this probability of winning')
    parser.add_argument('d', **argdefs.d)
    parser.add_argument('--asides', **argdefs.asides)
    parser.add_argument('--dsides', **argdefs.dsides)
    parser.add_argument('--stop', **argdefs.stop)
    parser.add_argument('-v', '--verbose', **argdefs.v)
    args = parser.parse_args()

    log_level = {0: 'WARNING', 1: 'INFO'}.get(args.verbose, 1)

    log_fmt = '%(asctime)s - %(message)s'
    logging.basicConfig(level=log_level, format=log_fmt)
    logger = logging.getLogger(__name__)

    utils.clean_argparse(args)
    battle_args = dict(d=args.d,
                       a_sides=args.asides,
                       d_sides=args.dsides,
                       stop=args.stop)
    a, p = find_min_troops(args.target, battle_args, logger=logger)
    print(f'{a} troops gives a win probability of {p}')


if __name__ == '__main__':
    main()
