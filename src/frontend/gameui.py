import pygame
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.game import Game
from typing import List, Tuple, Optional

# Colors for visualization
COLORS = {
    'background': (20, 25, 40),
    'card_white': (245, 245, 245),
    'card_border': (105, 105, 105),
    'trump_card': (255, 140, 0),
    'text_white': (255, 255, 255),
    'text_black': (0, 0, 0),
    'text_gray': (128, 128, 128),
    'section_border': (100, 100, 100),
    'player_0_color': (100, 200, 100),
    'player_1_color': (200, 100, 100),
    'board_color': (150, 150, 200),
    'defend_color': (200, 150, 100),
    'unplayed_color': (80, 80, 80),
    'highlight': (255, 255, 0)
}

# Card dimensions
CARD_WIDTH = 30
CARD_HEIGHT = 45
CARD_SPACING = 3
SECTION_HEIGHT = 80
SECTION_SPACING = 15

class Card:
    """Represents a visual card for display"""
    
    def __init__(self, index: int, x: int, y: int, is_present: bool = True):
        self.index = index  # Card index (0-31)
        self.x = x
        self.y = y
        self.is_present = is_present  # Whether this card is present in current row
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        
    @property
    def suit(self) -> int:
        """Get suit number (0=trump, 1-3=other suits)"""
        return self.index // 8
    
    @property 
    def rank(self) -> int:
        """Get rank (0=Ace, 1=King, ..., 7=Seven)"""
        return self.index % 8
    
    @property
    def rank_name(self) -> str:
        """Get display name for rank"""
        names = ['A', 'K', 'Q', 'J', '10', '9', '8', '7']
        return names[self.rank]
    
    @property
    def suit_name(self) -> str:
        """Get suit name"""
        if self.suit == 0:
            return 'T'  # Trump
        return ['T', 'H', 'D', 'C'][self.suit]
    
    @property
    def is_trump(self) -> bool:
        """Check if card is trump"""
        return self.suit == 0

