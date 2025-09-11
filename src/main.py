from backend.game import *
from frontend.board_visualiser import *
import numpy as np

def print_move_details(move, move_idx, player):
    """Print detailed information about a move"""
    print(f"\n--- Move {move_idx + 1} ---")
    
    # Cards removed from hand
    removed_cards = np.where(move[player, :] == -1)[0]
    if len(removed_cards) > 0:
        print(f"Player {player} plays cards: {removed_cards}")
    
    # Cards added to left to defend
    left_to_defend = np.where(move[3, :] == 1)[0]
    if len(left_to_defend) > 0:
        print(f"Cards added to attack: {left_to_defend}")
    
    # Cards removed from left to defend
    defended_cards = np.where(move[3, :] == -1)[0]
    if len(defended_cards) > 0:
        print(f"Cards defended: {defended_cards}")
    
    # Cards added to board
    board_cards = np.where(move[4, :] == 1)[0]
    if len(board_cards) > 0:
        print(f"Cards added to board: {board_cards}")
    
    # Check if it's a pass move
    if np.sum(np.abs(move)) == 0:
        print("PASS MOVE")

def show_all_moves_for_player(game, player):
    """Show all possible moves for a player"""
    print(f"\n{'='*50}")
    print(f"ALL POSSIBLE MOVES FOR PLAYER {player}")
    print(f"{'='*50}")
    
    # Show current state
    print(f"\nCurrent game state:")
    print(f"Player {player} hand: {np.where(game.state[player, :] == 1)[0]}")
    print(f"Opponent hand size: {np.sum(game.state[1-player, :])}")
    print(f"Cards to defend: {np.where(game.state[3, :] == 1)[0]}")
    print(f"Cards on board: {np.where(game.state[4, :] == 1)[0]}")
    print(f"Trump suit cards (0-7): {np.where(game.state[5, 0:8] == 1)[0]}")
    
    # Determine if player is attacking or defending
    is_attacking = game._is_player_attacking(player)
    print(f"Player {player} is {'ATTACKING' if is_attacking else 'DEFENDING'}")
    
    # Get all legal moves
    try:
        moves = game.get_all_legal_moves(player)
        print(f"\nTotal legal moves: {len(moves)}")
        
        if len(moves) == 0:
            print("No legal moves available!")
            return
        
        # Show each move
        for i, move in enumerate(moves):
            print_move_details(move, i, player)
            
            # Validate the move
            try:
                if is_attacking:
                    valid, beaten = game._attack(move, player)
                    print(f"Validation: Valid={valid}, Beaten={beaten}")
                else:
                    valid, is_redirect, is_complete = game._defend(move, player)
                    print(f"Validation: Valid={valid}, Redirect={is_redirect}, Complete={is_complete}")
            except Exception as e:
                print(f"Validation error: {e}")
        
    except Exception as e:
        print(f"Error generating moves: {e}")
        import traceback
        traceback.print_exc()

# Initialize game
game = Game()
board_visualiser = BoardVisualiser(game.state, 0)
print("Initial game state:")
print(board_visualiser)

# Show moves for both players
show_all_moves_for_player(game, 0)
show_all_moves_for_player(game, 1)

# Let's also test after making a move
print(f"\n{'='*70}")
print("TESTING AFTER MAKING A MOVE")
print(f"{'='*70}")

# Make a simple attack move with player 1 (if they can attack)
try:
    # Get player 1's first legal move
    p1_moves = game.get_all_legal_moves(1)
    if len(p1_moves) > 0 and game._is_player_attacking(1):
        first_move = p1_moves[0]
        print(f"\nMaking Player 1's first attack move...")
        
        # Apply the move
        valid, beaten = game.attack(first_move, 1)
        print(f"Move result: Valid={valid}, Beaten={beaten}")
        
        if valid:
            print("\nNew game state after move:")
            board_visualiser = BoardVisualiser(game.state, 0)
            print(board_visualiser)
            
            # Show moves for the defending player
            defending_player = 0  # Player 0 should now defend
            show_all_moves_for_player(game, defending_player)
        
except Exception as e:
    print(f"Error testing move: {e}")
    import traceback
    traceback.print_exc()
