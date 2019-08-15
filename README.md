# risk

This project has some functions for computing the probabilities of outcomes in the board game [Risk](https://en.wikipedia.org/wiki/Risk_(game)).

It uses a recursive approach that's a bit nicer than a direct implementation of a [pure statistics approach](http://www4.stat.ncsu.edu/~jaosborn/research/RISK.pdf).


# Arguments

See help: `python risk.py -h`

```
usage: risk.py [-h] [--stop STOP] a d

positional arguments:
  a            num. troops on attacking territory
  d            num. troops on defending territory

optional arguments:
  -h, --help   show this help message and exit
  --stop STOP  when attack has this many troops or fewer, stop
```


# Examples

For a battle where the attacking territory has 10 and the defending territory has 7:

    python risk.py 10 5

This will print:
```
(attack, defense): probability
(1, 1): 0.028092878284246413
(1, 2): 0.04781649215850439
(1, 3): 0.029224148925045684
(1, 4): 0.01646900113237808
(1, 5): 0.005461006848598092
(2, 0): 0.020066341631604583
(3, 0): 0.04306937234319355
(4, 0): 0.07561101389364897
(5, 0): 0.10547405944755822
(6, 0): 0.12157456616254411
(7, 0): 0.14544059489072236
(8, 0): 0.1468051595275586
(9, 0): 0.12376894769401886
(10, 0): 0.09112641706037806

defense: cumulative probability (at least)
0: 1.0
1: 0.12706352734877266
2: 0.09897064906452625
3: 0.05115415690602186
4: 0.021930007980976173
5: 0.005461006848598092

attack: cumulative probability (at least)
1: 1.0
2: 0.8729364726512274
3: 0.8528701310196228
4: 0.8098007586764293
5: 0.7341897447827803
6: 0.628715685335222
7: 0.5071411191726779
8: 0.36170052428195554
9: 0.2148953647543969
10: 0.09112641706037806

win prob: 0.8729364726512274
```

Some readings of the above output:
* The probability of attack overtaking defense is 87.3% (see last printed statement).
* The probability of attack having more than, say, 8 troops at the end of the engagement is 36.2%.
* The probability that the outcome of attack having exactly 8 troops at the end of the engagement is 14.7%.

To run it in Python:
```python
>>> import risk
>>> risk.calc_battle_probs(10, 7)
{(10, 0): 0.03386771415952837, (9, 0): 0.06323706306848197, (8, 0): 0.09529206908693112, (7, 0): 0.11386017602833826, (6, 0): 0.11615211502207937, (5, 0): 0.1159717383838905, (4, 0): 0.09843767152386411, (3, 0): 0.060036192808549695, (2, 0): 0.02922503013626597, (1, 1): 0.040915042190772355, (1, 2): 0.07532197109219943, (1, 3): 0.05871256743457267, (1, 4): 0.04781649215850439, (1, 5): 0.029224148925045684, (1, 6): 0.01646900113237808, (1, 7): 0.005461006848598092}
```

# Dependencies
None


# TODO
* Generalize for dice with N sides
* Generalize for multiple defense territories
