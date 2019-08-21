# risk

This project has some functions for computing the probabilities of battle outcomes in the board game [Risk](https://en.wikipedia.org/wiki/Risk_(game)).

A few advantages of this implementation:
* The probabilities are exact (doesn't use a simulator).
* It can compute probabilities for attacks on **multiple territories**!
* It can handle **dice bonuses** (e.g., a player rolling with 8-sided dice). This is helpful if you're playing on [warfish.net](www.warfish.net) or another platform that has user-created maps.
<!-- * Allows user to specify when they want to stop attacking. This is useful if they want to guarantee a certain number of troops on the attacking territory after the engagement—maybe to defend against a different adjacent territory. -->
* Under the hood, it uses dynamic programming, which is probably a bit cleaner than using matrix algebra (e.g., a direct implementation of [this paper](http://www4.stat.ncsu.edu/~jaosborn/research/RISK.pdf)).
* It runs quickly. Even for large inputs (e.g., 100 vs. 100), runtime is less than a second.

It also includes some functions that help with higher-level decision making:
* **Offensive troop allocation** (`min_troops.find_min_troops`): A function that finds the minimum number of troops that would guarantee a win probability that is *at least* some target probability. This is useful for deciding where to allocate troops before an attack.
* **Defensive troop allocation** (`fortify.fortify`): A function that allocates troops across defensive territories in *multiple battle configurations* in order to minimize the probability that you lose in *at least one* configuration. This is useful when allocating troops to protect the choke points of a continent, since you must hold *every* territory of that continent in order to receive the continent bonus. Note the battle configurations may be composed of multiple territories. See example below for further explanation. 

Code is written in Python 3.7.4.


# Table of contents

- [Arguments](#args)
- [Examples](#examples)
  - [Battle outcomes](#outcomes)
  - [Troop allocation](#alloc)
    - [Min troops](#mintroops)
    - [Fortification](#fortification)
- [Dependencies](#dependencies)
- [TODO](#todo)


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

For finding "min troops" (as described above):
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

A CLI for `fortify.fortify` hasn't been built yet :-(

<a name="examples"/>

# Examples

<a name="outcomes"/>

## Battle outcomes

If you have 5 troops and you're attacking a territory with 3 troops, the probability of overtaking the territory is:

```
>>> python3 battle.py 5 3
territory | attack win probability
        1 | 0.6416228964559516
```

To show the probability of all outcomes (`--all`):

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
* Instead of just one territory, you want to attack **three territories consecutively**, moving all your troops into conquered territories along the way. The second territory has 2 troops, and the third has 1.
* The **second territory** has a +2 defense bonus, meaning defense rolls with **8-sided dice** when defending that territory.

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

In Python:

```python
>>> from risk import battle
>>> battle_probs = battle.calc_probs(a=5, d=[3, 2, 1], d_sides=[6, 8, 6])
>>> battle_probs.dist
{Outcome(terr_idx=1, a_troops=1, d_troops=2): 0.38715323159729165, Outcome(terr_idx=1, a_troops=1, d_troops=1): 0.09612780006053091, Outcome(terr_idx=2, a_troops=1, d_troops=1): 0.09326837465921452, Outcome(terr_idx=2, a_troops=2, d_troops=0): 0.03540994291874709, Outcome(terr_idx=2, a_troops=3, d_troops=0): 0.029663547220175827, Outcome(terr_idx=0, a_troops=1, d_troops=1): 0.08332453584748056, Outcome(terr_idx=0, a_troops=1, d_troops=3): 0.13115845129680434, Outcome(terr_idx=0, a_troops=1, d_troops=2): 0.1438941163997636}
```
```python
>>> battle_probs.win  # indexed by territory
[0.64162289645596, 0.15834186479813744, 0.06507349013892291]
```
```python
>>> battle_probs.cumul.attack
[(CumulOutcome(terr_idx=2, troops_total=5, troops=3), 0.029663547220175827), (CumulOutcome(terr_idx=2, troops_total=4, troops=2), 0.06507349013892291), (CumulOutcome(terr_idx=2, troops_total=3, troops=1), 0.15834186479813744), (CumulOutcome(terr_idx=1, troops_total=2, troops=1), 0.64162289645596), (CumulOutcome(terr_idx=0, troops_total=1, troops=1), 1.0000000000000084)]
```
<!-- ```python
>>> from risk import printing
>>> printing.print_win_probs(battle_probs)  # one of a few printing functions
territory | attack win probability
        1 | 0.64162289645596
        2 | 0.15834186479813744
        3 | 0.06507349013892291
``` -->

<a name="alloc"/>

## Troop allocation

<a name="mintroops"/>

### Min troops

If you want to know the minimum number of attack troops that would guarantee victory with at least 0.95 probability in the above scenario, you could do the following:

```
>>> python3 min_troops.py 0.95 3 2 1 --dsides 6 8 6
17 troops gives a win probability of 0.953038445204023
```

<!-- With verbosity (`-v`), you can see the values tested:

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
``` -->

In Python:

```python
>>> from risk import min_troops
>>> min_troops.find_min_troops(0.95, dict(d=[3, 2, 1], d_sides=[6, 8, 6]))
17
```

<a name="fortification"/>

### Fortification

As a separate scenario, let's say there are **three choke points** in a continent you're trying to defend, and these choke points have the following configurations:
* Their 8 troops vs. your 4 troops (**0.83** probability of getting taken over).
* Their 8 troops vs. your 4 troops, but at this choke you have a +2 defensive bonus (**0.54** probability).
* Their 16 troops vs. three consecutive territories, which have 8 troops, 3 troops and 2 troops respectively (**0.64** probability). Let's say the first two territories are outside your continent, but the third is inside it.

<!-- If we assume the other player knows these odds and chooses to attack the *weakest* choke point *only*, then their odds of success will be max(0.83, 0.54, 0.64) = 0.83. If we want to allocate 10 troops toward our territories to minimize this probability: -->

<!-- ```python
>>> from risk import fortify
>>> arg_list = [dict(a=8, d=[4]),
...             dict(a=8, d=[4], d_sides=[8]),
...             dict(a=16, d=[8, 3, 2])]
>>> d_troops = 10
>>> fortified = fortify.fortify(arg_list, d_troops)
>>> for k, v in fortified._asdict().items():
...   print(f'{k}: {v}')
... 
args_new: ({'a': 8, 'd': [9]}, {'a': 8, 'd': [5], 'd_sides': [8]}, {'a': 16, 'd': [11, 4, 2]})
args_old: ({'a': 8, 'd': [4]}, {'a': 8, 'd': [4], 'd_sides': [8]}, {'a': 16, 'd': [8, 3, 2]})
allocation: [[5], [1], [3, 1, 0]]
p_min: 0.3931560099919826
p_any: 0.7578573335494463
method: 'weakest'
``` -->

<!-- This would add 5 troops to the first configuration, 1 to the second, and the remaining 4 to various territories in the third. The new maximum probabilty decreases to 0.39. (An additional step is assuming we know how many troops they'll be getting at the beginning of their turn, and adding this number to attack in each configuration.) -->

<!-- But what if we assume we'll be attacked at *all* choke points? In this case, the optimization problem is different in that we want to minimize the probability of the other player winning *one or more* of the engagements. Originally this probability was 1 - [(1 - 0.83) * (1 - 0.54) * (1 - 0.64)] = 0.97, and the previous allocation gave 0.76. To minimize this number specifically: -->

One reasonable strategy is to try to minimize the probability of the opponent winning *one or more* of the engagements. This probability is now 1 - [(1 - 0.83) * (1 - 0.54) * (1 - 0.64)] = **0.97**. If you have **10 troops** to allocate toward your territories to reduce this probability, the most optimal way to do so would be:

```python
>>> from risk import fortify
>>> arg_list = [dict(a=8, d=[4]),
...             dict(a=8, d=[4], d_sides=[8]),
...             dict(a=16, d=[8, 3, 2])]
>>> d_troops = 10
>>> fortified = fortify.fortify(arg_list, d_troops)
>>> for k, v in fortified._asdict().items():
...   print(f'{k}: {v}')
... 
args_new: ({'a': 8, 'd': [9]}, {'a': 8, 'd': [6], 'd_sides': [8]}, {'a': 16, 'd': [8, 4, 4]})
args_old: ({'a': 8, 'd': [4]}, {'a': 8, 'd': [4], 'd_sides': [8]}, {'a': 16, 'd': [8, 3, 2]})
allocation: [[5], [2], [0, 1, 2]]
p_max: 0.4302836340896645
p_any: 0.7344628440848463
method: 'any'
```

This would allocate 5 troops to the territory in the first configuration, 2 to the territory in the second, and the remaining 3 to various territories in the third. Given this allocation, the probability of being conquered in at least one of the engagements is 0.7—and therefore the probability of retaining your continent is 1 – 0.73 = 0.27.

**An aside**: A major personal [TODO](#todo) is to rewrite this fortification algorithm so that it optionally considers the strategic allocation of the opponent's troops after the player takes their turn (assuming we know the number of troops the opponent will allocate toward the battle configurations of interest before they attack). I haven't thought about it *too* much, but I imagine it might look something like a simple two-step, non-recursive version of [minimax](https://en.wikipedia.org/wiki/Minimax).


<a name="dependencies"/>

# Dependencies
None


<a name="todo"/>

# TODO
* Rewrite fortification algorithm so that it optionally considers the strategic allocation of the opponent's troops