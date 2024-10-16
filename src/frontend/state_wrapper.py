import numpy as np

class State:
    def __init__(self, state_matrix: np.ndarray):
        assert type(state_matrix) == np.ndarray, "State matrix must be a numpy array"
        assert state_matrix.shape == (6,32), "State matrix must have shape (6,32)"
        # assert state_matrix.dtype == bool, "State matrix must be a boolean array"

        self.state_matrix = state_matrix

    def get_state_matrix(self) -> np.ndarray:
        return self.state_matrix
    
    def get_p0_cards(self) -> np.ndarray:
        return self.state_matrix[0]
    
    def get_p1_cards(self) -> np.ndarray:
        return self.state_matrix[1]
    
    def get_unplayed_cards(self) -> np.ndarray:
        return self.state_matrix[2]
    
    def get_left_to_defend_cards(self) -> np.ndarray:
        return self.state_matrix[3]
    
    def get_cards_on_board(self) -> np.ndarray:
        return self.state_matrix[4]
    
    def get_metadata(self) -> np.ndarray:
        return self.state_matrix[5]
    
    def get_trump_card(self) -> np.ndarray:
        return np.append(self.state_matrix[5, :8], np.zeros(24, dtype=bool))
    
    def get_is_p0_turn(self) -> int:
        return self.state_matrix[5, 8]
    
    def get_is_p0_attacking(self) -> int:
        return self.state_matrix[5, 9]
    
    def get_is_pickup(self) -> int:
        return self.state_matrix[5, 10]