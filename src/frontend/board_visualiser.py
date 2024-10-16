from frontend.state_wrapper import State
from frontend.card_visualiser import CardVisualiser
from frontend.constants import RANKS, SUITS
import numpy as np

class BoardVisualiser:
    def __init__(self, state_matrix: np.ndarray, trump_suit: int):
        state_wrapper = State(state_matrix)
        self.state_wrapper = state_wrapper
        self.card_visualiser = CardVisualiser(trump_suit)

    # TODO: Add a set_state_matrix function 

    def __str__(self):
        return self.visualise_board()
    
    def visualise_board(self) -> str:
        p0_cards = self.card_visualiser.convert_cards_to_strings(self.state_wrapper.get_p0_cards())
        p1_cards = self.card_visualiser.convert_cards_to_strings(self.state_wrapper.get_p1_cards())
        unplayed_cards = self.card_visualiser.convert_cards_to_strings(self.state_wrapper.get_unplayed_cards())
        left_to_defend_cards = self.card_visualiser.convert_cards_to_strings(self.state_wrapper.get_left_to_defend_cards())
        cards_on_board = self.card_visualiser.convert_cards_to_strings(self.state_wrapper.get_cards_on_board())
        
        p0_cards_str = self._get_player_cards_str(p0_cards, 0)
        p1_cards_str = self._get_player_cards_str(p1_cards, 1)
        metadata_str = self._get_metadata_str(unplayed_cards)
        left_to_defend_cards_str = self._get_left_to_defend_cards_str(left_to_defend_cards)
        cards_on_board_str = self._get_cards_on_board_str(cards_on_board, left_to_defend_cards)
        
        #return f"{p0_cards_str}\n\n{p1_cards_str}\n\n{unplayed_cards_str}\n\n{left_to_defend_cards_str}\n\n{cards_on_board_str}"
        return "\n\n".join([metadata_str, cards_on_board_str, left_to_defend_cards_str, p0_cards_str, p1_cards_str,])
    
    def _get_player_cards_str(self, player_cards: np.ndarray, player_id: int) -> str:
        player_str = f"Player {player_id} cards: "
        player_str += " ".join(player_cards)
        
        return player_str
    
    def _get_metadata_str(self, unplayed_cards: np.ndarray) -> str:
        if self.state_wrapper.get_is_over():
            unplayed_str = f"---> GAME OVER, no cards left to draw. Player {int(not self.state_wrapper.get_p0_won())} won! <---"
        else:
            n_unplayed_cards = len(unplayed_cards)
            unplayed_str = f"Number of unplayed (in deck) cards: {n_unplayed_cards}"
            # unplayed_str = " ".join(unplayed_cards)

        trump_card = self.state_wrapper.get_trump_card()
        trump_str = f"The trump card is: {self.card_visualiser.convert_cards_to_strings(trump_card)}"
        
        turn_str = f"Turn: Player {int(not self.state_wrapper.get_is_p0_turn())}"
        attacker_str = f"Attacker: Player {int(not self.state_wrapper.get_is_p0_attacking())}"

        return "\n".join([unplayed_str, trump_str, attacker_str, turn_str])
    
    def _get_left_to_defend_cards_str(self, left_to_defend_cards: np.ndarray) -> str:
        left_to_defend_str = f"Cards left to defend: "
        left_to_defend_str += " ".join(left_to_defend_cards)
        
        return left_to_defend_str
    
    def _get_cards_on_board_str(self, cards_on_board: np.ndarray, left_to_defend_cards: np.ndarray) -> str:
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