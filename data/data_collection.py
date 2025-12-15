"""
Data Collection Module for Connect 4 AI
Automatically plays games and collects data for EDA and analysis
"""
import json
import csv
import time
import random
import os
import sys
from datetime import datetime

# Add parent directory to path to import ai module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai import (
    create_empty_board,
    copy_board,
    get_valid_moves,
    get_drop_row,
    check_win,
    is_board_full,
    is_terminal,
    minimax_without_ab,
    minimax_with_ab,
    iterative_deepening,
    MinimaxStats
)

class GameDataCollector:
    """Collects game data for analysis"""
    
    def __init__(self):
        self.games_data = []
        self.move_data = []
    
    def play_game(self, player1_algorithm='minimax_ab', player1_depth=5,
                  player2_algorithm='minimax_ab', player2_depth=5,
                  randomize_first=True):
        """
        Play a single game between two AI players
        
        Args:
            player1_algorithm: Algorithm for player 1 ('minimax', 'minimax_ab', 'iterative', 'random')
            player1_depth: Search depth for player 1
            player2_algorithm: Algorithm for player 2
            player2_depth: Search depth for player 2
            randomize_first: Whether to randomize starting player
        
        Returns:
            Dictionary with game results
        """
        board = create_empty_board()
        current_player = random.randint(1, 2) if randomize_first else 1
        move_count = 0
        game_start_time = time.time()
        
        # Game metadata
        game_id = len(self.games_data)
        game_moves = []
        
        while True:
            move_count += 1
            
            # Determine which algorithm to use
            if current_player == 1:
                algorithm = player1_algorithm
                depth = player1_depth
            else:
                algorithm = player2_algorithm
                depth = player2_depth
            
            # Get valid moves
            valid_moves = get_valid_moves(board)
            if not valid_moves:
                # Draw
                game_end_time = time.time()
                game_duration = game_end_time - game_start_time
                
                game_result = {
                    'game_id': game_id,
                    'winner': 0,  # Draw
                    'total_moves': move_count,
                    'game_duration': game_duration,
                    'player1_algorithm': player1_algorithm,
                    'player1_depth': player1_depth,
                    'player2_algorithm': player2_algorithm,
                    'player2_depth': player2_depth,
                    'timestamp': datetime.now().isoformat()
                }
                self.games_data.append(game_result)
                return game_result
            
            # Make move
            move_start_time = time.time()
            stats = MinimaxStats()
            best_move = None
            
            # Check for immediate wins/blocks first
            for col in valid_moves:
                row = get_drop_row(board, col)
                if row == -1:
                    continue
                new_board = copy_board(board)
                new_board[row][col] = current_player
                if check_win(new_board, row, col, current_player):
                    best_move = col
                    stats.nodes_expanded = 1
                    break
            
            if best_move is None:
                # Check for opponent's immediate win
                opponent = 3 - current_player
                for col in valid_moves:
                    row = get_drop_row(board, col)
                    if row == -1:
                        continue
                    new_board = copy_board(board)
                    new_board[row][col] = opponent
                    if check_win(new_board, row, col, opponent):
                        best_move = col
                        stats.nodes_expanded = 1
                        break
            
            # Use algorithm if no immediate win/block
            if best_move is None:
                # Calculate randomness based on depth (same as app.py)
                randomness = max(0.0, 0.25 - (depth * 0.03))
                randomness = min(0.2, randomness)
                
                if algorithm == 'random':
                    best_move = random.choice(valid_moves)
                    stats.nodes_expanded = 1
                elif algorithm == 'minimax':
                    _, best_move = minimax_without_ab(
                        board, depth, True, current_player, stats, randomness
                    )
                elif algorithm == 'minimax_ab':
                    _, best_move = minimax_with_ab(
                        board, depth, float('-inf'), float('inf'), True, current_player, stats, randomness
                    )
                elif algorithm == 'iterative':
                    best_move, final_depth, stats = iterative_deepening(
                        board, depth, current_player, time_limit=5.0, randomness=randomness
                    )
            
            move_time = time.time() - move_start_time
            
            # Record move data
            row = get_drop_row(board, best_move)
            board[row][best_move] = current_player
            
            move_record = {
                'game_id': game_id,
                'move_number': move_count,
                'player': current_player,
                'column': best_move,
                'row': row,
                'algorithm': algorithm,
                'depth': depth,
                'nodes_expanded': stats.nodes_expanded,
                'pruned_nodes': stats.pruned_nodes,
                'decision_time': move_time,
                'board_state': json.dumps(board),  # Store as JSON string
                'timestamp': datetime.now().isoformat()
            }
            self.move_data.append(move_record)
            game_moves.append(move_record)
            
            # Check for win
            if check_win(board, row, best_move, current_player):
                game_end_time = time.time()
                game_duration = game_end_time - game_start_time
                
                game_result = {
                    'game_id': game_id,
                    'winner': current_player,
                    'total_moves': move_count,
                    'game_duration': game_duration,
                    'player1_algorithm': player1_algorithm,
                    'player1_depth': player1_depth,
                    'player2_algorithm': player2_algorithm,
                    'player2_depth': player2_depth,
                    'timestamp': datetime.now().isoformat()
                }
                self.games_data.append(game_result)
                return game_result
            
            # Check for draw
            if is_board_full(board):
                game_end_time = time.time()
                game_duration = game_end_time - game_start_time
                
                game_result = {
                    'game_id': game_id,
                    'winner': 0,
                    'total_moves': move_count,
                    'game_duration': game_duration,
                    'player1_algorithm': player1_algorithm,
                    'player1_depth': player1_depth,
                    'player2_algorithm': player2_algorithm,
                    'player2_depth': player2_depth,
                    'timestamp': datetime.now().isoformat()
                }
                self.games_data.append(game_result)
                return game_result
            
            # Switch player
            current_player = 3 - current_player
    
    def collect_games(self, num_games=200, 
                     algorithms=['minimax', 'minimax_ab', 'iterative'],
                     depths=[3, 5, 7]):
        """
        Collect multiple games with different configurations
        
        Args:
            num_games: Number of games to play
            algorithms: List of algorithms to test
            depths: List of depths to test
        """
        print(f"Starting data collection: {num_games} games")
        print("=" * 60)
        
        game_configs = []
        for alg1 in algorithms:
            for alg2 in algorithms:
                for depth1 in depths:
                    for depth2 in depths:
                        game_configs.append((alg1, depth1, alg2, depth2))
        
        # Randomize configurations
        random.shuffle(game_configs)
        
        games_per_config = max(1, num_games // len(game_configs))
        total_collected = 0
        
        for i, (alg1, depth1, alg2, depth2) in enumerate(game_configs[:num_games]):
            if total_collected >= num_games:
                break
            
            try:
                result = self.play_game(
                    player1_algorithm=alg1,
                    player1_depth=depth1,
                    player2_algorithm=alg2,
                    player2_depth=depth2,
                    randomize_first=True
                )
                total_collected += 1
                
                if total_collected % 10 == 0:
                    print(f"Progress: {total_collected}/{num_games} games collected")
                    print(f"  Last game: {result['winner']} won in {result['total_moves']} moves")
            
            except Exception as e:
                print(f"Error in game {total_collected}: {e}")
                continue
        
        print("=" * 60)
        print(f"Data collection complete: {total_collected} games collected")
        print(f"Total moves recorded: {len(self.move_data)}")
    
    def save_to_csv(self, games_file=None, moves_file=None):
        """Save collected data to CSV files"""
        # Use data directory for output files
        data_dir = os.path.dirname(os.path.abspath(__file__))
        if games_file is None:
            games_file = os.path.join(data_dir, 'game_data.csv')
        if moves_file is None:
            moves_file = os.path.join(data_dir, 'move_data.csv')
        
        # Save games data
        if self.games_data:
            with open(games_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.games_data[0].keys())
                writer.writeheader()
                writer.writerows(self.games_data)
            print(f"Saved {len(self.games_data)} games to {games_file}")
        
        # Save moves data
        if self.move_data:
            with open(moves_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.move_data[0].keys())
                writer.writeheader()
                writer.writerows(self.move_data)
            print(f"Saved {len(self.move_data)} moves to {moves_file}")
    
    def save_to_json(self, games_file=None, moves_file=None):
        """Save collected data to JSON files"""
        # Use data directory for output files
        data_dir = os.path.dirname(os.path.abspath(__file__))
        if games_file is None:
            games_file = os.path.join(data_dir, 'game_data.json')
        if moves_file is None:
            moves_file = os.path.join(data_dir, 'move_data.json')
        
        if self.games_data:
            with open(games_file, 'w') as f:
                json.dump(self.games_data, f, indent=2)
            print(f"Saved {len(self.games_data)} games to {games_file}")
        
        if self.move_data:
            with open(moves_file, 'w') as f:
                json.dump(self.move_data, f, indent=2)
            print(f"Saved {len(self.move_data)} moves to {moves_file}")


def main():
    """Main function to run data collection"""
    collector = GameDataCollector()
    
    # Collect games with various configurations
    collector.collect_games(
        num_games=200,
        algorithms=['minimax', 'minimax_ab', 'iterative'],
        depths=[3, 5, 7]
    )
    
    # Save data
    collector.save_to_csv()
    collector.save_to_json()
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("Summary Statistics:")
    print("=" * 60)
    
    if collector.games_data:
        winners = [g['winner'] for g in collector.games_data]
        total_moves = [g['total_moves'] for g in collector.games_data]
        durations = [g['game_duration'] for g in collector.games_data]
        
        print(f"Total games: {len(collector.games_data)}")
        print(f"Player 1 wins: {winners.count(1)}")
        print(f"Player 2 wins: {winners.count(2)}")
        print(f"Draws: {winners.count(0)}")
        print(f"Average moves per game: {sum(total_moves) / len(total_moves):.2f}")
        print(f"Average game duration: {sum(durations) / len(durations):.2f}s")
        print(f"Total moves recorded: {len(collector.move_data)}")


if __name__ == '__main__':
    main()

