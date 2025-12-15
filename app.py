"""
Flask API server for Connect Four AI
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import time
import random
from ai import (
    minimax_without_ab,
    minimax_with_ab,
    iterative_deepening,
    MinimaxStats,
    get_valid_moves,
    get_drop_row,
    copy_board,
    check_win,
    is_terminal
)
from ai.game_state import COLS

app = Flask(__name__, static_folder='web')
CORS(app)  # Enable CORS for JavaScript frontend

@app.route('/')
def index():
    """Serve the main game page"""
    return send_from_directory('web', 'index.html')

@app.route('/game.js')
def serve_game_js():
    """Serve the game JavaScript file"""
    return send_from_directory('web', 'game.js')

# Global metrics tracking
metrics = {
    # Human vs AI stats
    'games_played': 0,
    'ai_wins': 0,
    'human_wins': 0,
    'draws': 0,
    # AI vs AI stats
    'ai_vs_ai_games_played': 0,
    'ai_vs_ai_player1_wins': 0,
    'ai_vs_ai_player2_wins': 0,
    'ai_vs_ai_draws': 0,
    # Performance metrics (combined)
    'total_nodes_expanded': 0,
    'total_pruned_nodes': 0,
    'total_decision_time': 0,
    'move_count': 0
}

@app.route('/api/move', methods=['POST'])
def get_move():
    """Get the best move from the AI"""
    data = request.json
    board = data.get('board')
    player = data.get('player', 2)  # AI is player 2 by default
    algorithm = data.get('algorithm', 'minimax_ab')  # 'minimax', 'minimax_ab', 'iterative', 'random'
    depth = data.get('depth', 5)
    time_limit = data.get('time_limit', 5.0)
    
    # Convert depth to int if it's a string
    if isinstance(depth, str):
        try:
            depth = int(depth)
        except ValueError:
            return jsonify({'error': f'Invalid depth: {depth}'}), 400
    
    # Normalize algorithm string (strip whitespace, convert to lowercase)
    if algorithm:
        algorithm = str(algorithm).strip().lower()
    else:
        algorithm = 'minimax_ab'
    
    # Debug logging
    print(f"DEBUG: Received algorithm: '{algorithm}' (type: {type(algorithm)})")
    print(f"DEBUG: Full request data: {data}")
    
    # Validate algorithm
    valid_algorithms = ['minimax', 'minimax_ab', 'iterative', 'random']
    if algorithm not in valid_algorithms:
        print(f"ERROR: Invalid algorithm received: '{algorithm}'")
        print(f"ERROR: Valid algorithms are: {valid_algorithms}")
        return jsonify({'error': f'Invalid algorithm: "{algorithm}". Valid options: {valid_algorithms}'}), 400
    
    # Accept an empty board (new game) but reject missing payload
    if board is None:
        return jsonify({'error': 'Board is required'}), 400
    
    start_time = time.time()
    stats = MinimaxStats()
    best_move = None
    final_depth = depth
    
    try:
        # Check for immediate wins or blocks first
        valid_moves = get_valid_moves(board)
        if not valid_moves:
            return jsonify({
                'move': None,
                'value': 0,
                'nodes_expanded': 0,
                'pruned_nodes': 0,
                'decision_time': 0,
                'depth': 0
            })
        
        # Check for immediate win
        for col in valid_moves:
            row = get_drop_row(board, col)
            if row == -1:
                continue
            new_board = copy_board(board)
            new_board[row][col] = player
            if check_win(new_board, row, col, player):
                decision_time = time.time() - start_time
                update_metrics(0, 0, decision_time)
                return jsonify({
                    'move': col,
                    'value': 10000,
                    'nodes_expanded': 1,
                    'pruned_nodes': 0,
                    'decision_time': decision_time,
                    'depth': 0
                })
        
        # Check for opponent's immediate win (must block)
        opponent = 3 - player
        for col in valid_moves:
            row = get_drop_row(board, col)
            if row == -1:
                continue
            new_board = copy_board(board)
            new_board[row][col] = opponent
            if check_win(new_board, row, col, opponent):
                decision_time = time.time() - start_time
                update_metrics(0, 0, decision_time)
                return jsonify({
                    'move': col,
                    'value': -10000,
                    'nodes_expanded': 1,
                    'pruned_nodes': 0,
                    'decision_time': decision_time,
                    'depth': 0
                })
        
        # Run the selected algorithm
        if algorithm == 'random':
            # Random algorithm - just pick a random valid move (no depth needed)
            if not valid_moves:
                return jsonify({
                    'move': None,
                    'value': 0,
                    'nodes_expanded': 0,
                    'pruned_nodes': 0,
                    'decision_time': 0,
                    'depth': 0
                })
            best_move = random.choice(valid_moves)
            value = 0
            stats.nodes_expanded = 1
            stats.pruned_nodes = 0  # Explicitly set for random
        elif algorithm == 'minimax':
            # Calculate randomness based on depth (lower depth = more randomness/mistakes)
            randomness = max(0.0, 0.25 - (depth * 0.03))
            randomness = min(0.2, randomness)  # Cap at 20% for very low depths
            value, best_move = minimax_without_ab(board, depth, True, player, stats, randomness)
        elif algorithm == 'minimax_ab':
            # Calculate randomness based on depth (lower depth = more randomness/mistakes)
            randomness = max(0.0, 0.25 - (depth * 0.03))
            randomness = min(0.2, randomness)  # Cap at 20% for very low depths
            value, best_move = minimax_with_ab(
                board, depth, float('-inf'), float('inf'), True, player, stats, randomness
            )
        elif algorithm == 'iterative':
            # Calculate randomness based on depth (lower depth = more randomness/mistakes)
            randomness = max(0.0, 0.25 - (depth * 0.03))
            randomness = min(0.2, randomness)  # Cap at 20% for very low depths
            best_move, final_depth, stats = iterative_deepening(
                board, depth, player, time_limit, randomness
            )
            value = 0  # Iterative deepening doesn't return value directly
        else:
            return jsonify({'error': f'Invalid algorithm: {algorithm}'}), 400
        
        # Validate best_move before returning
        if best_move is None or best_move < 0 or best_move >= COLS:
            return jsonify({'error': f'Invalid move returned: {best_move}'}), 500
        
        decision_time = time.time() - start_time
        update_metrics(stats.nodes_expanded, stats.pruned_nodes, decision_time)
        
        return jsonify({
            'move': best_move,
            'value': value if algorithm != 'iterative' else 0,
            'nodes_expanded': stats.nodes_expanded,
            'pruned_nodes': stats.pruned_nodes,
            'decision_time': decision_time,
            'depth': final_depth
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get current game metrics"""
    avg_nodes = (metrics['total_nodes_expanded'] / metrics['move_count']
                 if metrics['move_count'] > 0 else 0)
    avg_time = (metrics['total_decision_time'] / metrics['move_count']
                if metrics['move_count'] > 0 else 0)
    avg_pruned = (metrics['total_pruned_nodes'] / metrics['move_count']
                  if metrics['move_count'] > 0 else 0)
    
    # Calculate win rates
    human_vs_ai_win_rate = (metrics['ai_wins'] / metrics['games_played']
                            if metrics['games_played'] > 0 else 0)
    ai_vs_ai_total = metrics['ai_vs_ai_games_played']
    ai_vs_ai_player1_rate = (metrics['ai_vs_ai_player1_wins'] / ai_vs_ai_total
                             if ai_vs_ai_total > 0 else 0)
    ai_vs_ai_player2_rate = (metrics['ai_vs_ai_player2_wins'] / ai_vs_ai_total
                             if ai_vs_ai_total > 0 else 0)
    
    return jsonify({
        # Human vs AI stats
        'games_played': metrics['games_played'],
        'ai_wins': metrics['ai_wins'],
        'human_wins': metrics['human_wins'],
        'draws': metrics['draws'],
        'win_rate': human_vs_ai_win_rate,
        # AI vs AI stats
        'ai_vs_ai_games_played': metrics['ai_vs_ai_games_played'],
        'ai_vs_ai_player1_wins': metrics['ai_vs_ai_player1_wins'],
        'ai_vs_ai_player2_wins': metrics['ai_vs_ai_player2_wins'],
        'ai_vs_ai_draws': metrics['ai_vs_ai_draws'],
        'ai_vs_ai_player1_win_rate': ai_vs_ai_player1_rate,
        'ai_vs_ai_player2_win_rate': ai_vs_ai_player2_rate,
        # Performance metrics
        'average_nodes_expanded': avg_nodes,
        'average_decision_time': avg_time,
        'average_pruned_nodes': avg_pruned,
        'total_moves': metrics['move_count']
    })

