"""
Iterative deepening implementation for Connect Four AI
"""
import time
from .minimax import minimax_with_ab, MinimaxStats
from .game_state import get_valid_moves, get_drop_row, copy_board, check_win

def iterative_deepening(board, max_depth, player, time_limit=5.0):
    """
    Iterative deepening search with time limit.
    Returns (best_move, final_depth, stats)
    """
    stats = MinimaxStats()
    start_time = time.time()
    best_move = None
    final_depth = 0
    
    # Check for immediate wins or blocks first
    valid_moves = get_valid_moves(board)
    if not valid_moves:
        return (None, 0, stats)
    
    # Check for immediate win
    for col in valid_moves:
        row = get_drop_row(board, col)
        if row == -1:
            continue
        new_board = copy_board(board)
        new_board[row][col] = player
        if check_win(new_board, row, col, player):
            return (col, 0, stats)
    
    # Check for opponent's immediate win (must block)
    opponent = 3 - player
    for col in valid_moves:
        row = get_drop_row(board, col)
        if row == -1:
            continue
        new_board = copy_board(board)
        new_board[row][col] = opponent
        if check_win(new_board, row, col, opponent):
            return (col, 0, stats)
    
    # Iterative deepening
    for depth in range(1, max_depth + 1):
        if time.time() - start_time > time_limit:
            break
        
        stats.reset()
        _, best_move = minimax_with_ab(
            board, depth, float('-inf'), float('inf'), True, player, stats
        )
        final_depth = depth
        
        # If we found a winning move, return immediately
        if best_move is not None:
            row = get_drop_row(board, best_move)
            if row != -1:
                new_board = copy_board(board)
                new_board[row][best_move] = player
                if check_win(new_board, row, best_move, player):
                    return (best_move, depth, stats)
    
    return (best_move, final_depth, stats)

