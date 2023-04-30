from random import randrange

from skytemple_files.dungeon_data.mappa_bin import MAX_WEIGHT

from skytemple_randomizer.randomizer.util.util import sample_with_minimum_distance


def random_weights(k):
    """
    Returns k random weights, with relative equal distance, in a range of *0.75-*1
    """
    smallest_possible_d = int(MAX_WEIGHT / k)
    d = int(smallest_possible_d * (randrange(75, 100) / 100))
    # We actually subtract the d and add it later to all of the items,
    # to make the first entry also a bit more likely
    weights = [w + d for w in sample_with_minimum_distance(MAX_WEIGHT - d, k, d)]
    # The last weight needs to have 10000
    highest_index = weights.index(max(weights))
    weights[highest_index] = MAX_WEIGHT
    return weights
