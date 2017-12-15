
import numpy as np
import pandas as pd


def get_loss_probs(dice, sides):
    '''
    Calculate probability of defense losing each possible number of troops.
    
    Args:
        dice (tup): Number of dice for attack and defense, respectively. E.g.,
            if attack is using 3 dice and defense 1, then this would be (3,1)
        sides (tup): Number of sides on dice for attack and defense, respectively.
            In tabletop game, this is (6,6), but in Warfish it can vary depending
            on defense or attack bonuses
    
    Returns:
        dict (of floats): Probability defense suffers losses indicated in key
    '''

    # Enumerate all possible roll combinations. First rows are for attack
    # (up to 3) and last rows are for defense (up to 2).
    possible_sides = []
    for i in range(2):
        for _ in range(dice[i]):
            possible_sides.append(range(1,sides[i]+1))
    all_roll_combos = np.array(np.meshgrid(*possible_sides)).reshape(sum(dice),-1).T

    # Sort attack and defense columns separately in ascending order.
    sort_rows_asc = lambda array2d: -np.array(map(sorted, -array2d))
    attack = sort_rows_asc(all_roll_combos[:,:dice[0]])
    defense = sort_rows_asc(all_roll_combos[:,dice[0]:])

    # Calculate number of troops defense loses in each engagement.
    max_losses = min(dice)
    defense_losses = (attack[:,:max_losses] > defense[:,:max_losses]).sum(axis=1)

    # Calculate frequencies of each loss number for defense.
    freqs = {}
    for l in defense_losses:
        freqs[l] = freqs.get(l,0) + 1

    # Calculate probs by dividing by number of combos.
    loss_probs = {lost:freq/float(len(defense_losses)) for lost,freq in freqs.iteritems()}

    return loss_probs


def get_probs(sides):
    '''Calculate probability of defense losing each possible number of troops
    for each possible combination of number of dice (e.g., attack's 3 dice vs.
    defense's 2, or attack's 1 vs. defense's 1).

    Args:
        sides (tup): Number of sides on dice for attack and defense, respectively.
            In tabletop game, this is (6,6), but in Warfish it can vary depending
            on defense or attack bonuses
    
    Returns:
        dict (of dicts): Key is tuple for attack and defense dice. Value is
            output from get_loss_probs()
    '''
    probs = {}
    for attack_dice in range(1,4):  # attack can roll 1, 2 or 3 dice
        for defense_dice in range(1,3):  # defense can roll 1 or 2 dice
            dice = (attack_dice, defense_dice)
            probs[dice] = get_loss_probs(dice, sides)

    return probs


def get_outcomes(armies, sides):
    '''Compute the probability of each absorbing state. From here, win ratios
    can be easily calculated.

    Modeling comes from Osborne's paper:
        http://www4.stat.ncsu.edu/~jaosborn/research/RISK.pdf

    More elegant solution would've been:
        https://minimallysufficient.github.io/2015/01/01/risk-probabilities.html
    
    Args:
        armies (tuple of ints): initial attacking armies (this is num troops - 1
            since attack needs to leave at least one troop behind) and initial
            defending armies. E.g., if there are 10 troops on the attacker's
            territory and 7 on the defender's, then this would be (9,7)
        sides (tup): Number of sides on dice for attack and defense, respectively.
            In tabletop game, this is (6,6), but in Warfish it can vary depending
            on defense or attack bonuses
        
    Returns:
        dict of tuple:float: Tuple is the outcome in terms of attacking/defending
            armies (attack then defense), and float is the probability of that
            outcome occurring.
    '''

    def to_str(arr):
        '''Helper fun for converting (lists of) tuples to str.'''
        if isinstance(arr, tuple):
            return str(arr)
        else:
            return [str(x) for x in arr]
    
    A, D = armies
    probs = get_probs(sides)
    
    # Get list of transient and absorbing pairings of attacking armies and
    # defending armies. E.g., (3,1), which is 3 attacking armies vs 1 defending
    # army, is transient since no one has been defeated, but (3,0) is absorbing.
    transients = [(a,d) for a in range(1,A+1) for d in range(1,D+1)]
    absorbings = [(0,d) for d in range(1,D+1)] + [(a,0) for a in range(1,A+1)]

    # Create/initialize matrices from Osborne's paper.
    Q = pd.DataFrame(np.zeros((A*D,A*D)))
    R = pd.DataFrame(np.zeros((A*D,A+D)))
    I = np.identity(A+D)
    zeros = np.zeros((A+D,A*D))

    # Add column names and indices for debugging and easier slicing.
    Q.index = to_str(transients)
    Q.columns = to_str(transients)
    R.index = to_str(transients)
    R.columns = to_str(absorbings)

    # Add probabilities to the Q and R matrices.
    for transient in transients:

        a, d = transient
        dice = (min(3,a), min(2,d))
        max_losses = min(dice)
        loss_probs = probs[dice]

        for d_loss, loss_prob in loss_probs.iteritems():
            
            a_loss = max_losses - d_loss
            a_new, d_new = a - a_loss, d - d_loss

            matrix = Q if min(a_new, d_new)>0 else R
            matrix.loc[to_str(transient), to_str((a_new, d_new))] = loss_prob

    # Instead of multiplying P by itself until all nonzero probabilities
    # are in the absorbing states, can just do this calculation.
    F = np.linalg.inv(np.identity(Q.shape[0]) - Q).dot(R)
    
    # Last row of F has final probability of each absorbing state. Other
    # rows of F have intermediate probabilities, which we won't use here.
    return {absorbing:prob for absorbing, prob in zip(absorbings, F[-1,:])}


def attack_win_prob(outcomes):
    '''Given outcomes, calculate the probability of attack winning. The outcomes
    variable is returned from compute_outcomes().
    '''
    return sum([prob for absorbing, prob in outcomes.iteritems() if absorbing[1]==0])
