import numpy as np
from enum import Enum

RANKS = np.array(['A', 'K', 'Q', 'J', 'T', '9', '8', '7'])
SUITS = np.array(['♠', '♣', '♦', '♥'])

class StateMatrix(Enum):
    """
    Represents the different rows present in the state matrix for
    easier indexing and readability.
    """
    PLAYER_0: int = 0
    PLAYER_1: int = 1
    UNPLAYED: int = 2
    LEFT2DEF: int = 3
    ON_BOARD: int = 4
    METADATA: int = 5

class MoveType(Enum):
    """
    Represents the different types of moves that a player can make.
    """
    ATTACK = 0
    DEFEND = 1
    NRW = 2  # Nachwerfen