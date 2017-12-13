
import numpy as np


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
    probs = {lost:freq/float(len(defense_losses)) for lost,freq in freqs.iteritems()}

    return probs


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
