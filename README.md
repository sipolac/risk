# risk

This project has some functions for computing the probabilities of outcomes in the board game [Risk](https://en.wikipedia.org/wiki/Risk_(game)).

A few advantages of this implementation:
* The probabilities are exact (doesn't use a simulator)
* It runs very quickly for typical inputs.
* It can compute probabilities for **multiple territories**!
* It can handle **dice bonuses** (e.g., a player rolling with 8-sided dice). This is helpful if you're playing on [warfish.net](warfish.net) or another platform that has user-created maps.
* Allows user to specify when they want to stop attacking. This is useful if they want to guarantee a certain number of troops on the attacking territory after the engagement---maybe to defend against a different adjacent territory.
* Under the hood, it's a bit cleaner than the direct implementation of a [Markov-based statistics approach](http://www4.stat.ncsu.edu/~jaosborn/research/RISK.pdf).

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

For a battle where the attacking territory has 3 and the defending territory has 2:

```bash
>>> python3 risk.py 3 2
territory | attack | defense | probability
        1 |      1 |       1 | 0.18904320987654322
        1 |      1 |       2 | 0.44830246913580246
        1 |      2 |       0 | 0.13503086419753088
        1 |      3 |       0 | 0.22762345679012347
................................................................
territory |  attack | cumulative probability (at least)
        1 |       1 | 1.0
        1 |       2 | 0.3626543209876544
        1 |       3 | 0.22762345679012347
................................................................
territory | defense | cumulative probability (at least)
        1 |       0 | 1.0
        1 |       1 | 0.6373456790123457
        1 |       2 | 0.44830246913580246
................................................................
territory | win probability
        1 | 0.3626543209876544
```

If there's an additional territory, which has one troop on it:

```bash
>>> python3 risk.py 3 2 1
territory | attack | defense | probability
        1 |      1 |       1 | 0.18904320987654322
        1 |      1 |       2 | 0.44830246913580246
        2 |      1 |       1 | 0.26781121399176955
        2 |      2 |       0 | 0.09484310699588479
................................................................
territory |  attack | cumulative probability (at least)
        1 |       1 | 1.0
        2 |       1 | 0.3626543209876543
        2 |       2 | 0.09484310699588479
................................................................
territory | defense | cumulative probability (at least)
        2 |       0 | 1.0
        2 |       1 | 0.9051568930041153
        1 |       1 | 0.6373456790123457
        1 |       2 | 0.44830246913580246
................................................................
territory | win probability
        1 | 0.3626543209876543
        2 | 0.09484310699588479
```

If that last territory has a defense bonus of +2 (i.e., a 8-sided die):

```bash
>>> python3 risk.py 3 2 1 --dsides 6 8
territory | attack | defense | probability
        1 |      1 |       1 | 0.18904320987654322
        1 |      1 |       2 | 0.44830246913580246
        2 |      1 |       1 | 0.2915219907407408
        2 |      2 |       0 | 0.07113233024691357
................................................................
territory |  attack | cumulative probability (at least)
        1 |       1 | 1.0
        2 |       1 | 0.3626543209876544
        2 |       2 | 0.07113233024691357
................................................................
territory | defense | cumulative probability (at least)
        2 |       0 | 1.0
        2 |       1 | 0.9288676697530865
        1 |       1 | 0.6373456790123457
        1 |       2 | 0.44830246913580246
................................................................
territory | win probability
        1 | 0.3626543209876544
        2 | 0.07113233024691357
```

And if you (as attack) want to stop attacking when you have 2 or fewer troops:

```bash
>>> python3 risk.py 3 2 1 --dsides 6 8 --stop 2
territory | attack | defense | probability
        1 |      1 |       2 | 0.44830246913580246
        1 |      2 |       1 | 0.32407407407407407
        2 |      2 |       1 | 0.22762345679012347
................................................................
territory |  attack | cumulative probability (at least)
        1 |       1 | 1.0
        1 |       2 | 0.5516975308641976
        2 |       2 | 0.22762345679012347
................................................................
territory | defense | cumulative probability (at least)
        2 |       1 | 1.0
        1 |       1 | 0.7723765432098766
        1 |       2 | 0.44830246913580246
................................................................
territory | win probability
        1 | 0.22762345679012347
```

## Python

```python
>>> import risk
>>> battle_probs = risk.calc_battle_probs(3, [2, 1], d_sides=[6, 8], stop=2)
>>> battle_probs  # key is (territory, attack, defense)
{(1, 2, 1): 0.22762345679012347, (0, 1, 2): 0.44830246913580246, (0, 2, 1): 0.32407407407407407}
>>> risk.calc_win_prob(battle_probs)  # indexed by territory
[0.22762345679012347]
>>> risk.calc_cum_probs(battle_probs, attack=True)  # cumulative for attack
OrderedDict([((0, 1), 1.0), ((0, 2), 0.5516975308641976), ((1, 2), 0.22762345679012347)])
```

# Dependencies
None


# TODO
* Think of a better way to compute/display cumulative probabilities
* Clean up code for printing
* Write tests, not just spot check vs. simulator
