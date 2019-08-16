# risk

This project has some functions for computing the probabilities of outcomes in the board game [Risk](https://en.wikipedia.org/wiki/Risk_(game)).

A few advantages of this implementation:
* The probabilities are exact (it doesn't use simulation).
* It's very fast for typical inputs.
* It generalizes to dice with N sides. This is helpful if you're playing on [warfish.net](warfish.net) or another platform that has user-created maps with attack/defense bonuses.
* Allows user to specify when they want to stop attacking. This is useful if they want to guarantee a certain number of troops on the attacking territory after the engagement---maybe to defend against a different adjacent territory.
* Under the hood, it's a bit cleaner than the direct implementation of a [Markov-based statistics approach](http://www4.stat.ncsu.edu/~jaosborn/research/RISK.pdf).

Code is written in Python 3.7.4.


# Arguments

See help: `python risk.py -h`

```
usage: risk.py [-h] [--asides ASIDES] [--dsides DSIDES] [--stop STOP] a d

positional arguments:
  a                number of troops on attacking territory
  d                number of troops on defending territory

optional arguments:
  -h, --help       show this help message and exit
  --asides ASIDES  number of sides on attack dice
  --dsides DSIDES  number of sides on defense dice
  --stop STOP      when attack has this many troops or fewer, stop
```


# Examples

## Command line

For a battle where the attacking territory has 5 and the defending territory has 4:

```
>>> python risk.py 5 4
(attack, defense): probability
(1, 1): 0.08263191440573789
(1, 2): 0.16578464212787658
(1, 3): 0.1438941163997636
(1, 4): 0.13115845129680434
(2, 0): 0.0590227960040985
(3, 0): 0.11472143265834381
(4, 0): 0.16465818335269697
(5, 0): 0.13812846375467833

defense: cumulative probability (at least)
0: 1.0
1: 0.5234691242301824
2: 0.4408372098244445
3: 0.27505256769656794
4: 0.13115845129680434

attack: cumulative probability (at least)
1: 1.0000000000000002
2: 0.4765308757698176
3: 0.41750807976571913
4: 0.3027866471073753
5: 0.13812846375467833

win prob: 0.47653087576981756
```

Some readings of the above output:
* The probability of attack overtaking defense is 47.7% (see last printed line).
* The probability of attack having *at least* 3 troops at the end of the engagement is 41.8%.
* The probability of attack having *exactly* 3 troops at the end of the engagement is 11.5%.

If defense has a +2 bonus and is therefore rolling with 8-sided dice:

```
>>> python3 risk.py 10 5 --dsides 8
(attack, defense): probability
(1, 1): 0.08373009443903778
(1, 2): 0.19414771967101685
(1, 3): 0.2379265900038769
(1, 4): 0.26489844930516626
(2, 0): 0.038059133835926254
(3, 0): 0.06613429494193751
(4, 0): 0.07139900856820838
(5, 0): 0.043704709234880686

defense: cumulative probability (at least)
0: 1.0000000000000508
1: 0.7807028534190978
2: 0.6969727589800601
3: 0.5028250393090432
4: 0.26489844930516626

attack: cumulative probability (at least)
1: 1.0000000000000506
2: 0.21929714658095284
3: 0.18123801274502657
4: 0.11510371780308906
5: 0.043704709234880686

win prob: 0.21929714658095284
```

You see that attack's win probability drops to 21.9%

## Python

```python
>>> import risk
>>> battle_probs = risk.calc_battle_probs(5, 4, d_sides=8)
>>> battle_probs
{(1, 4): 0.26489844930516626, (1, 3): 0.2379265900038769, (1, 2): 0.19414771967101685, (1, 1): 0.08373009443903778, (2, 0): 0.038059133835926254, (3, 0): 0.06613429494193751, (4, 0): 0.07139900856820838, (5, 0): 0.043704709234880686}
>>> risk.calc_win_prob(battle_probs)
0.21929714658095284
>>> risk.calc_cum_probs(battle_probs, attack=True)  # cumulative probs for attack's values
OrderedDict([(1, 1.0000000000000506), (2, 0.21929714658095284), (3, 0.18123801274502657), (4, 0.11510371780308906), (5, 0.043704709234880686)])
```

# Dependencies
None


# TODO
* Generalize for multiple defense territories
