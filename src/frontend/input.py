import numpy as np
from frontend.state_wrapper import State
from frontend.card_visualiser import CardVisualiser
from frontend.board_visualiser import BoardVisualiser
from typing import Optional
from frontend.constants import MoveType, StateMatrix

class Move:
    def __init__(self, move_type: MoveType, move_matrix: Optional[np.ndarray] = None):
        assert type(move_type) == MoveType, "Move type must be a MoveType"

        if move_matrix is not None:
            assert type(move_matrix) == np.ndarray, "Move matrix must be a numpy array"
            assert move_matrix.shape == (6,32), "Move matrix must have shape (6,32)"
            assert move_matrix.dtype == bool, "Move matrix must be a boolean array"
            self.move_matrix = move_matrix
        else:
            self.move_matrix = np.zeros((6, 32), dtype=bool)

        self.move_type = move_type

    def get_move_matrix(self) -> np.ndarray:
        return self.move_matrix
    
    def get_move_type(self) -> MoveType:
        return self.move_type
    
    def set_move_row(self, row_index: int, row: np.ndarray): # FIXME:
        if row_index < 0 or row_index >= 6:
            raise ValueError("Row index must be between 0 and 5")
        if row.shape != (32,):
            raise ValueError("Row must have shape (32,)")
        if row.dtype != bool:
            raise ValueError("Row must be a boolean array")
        
        self.move_matrix[row_index] = row
    
    def __add__(self, other):
        if type(other) != Move:
            raise ValueError("Cannot add a Move object with a non-Move object")
        
        if self.move_type != other.get_move_type():
            raise ValueError("Cannot add moves of different types")
        
        return Move(self.move_type, self.move_matrix + other.get_move_matrix())

class Player:
    def __init__(self, player_id: int, trump: int):
        assert type(player_id) == int, "Player ID must be an integer"
        assert player_id in {0, 1}, "Player ID must be 0 or 1"

        self.player_id = player_id
        self.card_visualiser = CardVisualiser(trump)
        self.trump = trump

    def get_player_id(self) -> int:
        return self.player_id
    
    def get_own_cards_selection(self, own_cards_str: list) -> str:
        # Create headers
        headers = ["Index"] + [str(i) for i in range(len(own_cards_str))]

        # Create rows with index and card strings
        rows = [["Card"] + own_cards_str.tolist()]

        # Calculate column widths
        col_widths = [max(len(item) for item in col) for col in zip(*([headers] + rows))]

        # Create a format string for each row
        row_format = " | ".join("{:<" + str(width) + "}" for width in col_widths)

        # Print the headers
        selection_str_components = []
        selection_str_components.append(row_format.format(*headers))
        selection_str_components.append("-" * (sum(col_widths) + 3 * (len(headers) - 1)))

        # Print each row
        for row in rows:
            selection_str_components.append(row_format.format(*row))

        return "\n".join(selection_str_components)

    def select_own_card(self, state_wrapper: State):
        own_cards = state_wrapper.get_p0_cards() if self.player_id == 0 else state_wrapper.get_p1_cards()
        own_cards_str = self.card_visualiser.convert_cards_to_strings(own_cards)

        own_card_selection = self.get_own_cards_selection(own_cards_str)
        
        print(own_card_selection)

        while True:
            try:
                selected_card_index = int(input("Select the index of the card you want to play: "))
            except ValueError:
                print(f"Invalid input. Please enter a number between 0 and {len(own_cards_str) - 1}.")
                continue

            if selected_card_index < 0 or selected_card_index >= len(own_cards_str):
                print(f"Invalid index. Please enter a number between 0 and {len(own_cards_str) - 1}.")
                continue
            else:
                break

        selected_card = np.zeros(32, dtype=int)
        selected_card[np.where(own_cards)[0][selected_card_index]] = True

        # print(self.card_visualiser.convert_cards_to_strings(selected_card))

        return selected_card

    def get_attack(self, state_matrix: np.ndarray):
        current_state = State(state_matrix)
        current_move = Move(MoveType.ATTACK)

        print("It is your turn to attack.")
        while True:
            print("Controls: view board (b), select card (s), end turn (e).")
            command = input("Enter command: ")
            if command == "b":
                print(BoardVisualiser(current_state.get_state_matrix(), self.trump)) # TODO:  Modify BoardVisualiser to take in state object?

            elif command == "s":
                selected_card = self.select_own_card(current_state)
                new_move = Move(MoveType.ATTACK)
                new_move.set_move_row(0, - np.array(selected_card, dtype=bool)) # FIXME:
                current_move += new_move

            elif command == "e":
                break
            
            else:
                print("Invalid command. Please enter 'b', 's', or 'e'.")

        return current_move



if __name__ == "__main__":
    p = Player(0, 0)
    matrix = np.zeros((6, 32), dtype=bool)
    matrix[0, [0,1,2,3,12,5]] = True
    print(p.get_attack(matrix))