class GameStateVisualizer:
    """Visualizer for Durak game state based on the 6x32 matrix structure"""
    
    def __init__(self, matrix_list=None):
        pygame.init()
        self.screen = pygame.display.set_mode((1600, 900))  # Increased width to accommodate smaller cards
        pygame.display.set_caption("Durak Game State Visualizer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        self.large_font = pygame.font.Font(None, 24)
        
        # Game state and matrix management
        self.game = Game()
        self.matrix_list = matrix_list if matrix_list is not None else []
        self.current_matrix_index = 0
        self.running = True
        
        # Validate matrices if provided
        if self.matrix_list:
            valid_matrices = []
            for i, matrix in enumerate(self.matrix_list):
                if isinstance(matrix, np.ndarray) and matrix.shape == (6, 32):
                    valid_matrices.append(matrix)
                else:
                    print(f"Warning: Matrix {i} has invalid shape {matrix.shape if hasattr(matrix, 'shape') else 'unknown'}, skipping")
            self.matrix_list = valid_matrices
            
            # Load first matrix if available
            if self.matrix_list:
                self.load_matrix(0)
        
        # Layout parameters
        self.start_x = 50
        self.start_y = 50
        self.row_labels = [
            "Player 0's Hand",
            "Player 1's Hand", 
            "Unplayed Cards",
            "Cards Left to Defend",
            "Cards Played on Board",
            "Trump Card (Koser) & Game Flags"
        ]
        
        # Testing variables
        self.test_player = 0
        self.last_generated_moves = []
        self.move_generation_info = ""
        
    def load_matrix(self, index):
        """Load a matrix from the list into the game state"""
        if 0 <= index < len(self.matrix_list):
            self.game.state = self.matrix_list[index].copy()
            self.current_matrix_index = index
            print(f"Loaded matrix {index + 1} of {len(self.matrix_list)}")
        
    def next_matrix(self):
        """Load the next matrix in the list"""
        if self.current_matrix_index + 1 < len(self.matrix_list):
            self.load_matrix(self.current_matrix_index + 1)
        
    def has_next_matrix(self):
        """Check if there's a next matrix available"""
        return self.current_matrix_index + 1 < len(self.matrix_list)
        
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if Next button was clicked
                if hasattr(self, 'next_button_rect') and self.next_button_rect.collidepoint(event.pos):
                    if self.next_button_enabled:
                        self.next_matrix()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    # New game
                    self.game = Game()
                elif event.key == pygame.K_SPACE:
                    # Generate and display random move
                    self.show_random_move()
                elif event.key == pygame.K_r:
                    # Reset to initial state
                    self.game = Game()
                elif event.key == pygame.K_RIGHT:
                    # Next matrix (arrow key shortcut)
                    self.next_matrix()
                elif event.key == pygame.K_a:
                    # Test attack move generation
                    self.test_attack_moves()
                elif event.key == pygame.K_d:
                    # Test defense move generation
                    self.test_defense_moves()
                elif event.key == pygame.K_t:
                    # Toggle between players for testing
                    self.toggle_test_player()
    
    def show_random_move(self):
        """Generate and apply a random legal move"""
        try:
            # Determine current player and if they're attacking
            current_player = 0 if self.game.state[5, 8] else 1
            is_attacking = self.game._is_player_attacking(current_player)
            
            # Get all legal moves
            moves = self.game.get_all_legal_moves(current_player, 'auto')
            
            if len(moves) > 0:
                # Apply a random move
                random_move = moves[np.random.randint(len(moves))]
                
                if is_attacking:
                    self.game.attack(random_move, current_player)
                else:
                    self.game.defend(random_move, current_player)
                    
                print(f"Applied random move for Player {current_player} ({'attacking' if is_attacking else 'defending'})")
            else:
                print("No legal moves available")
                
        except Exception as e:
            print(f"Error applying random move: {e}")
    
    def test_attack_moves(self):
        """Test attack move generation for the current test player"""
        try:
            print(f"\n=== Testing Attack Moves for Player {self.test_player} ===")
            
            # Generate attack moves
            attack_moves = self.game._generate_attack_moves_vectorized(self.test_player)
            
            print(f"Generated {len(attack_moves)} attack moves")
            self.last_generated_moves = attack_moves
            self.move_generation_info = f"Attack moves for Player {self.test_player}: {len(attack_moves)} moves"
            
            # Print details of first few moves
            for i, move in enumerate(attack_moves[:5]):  # Show first 5 moves
                print(f"Move {i+1}:")
                print(f"  Player hand changes: {np.sum(move[self.test_player, :])}")
                print(f"  Cards left to defend: {np.sum(move[3, :])}")
                print(f"  Cards played on board: {np.sum(move[4, :])}")
                
            if len(attack_moves) > 5:
                print(f"... and {len(attack_moves) - 5} more moves")
                
        except Exception as e:
            print(f"Error testing attack moves: {e}")
            self.move_generation_info = f"Error testing attack moves: {str(e)}"
    
    def test_defense_moves(self):
        """Test defense move generation for the current test player"""
        try:
            print(f"\n=== Testing Defense Moves for Player {self.test_player} ===")
            
            # Generate defense moves
            defense_moves = self.game._generate_defense_moves_vectorized(self.test_player)
            
            print(f"Generated {len(defense_moves)} defense moves")
            self.last_generated_moves = defense_moves
            self.move_generation_info = f"Defense moves for Player {self.test_player}: {len(defense_moves)} moves"
            
            # Print details of first few moves
            for i, move in enumerate(defense_moves[:5]):  # Show first 5 moves
                print(f"Move {i+1}:")
                print(f"  Player hand changes: {np.sum(move[self.test_player, :])}")
                print(f"  Cards left to defend changes: {np.sum(move[3, :])}")
                print(f"  Cards played on board changes: {np.sum(move[4, :])}")
                
            if len(defense_moves) > 5:
                print(f"... and {len(defense_moves) - 5} more moves")
                
        except Exception as e:
            print(f"Error testing defense moves: {e}")
            self.move_generation_info = f"Error testing defense moves: {str(e)}"
    
    def toggle_test_player(self):
        """Toggle between Player 0 and Player 1 for testing"""
        self.test_player = 1 - self.test_player
        print(f"Switched to testing Player {self.test_player}")
        self.move_generation_info = f"Now testing Player {self.test_player}"
    
    def draw_card_compact(self, card: Card, row_color: Tuple[int, int, int], row_index: int = -1):
        """Draw a compact card representation"""
        if row_index == 5 and card.index >= 8:
            # Special handling for Row 5 flags (positions 8+)
            flag_meanings = {
                8: "P0 Turn",
                9: "P0 Attack", 
                10: "Pickup",
                11: "Game Over",
                12: "P0 Won"
            }
            
            if card.is_present:
                color = COLORS['highlight']
                border_color = COLORS['card_border']
                text_color = COLORS['text_black']
            else:
                color = COLORS['unplayed_color']
                border_color = COLORS['text_gray']
                text_color = COLORS['text_white']  # Changed to white for better readability
            
            # Draw card rectangle
            pygame.draw.rect(self.screen, color, card.rect)
            pygame.draw.rect(self.screen, border_color, card.rect, 1)
            
            # Draw flag meaning instead of card info
            if card.index in flag_meanings:
                text = flag_meanings[card.index]
                # Use smaller font size for better fit in wider cards
                text_surface = pygame.font.Font(None, 16).render(text, True, text_color)
                text_rect = text_surface.get_rect(center=card.rect.center)
                self.screen.blit(text_surface, text_rect)
        else:
            # Normal card display
            if card.is_present:
                # Card is present - draw filled
                color = COLORS['trump_card'] if card.is_trump else COLORS['card_white']
                border_color = COLORS['card_border']
            else:
                # Card is not present - draw grayed out
                color = COLORS['unplayed_color']
                border_color = COLORS['text_gray']
            
            # Draw card rectangle
            pygame.draw.rect(self.screen, color, card.rect)
            pygame.draw.rect(self.screen, border_color, card.rect, 1)
            
            if card.is_present:
                # Draw card info
                text = f"{card.rank_name}{card.suit_name}"
                text_color = COLORS['text_black'] if not card.is_trump else COLORS['text_white']
                text_surface = pygame.font.Font(None, 14).render(text, True, text_color)
                text_rect = text_surface.get_rect(center=card.rect.center)
                self.screen.blit(text_surface, text_rect)
    
    def draw_row(self, row_index: int, y_position: int):
        """Draw a complete row of the state matrix"""
        row_data = self.game.state[row_index, :]
        
        # Row label
        label_text = f"Row {row_index}: {self.row_labels[row_index]}"
        label_surface = self.font.render(label_text, True, COLORS['text_white'])
        self.screen.blit(label_surface, (self.start_x, y_position - 25))
        
        # Row color coding
        row_colors = [
            COLORS['player_0_color'],
            COLORS['player_1_color'], 
            COLORS['unplayed_color'],
            COLORS['defend_color'],
            COLORS['board_color'],
            COLORS['highlight']
        ]
        
        # Draw cards in this row
        if row_index == 5:
            # Special handling for Row 5 - only show trump cards (0-7) and flags (8-12)
            # Trump cards (0-7) with normal spacing
            for card_idx in range(8):
                x = self.start_x + card_idx * (CARD_WIDTH + CARD_SPACING)
                is_present = bool(row_data[card_idx])
                card = Card(card_idx, x, y_position, is_present)
                self.draw_card_compact(card, row_colors[row_index], row_index)
            
            # Add spacing between trump cards and flags
            flag_start_x = self.start_x + 8 * (CARD_WIDTH + CARD_SPACING) + 30
            flag_width = 60  # Wider slots for flags
            flag_spacing = 5
            
            # Flag cards (8-12) with wider spacing
            for i, card_idx in enumerate(range(8, min(13, len(row_data)))):
                x = flag_start_x + i * (flag_width + flag_spacing)
                is_present = bool(row_data[card_idx])
                card = Card(card_idx, x, y_position, is_present)
                # Create wider rect for flags
                card.rect = pygame.Rect(x, y_position, flag_width, CARD_HEIGHT)
                self.draw_card_compact(card, row_colors[row_index], row_index)
        else:
            # Normal card display for other rows
            for card_idx in range(32):
                x = self.start_x + card_idx * (CARD_WIDTH + CARD_SPACING)
                is_present = bool(row_data[card_idx])
                card = Card(card_idx, x, y_position, is_present)
                self.draw_card_compact(card, row_colors[row_index], row_index)
        
        # Draw count for this row
        count = np.sum(row_data)
        if row_index == 5:
            # Special handling for Row 5 - show trump card and flags
            trump_cards = np.where(row_data[0:8] == 1)[0]
            trump_info = f"Trump: {trump_cards[0]} (Koser)" if len(trump_cards) > 0 else "Trump: None"
            
            # Game state flags with descriptions
            flags_info = []
            if len(row_data) > 8:
                flags_info.append(f"P0 Turn: {bool(row_data[8])}")
            if len(row_data) > 9:
                flags_info.append(f"P0 Attack: {bool(row_data[9])}")
            if len(row_data) > 10:
                flags_info.append(f"Pickup: {bool(row_data[10])}")
            if len(row_data) > 11:
                flags_info.append(f"Game Over: {bool(row_data[11])}")
            if len(row_data) > 12:
                flags_info.append(f"P0 Won: {bool(row_data[12])}")
            
            # Display trump info (positioned after the wider flag cards)
            trump_surface = self.small_font.render(trump_info, True, COLORS['trump_card'])
            # Position after trump cards (8) + flags (5) with wider spacing
            count_x = self.start_x + 8 * (CARD_WIDTH + CARD_SPACING) + 30 + 5 * (60 + 5) + 20
            self.screen.blit(trump_surface, (count_x, y_position))
            
            # Display flags info in 2 rows for better readability
            # Row 1: P0 Turn, P0 Attack, Pickup
            row1_flags = flags_info[:3] if len(flags_info) >= 3 else flags_info
            row1_text = " | ".join(row1_flags)
            row1_surface = self.small_font.render(row1_text, True, COLORS['text_white'])
            self.screen.blit(row1_surface, (count_x, y_position + 20))
            
            # Row 2: Game Over, P0 Won
            if len(flags_info) > 3:
                row2_flags = flags_info[3:]
                row2_text = " | ".join(row2_flags)
                row2_surface = self.small_font.render(row2_text, True, COLORS['text_white'])
                self.screen.blit(row2_surface, (count_x, y_position + 35))
        else:
            count_text = f"Count: {count}"
            count_surface = self.small_font.render(count_text, True, COLORS['text_white'])
            count_x = self.start_x + 32 * (CARD_WIDTH + CARD_SPACING) + 20
            self.screen.blit(count_surface, (count_x, y_position + 20))
    
    def draw_game_state_info(self):
        """Draw additional game state information with better readability"""
        info_x = self.start_x
        info_y = self.start_y + 6 * (SECTION_HEIGHT + SECTION_SPACING) - 20  # Moved up by 70 pixels
        
        # Create a background panel for better readability
        panel_width = 600
        panel_height = 280  # Increased height to accommodate testing info
        panel_rect = pygame.Rect(info_x - 10, info_y - 10, panel_width, panel_height)
        pygame.draw.rect(self.screen, (40, 45, 60), panel_rect)  # Dark blue background
        pygame.draw.rect(self.screen, COLORS['section_border'], panel_rect, 2)  # Border
        
        # Game state flags from row 5
        state_info = [
            f"Player 0's Turn: {bool(self.game.state[5, 8])}",
            f"Player 0 Attacking: {bool(self.game.state[5, 9])}",
            f"Pickup Flag: {bool(self.game.state[5, 10]) if len(self.game.state[5]) > 10 else 'N/A'}",
            f"Game Over: {bool(self.game.state[5, 11]) if len(self.game.state[5]) > 11 else 'N/A'}",
            f"Player 0 Won: {bool(self.game.state[5, 12]) if len(self.game.state[5]) > 12 else 'N/A'}",
        ]
        
        # Trump card info
        trump_cards = np.where(self.game.state[5, 0:8] == 1)[0]
        trump_text = f"Trump Card: {trump_cards[0] if len(trump_cards) > 0 else 'None'}"
        
        # Current player and action
        current_player = 0 if self.game.state[5, 8] else 1
        try:
            is_attacking = self.game._is_player_attacking(current_player)
            action = "Attacking" if is_attacking else "Defending"
            current_action = f"Current: Player {current_player} {action}"
        except:
            current_action = f"Current: Player {current_player}"
        
        # Deck info
        deck_info = f"Deck Size: {len(self.game.deck)} cards"
        
        all_info = [trump_text, current_action, deck_info] + state_info
        
        for i, info in enumerate(all_info):
            if i < 3:
                color = COLORS['highlight']  # Important info in yellow
                font = self.font  # Larger font for important info
            else:
                color = (220, 220, 220)  # Light gray for details
                font = self.font  # Regular font
            
            info_surface = font.render(info, True, color)
            self.screen.blit(info_surface, (info_x, info_y + i * 25))
        
        # Add move generation testing info
        testing_y = info_y + len(all_info) * 25 + 10
        
        # Testing section title
        test_title = self.font.render("Move Generation Testing", True, COLORS['highlight'])
        self.screen.blit(test_title, (info_x, testing_y))
        testing_y += 20
        
        # Display current test player
        test_player_text = f"Test Player: {self.test_player}"
        test_player_surface = self.small_font.render(test_player_text, True, COLORS['text_white'])
        self.screen.blit(test_player_surface, (info_x, testing_y))
        testing_y += 15
        
        # Display move generation info
        if self.move_generation_info:
            info_surface = self.small_font.render(self.move_generation_info, True, COLORS['highlight'])
            self.screen.blit(info_surface, (info_x, testing_y))
            testing_y += 15
        
        # Display number of last generated moves
        if len(self.last_generated_moves) > 0:
            moves_text = f"Last test: {len(self.last_generated_moves)} moves generated"
            moves_surface = self.small_font.render(moves_text, True, COLORS['text_white'])
            self.screen.blit(moves_surface, (info_x, testing_y))
    
    def draw_legend(self):
        """Draw legend explaining the visualization"""
        legend_x = self.start_x + 32 * (CARD_WIDTH + CARD_SPACING) + 100
        legend_y = self.start_y
        
        legend_items = [
            ("Row 0: Player 0's Hand", COLORS['player_0_color']),
            ("Row 1: Player 1's Hand", COLORS['player_1_color']),
            ("Row 2: Unplayed Cards", COLORS['unplayed_color']),
            ("Row 3: Cards to Defend", COLORS['defend_color']),
            ("Row 4: Cards on Board", COLORS['board_color']),
            ("Row 5: Trump/Game State", COLORS['highlight']),
            ("", None),
            ("Trump Cards (Orange)", COLORS['trump_card']),
            ("Regular Cards (White)", COLORS['card_white']),
            ("Absent Cards (Gray)", COLORS['unplayed_color']),
        ]
        
        legend_title = self.large_font.render("Legend", True, COLORS['text_white'])
        self.screen.blit(legend_title, (legend_x, legend_y))
        legend_y += 30
        
        for i, (text, color) in enumerate(legend_items):
            if text == "":
                legend_y += 10
                continue
                
            if color:
                # Draw color box
                color_rect = pygame.Rect(legend_x, legend_y + 3, 15, 15)
                pygame.draw.rect(self.screen, color, color_rect)
                pygame.draw.rect(self.screen, COLORS['card_border'], color_rect, 1)
                
                # Draw text
                text_surface = self.small_font.render(text, True, COLORS['text_white'])
                self.screen.blit(text_surface, (legend_x + 25, legend_y))
            
            legend_y += 20
    
    def draw_controls(self):
        """Draw control instructions"""
        controls_x = self.start_x + 32 * (CARD_WIDTH + CARD_SPACING) + 100
        controls_y = self.start_y + 300
        
        controls_title = self.large_font.render("Controls", True, COLORS['text_white'])
        self.screen.blit(controls_title, (controls_x, controls_y))
        controls_y += 30
        
        # Draw Next button
        button_width = 100
        button_height = 30
        next_button_rect = pygame.Rect(controls_x, controls_y, button_width, button_height)
        
        # Check if next button should be enabled
        has_next = self.has_next_matrix()
        button_color = COLORS['highlight'] if has_next else COLORS['unplayed_color']
        text_color = COLORS['text_black'] if has_next else COLORS['text_gray']
        
        pygame.draw.rect(self.screen, button_color, next_button_rect)
        pygame.draw.rect(self.screen, COLORS['card_border'], next_button_rect, 2)
        
        # Button text with matrix info
        if self.matrix_list:
            button_text = f"Next ({self.current_matrix_index + 1}/{len(self.matrix_list)})"
        else:
            button_text = "Next (No matrices)"
            
        button_surface = self.small_font.render(button_text, True, text_color)
        button_text_rect = button_surface.get_rect(center=next_button_rect.center)
        self.screen.blit(button_surface, button_text_rect)
        
        # Store button rect for click detection
        self.next_button_rect = next_button_rect
        self.next_button_enabled = has_next
        
        controls_y += button_height + 10
        
        controls = [
            "N - New Game",
            "SPACE - Random Move", 
            "R - Reset Game",
            "RIGHT - Next Matrix",
            "A - Test Attack Moves",
            "D - Test Defense Moves", 
            "T - Toggle Test Player",
            "ESC - Quit"
        ]
        
        for control in controls:
            control_surface = self.small_font.render(control, True, COLORS['text_white'])
            self.screen.blit(control_surface, (controls_x, controls_y))
            controls_y += 20
    
    def draw_matrix_representation(self):
        """Draw a numerical representation of the state matrix with better readability"""
        matrix_x = self.start_x + 620  # Position to the right of the game state info panel
        matrix_y = self.start_y + 6 * (SECTION_HEIGHT + SECTION_SPACING) - 20  # Same vertical position as game state info
        
        # Create background panel
        panel_width = 600
        panel_height = 150
        panel_rect = pygame.Rect(matrix_x - 10, matrix_y - 10, panel_width, panel_height)
        pygame.draw.rect(self.screen, (40, 45, 60), panel_rect)  # Dark blue background
        pygame.draw.rect(self.screen, COLORS['section_border'], panel_rect, 2)  # Border
        
        title = self.large_font.render("State Matrix (6x32) - First 16 columns", True, COLORS['text_white'])
        self.screen.blit(title, (matrix_x, matrix_y))
        matrix_y += 30
        
        # Show first 16 columns of the matrix for readability
        for row in range(6):
            row_text = f"Row {row}: "
            for col in range(min(16, 32)):
                value = int(self.game.state[row, col])
                row_text += f"{value}"
            
            if 32 > 16:
                row_text += "..."
                
            # Use brighter colors for better contrast
            color = (180, 180, 180) if np.sum(self.game.state[row, :]) == 0 else COLORS['highlight']
            text_surface = self.font.render(row_text, True, color)  # Use regular font instead of small_font
            self.screen.blit(text_surface, (matrix_x, matrix_y))
            matrix_y += 20  # Increased spacing
    
    def draw(self):
        """Main drawing function"""
        # Clear screen
        self.screen.fill(COLORS['background'])
        
        # Draw title
        title = self.large_font.render("Durak Game State Visualizer", True, COLORS['text_white'])
        title_rect = title.get_rect(center=(self.screen.get_width()//2, 25))
        self.screen.blit(title, title_rect)
        
        # Draw each row of the state matrix
        for row_index in range(6):
            y_pos = self.start_y + row_index * (SECTION_HEIGHT + SECTION_SPACING)
            self.draw_row(row_index, y_pos)
        
        # Draw additional information
        self.draw_game_state_info()
        self.draw_legend()
        self.draw_controls()
        self.draw_matrix_representation()
        
        pygame.display.flip()
    
    def run(self):
        """Main visualization loop"""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    visualizer = GameStateVisualizer()
    visualizer.run()
