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


def find_min_troops(target, battle_args, upper_bound_start=8, logger=None):
    """Finds number of attack troops given a target probability of winning.

    The returned number is the smallest number of troops that would guarantee
    a win probability that is *at least* the target probability. The win
    probability is for conquering *all* defense territories.

    Args:
        target (float): Win probability should be above this target
        battle_args (dict): Args to be passed to calc_probs
        upper_bound_start (int): Starting upper bound on number of attack
            troops. If it's too low, it'll be increased
        logger (logger): Logger

    Returns:
        (tuple) Number of troops, and probability of winning.
    """
    assert 0 < target < 1
    assert isinstance(battle_args, dict)
    assert upper_bound_start > 0

    logger = logger or logging.getLogger(__name__)

    def calc_prob(a):
        battle_args['a'] = a
        return battle.calc_probs(**battle_args).win[-1]

    lo, hi = 1, upper_bound_start

    logger.info(f'testing upper bound {hi}...')
    p = calc_prob(hi)
    while p < target:
        lo = hi + 1
        hi *= 2
        logger.info(f'not high enough; trying range {lo} to {hi}...')
        p = calc_prob(hi)

    logger.info('searching for number of troops...')
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
    a = mid

    # Since we want prob >= target, increment if that isn't true.
    if p < target:
        a += 1
        p = calc_prob(a)
        logger.info((f'incrementing to {a}, putting {p} above {target}'))

    logger.info(f'found: {a} with prob of {p}')
    return a


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('target',
                        type=float,
                        help='desired probability of winning')
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
    res = find_min_troops(args.target, battle_args, logger=logger)
    print(f'{res.troops} troops gives a win probability of {res.win_prob}')


if __name__ == '__main__':
    main()
