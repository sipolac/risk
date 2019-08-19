# risk

This project has some functions for computing the probabilities of battle outcomes in the board game [Risk](https://en.wikipedia.org/wiki/Risk_(game)).

A few advantages of this implementation:
* The probabilities are exact (doesn't use a simulator).
* It can compute probabilities for attacks on **multiple territories**!
* It can handle **dice bonuses** (e.g., a player rolling with 8-sided dice). This is helpful if you're playing on [warfish.net](www.warfish.net) or another platform that has user-created maps.
* Allows user to specify when they want to stop attacking. This is useful if they want to guarantee a certain number of troops on the attacking territory after the engagement—maybe to defend against a different adjacent territory.
* Under the hood, it uses dynamic programming, which is probably a bit cleaner than using matrix algebra (e.g., a direct implementation of [this paper](http://www4.stat.ncsu.edu/~jaosborn/research/RISK.pdf)).
* It runs quickly. Even for large inputs (e.g., 100 vs. 100), runtime is less than a second.

I've also included a function that helps you find the smallest number of troops that would guarantee a win probability that is *at least* some target probability. This is useful for deciding where to allocate troops at the beginning of a turn.

Code is written in Python 3.7.4.


# Table of contents

- [Arguments](#args)
- [Examples](#examples)
  - [Command line](#cmd)
    - [Battle outcomes](#cmd_outcomes)
    - [Troop allocation](#cmd_alloc)
  - [Python](#py)
    - [Battle outcomes](#py_outcomes)
    - [Troop allocation](#py_alloc)
    - [Other](#py_other)
- [Dependencies](#dependencies)


<a name="args"/>

# Arguments

For battle probabilties:
```
>>> python3 battle.py -h
usage: battle.py [-h] [--asides [ASIDES [ASIDES ...]]]
                 [--dsides [DSIDES [DSIDES ...]]] [--stop STOP] [--all]
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
  --all                 show all values
```

For troop allocation (described [below](#cmd_alloc)):
```
>>> python3 min_troops.py -h
usage: min_troops.py [-h] [--asides [ASIDES [ASIDES ...]]]
                     [--dsides [DSIDES [DSIDES ...]]] [--stop STOP] [-v]
                     target d [d ...]

positional arguments:
  target                desired probability of winning
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
  -v, --verbose         verbosity
```

<a name="examples"/>

# Examples

<a name="cmd"/>

## Command line

<a name="cmd_outcomes"/>

### Battle outcomes

If you have 5 troops and you're attacking a territory with 3 troops, the probability of overtaking the territory is:

```
>>> python3 battle.py 5 3
territory | attack win probability
        1 | 0.6416228964559516
```

To show all outcome probabilities (`--all`):

```
>>> python3 battle.py 5 3 --all
territory | attack | defense | probability
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
>>> python3 battle.py 5 3 2 1 --dsides 6 8 6 --all
territory | attack | defense | probability
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

<a name="cmd_alloc"/>

### Troop allocation

If you want to *find* the minimum number of attack troops that would guarantee victory with at least 0.95 probability in the above scenario, you could do the following:

```
>>> python3 min_troops.py 0.95 3 2 1 --dsides 6 8 6
17 troops gives a win probability of 0.953038445204023
```

With verbosity (`-v`), you can see the values tested:

```
>>> python3 min_troops.py 0.95 3 2 1 --dsides 6 8 6 -v
2019-08-19 00:12:27,077 - testing upper bound 8...
2019-08-19 00:12:27,129 - not high enough; trying range 9 to 16...
2019-08-19 00:12:27,130 - not high enough; trying range 17 to 32...
2019-08-19 00:12:27,134 - searching for number of troops...
2019-08-19 00:12:27,136 - 24 (midpoint of 17 and 32) gives 0.9964873460982187
2019-08-19 00:12:27,139 - 20 (midpoint of 17 and 23) gives 0.9840648899621028
2019-08-19 00:12:27,141 - 18 (midpoint of 17 and 19) gives 0.9670287614740551
2019-08-19 00:12:27,143 - 17 (midpoint of 17 and 17) gives 0.953038445204023
17 troops gives a win probability of 0.953038445204023
```


<a name="py"/>

## Python

<a name="py_outcomes"/>

### Battle outcomes

Using the scenario from above:

```python
>>> from risk import battle
>>> battle_probs = battle.calc_probs(a=5, d=[3, 2, 1], d_sides=[6, 8, 6])
>>> battle_probs.dist
{Outcome(terr_idx=1, a_troops=1, d_troops=2): 0.38715323159729165, Outcome(terr_idx=1, a_troops=1, d_troops=1): 0.09612780006053091, Outcome(terr_idx=2, a_troops=1, d_troops=1): 0.09326837465921452, Outcome(terr_idx=2, a_troops=2, d_troops=0): 0.03540994291874709, Outcome(terr_idx=2, a_troops=3, d_troops=0): 0.029663547220175827, Outcome(terr_idx=0, a_troops=1, d_troops=1): 0.08332453584748056, Outcome(terr_idx=0, a_troops=1, d_troops=3): 0.13115845129680434, Outcome(terr_idx=0, a_troops=1, d_troops=2): 0.1438941163997636}
>>> battle_probs.win  # indexed by territory
[0.64162289645596, 0.15834186479813744, 0.06507349013892291]
>>> battle_probs.cumul.attack
[(CumulOutcome(terr_idx=2, troops_total=5, troops=3), 0.029663547220175827), (CumulOutcome(terr_idx=2, troops_total=4, troops=2), 0.06507349013892291), (CumulOutcome(terr_idx=2, troops_total=3, troops=1), 0.15834186479813744), (CumulOutcome(terr_idx=1, troops_total=2, troops=1), 0.64162289645596), (CumulOutcome(terr_idx=0, troops_total=1, troops=1), 1.0000000000000084)]
>>> from risk import printing
>>> printing.print_win_probs(battle_probs)  # one of a few printing functions
territory | attack win probability
        1 | 0.64162289645596
        2 | 0.15834186479813744
        3 | 0.06507349013892291
```


<a name="py_alloc"/>

### Troop allocation

Again, using the scenario above:

```python
>>> from risk import min_troops
>>> min_troops.find_min_troops(0.95, dict(d=[3, 2, 1], d_sides=[6, 8, 6]))
MinTroops(troops=17, win_prob=0.953038445204023)
```

<a name="py_other"/>

### Other

For a version of `risk.battle.calc_probs` that uses simulation to compute *approximate* probabilities, see `risk.battle.calc_probs_sim`. For the printing functions used for the shell, see `risk.printing`.


<a name="dependencies"/>

# Dependencies
None
