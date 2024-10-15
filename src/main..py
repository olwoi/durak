from backend.game import *
from frontend.board_visualiser import *

game = Game()
statewrapper = State(game.state)
board_visualiser = BoardVisualiser(statewrapper,0)
print(board_visualiser)
