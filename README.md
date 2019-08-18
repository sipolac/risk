# risk

This project has some functions for computing the probabilities of outcomes in the board game [Risk](https://en.wikipedia.org/wiki/Risk_(game)).

A few advantages of this implementation:
* The probabilities are exact (doesn't use a simulator).
* It runs very quickly for typical inputs.
* It can compute probabilities for **multiple territories**!
* It can handle **dice bonuses** (e.g., a player rolling with 8-sided dice). This is helpful if you're playing on [warfish.net](warfish.net) or another platform that has user-created maps.
* Allows user to specify when they want to stop attacking. This is useful if they want to guarantee a certain number of troops on the attacking territory after the engagement---maybe to defend against a different adjacent territory.
* Under the hood, it uses dynamic programming, which is a bit cleaner than the direct implementation of a [Markov-based statistics approach](http://www4.stat.ncsu.edu/~jaosborn/research/RISK.pdf).

Code is written in Python 3.7.4.


# Arguments

See help: `python risk.py -h`

```
usage: risk.py [-h] [--asides [ASIDES [ASIDES ...]]]
               [--dsides [DSIDES [DSIDES ...]]] [--stop STOP]
               a d [d ...]

positional arguments:
  a                     number of troops on attacking territory
  d                     number of troops on defending territory; use multiple
                        values for multiple territories

optional arguments:
  -h, --help            show this help message and exit
  --asides [ASIDES [ASIDES ...]]
                        number of sides on attack dice; use multiple values
                        for multiple territories or single value to represent
                        all territories
  --dsides [DSIDES [DSIDES ...]]
                        number of sides on defense dice; use multiple values
                        for multiple territories or single value to represent
                        all territories
  --stop STOP           when attack has this many troops or fewer, stop
```


# Examples

## Command line

If you have 5 troops and you're attacking a territory with 3:

```bash
>>> python3 battle.py 5 3
territory | attack | defense | exact probability
        1 |      1 |       1 | 0.08332453584748056
        1 |      1 |       2 | 0.1438941163997636
        1 |      1 |       3 | 0.13115845129680434
        1 |      2 |       0 | 0.05951752560534325
        1 |      3 |       0 | 0.12868912951264105
        1 |      4 |       0 | 0.20822626934436866
        1 |      5 |       0 | 0.24518997199359854

.......................attack (cumulative)........................
territory | troops on territory | troops remaining | cum. prob.
        1 |                   5 |                5 | 0.24518997199359854
        1 |                   4 |                4 | 0.4534162413379672
        1 |                   3 |                3 | 0.5821053708506083
        1 |                   2 |                2 | 0.6416228964559516
        1 |                   1 |                1 | 1.0

.......................defense (cumulative).......................
territory | troops on territory | troops remaining | cum. prob.
        1 |                   3 |                3 | 0.13115845129680434
        1 |                   2 |                2 | 0.27505256769656794
        1 |                   1 |                1 | 0.3583771035440485
        1 |                   0 |                0 | 1.0

territory | attack win probability
        1 | 0.6416228964559516
```

Let's add a few wrinkles:
* You want to attack an additional territory, which has two troops on it.
* This additional territory has a +2 bonus for defense (meaning defense rolls with 8-sided dice).
* You want to stop when you have 2 troops (or fewer), to be conservative.

```bash
>>> python3 battle.py 5 3 2 --dsides 6 8 --stop 2
territory | attack | defense | exact probability
        1 |      1 |       3 | 0.13115845129680434
        1 |      2 |       1 | 0.09368568628520269
        1 |      2 |       2 | 0.19305049156738469
        2 |      1 |       2 | 0.12372472340818008
        2 |      2 |       1 | 0.10573379249943474
        2 |      2 |       2 | 0.23799944471783396
        2 |      3 |       0 | 0.063388800628705
        2 |      4 |       0 | 0.05125860959646383

.......................attack (cumulative)........................
territory | troops on territory | troops remaining | cum. prob.
        2 |                   4 |                5 | 0.05125860959646383
        2 |                   3 |                4 | 0.11464741022516883
        2 |                   2 |                3 | 0.4583806474424375
        2 |                   1 |                2 | 0.5821053708506176
        1 |                   2 |                2 | 0.8688415487032051
        1 |                   1 |                1 | 1.0000000000000093

.......................defense (cumulative).......................
territory | troops on territory | troops remaining | cum. prob.
        1 |                   3 |                5 | 0.13115845129680434
        1 |                   2 |                4 | 0.324208942864189
        1 |                   1 |                3 | 0.4178946291493917
        2 |                   2 |                2 | 0.7796187972754057
        2 |                   1 |                1 | 0.8853525897748404
        2 |                   0 |                0 | 1.0000000000000093

territory | attack win probability
        1 | 0.5821053708506176
        2 | 0.11464741022516883
```


## Python

```python
>>> from risk import battle
>>> battle_probs = battle.calc_battle_probs(5, [3, 2], d_sides=[6, 8], stop=2)
>>> battle_probs  # key is (territory, attack, defense)
{(1, 2, 2): 0.23799944471783396, (1, 2, 1): 0.10573379249943474, (1, 3, 0): 0.063388800628705, (1, 4, 0): 0.05125860959646383, (1, 1, 2): 0.12372472340818008, (0, 2, 1): 0.09368568628520269, (0, 1, 3): 0.13115845129680434, (0, 2, 2): 0.19305049156738469}
>>> battle.calc_win_probs(battle_probs)  # indexed by territory
[0.5821053708506176, 0.11464741022516883]
```

See function `battle.calc_cum_probs` for computing cumulative frequencies. For a version of `battle.calc_battle_probs` that uses simulation to compute *approximate* probabilities, see `battle.simulate`.


# Dependencies
None
