from backend.game import *
from frontend.board_visualiser import *

game = Game()
board_visualiser = BoardVisualiser(game.state,0)
print(board_visualiser)
