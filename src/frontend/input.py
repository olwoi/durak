import numpy as np
from frontend.state_wrapper import State
from frontend.card_visualiser import CardVisualiser
from frontend.board_visualiser import BoardVisualiser
from typing import Optional
from frontend.constants import MoveType, StateMatrix

class Move:
    def __init__(self, move_type: MoveType, move_matrix: Optional[np.ndarray] = None):
        """
        Initialise the move object with the given move type and move matrix.

        Parameters:
            move_type (MoveType): The type of move.
            move_matrix (np.ndarray): A numpy array of shape (6,32) representing the move matrix. Defaults to None.
        """
        assert type(move_type) == MoveType, "Move type must be a MoveType"

        if move_matrix is not None:
            # Validate input matrix if provided
            assert type(move_matrix) == np.ndarray, "Move matrix must be a numpy array"
            assert move_matrix.shape == (6,32), "Move matrix must have shape (6,32)"
            assert move_matrix.dtype == int, "Move matrix must be a int array"
            self.move_matrix = move_matrix

        else:
            # Defaults to empty matrix if not provided
            self.move_matrix = np.zeros((6, 32), dtype=int)

        self.move_type = move_type

    def __str__(self) -> str:
        """
        Convert the move object to a string representation.

        Returns:
            str: A string representation of the move object.
        """
        return f"Move type: {self.move_type}\nMove matrix:\n{self.move_matrix}"

    def get_move_matrix(self) -> np.ndarray:
        """
        Get the move matrix of the move object.

        Returns:
            np.ndarray: The move matrix of the move object.
        """
        return self.move_matrix
    
    def get_move_type(self) -> MoveType:
        """
        Get the move type of the move object.

        Returns:
            MoveType: The move type of the move object.
        """
        return self.move_type
    
    def set_move_row(self, row_index: int, row: np.ndarray):
        """
        Set a row of the move matrix to the given row.

        Parameters:
            row_index (int): The index of the state matrix row to set.
            row (np.ndarray): The row to set it to.

        Raises:
            ValueError: If the row index is not between 0 and 5, the row shape is not (32,), 
                        or the row dtype is not int.
        """
        if row_index < 0 or row_index >= 6:
            raise ValueError("Row index must be between 0 and 5")
        
        if row.shape != (32,):
            raise ValueError("Row must have shape (32,)")
        
        if row.dtype != int:
            raise ValueError("Row must be a integer array")
        
        self.move_matrix[row_index] = row
    
    def __add__(self, other):
        """
        Add two Move objects together.

        Parameters:
            other (Move): The other Move object to add.

        Returns:
            Move: The sum of the two Move objects.
        """
        if type(other) != Move:
            raise ValueError("Cannot add a Move object with a non-Move object")
        
        if self.move_type != other.get_move_type():
            raise ValueError("Cannot add moves of different types")
        
        # Return a new Move object with the sum of the move matrices
        return Move(self.move_type, self.move_matrix + other.get_move_matrix())

