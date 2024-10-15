from state_wrapper import State
from card_visualiser import CardVisualiser, RANKS, SUITS
import numpy as np

class BoardVisualiser:
    def __init__(self, state: State, trump_suit: int):
        self.state = state
        self.card_visualiser = CardVisualiser(trump_suit)

    def __str__(self):
        return self.visualise_board()
    
    def visualise_board(self) -> str:
        """
        Visualises the current state of the board.
        
        Returns:
            str: A string representation of the current state of the board.
        """
        p0_cards = self.card_visualiser.convert_cards_to_strings(self.state.get_p0_cards())
        p1_cards = self.card_visualiser.convert_cards_to_strings(self.state.get_p1_cards())
        unplayed_cards = self.card_visualiser.convert_cards_to_strings(self.state.get_unplayed_cards())
        left_to_defend_cards = self.card_visualiser.convert_cards_to_strings(self.state.get_left_to_defend_cards())
        cards_on_board = self.card_visualiser.convert_cards_to_strings(self.state.get_cards_on_board())
        metadata = self.state.get_metadata()
        
        p0_cards_str = self._get_player_cards_str(p0_cards, 0)
        p1_cards_str = self._get_player_cards_str(p1_cards, 1)
        unplayed_cards_str = self._get_metadata_str(unplayed_cards, metadata)
        left_to_defend_cards_str = self._get_left_to_defend_cards_str(left_to_defend_cards)
        cards_on_board_str = self._get_cards_on_board_str(cards_on_board, left_to_defend_cards)
        
        #return f"{p0_cards_str}\n\n{p1_cards_str}\n\n{unplayed_cards_str}\n\n{left_to_defend_cards_str}\n\n{cards_on_board_str}"
        return "\n\n".join([unplayed_cards_str, cards_on_board_str, left_to_defend_cards_str, p0_cards_str, p1_cards_str,])
    
    def _get_player_cards_str(self, player_cards: np.ndarray, player_id: int) -> str:
        """
        Gets the string representation of a player's cards.
        
        Parameters:
            cards (np.ndarray): The cards of the player.
            player_id (int): The ID of the player.
        
        Returns:
            str: A string representation of the player's cards.
        """
        player_str = f"Player {player_id} cards: "
        player_str += " ".join(player_cards)
        
        return player_str
    
    def _get_metadata_str(self, unplayed_cards: np.ndarray, metadata: np.ndarray) -> str:
        n_unplayed_cards = len(unplayed_cards)
        # TODO: Change back after verification
        # unplayed_str = f"Number of unplayed (in deck) cards: {n_unplayed_cards}"
        unplayed_str = " ".join(unplayed_cards)

        trump_rank = RANKS[metadata[:8].argmax()]
        trump_suit = SUITS[self.card_visualiser.suit_indices[0]]
        trump_str = f"The trump card is: {trump_rank}{trump_suit}"
        
        turn_str = f"It is currently Player {int(~metadata[8])}'s turn"
        attacker_str = f"Attacker: Player {int(~metadata[9])}"

        return "\n".join([unplayed_str, trump_str, attacker_str, turn_str])
    
    def _get_left_to_defend_cards_str(self, left_to_defend_cards: np.ndarray) -> str:
        """
        Gets the string representation of the cards left to defend.
        
        Parameters:
            cards (np.ndarray): The cards left to defend.
        
        Returns:
            str: A string representation of the cards left to defend.
        """
        left_to_defend_str = f"Cards left to defend: "
        left_to_defend_str += " ".join(left_to_defend_cards)
        
        return left_to_defend_str
    
    def _get_cards_on_board_str(self, cards_on_board: np.ndarray, left_to_defend_cards: np.ndarray) -> str:
        """
        Gets the string representation of the cards on the board.
        
        Parameters:
            cards_on_board (np.ndarray): The cards currently on the board.
            left_to_defend_cards (np.ndarray): The cards that are left to defend.
        
        Returns:
            str: A string representation of the cards on the board.
        """
        cards_on_board_str = f"Cards on board (no longer needed to defend): "

        cards_on_board_not_to_defend = np.setdiff1d(cards_on_board, left_to_defend_cards)
        cards_on_board_str += " ".join(cards_on_board_not_to_defend)
        
        return cards_on_board_str
    
if __name__ == "__main__":
    matrix = np.zeros((6, 32), dtype=bool)

    matrix[0, [0,1,2,3,12,5,20]] = True
    matrix[1, [6,7,8,9,10,11,21]] = True
    matrix[2, [4,13,14,15,16,17,26,27,28,29,30,31,18,19,22]] = True
    matrix[3, [23]] = True
    matrix[4, [23,24,25]] = True
    matrix[5, [4,8]] = True

    state = State(matrix)
    board_visualiser = BoardVisualiser(state, 0)
    print(board_visualiser)