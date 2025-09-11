from durak_model import DurakModel
from game import Game

class GameManager:
    def __init__(self, max_moves: int):
        """
        Initialize the GameManager with two Durak models, a Game instance, and a maximum number of moves.

        Args:
            max_moves (int): The maximum number of moves allowed in the game.
        """
        self.model_1 = DurakModel()  # First Durak model
        self.model_2 = DurakModel()  # Second Durak model
        self.game = Game()           # Instance of the Game class
        self.max_moves = max_moves   # Maximum number of moves allowed
        self.current_move_count = 0  # Tracks the number of moves played
