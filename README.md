# risk

This project has some functions for computing the probabilities of battle outcomes in the board game [Risk](https://en.wikipedia.org/wiki/Risk_(game)).

A few advantages of this implementation:
* The probabilities are exact (doesn't use a simulator).
* It runs quickly. Even for large inputs (e.g., 100 vs. 100), runtime is less than a second.
* It can compute probabilities for attacks on **multiple territories**!
* It can handle **dice bonuses** (e.g., a player rolling with 8-sided dice). This is helpful if you're playing on [warfish.net](www.warfish.net) or another platform that has user-created maps.
* Allows user to specify when they want to stop attacking. This is useful if they want to guarantee a certain number of troops on the attacking territory after the engagement—maybe to defend against a different adjacent territory.
* Under the hood, it uses dynamic programming, which is probably a bit cleaner than using matrix algebra (e.g., a direct implementation of [this paper](http://www4.stat.ncsu.edu/~jaosborn/research/RISK.pdf)).

I've also included a function that helps you find the smallest number of troops that would guarantee a win probability that is *at least* some target probability. This is useful for deciding where to allocate troops at the beginning of a turn.

Code is written in Python 3.7.4.


# Arguments

See help: `python3 outcomes.py -h`

```
usage: outcomes.py [-h] [--asides [ASIDES [ASIDES ...]]]
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

### Battle outcomes

If you have 5 troops and you're attacking a territory with 3 troops:

```
>>> python3 outcomes.py 5 3
territory | attack | defense | exact probability
        1 |      1 |       1 | 0.08332453584748056
        1 |      1 |       2 | 0.1438941163997636
        1 |      1 |       3 | 0.13115845129680434
        1 |      2 |       0 | 0.05951752560534325
        1 |      3 |       0 | 0.12868912951264105
        1 |      4 |       0 | 0.20822626934436866
        1 |      5 |       0 | 0.24518997199359854

.......................attack (cumulative)........................
territory | troops on territory | troops remaining | cumulative prob.
        1 |                   5 |                5 | 0.24518997199359854
        1 |                   4 |                4 | 0.4534162413379672
        1 |                   3 |                3 | 0.5821053708506083
        1 |                   2 |                2 | 0.6416228964559516
        1 |                   1 |                1 | 1.0

.......................defense (cumulative).......................
territory | troops on territory | troops remaining | cumulative prob.
        1 |                   3 |                3 | 0.13115845129680434
        1 |                   2 |                2 | 0.27505256769656794
        1 |                   1 |                1 | 0.3583771035440485
        1 |                   0 |                0 | 1.0

territory | attack win probability
        1 | 0.6416228964559516
```

Let's add a few wrinkles:
* Instead of just one territory, you want to attack **three territories consecutively**, moving all your troops onto conquered territories along the way. The second territory has 2 troops, and the third has 1.
* The second of the three territories has a +2 defense bonus, meaning defense rolls with **8-sided dice** when defending that territory.

```
>>> python3 outcomes.py 5 3 2 1 --dsides 6 8 6
territory | attack | defense | exact probability
        1 |      1 |       1 | 0.08332453584748056
        1 |      1 |       2 | 0.1438941163997636
        1 |      1 |       3 | 0.13115845129680434
        2 |      1 |       1 | 0.09612780006053091
        2 |      1 |       2 | 0.38715323159729165
        3 |      1 |       1 | 0.09326837465921452
        3 |      2 |       0 | 0.03540994291874709
        3 |      3 |       0 | 0.029663547220175827

.......................attack (cumulative)........................
territory | troops on territory | troops remaining | cumulative prob.
        3 |                   3 |                5 | 0.029663547220175827
        3 |                   2 |                4 | 0.06507349013892291
        3 |                   1 |                3 | 0.15834186479813744
        2 |                   1 |                2 | 0.64162289645596
        1 |                   1 |                1 | 1.0000000000000084

.......................defense (cumulative).......................
territory | troops on territory | troops remaining | cumulative prob.
        1 |                   3 |                6 | 0.13115845129680434
        1 |                   2 |                5 | 0.27505256769656794
        1 |                   1 |                4 | 0.3583771035440485
        2 |                   2 |                3 | 0.7455303351413402
        2 |                   1 |                2 | 0.841658135201871
        3 |                   1 |                1 | 0.9349265098610856
        3 |                   0 |                0 | 1.0000000000000084

territory | attack win probability
        1 | 0.64162289645596
        2 | 0.15834186479813744
        3 | 0.06507349013892291
```


### Troop allocation

If you want to *find* the minimum number of attack troops that would guarantee victory with at least 0.95 probability in the above scenario, we could do the following:

```
>>> python3 min_troops.py 0.95 3 2 1 --dsides 6 8 6
17 troops gives a win probability of 0.953038445204023
```

With verbosity (`-v`), we can see the values tested:

```
>>> python3 min_troops.py 0.95 3 2 1 --dsides 6 8 6 -v
2019-08-19 00:12:27,077 - testing upper bound 8...
2019-08-19 00:12:27,129 - not high enough; trying range 9 to 16...
2019-08-19 00:12:27,130 - not high enough; trying range 17 to 32...
2019-08-19 00:12:27,134 - searching for number of troops...
2019-08-19 00:12:27,136 - 24 (within bounds 17 to 32) gives 0.9964873460982187
2019-08-19 00:12:27,139 - 20 (within bounds 17 to 23) gives 0.9840648899621028
2019-08-19 00:12:27,141 - 18 (within bounds 17 to 19) gives 0.9670287614740551
2019-08-19 00:12:27,143 - 17 (within bounds 17 to 17) gives 0.953038445204023
17 troops gives a win probability of 0.953038445204023
```


## Python

```python
>>> from risk import outcomes
>>> battle_probs = outcomes.calc_battle_probs(a=5, d=[3, 2, 1], d_sides=[6, 8, 6])
>>> battle_probs  # key is (territory, attack, defense)
{(1, 1, 2): 0.38715323159729165, (1, 1, 1): 0.09612780006053091, (2, 1, 1): 0.09326837465921452, (2, 2, 0): 0.03540994291874709, (2, 3, 0): 0.029663547220175827, (0, 1, 1): 0.08332453584748056, (0, 1, 3): 0.13115845129680434, (0, 1, 2): 0.1438941163997636}
>>> outcomes.calc_win_probs(battle_probs)  # indexed by territory
[0.64162289645596, 0.15834186479813744, 0.06507349013892291]
```

See function `outcomes.calc_cum_probs` for computing cumulative probabilities and `min_troops.find_min_troops` for (as you might guess) finding min troops, as described above. For a version of `outcomes.calc_battle_probs` that uses simulation to compute *approximate* probabilities, see `outcomes.simulate`.


# Dependencies
None
