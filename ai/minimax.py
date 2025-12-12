"""
Minimax algorithm implementations:
1. Minimax without alpha-beta pruning
2. Minimax with alpha-beta pruning
"""
from .game_state import get_valid_moves, get_drop_row, copy_board, check_win, is_terminal, COLS
from .heuristic import evaluate_board

class MinimaxStats:
    """Track statistics for minimax search"""
    def __init__(self):
        self.nodes_expanded = 0
        self.pruned_nodes = 0
    
    def reset(self):
        self.nodes_expanded = 0
        self.pruned_nodes = 0

def minimax_without_ab(board, depth, maximizing_player, player, stats=None):
    """
    Minimax algorithm without alpha-beta pruning.
    Returns (best_value, best_move)
    """
    if stats is None:
        stats = MinimaxStats()
    
    stats.nodes_expanded += 1
    
    # Check for terminal states
    is_term, winner = is_terminal(board)
    if is_term:
        if winner == player:
            return (10000 - depth, None)  # Win for maximizing player
        elif winner == 3 - player:
            return (-10000 + depth, None)  # Loss for maximizing player
        else:
            return (0, None)  # Draw
    
    if depth == 0:
        return (evaluate_board(board, player), None)
    
    valid_moves = get_valid_moves(board)
    if not valid_moves:
        return (0, None)  # Draw
    
    # Order moves (center columns first)
    ordered_moves = order_moves(valid_moves)
    
    if maximizing_player:
        max_eval = float('-inf')
        best_move = ordered_moves[0]
        
        for col in ordered_moves:
            row = get_drop_row(board, col)
            if row == -1:
                continue
            
            new_board = copy_board(board)
            new_board[row][col] = player
            
            # Check for immediate win
            if check_win(new_board, row, col, player):
                return (10000 - depth, col)
            
            eval_score, _ = minimax_without_ab(new_board, depth - 1, False, player, stats)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = col
        
        return (max_eval, best_move)
    else:
        min_eval = float('inf')
        best_move = ordered_moves[0]
        
        opponent = 3 - player
        for col in ordered_moves:
            row = get_drop_row(board, col)
            if row == -1:
                continue
            
            new_board = copy_board(board)
            new_board[row][col] = opponent
            
            # Check for immediate win
            if check_win(new_board, row, col, opponent):
                return (-10000 + depth, col)
            
            eval_score, _ = minimax_without_ab(new_board, depth - 1, True, player, stats)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = col
        
        return (min_eval, best_move)

def minimax_with_ab(board, depth, alpha, beta, maximizing_player, player, stats=None):
    """
    Minimax algorithm with alpha-beta pruning.
    Returns (best_value, best_move)
    """
    if stats is None:
        stats = MinimaxStats()
    
    stats.nodes_expanded += 1
    
    # Check for terminal states
    is_term, winner = is_terminal(board)
    if is_term:
        if winner == player:
            return (10000 - depth, None)  # Win for maximizing player
        elif winner == 3 - player:
            return (-10000 + depth, None)  # Loss for maximizing player
        else:
            return (0, None)  # Draw
    
    if depth == 0:
        return (evaluate_board(board, player), None)
    
    valid_moves = get_valid_moves(board)
    if not valid_moves:
        return (0, None)  # Draw
    
    # Order moves (center columns first)
    ordered_moves = order_moves(valid_moves)
    
    if maximizing_player:
        max_eval = float('-inf')
        best_move = ordered_moves[0]
        
        for col in ordered_moves:
            row = get_drop_row(board, col)
            if row == -1:
                continue
            
            new_board = copy_board(board)
            new_board[row][col] = player
            
            # Check for immediate win
            if check_win(new_board, row, col, player):
                return (10000 - depth, col)
            
            eval_score, _ = minimax_with_ab(new_board, depth - 1, alpha, beta, False, player, stats)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = col
            
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                stats.pruned_nodes += len(ordered_moves) - ordered_moves.index(col) - 1
                break  # Alpha-beta pruning
        
        return (max_eval, best_move)
    else:
        min_eval = float('inf')
        best_move = ordered_moves[0]
        
        opponent = 3 - player
        for col in ordered_moves:
            row = get_drop_row(board, col)
            if row == -1:
                continue
            
            new_board = copy_board(board)
            new_board[row][col] = opponent
            
            # Check for immediate win
            if check_win(new_board, row, col, opponent):
                return (-10000 + depth, col)
            
            eval_score, _ = minimax_with_ab(new_board, depth - 1, alpha, beta, True, player, stats)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = col
            
            beta = min(beta, eval_score)
            if beta <= alpha:
                stats.pruned_nodes += len(ordered_moves) - ordered_moves.index(col) - 1
                break  # Alpha-beta pruning
        
        return (min_eval, best_move)

def order_moves(moves):
    """Order moves by prioritizing center columns"""
    center = COLS // 2
    return sorted(moves, key=lambda x: abs(x - center))