class Player:
    def __init__(self, player_id: int, trump: int):
        """
        Initialise the player object with the given player ID and trump suit.

        Parameters:
            player_id (int): The ID of the player. Must be either 0 or 1.
            trump (int): The trump suit of the game. Must be an integer in the range 0-3.
        """
        assert type(player_id) == int, "Player ID must be an integer"
        assert player_id in {0, 1}, "Player ID must be 0 or 1"

        self.player_id = player_id
        self.card_visualiser = CardVisualiser(trump)
        self.trump = trump

    def get_player_id(self) -> int:
        """
        Get the player ID.

        Returns:
            int: The player ID.
        """
        return self.player_id
    
    def get_own_cards_selection(self, own_cards_str: list) -> str:
        """
        Get the selection of the player's own cards as a formatted string.

        Parameters:
            own_cards_str (list): A list of strings representing the player's own cards.

        Returns:
            str: A formatted string representing the selection of the player's own cards.
        """
        # Create headers
        headers = ["Index"] + [str(i) for i in range(len(own_cards_str))]

        # Create rows with index and card strings
        rows = [["Card"] + own_cards_str.tolist()]

        # Calculate column widths
        col_widths = [max(len(item) for item in col) for col in zip(*([headers] + rows))]

        # Create a format string for each row
        row_format = " | ".join("{:<" + str(width) + "}" for width in col_widths)

        # Append headers and separator
        selection_str_components = []
        selection_str_components.append(row_format.format(*headers))
        selection_str_components.append("-" * (sum(col_widths) + 3 * (len(headers) - 1)))

        # Append rows with cards
        for row in rows:
            selection_str_components.append(row_format.format(*row))

        return "\n".join(selection_str_components)

    def select_own_card(self, state_wrapper: State) -> Optional[np.ndarray]:
        """
        Interactively select a card from the player's own cards.

        Parameters:
            state_wrapper (State): The state object representing the current game state.

        Returns:
            Optional[np.ndarray]: A numpy array of size 32 representing the selected card, or None if the selection was cancelled.
        """
        # Get the player's own cards as a list of strings
        own_cards = state_wrapper.get_p0_cards() if self.player_id == 0 else state_wrapper.get_p1_cards()
        own_cards_str = self.card_visualiser.convert_cards_to_strings(own_cards)

        # Print the selection of the player's own cards
        own_card_selection = self.get_own_cards_selection(own_cards_str)
        print(own_card_selection)

        while True:
            # Get the user input for the selected card
            selection_input = input("Select the index of the card you want to play (type 'c' to cancel): ")
            if selection_input == "c":
                # Cancel the selection
                return None
            
            try:
                # Check if the input is a valid index
                selected_card_index = int(selection_input)

            except ValueError:
                print(f"Invalid input. Please enter a number between 0 and {len(own_cards_str) - 1}.")
                continue

            if selected_card_index < 0 or selected_card_index >= len(own_cards_str):
                print(f"Invalid index. Please enter a number between 0 and {len(own_cards_str) - 1}.")
                continue

            else:
                # Break the loop if the input is valid
                break

        # Create the representation for the selected card and return it
        selected_card = np.zeros(32, dtype=int)
        selected_card[np.where(own_cards)[0][selected_card_index]] = True

        return selected_card

    def get_attack(self, state_matrix: np.ndarray) -> Move:
        """
        Interactively create the attack move for the player.

        Parameters:
            state_matrix (np.ndarray): The state matrix representing the current game state.

        Returns:
            Move: The attack move created by the player.
        """
        # Store current state for visualisation and an empty move
        current_state = State(state_matrix)
        current_move = Move(MoveType.ATTACK)

        print("It is your turn to attack.")
        while True:
            # Take user input on move
            print("Controls: view board (b), select card (s), end turn (e).")
            command = input("Enter command: ")

            if command == "b":
                # Show the board state
                print(BoardVisualiser(current_state.get_state_matrix(), self.trump)) # TODO:  Modify BoardVisualiser to take in state object?

            elif command == "s":
                # Select a card to play
                selected_card = self.select_own_card(current_state)

                if selected_card is None:
                    # Skip if cancelled
                    continue
                
                # Create a new move with the selected card
                new_move = Move(MoveType.ATTACK)

                # Update rows of move based on card selection
                if self.player_id == 0:
                    new_move.set_move_row(StateMatrix.PLAYER_0.value, - selected_card)

                else:
                    new_move.set_move_row(StateMatrix.PLAYER_1.value, - selected_card)

                new_move.set_move_row(StateMatrix.LEFT2DEF.value, selected_card)
                new_move.set_move_row(StateMatrix.ON_BOARD.value, selected_card)

                # Apply the move to the current state
                current_state.apply_move(new_move)

                # Update the current move with the new move
                current_move += new_move

            elif command == "e":
                # End the turn
                break
            
            else:
                print("Invalid command. Please enter 'b', 's', or 'e'.")

        return current_move



# if __name__ == "__main__":
#     p = Player(0, 0)
#     matrix = np.zeros((6, 32), dtype=bool)
#     matrix[0, [0,1,2,3,12,5]] = True
#     print(p.get_attack(matrix))