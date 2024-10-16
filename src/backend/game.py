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
    5       |       Extra Values     | 9: Player 0 is attacking, 10 is pickup, 11 is_over, 12 P0_won
    """

    def __init__(self):

        self.state = np.zeros((6, 32), dtype=bool)
        # Shuffle deck and deal cards
        deck = np.random.permutation(32)
        coser = np.random.randint(0,7)
        deck = deck[np.where(deck != coser)]
        

        self.state[2,0:] = 1 # Set all cards to unplayed
        self.state[0,0:],self.state[2,0:]=set_hand(self.state[0,0:],deck[0:6],self.state[2,0:])
        self.state[1,0:],self.state[2,0:]=set_hand(self.state[1,0:],deck[6:12],self.state[2,0:])
        self.deck = np.append(deck[12:],coser)

        self.state[5,coser] = 1

    #Legacy Code
    def send_state(self,boolean):
        return self.state,boolean

    # Legacy code
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
        Returns:
            valid: Bool True if the move played is valid and executed
            Beaten: Bool True if no cards where added to left to defend

        """
        assert np.allclose(move[1-player], ZEROES) # Opponents hand doesnt change
        assert np.allclose(move[2,:],ZEROES) #Cards arent being pulled

        new = self.state + move
        
        
        # Check whether player has been updated correctly
        # Check that oppononents cards havent changed
        
        if not np.isclose(self.state[1-player,0:],new[1-player,0:]): # Opponents hand is the same post and pre move
            print("Opponents cards changed during attack")
            return (False, False)
        
        #Any card that is added to left 2 defend hast to be also added to cards on board
        if not np.allclose(move[3,0:],move[4,0:]): 
            print("Cards played on board not updated")
            return (False, False)


        # Isolate all the values of cards that could legally could be added to the board :LegalToAdd
        played = self.state[4,0:8] +self.state[4,8:16] + self.state[4,17:23] + self.state[4,24:31]
        played[np.where(played>=1)] = 1
        if np.allclose(played, ZEROES): #Empty board any attack is legal
            LegaltoAdd = np.ones(32)
            added2 = new[3,:7] + new[3,8:15] + new[3,16:23]
            if len(np.unique(played)!= 1): # Ensure only one denomination of card is played
                return (False, False)
            if np.sum(new[3,:])<= np.sum(new[1-player,:]):
                self.state = new
                return (True, False)
            else:
                print("Defender doesnt have enough cards")
                return (False,False)
            
        else: #Board is not empty
            if np.sum(move) == 0:
                return (True, True)
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
            return (False, False)

        # Cant add card that has not been played 
        if np.isclose(np.sum(leftdefendmove),np.dot(LegaltoAdd,leftdefendmove)): 
            if np.sum(new[3,:])<= np.sum(new[1-player,:]):
                self.state = new
                return (True, False)
            else:
                print("Defender doesnt have enough cards")
                return (False,False)
        else:
        
            print("Cant add card that hasnt been played")
            return False, False
    def defend(self,move,player):
        """
        Calls _defend and sets self.state if appropriate
        """
        valid,is_redirect,is_complete = self._defend(move,player)
        if valid:
            self.state = np.array(self.state+move,dtype=bool)
        return (valid,is_redirect,is_complete)
    def _defend(self,move,player):
        """
        Checks that move is a valid defence, meaning that all cards that were being attacked where defended
        To do this following needs to be checked:
        - The left to be defended cards (row 3 ) are 0 after move
        - The cards that were used in defence (move row 4) were in the hand of the player (row player)
        - The cards that were used in defence (move row 4) were on the board (row 4)
        - The cards that were used in defence (move row 4) are no longer in the hand of the player (row player)
        Params:
            move: newstate - self.state
            player: player thats playing
        
        Returns:
            valid: Bool
            
        """
        new = self.state + move
        assert np.allclose(move[1-player], ZEROES) # Opponents hand doesnt change
        assert np.allclose(move[2,:],ZEROES) #Cards arent being pulled
        

        if np.sum(new[3,:]) >= np.sum(self.state[3,:]): # Attempted redirect or flash
            if np.sum(self.state[4:0]-self.state[3,:]) != 0:
                return (False,False,False) # Cant redirect if you already started defending
            
            rankonboard = self.state[4,0:8] +self.state[4,8:16] + self.state[4,17:23] + self.state[4,24:31]
            
            if np.sum(move[3,:]) == 0 and np.allclose(move[player,:],ZEROES) : 
                if self.state[player,np.where(rankonboard>=1)[0]] != 1:
                    print("player doesnt have the trump card to redirect")
                    return (False,False,False)
                else:
                    return (True,True,False)
            else: #TODO Check for redirect
                redirectedcard = np.where(move[3,:]==1)
                if np.allclose(np.where(rankonboard==1),(redirectedcard%7)): #The card added by move must be of same rank 
                    return (True,True,False)
                else:
                    print("Card of wrong rank used to redirect")
                    return (False,False,False)   
        else:
            if np.sum(new[3,:])+1==np.sum(self.state[3,:]) and (np.sum(move[4,:] == 2)): # Attempted Defense of exactly 1 card
                cardsdefended  = np.where(move==-1)[0]

                cardsused = ZEROES - move[3,:]
                if not np.allclose(cardsused @ self.state[player,:].T, cardsused):
                    print(f'Cards have been used that arent in player {player}`s hand')
                    return (False,False,False)
                else:
                    if np.sum(new[3,:]) == 0:
                        return (True,False,True)
                    return(True,False,False)
            else:
                print("Unaccouted for sequence")
                return (False,False,False)
                
    def check_wurf(self,move,player):
        assert move[3,:] - move[player, :] == 0
        if not np.allclose(self.state[player,:]@move[3,:].T,move[3,:].T):
            print("Player added a card thats not in their hand")
            return False
        
        played = self.state[4,0:8] +self.state[4,8:16] + self.state[4,17:23] + self.state[4,24:31]
        played[np.where(played>=1)] = 1
        LegaltoAdd = np.zeros(32)
        indices = np.where(played == 1)[0]
        LegaltoAdd[indices] = 1
        LegaltoAdd[indices + 8] = 1
        LegaltoAdd[indices + 16] = 1
        LegaltoAdd[indices + 24] = 1

        leftdefendmove = self.state[3,:] + move[3,:]
        if np.isclose(np.sum(leftdefendmove),np.dot(LegaltoAdd,leftdefendmove)):
            return True
        else:
            print("Cant add card that hasnt been played")
            return False

        pass

    def ExecutePickup(self,player):
        """
        Empties left2def and onboard and gives these cards to player
        """

        self.state[player,:] +=self.state[4,:]
        self.state[3,:] = False
        self.state[4,:] = False 

        return

    def drawto6(self,attacker,rek=False):
        """
        Draws cards for attacker first then for defender, if there are no cards left at a point sets winner variables
    
        """
        cardsleftattacker = np.sum(self.state[attacker,:])
        cardsleft = len(self.deck)
        if cardsleftattacker <6:
            if cardsleft == 0 and cardsleftattacker == 0:
                self.state[5,11] = 1
                self.state[5,12] = 1-attacker
                return
            else:
                if cardsleft < 6-cardsleftattacker:
                    self.state[attacker,self.deck] = 1
                    self.state[2,self.deck] = 0
                    self.deck = []
                else:
                    self.state[attacker,self.deck[0:6-cardsleftattacker]] = 1
                    self.state[2,self.deck[0:6-cardsleftattacker]] = 0
                    self.deck = self.deck[6-cardsleftattacker:]
        if not rek:
            self.drawto6(1-attacker,rek=True)


if __name__ == '__main__':
    game = Game()
        
