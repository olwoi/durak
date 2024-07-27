import numpy as np


ONES = np.ones(32)
ZEROES = np.zeros(32)

def set_hand(hand, random,unplayed):
    for r in random:
        hand[r] = 1
        unplayed[r] = 0
    return hand, unplayed


class Game:
    state: np.ndarray
    """ Folowing is the structure of state, it described all the information in the game
    Row     |       Purpose          | Extra Values Index
    0       |       Player 0's Hand  | 0: Trump Ace, 1: Trump King, etc
    1       |      Player 1's Hand   | 0: Trump Ace, 1: Trump King, etc
    2       |      Unplayed Cards    | 0: Trump Ace, 1: Trump King, etc
    3       |   Cards left to Defend | 0: Trump Ace, 1: Trump King, etc
    4       |   Cards Played on Board| 0: Trump Ace, 1: Trump King, etc
    5       |   Coser | Extra Values | 0: Ace,...,7: Seven, 8: Player 0's Turn,
    5       |       Extra Values     | 9: Player 1's Turn, 10: Player 0 is attacking
    """

    def __init__(self):

        self.state = np.zeros((32, 5))
        # Shuffle deck and deal cards
        deck = np.random.permutation(52)
        self.state[2,0:] = 1 # Set all cards to unplayed
        self.state[0,0:],self.state[2,0:]=set_hand(self.state[0,0:],deck[0:7],self.state[2,0:])
        self.state[1,0:],self.state[2,0:]=set_hand(self.state[1,0:],deck[8:15],self.state[2,0:])
    
    # 
    def user_update(self, move):
        if self.state[5,8] and self.state[0,8]: # Player 0's turn to attack
            legal = self.attack(move,0) # Player 0 attacks
    def attack(self,move,player):
        new = self.state + move
        # Check whether player has been updated correctly
        if self.state[5,8+player] == new[5,8+player]:
            print("Player not updated during attack")
            return False
        # Check that oppononents cards havent changed
        if not np.isclose(self.state[1-player,0:],new[1-player,0:]):
            print("Opponents cards changed during attack")
            return False

        # Isolate all the values of cards that could legally could be added to the board :LegalToAdd
        played = self.state[4,0:7] +self.state[4,8:15] + self.state[4,16:23] + self.state[4,24:31]
        LegaltoAdd = np.zeros(32)
        indices = np.where(played == 1)[0]
        LegaltoAdd[indices] = 1
        LegaltoAdd[indices + 8] = 1
        LegaltoAdd[indices + 16] = 1
        LegaltoAdd[indices + 24] = 1
        leftdefendmove = new[3,0:]
        # Check that the cards that are being added where in the players hand
        # ONES@new[3,0:].T Whatever cards that have been added by the player
        # self.state[4,0:]@new[3,0:].T The cards that have been played that are also in the had previously

        if np.allclose(ONES@new[3,0:].T,self.state[4,0:]@new[3,0:].T):
            print("Player added cards that were not in their hand")
            return False

        # Cant add card that has not been played UNLESS it is the first move
        if np.isclose(np.sum(leftdefendmove),np.dot(LegaltoAdd,leftdefendmove)): 
            print("Player added cards that were not on the board")
            return False


        
        
        
        return new, LegaltoAdd
            
        
    


if __name__ == '__main__':
    game = Game()
        
