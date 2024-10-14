from typing import List
import numpy as np

RANKS = np.array(['A', 'K', 'Q', 'J', 'T', '9', '8', '7'])
SUITS = np.array(['♠', '♣', '♦', '♥'])

import numpy as np

def get_suit_ordering(trump: int) -> np.ndarray:
    """
    Get the ordering of the suits in the game based on a trump.
    
    The order is determined by placing the trump suit first, followed by the rest of the suits in their default order.

    Parameters:
        trump (int): The trump suit, which defines which suit is the most powerful. Must be an integer in the range 0-3.

    Returns:
        numpy.ndarray: An array representing the ordering of the suits.
    """
    assert type(trump) == int, "Trump must be an integer"
    assert trump in {0, 1, 2, 3}, "Trump must be in the range 0-3"

    order = np.arange(4)
    order = np.delete(order, np.where(order == trump))
    order = np.insert(order, 0, trump)

    return order

# TODO: Add function to act like get_card_list, but give array of int's
# that may give more versatility. See convert_cards_to_strings as reference.

def get_card_list(trump: int) -> np.ndarray:
    # TODO: Modify function to return int list and use convert_cards_to_strings 
    # afterwards in an additional function
    """
    Calculates the array of 32 cards in string representation based on the trump of the game.

    Parameters:
        trump (int): The trump suit of the game.

    Returns:
        numpy.ndarray: An array of 32 cards in string representation.
    """
    ordering = get_suit_ordering(trump)
    ordered_suits = SUITS[ordering]

    # Create the 32 cards
    ranks = np.tile(RANKS, 4).reshape(4, 8)
    suits = np.tile(ordered_suits[:, None], 8).reshape(4, 8)
    cards = np.char.add(ranks, suits)

    return cards.flatten()

def convert_cards_to_strings(cards: np.ndarray, trump: int) ->  np.ndarray:
    """
    Converts a boolean array of size 32 representing the cards to be displayed into a list of card strings.

    Parameters:
        cards (np.ndarray): A boolean array of size 32 representing the cards to be displayed.
        trump (int): An integer representing the ordering of the suits.

    Returns:
        List[str]: A list of card strings.
    """
    assert type(cards) == np.ndarray, "Cards must be a numpy array"
    assert cards.shape == (32,), "Cards must be a 1D array of length 32"
    assert cards.dtype == bool, "Cards must be a boolean array"

    # Get the card list
    card_list = get_card_list(trump)
    selected_cards = card_list[cards]

    return selected_cards

# TODO: Convert convert_* functions into singular class for centralised management
def convert_boolean_matrix(matrix: np.ndarray, trump: int) -> List[np.ndarray]:
    """
    Converts a boolean matrix of size (n, 32) representing the cards to be displayed into a list of card strings.

    Parameters:
        matrix (np.ndarray): A boolean matrix of size (n, 32) representing the cards to be displayed.
        trump (int): An integer representing the ordering of the suits.

    Returns:
        List[np.ndarray]: A list of card strings.
    """
    assert type(matrix) == np.ndarray, "Matrix must be a numpy array"
    assert matrix.shape[1] == 32, "Matrix must have 32 columns"
    assert matrix.dtype == bool, "Matrix must be a boolean array"

    card_list = get_card_list(trump)

    # Get the selected cards for each row (location)
    selected_cards = [card_list[cards] for cards in matrix]

    return selected_cards

if __name__ == '__main__':
    matrix = np.zeros((4, 32), dtype=bool)
    matrix[0, [3,6,8]] = True
    matrix[1, [4,5,11]] = True
    trump = 2

    output = convert_boolean_matrix(matrix, trump)
    print(output)