import numpy as np
#from frontend.input import Move

class State:
    def __init__(self, state_matrix: np.ndarray):
        """
        Initialise the state wrapper using the given state matrix.

        Parameters:
            state_matrix (np.ndarray): A boolean array of shape (6,32) representing the state of the game.
        """
        # Check that the state matrix is a numpy array of the correct shape
        assert type(state_matrix) == np.ndarray, "State matrix must be a numpy array"
        assert state_matrix.shape == (6,32), "State matrix must have shape (6,32)"
        # assert state_matrix.dtype == bool, "State matrix must be a boolean array"

        self.state_matrix = state_matrix

    def get_state_matrix(self) -> np.ndarray:
        """
        Get the state matrix of the game.

        Returns:
            np.ndarray: The state matrix of the game.
        """
        return self.state_matrix
    
    def get_p0_cards(self) -> np.ndarray:
        """
        Get the cards held by player 0.

        Returns:
            np.ndarray: A boolean array of size 32 representing the cards held by player 0.
        """
        return self.state_matrix[0]
    
    def get_p1_cards(self) -> np.ndarray:
        """
        Get the cards held by player 1.

        Returns:
            np.ndarray: A boolean array of size 32 representing the cards held by player 1.
        """
        return self.state_matrix[1]
    
    def get_unplayed_cards(self) -> np.ndarray:
        """
        Get the cards that have not been played yet.

        Returns:
            np.ndarray: A boolean array of size 32 representing the cards that have not been played yet.
        """
        return self.state_matrix[2]
    
    def get_left_to_defend_cards(self) -> np.ndarray:
        """
        Get the cards that are left to defend.

        Returns:
            np.ndarray: A boolean array of size 32 representing the cards that are left to defend.
        """
        return self.state_matrix[3]
    
    def get_cards_on_board(self) -> np.ndarray:
        """
        Get the cards that are currently on the board.
        
        Returns:
            np.ndarray: A boolean array of size 32 representing the cards that are currently on the board.
        """
        return self.state_matrix[4]
    
    def get_metadata(self) -> np.ndarray:
        """
        Get the row of metadata in the state matrix.

        Returns:
            np.ndarray: A boolean array of size 13 representing the metadata of the
        """
        return self.state_matrix[5]
    
    def get_trump_card(self) -> np.ndarray:
        """
        Get the trump card of the game.

        Returns:
            np.ndarray: A boolean array of size 32 representing the trump card of the game.
        """
        return np.append(self.state_matrix[5, :8], np.zeros(24, dtype=bool))
    
    def get_is_p0_turn(self) -> bool:
        """
        Get whether it is player 0's turn.

        Returns:
            bool: True if it is player 0's turn, False otherwise.
        """
        return self.state_matrix[5, 8]
    
    def get_is_p0_attacking(self) -> bool:
        """
        Get whether player 0 is attacking.

        Returns:
            bool: True if player 0 is attacking, False otherwise.
        """
        return self.state_matrix[5, 9]
    
    def get_is_pickup(self) -> bool:
        """
        Get whether the current move is a pickup.

        Returns:
            bool: True if the current move is a pickup, False otherwise.
        """
        return self.state_matrix[5, 10]
    
    def get_is_over(self) -> bool:
        """
        Get whether the game is over.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        return self.state_matrix[5, 11]
    
    def get_p0_won(self) -> bool:
        """
        Get whether player 0 won the game.

        Returns:
            bool: True if player 0 won the game, False otherwise.
        """
        return self.state_matrix[5, 12]
    
    def apply_move(self, move: 'Move'):
        """
        Apply the given move to the state matrix. Does a simple check for validity.

        Parameters:
            move (Move): The move to apply to the state matrix.

        Raises:
            ValueError: If the move is invalid.
        """
        new_state_matrix = move.get_move_matrix() + np.array(self.state_matrix, dtype=int)
        
        if np.any((new_state_matrix != 0) * (new_state_matrix != 1)):
            print(new_state_matrix)
            raise ValueError("State matrix must contain only 0s and 1s")
        
        self.state_matrix = np.array(new_state_matrix, dtype=bool)