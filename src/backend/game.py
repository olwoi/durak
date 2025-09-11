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
        np.random.seed(47)

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
        
        # Initialize game state: Player 0 starts and is attacking
        self.state[5,8] = 1  # Player 0's turn
        self.state[5,9] = 1  # Player 0 is attacking
        self._defense_matrix = self._build_defense_matrix()

    
    def _build_defense_matrix(self):
        """
        Precompute which cards can defend which attacks in a 32x32 boolean matrix.
        
        Matrix Structure:
        - Rows represent attacking cards (0-31)
        - Columns represent defending cards (0-31) 
        - defense_matrix[attack_card][defend_card] = True if defend_card can beat attack_card
        
        """
        defense_matrix = np.zeros((32, 32), dtype=bool)
        
        cards = np.arange(32)
        suits = cards // 8
        ranks = cards % 8
        
        # Vectorized computation of all defense relationships
        for attack_card in range(32):
            attack_suit, attack_rank = attack_card // 8, attack_card % 8
            
            # Same suit, higher rank
            same_suit = (suits == attack_suit) & (ranks > attack_rank)
            # Trump vs non-trump
            trump_defense = (suits == 0) & (attack_suit != 0)
            
            defense_matrix[attack_card] = same_suit | trump_defense
        
        return defense_matrix

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
        out = self._attack(move,player)
        self.state = np.array(self.state,dtype=bool)
        return out
        
    def _attack(self,move,player):
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
        
        if not np.allclose(self.state[1-player,0:],new[1-player,0:]): # Opponents hand is the same post and pre move
            print("Opponents cards changed during attack")
            return (False, False)
        
        #Any card that is added to left 2 defend hast to be also added to cards on board
        if not np.allclose(move[3,0:],move[4,0:]): 
            print("Cards played on board not updated")
            return (False, False)
        if not np.allclose(-move[player,:], move[3,:]):
            print("Card removed without adding to board")
            return(False,False)
        if not np.allclose(new[3,0:],self.state[player,0:]*new[3,0:]):
            print("Player added cards that were not in their hand")
            return (False, False)


        # Isolate all the values of cards that could legally could be added to the board :LegalToAdd
        played = self.state[4,0:8] +self.state[4,8:16] + self.state[4,16:24] + self.state[4,24:32]
        played[np.where(played>=1)] = 1
        if np.allclose(played, np.zeros(8)): #Empty board any attack is legal

            LegaltoAdd = np.ones(32)
            added2 = new[3,:8] + new[3,8:16] + new[3,16:24] + new[3,24:]
            
            if len(added2[np.where(added2!= 0)])>= 2: # Ensure only one denomination of card is played
                print("more than 1 denomination")
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
            if np.sum(self.state[4:0]^self.state[3,:]) != 0:
                return (False,False,False) # Cant redirect if you already started defending
            
            rankonboard = self.state[4,0:8] +self.state[4,8:16] + self.state[4,16:24] + self.state[4,24:]
            
            if np.sum(move[3,:]) == 0 and np.allclose(move[player,:],ZEROES) : #Attempted Flash
                if self.state[player,np.where(rankonboard>=1)[0]] != 1:
                    print("player doesnt have the trump card to redirect")
                    return (False,False,False)
                else:
                    return (True,True,False)
            else: #Normal redirect
                redirectedcard = np.where(move[3,:]==1)[0]
                if np.allclose(np.where(rankonboard==1)[0],(redirectedcard%8)): #The card added by move must be of same rank 
                    return (True,True,False)
                else:
                    print("Card of wrong rank used to redirect")
                    return (False,False,False)   
        else:
            print("we here")
            print(f"{ np.sum(new[3,:])+1==np.sum(self.state[3,:])}")
            if np.sum(new[3,:])+1==np.sum(self.state[3,:]) and (np.sum(move[4,:]) == 1): # Attempted Defense of exactly 1 card
                cardsdefended  = np.where(move==-1)[0]

                card2def = ZEROES - move[3,:]
                defendingcard = move[4,:]
        

                if not np.allclose(defendingcard * self.state[player,:], defendingcard):
                    print(defendingcard)
                    print(defendingcard * self.state[player,:])
                    print(f'Cards have been used that arent in player {player}`s hand')
                    return (False,False,False)
                card2def=card2def[np.where(card2def==1)]
                defendingcard = defendingcard[np.where(defendingcard==1)]
                if card2def//8 == defendingcard//8: #Defense with same suit
                    if card2def<defendingcard:
                        print("Card is of the same suit but too low")
                        return (False,False,False)
                elif card2def//8 != 0:
                    print("Card isnt of the same suit and isnt trump")
                    return (False,False,False)
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

    def generate_all_moves_vectorized(self, player, is_attacking=True):
        """
        Ultra-efficient move generation using pure numpy operations
        
        Args:
            player: 0 or 1
            is_attacking: True for attack moves, False for defense moves
            
        Returns:
            np.ndarray: Shape (n_moves, 6, 32) containing all possible moves
        """
        if is_attacking:
            return self._generate_attack_moves_vectorized(player)
        else:
            return self._generate_defense_moves_vectorized(player)
    
    def _generate_attack_moves_vectorized(self, player):
        """Generate attack moves using pure numpy operations"""
        player_hand = self.state[player, :]
        opponent_cards = np.sum(self.state[1-player, :])
        
        # Get board state
        played = self.state[4, 0:8] + self.state[4, 8:16] + self.state[4, 16:24] + self.state[4, 24:32]
        played = (played >= 1).astype(bool)
        
        # Get hand cards grouped by rank
        hand_by_rank = np.zeros((8, 4), dtype=bool)
        for rank in range(8):
            for suit in range(4):
                hand_by_rank[rank, suit] = player_hand[rank + suit * 8]
        
        moves_list = []
        
        if not np.any(played):  # Empty board
            # For each rank that player has cards of
            for rank in range(8):
                rank_cards = np.where(hand_by_rank[rank])[0]
                if len(rank_cards) > 0:
                    # Generate all non-empty subsets of cards of this rank
                    max_cards = min(len(rank_cards), opponent_cards)
                    for subset_size in range(1, max_cards + 1):
                        # Use bit manipulation to generate all combinations
                        from itertools import combinations
                        for card_indices in combinations(rank_cards, subset_size):
                            move = np.zeros((6, 32), dtype=int)  # Use int instead of bool
                            for suit_idx in card_indices:
                                card_idx = rank + suit_idx * 8
                                move[player, card_idx] = -1  # Remove from hand
                                move[3, card_idx] = 1
                                move[4, card_idx] = 1
                            # No need to convert since we're already using -1
                            moves_list.append(move)
        else:  # Non-empty board
            legal_ranks = np.where(played)[0]
            current_attack_size = np.sum(self.state[3, :])
            
            for rank in legal_ranks:
                rank_cards = np.where(hand_by_rank[rank])[0]
                if len(rank_cards) > 0:
                    max_additional = min(len(rank_cards), opponent_cards - current_attack_size)
                    for subset_size in range(1, max_additional + 1):
                        from itertools import combinations
                        for card_indices in combinations(rank_cards, subset_size):
                            move = np.zeros((6, 32), dtype=int)  # Use int instead of bool
                            for suit_idx in card_indices:
                                card_idx = rank + suit_idx * 8
                                move[player, card_idx] = -1  # Remove from hand
                                move[3, card_idx] = 1
                                move[4, card_idx] = 1
                            moves_list.append(move)
            
            # Add pass move
            pass_move = np.zeros((6, 32), dtype=int)  # Use int instead of bool
            moves_list.append(pass_move)
        
        if moves_list:
            return np.array(moves_list)
        else:
            return np.array([]).reshape(0, 6, 32)
    
    def _generate_defense_moves_vectorized(self, player):
        """Using precomputed lookup table"""
        player_hand = self.state[player, :]
        attack_indices = np.where(self.state[3, :])[0]
        
        if len(attack_indices) == 0:
            return np.array([]).reshape(0, 6, 32)
        
        # Use precomputed matrix with boolean indexing
        valid_defenses = self._defense_matrix[attack_indices] & player_hand[None, :]
        attack_idx, defend_idx = np.where(valid_defenses)
        
        if len(attack_idx) > 0:
            # Map back to actual attack indices
            actual_attacks = attack_indices[attack_idx]
            
            # Create all moves vectorially
            n_moves = len(actual_attacks)
            moves = np.tile(np.zeros((6, 32), dtype=int), (n_moves, 1, 1))
            moves[np.arange(n_moves), player, defend_idx] = -1
            moves[np.arange(n_moves), 3, actual_attacks] = -1
            moves[np.arange(n_moves), 4, defend_idx] = 1
            
            # Add pickup
            pickup = np.zeros((1, 6, 32), dtype=int)
            return np.vstack([moves, pickup])
        else:
            return np.zeros((1, 6, 32), dtype=int)
    
    def get_all_legal_moves(self, player, move_type='auto'):
        """
        Main interface for getting all legal moves for a player
        
        Args:
            player: 0 or 1
            move_type: 'attack', 'defense', or 'auto' (determines based on game state)
            
        Returns:
            np.ndarray: All legal moves as (n_moves, 6, 32) array
        """
        if move_type == 'auto':
            # Determine if player should be attacking or defending
            is_attacking = self._is_player_attacking(player)
        else:
            is_attacking = (move_type == 'attack')
        
        return self.generate_all_moves_vectorized(player, is_attacking)
    
    def _is_player_attacking(self, player):
        """Determine if a player is in attacking or defending position"""
        # If there are cards to defend and it's this player's turn to defend
        cards_to_defend = np.sum(self.state[3, :])
        player_turn = self.state[5, 8]  # Player 0's turn flag
        player_attacking = self.state[5, 9]  # Player 0 attacking flag
        
        if cards_to_defend > 0:
            # There are cards on board to defend
            if player == 0:
                return not (player_turn and not player_attacking)  # P0 defends when it's their turn but not attacking
            else:
                return not (not player_turn and player_attacking)  # P1 defends when it's not P0's turn but P0 is attacking
        else:
            # No cards to defend, check who should attack
            if player == 0:
                return player_turn and player_attacking
            else:
                return not player_turn and not player_attacking
    
    def validate_move_fast(self, move, player, is_attacking=None):
        """
        Fast move validation using the existing validation logic
        
        Args:
            move: 6x32 move array
            player: 0 or 1
            is_attacking: True/False, or None to auto-detect
            
        Returns:
            tuple: (is_valid, additional_info)
        """
        if is_attacking is None:
            is_attacking = self._is_player_attacking(player)
        
        if is_attacking:
            return self._attack(move, player)
        else:
            return self._defend(move, player)
    
    def count_legal_moves(self, player, move_type='auto'):
        """
        Count the number of legal moves without generating them all
        Useful for game tree analysis
        """
        moves = self.get_all_legal_moves(player, move_type)
        return len(moves)
    
    def _generate_attack_moves_fully_vectorized(self, player):
        """Completely vectorized - no loops at all"""
        player_hand = self.state[player, :]
        opponent_cards = np.sum(self.state[1-player, :])
        
        # Reshape to work with ranks and suits
        cards_matrix = self.state[player, :].reshape(4, 8)  # (suits, ranks)
        board_matrix = self.state[4, :].reshape(4, 8)
        
        # Get ranks that are on board and that player has
        board_ranks = np.any(board_matrix, axis=0)  # Shape: (8,)
        player_ranks = np.any(cards_matrix, axis=0)  # Shape: (8,)
        
        if not np.any(board_ranks):  # Empty board
            valid_ranks = player_ranks
        else:  # Non-empty board
            valid_ranks = player_ranks & board_ranks
        
        valid_rank_indices = np.where(valid_ranks)[0]
        
        if len(valid_rank_indices) == 0:
            if np.any(board_ranks):
                return np.zeros((1, 6, 32), dtype=int)
            else:
                return np.array([]).reshape(0, 6, 32)
        
        # Generate all moves using pure numpy operations
        all_moves = []
        current_attacks = np.sum(self.state[3, :]) if np.any(board_ranks) else 0
        
        # Process each rank's card combinations
        for rank in valid_rank_indices:
            # Get suits available for this rank
            available_suits = np.where(cards_matrix[:, rank])[0]
            n_suits = len(available_suits)
            
            if n_suits == 0:
                continue
            
            max_cards = min(n_suits, opponent_cards - current_attacks)
            if max_cards <= 0:
                continue
            
            # Generate all valid combinations using numpy operations
            # Create all possible bit patterns for subsets
            all_patterns = np.arange(1, 2**n_suits)
            pattern_sizes = np.unpackbits(
                np.array(all_patterns, dtype=np.uint8).view(np.uint8).reshape(-1, 1), 
                axis=1, count=n_suits, bitorder='little'
            ).sum(axis=1)
            
            valid_patterns = all_patterns[pattern_sizes <= max_cards]
            
            # Convert patterns to actual moves
            n_valid = len(valid_patterns)
            if n_valid == 0:
                continue
                
            # Create all moves for this rank at once
            rank_moves = np.zeros((n_valid, 6, 32), dtype=int)
            
            for i, pattern in enumerate(valid_patterns):
                # Extract selected suits
                suit_bits = np.unpackbits(
                    np.array([pattern], dtype=np.uint8), 
                    count=n_suits, bitorder='little'
                )[0]
                selected_suits = available_suits[suit_bits.astype(bool)]
                
                # Convert to card indices
                card_indices = rank + selected_suits * 8
                
                # Set move values
                rank_moves[i, player, card_indices] = -1
                rank_moves[i, 3, card_indices] = 1
                rank_moves[i, 4, card_indices] = 1
            
            all_moves.extend(rank_moves)
        
        # Add pass move if board is not empty
        if np.any(board_ranks):
            all_moves.append(np.zeros((6, 32), dtype=int))
        
        return np.array(all_moves) if all_moves else np.array([]).reshape(0, 6, 32)
    
if __name__ == '__main__':
    game = Game()
    # print(game.state)
    move = np.zeros((6,32))
    move[1,0] = -1
    move[3,0] = 1
    move[4,0] = 1
    # move[1,1] = -1
    # move[3,1] = 1
    # move[4,1] = 1
    out = game.attack(move,1)
    if out[0]:
        print(game.state)
    
    print(out)

