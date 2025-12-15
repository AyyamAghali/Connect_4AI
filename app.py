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

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for JavaScript frontend

@app.route('/')
def index():
    """Serve the main game page"""
    return send_from_directory('.', 'index.html')

@app.route('/game.js')
def serve_game_js():
    """Serve the game JavaScript file"""
    return send_from_directory('.', 'game.js')

# Global metrics tracking
metrics = {
    'games_played': 0,
    'ai_wins': 0,
    'human_wins': 0,
    'draws': 0,
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
            best_move = random.choice(valid_moves)
            value = 0
            stats.nodes_expanded = 1
        elif algorithm == 'minimax':
            value, best_move = minimax_without_ab(board, depth, True, player, stats)
        elif algorithm == 'minimax_ab':
            value, best_move = minimax_with_ab(
                board, depth, float('-inf'), float('inf'), True, player, stats
            )
        elif algorithm == 'iterative':
            best_move, final_depth, stats = iterative_deepening(
                board, depth, player, time_limit
            )
            value = 0  # Iterative deepening doesn't return value directly
        else:
            return jsonify({'error': 'Invalid algorithm'}), 400
        
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
    
    return jsonify({
        'games_played': metrics['games_played'],
        'ai_wins': metrics['ai_wins'],
        'human_wins': metrics['human_wins'],
        'draws': metrics['draws'],
        'win_rate': (metrics['ai_wins'] / metrics['games_played']
                     if metrics['games_played'] > 0 else 0),
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
        'games_played': 0,
        'ai_wins': 0,
        'human_wins': 0,
        'draws': 0,
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
    winner = data.get('winner')  # 1 = human, 2 = AI, 0 = draw
    
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

