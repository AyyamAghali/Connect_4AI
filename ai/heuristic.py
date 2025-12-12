"""
Heuristic evaluation function for Connect Four
Evaluates non-terminal board states using various features
"""
from .game_state import COLS, ROWS

def evaluate_board(board, player):
    """
    Evaluate the board state from the perspective of the given player.
    Returns a score where positive values favor the player.
    """
    opponent = 3 - player  # If player is 1, opponent is 2; if player is 2, opponent is 1
    score = 0
    
    # 1. Center column control (more valuable)
    center_col = COLS // 2
    for row in range(ROWS):
        if board[row][center_col] == player:
            score += 3
        elif board[row][center_col] == opponent:
            score -= 3
    
    # 2. Evaluate all possible 4-in-a-row sequences
    # Horizontal sequences
    for row in range(ROWS):
        for col in range(COLS - 3):
            score += evaluate_sequence(board, row, col, 0, 1, player, opponent)
    
    # Vertical sequences
    for row in range(ROWS - 3):
        for col in range(COLS):
            score += evaluate_sequence(board, row, col, 1, 0, player, opponent)
    
    # Diagonal (top-left to bottom-right)
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            score += evaluate_sequence(board, row, col, 1, 1, player, opponent)
    
    # Diagonal (top-right to bottom-left)
    for row in range(ROWS - 3):
        for col in range(3, COLS):
            score += evaluate_sequence(board, row, col, 1, -1, player, opponent)
    
    return score

def evaluate_sequence(board, start_row, start_col, delta_row, delta_col, player, opponent):
    """
    Evaluate a sequence of 4 cells in a specific direction.
    Returns a score based on the potential of this sequence.
    """
    player_count = 0
    opponent_count = 0
    empty_count = 0
    
    for i in range(4):
        row = start_row + i * delta_row
        col = start_col + i * delta_col
        cell = board[row][col]
        
        if cell == player:
            player_count += 1
        elif cell == opponent:
            opponent_count += 1
        else:
            empty_count += 1
    
    # If both players have pieces, this sequence is blocked
    if opponent_count > 0 and player_count > 0:
        return 0
    
    # Score based on potential
    if player_count == 4:
        return 10000  # Win
    if opponent_count == 4:
        return -10000  # Loss
    if opponent_count == 3 and empty_count == 1:
        return -1000  # Opponent threat (must block)
    if player_count == 3 and empty_count == 1:
        return 1000  # Our threat (can win)
    if opponent_count == 2 and empty_count == 2:
        return -100  # Opponent potential
    if player_count == 2 and empty_count == 2:
        return 100  # Our potential
    if player_count == 1 and empty_count == 3:
        return 10  # Our start
    if opponent_count == 1 and empty_count == 3:
        return -10  # Opponent start
    
    return 0

