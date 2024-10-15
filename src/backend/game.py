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
    deck: np.ndarray
    """ Folowing is the structure of state, it described all the information in the game
    Row     |       Purpose          | Extra Values Index
    0       |       Player 0's Hand  | 0: Trump Ace, 1: Trump King, etc
    1       |      Player 1's Hand   | 0: Trump Ace, 1: Trump King, etc
    2       |      Unplayed Cards    | 0: Trump Ace, 1: Trump King, etc
    3       |   Cards left to Defend | 0: Trump Ace, 1: Trump King, etc
    4       |   Cards Played on Board| 0: Trump Ace, 1: Trump King, etc
    5       |   Coser | Extra Values | 0: Ace,...,7: Seven, 8: Player 0's Turn,
    5       |       Extra Values     | 9: Player 0 is attacking
    """

    def __init__(self):

        self.state = np.zeros((32, 6))
        # Shuffle deck and deal cards
        deck = np.random.permutation(32)
        coser = np.random.randint(0,7)
        deck = deck[np.where(deck != coser)]

        self.state[2,0:] = 1 # Set all cards to unplayed
        self.state[0,0:],self.state[2,0:]=set_hand(self.state[0,0:],deck[0:6],self.state[2,0:])
        self.state[1,0:],self.state[2,0:]=set_hand(self.state[1,0:],deck[6:12],self.state[2,0:])
        self.deck = deck[12:]

        self.state[5,coser] = 1

    
    def send_state(self,boolean):
        return self.state,boolean


    def user_update(self, move):
        if self.state[5,8] and self.state[5,9]: # Player 0's turn to attack
            legal = self.attack(move,0) # Player 0 attacks
            if not legal:
                self.send_state(False)
            else: 
                self.state[5,8] = 0
                self.send_state(True)
        elif not self.state[5,8] and not self.state[5,9]: # Player 1's turn to attack
            legal = self.attack(move,1) # Player 1 attacks
            if not legal:
                self.send_state(False)
            else:  
                self.state[5,8] = 1
                self.send_state(True)
        elif self.state[5,8] and not self.state[5,10]: # Player 0's turn to defend
            pass
    

        
    def attack(self,move,player):
        """
        Checks whether move is legal if so updates it and returns true, false otherwise
        
        Params:
            move: ndarray() Changes made to state by player
            player: 0-1 indicates what player attempted to do this move
        
        """
        assert np.allclose(move[1-player], ZEROES) # Opponents hand doesnt change
        assert np.allclose(move[2,:],ZEROES) #Cards arent being pulled

        #TODO make sure that opponent has enough cards left 2 defend

        new = self.state + move
        
        
        # Check whether player has been updated correctly
        # Check that oppononents cards havent changed
        
        if not np.isclose(self.state[1-player,0:],new[1-player,0:]): # Opponents hand is the same post and pre move
            print("Opponents cards changed during attack")
            return False
        
        #Any card that is added to left 2 defend hast to be also added to cards on board
        if not np.allclose(move[3,0:],move[4,0:]): 
            print("Cards played on board not updated")
            return False


        # Isolate all the values of cards that could legally could be added to the board :LegalToAdd
        played = self.state[4,0:8] +self.state[4,8:16] + self.state[4,17:23] + self.state[4,24:31]
        played[np.where(played>=1)] = 1
        if np.allclose(played, ZEROES): #Empty board any attack is legal
            LegaltoAdd = np.ones(32)
            added2 = new[3,:7] + new[3,8:15] + new[3,16:23]
            if len(np.unique(played)!= 1): # Ensure only one denomination of card is played
                return False
            self.state = new
            return True
            
        else:
            LegaltoAdd = np.zeros(32)
            
            #Make multiple occurences of cards of same denomination be no issue
            
            indices = np.where(played == 1)[0]
            LegaltoAdd[indices] = 1
            LegaltoAdd[indices + 8] = 1
            LegaltoAdd[indices + 16] = 1
            LegaltoAdd[indices + 24] = 1
        leftdefendmove = new[3,0:]


        # Check that the cards that are being added where in the players hand
        # ONES@new[3,0:].T Whatever cards that have been added by the player
        # self.state[player,0:]@new[3,0:].T The cards that have been played that are also in the had previously

        if np.allclose(ONES@new[3,0:].T,self.state[player,0:]@new[3,0:].T):
            print("Player added cards that were not in their hand")
            return False

        # Cant add card that has not been played UNLESS it is the first move
        if np.isclose(np.sum(leftdefendmove),np.dot(LegaltoAdd,leftdefendmove)): 
            if not np.isclose(np.sum(indices),0):
                self.state = new
                return True
            print("Player added cards that were not on the board")
            return False
        

        self.state = new
        return True
    
    def defend(self,move,player):
        """
        Checks that move is a valid defence, meaning that all cards that were being attacked where defended
        To do this following needs to be checked:
        - The left to be defended cards (row 3 ) are 0 after move
        - The cards that were used in defence (move row 4) were in the hand of the player (row player)
        - The cards that were used in defence (move row 4) were on the board (row 4)
        - The cards that were used in defence (move row 4) are no longer in the hand of the player (row player)

        """
        new = self.state + move
        assert np.allclose(move[1-player], ZEROES) # Opponents hand doesnt change
        assert np.allclose(move[2,:],ZEROES) #Cards arent being pulled
        

        if np.sum(new[3,:]) != 0: # Attempted redirect or flash
            if np.sum(self.state[4:0]) != 0:
                return False # Cant redirect if you already started defending
            if np.sum(move[3,:]) == 0: #TODO Check for flash

                pass
            else: #TODO Check for redirect
                pass
        else:
            if np.sum(new[3,:])+1==np.sum(self.state[3,:]) and (np.sum(move[4,:] == 2)): # Attempted Defense of exactly 1 card
                cardsdefended  = np.where(move==-1)[0]

                cardsused = move[4,:]-move[np.where(move==-1)]
                if not np.allclose(cardsused @ self.state[player,:], cardsused):
                    print(f'Cards have been used that arent in player {player}`s hand')
                    return False
                pass
            else: #attempted pickup
                #TODO
                pass

        pass
    


            
        
    


if __name__ == '__main__':
    game = Game()
        
