"""
Simple test script to verify AI implementation
"""
from ai import (
    create_empty_board,
    minimax_without_ab,
    minimax_with_ab,
    iterative_deepening,
    MinimaxStats,
    drop_piece
)

def test_minimax():
    """Test minimax algorithms"""
    print("Testing Minimax Algorithms...")
    
    # Create a test board
    board = create_empty_board()
    
    # Make a few moves
    result = drop_piece(board, 3, 1)  # Player 1 in center
    if result:
        row, board = result
        print(f"Player 1 placed at row {row}, col 3")
    
    result = drop_piece(board, 3, 2)  # Player 2 in center
    if result:
        row, board = result
        print(f"Player 2 placed at row {row}, col 3")
    
    # Test minimax without alpha-beta
    print("\n--- Minimax without Alpha-Beta ---")
    stats = MinimaxStats()
    value, move = minimax_without_ab(board, depth=3, maximizing_player=True, player=1, stats=stats)
    print(f"Best move: {move}, Value: {value}")
    print(f"Nodes expanded: {stats.nodes_expanded}")
    
    # Test minimax with alpha-beta
    print("\n--- Minimax with Alpha-Beta ---")
    stats = MinimaxStats()
    value, move = minimax_with_ab(
        board, depth=3, alpha=float('-inf'), beta=float('inf'),
        maximizing_player=True, player=1, stats=stats
    )
    print(f"Best move: {move}, Value: {value}")
    print(f"Nodes expanded: {stats.nodes_expanded}")
    print(f"Pruned nodes: {stats.pruned_nodes}")
    
    # Test iterative deepening
    print("\n--- Iterative Deepening ---")
    move, depth, stats = iterative_deepening(board, max_depth=5, player=1, time_limit=2.0)
    print(f"Best move: {move}, Final depth: {depth}")
    print(f"Nodes expanded: {stats.nodes_expanded}")
    print(f"Pruned nodes: {stats.pruned_nodes}")
    
    print("\nAll tests completed!")

if __name__ == '__main__':
    test_minimax()

