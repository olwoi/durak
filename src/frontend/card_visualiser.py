import numpy as np

RANKS = np.array(['A', 'K', 'Q', 'J', 'T', '9', '8', '7'])
SUITS = np.array(['♠', '♣', '♦', '♥'])

class CardVisualiser():
    def __init__(self, trump_suit: int):
        self.set_suit_ordering(trump_suit)
        self.set_card_list()

    def set_suit_ordering(self, trump_suit: int):
        """
        Get the ordering of the suits in the game based on a trump suit.
        
        The order is determined by placing the trump suit first, followed by the rest of the suits in their default order.

        Parameters:
            trump (int): The trump suit, which defines which suit is the most powerful. Must be an integer in the range 0-3.

        Returns:
            numpy.ndarray: An array representing the ordering of the suits.
        """
        assert type(trump_suit) == int, "Trump must be an integer"
        assert trump_suit in {0, 1, 2, 3}, "Trump must be in the range 0-3"

        order = np.arange(4)
        order = np.delete(order, np.where(order == trump_suit))
        order = np.insert(order, 0, trump_suit)

        self.suit_indices = order
    
    def set_card_list(self) -> np.ndarray:
        """
        Calculates the array of 32 cards in string representation based on the trump of the game.

        Returns:
            numpy.ndarray: An array of 32 cards in string representation.
        """
        ordered_suits = SUITS[self.suit_indices]

        # Create the 32 cards
        ranks = np.tile(RANKS, 4).reshape(4, 8)
        suits = np.tile(ordered_suits[:, None], 8).reshape(4, 8)
        cards = np.char.add(ranks, suits)

        self.card_list = cards.flatten()
    
    def convert_cards_to_strings(self, cards: np.ndarray) -> np.ndarray:
        """
        Converts a boolean array of size 32 representing the cards to be displayed into a list of card strings.

        Parameters:
            cards (np.ndarray): A boolean array of size 32 representing the cards to be displayed.

        Returns:
            np.ndarray: A list of card strings.
        """
        assert type(cards) == np.ndarray, "Cards must be a numpy array"
        assert cards.shape == (32,), "Cards must be a 1D array of length 32"
        # assert cards.dtype == bool, "Cards must be a boolean array"

        # Retrieve selected cards from card list
        selected_cards = self.card_list[cards]

        return selected_cards