@app.route('/api/metrics/reset', methods=['POST'])
def reset_metrics():
    """Reset all metrics"""
    global metrics
    metrics = {
        # Human vs AI stats
        'games_played': 0,
        'ai_wins': 0,
        'human_wins': 0,
        'draws': 0,
        # AI vs AI stats
        'ai_vs_ai_games_played': 0,
        'ai_vs_ai_player1_wins': 0,
        'ai_vs_ai_player2_wins': 0,
        'ai_vs_ai_draws': 0,
        # Performance metrics
        'total_nodes_expanded': 0,
        'total_pruned_nodes': 0,
        'total_decision_time': 0,
        'move_count': 0
    }
    return jsonify({'status': 'reset'})

@app.route('/api/game/end', methods=['POST'])
def game_end():
    """Record game end result"""
    data = request.json
    winner = data.get('winner')  # 1 = player 1, 2 = player 2, 0 = draw
    game_mode = data.get('game_mode', 'ai')  # 'ai' = human vs AI, 'ai_vs_ai' = AI vs AI
    
    if game_mode == 'ai_vs_ai':
        # Track AI vs AI games separately
        metrics['ai_vs_ai_games_played'] += 1
        if winner == 1:
            metrics['ai_vs_ai_player1_wins'] += 1
        elif winner == 2:
            metrics['ai_vs_ai_player2_wins'] += 1
        else:
            metrics['ai_vs_ai_draws'] += 1
    else:
        # Track Human vs AI games
        metrics['games_played'] += 1
        if winner == 2:
            metrics['ai_wins'] += 1
        elif winner == 1:
            metrics['human_wins'] += 1
        else:
            metrics['draws'] += 1
    
    return jsonify({'status': 'recorded'})

def update_metrics(nodes_expanded, pruned_nodes, decision_time):
    """Update global metrics"""
    metrics['move_count'] += 1
    metrics['total_nodes_expanded'] += nodes_expanded
    metrics['total_pruned_nodes'] += pruned_nodes
    metrics['total_decision_time'] += decision_time

if __name__ == '__main__':
    print("Starting Connect Four AI server...")
    print("=" * 50)
    print("Game available at: http://localhost:5001")
    print("=" * 50)
    print("API endpoints:")
    print("  GET  /              - Game interface")
    print("  POST /api/move      - Get AI move")
    print("  GET  /api/metrics   - Get game metrics")
    print("  POST /api/metrics/reset - Reset metrics")
    print("  POST /api/game/end  - Record game end")
    print("=" * 50)
    app.run(debug=True, port=5001, host='127.0.0.1')

