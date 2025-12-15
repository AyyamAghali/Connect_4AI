"""
Minimax algorithm implementations:
1. Minimax without alpha-beta pruning
2. Minimax with alpha-beta pruning
"""
import random
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

def minimax_without_ab(board, depth, maximizing_player, player, stats=None, randomness=0.0):
    """
    Minimax algorithm without alpha-beta pruning.
    Returns (best_value, best_move)
    
    Args:
        randomness: Probability (0.0-1.0) of making a random move instead of best move
                    Higher values make AI weaker and more beatable
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
        eval_score = evaluate_board(board, player)
        # Add small random noise for lower depths to allow draws
        if randomness > 0:
            noise = random.uniform(-randomness * 50, randomness * 50)
            eval_score += noise
        return (eval_score, None)
    
    valid_moves = get_valid_moves(board)
    if not valid_moves:
        return (0, None)  # Draw
    
    # Order moves (center columns first), then shuffle to break ties
    ordered_moves = order_moves(valid_moves)
    random.shuffle(ordered_moves)  # Shuffle to break deterministic patterns
    
    if maximizing_player:
        max_eval = float('-inf')
        best_moves = []  # Store all moves with best evaluation
        
        for col in ordered_moves:
            row = get_drop_row(board, col)
            if row == -1:
                continue
            
            new_board = copy_board(board)
            new_board[row][col] = player
            
            # Check for immediate win
            if check_win(new_board, row, col, player):
                return (10000 - depth, col)
            
            eval_score, _ = minimax_without_ab(new_board, depth - 1, False, player, stats, randomness)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_moves = [col]  # Reset best moves list
            elif eval_score == max_eval:
                best_moves.append(col)  # Add to equally good moves
        
        # Randomly select from equally good moves, or make random mistake
        if randomness > 0 and random.random() < randomness:
            best_move = random.choice(ordered_moves)
        elif best_moves:
            best_move = random.choice(best_moves)  # Randomize among best moves
        else:
            best_move = ordered_moves[0]
        
        return (max_eval, best_move)
    else:
        min_eval = float('inf')
        best_moves = []  # Store all moves with best evaluation
        
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
            
            eval_score, _ = minimax_without_ab(new_board, depth - 1, True, player, stats, randomness)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_moves = [col]  # Reset best moves list
            elif eval_score == min_eval:
                best_moves.append(col)  # Add to equally good moves
        
        # Randomly select from equally good moves, or make random mistake
        if randomness > 0 and random.random() < randomness:
            best_move = random.choice(ordered_moves)
        elif best_moves:
            best_move = random.choice(best_moves)  # Randomize among best moves
        else:
            best_move = ordered_moves[0]
        
        return (min_eval, best_move)

def minimax_with_ab(board, depth, alpha, beta, maximizing_player, player, stats=None, randomness=0.0):
    """
    Minimax algorithm with alpha-beta pruning.
    Returns (best_value, best_move)
    
    Args:
        randomness: Probability (0.0-1.0) of making a random move instead of best move
                    Higher values make AI weaker and more beatable
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
        eval_score = evaluate_board(board, player)
        # Add small random noise for lower depths to allow draws
        if randomness > 0:
            noise = random.uniform(-randomness * 50, randomness * 50)
            eval_score += noise
        return (eval_score, None)
    
    valid_moves = get_valid_moves(board)
    if not valid_moves:
        return (0, None)  # Draw
    
    # Order moves (center columns first), then shuffle to break ties
    ordered_moves = order_moves(valid_moves)
    random.shuffle(ordered_moves)  # Shuffle to break deterministic patterns
    
    if maximizing_player:
        max_eval = float('-inf')
        best_moves = []  # Store all moves with best evaluation
        
        for col in ordered_moves:
            row = get_drop_row(board, col)
            if row == -1:
                continue
            
            new_board = copy_board(board)
            new_board[row][col] = player
            
            # Check for immediate win
            if check_win(new_board, row, col, player):
                return (10000 - depth, col)
            
            eval_score, _ = minimax_with_ab(new_board, depth - 1, alpha, beta, False, player, stats, randomness)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_moves = [col]  # Reset best moves list
            elif eval_score == max_eval:
                best_moves.append(col)  # Add to equally good moves
            
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                stats.pruned_nodes += len(ordered_moves) - ordered_moves.index(col) - 1
                break  # Alpha-beta pruning
        
        # Randomly select from equally good moves, or make random mistake
        if randomness > 0 and random.random() < randomness:
            best_move = random.choice(ordered_moves)
        elif best_moves:
            best_move = random.choice(best_moves)  # Randomize among best moves
        else:
            best_move = ordered_moves[0]
        
        return (max_eval, best_move)
    else:
        min_eval = float('inf')
        best_moves = []  # Store all moves with best evaluation
        
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
            
            eval_score, _ = minimax_with_ab(new_board, depth - 1, alpha, beta, True, player, stats, randomness)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_moves = [col]  # Reset best moves list
            elif eval_score == min_eval:
                best_moves.append(col)  # Add to equally good moves
            
            beta = min(beta, eval_score)
            if beta <= alpha:
                stats.pruned_nodes += len(ordered_moves) - ordered_moves.index(col) - 1
                break  # Alpha-beta pruning
        
        # Randomly select from equally good moves, or make random mistake
        if randomness > 0 and random.random() < randomness:
            best_move = random.choice(ordered_moves)
        elif best_moves:
            best_move = random.choice(best_moves)  # Randomize among best moves
        else:
            best_move = ordered_moves[0]
        
        return (min_eval, best_move)

def order_moves(moves):
    """Order moves by prioritizing center columns"""
    center = COLS // 2
    return sorted(moves, key=lambda x: abs(x - center))

