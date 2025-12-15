"""
Data Preprocessing Pipeline for Connect 4 Game Data
Handles feature engineering, data cleaning, and normalization
"""
import pandas as pd
import numpy as np
import json
import os
from typing import Dict, List, Tuple

class Connect4Preprocessor:
    """Preprocess Connect 4 game data for analysis"""
    
    def __init__(self, games_file=None, moves_file=None):
        """
        Initialize preprocessor with data files
        
        Args:
            games_file: Path to games CSV file (default: data/game_data.csv)
            moves_file: Path to moves CSV file (default: data/move_data.csv)
        """
        data_dir = os.path.dirname(os.path.abspath(__file__))
        self.games_file = games_file or os.path.join(data_dir, 'game_data.csv')
        self.moves_file = moves_file or os.path.join(data_dir, 'move_data.csv')
        self.games_df = None
        self.moves_df = None
        self.processed_games_df = None
        self.processed_moves_df = None
    
    def load_data(self):
        """Load data from CSV files"""
        print("Loading data...")
        self.games_df = pd.read_csv(self.games_file)
        self.moves_df = pd.read_csv(self.moves_file)
        print(f"Loaded {len(self.games_df)} games and {len(self.moves_df)} moves")
    
    def handle_missing_values(self):
        """Handle missing values in the dataset"""
        print("\nHandling missing values...")
        
        # Check for missing values in games data
        games_missing = self.games_df.isnull().sum()
        if games_missing.sum() > 0:
            print("Missing values in games data:")
            print(games_missing[games_missing > 0])
            # Fill missing values with appropriate defaults
            self.games_df = self.games_df.fillna({
                'winner': 0,  # Assume draw if missing
                'total_moves': self.games_df['total_moves'].median(),
                'game_duration': self.games_df['game_duration'].median()
            })
        
        # Check for missing values in moves data
        moves_missing = self.moves_df.isnull().sum()
        if moves_missing.sum() > 0:
            print("Missing values in moves data:")
            print(moves_missing[moves_missing > 0])
            # Fill missing values
            self.moves_df = self.moves_df.fillna({
                'nodes_expanded': 0,
                'pruned_nodes': 0,
                'decision_time': self.moves_df['decision_time'].median()
            })
        
        print("Missing values handled")
    
    def detect_outliers(self, threshold=3):
        """
        Detect outliers using Z-score method
        
        Args:
            threshold: Z-score threshold for outlier detection
        
        Returns:
            Dictionary with outlier information
        """
        print("\nDetecting outliers...")
        outliers_info = {}
        
        # Detect outliers in games data
        numeric_cols = ['total_moves', 'game_duration']
        for col in numeric_cols:
            z_scores = np.abs((self.games_df[col] - self.games_df[col].mean()) / self.games_df[col].std())
            outliers = self.games_df[z_scores > threshold]
            outliers_info[f'games_{col}'] = {
                'count': len(outliers),
                'indices': outliers.index.tolist()
            }
            print(f"  {col}: {len(outliers)} outliers detected")
        
        # Detect outliers in moves data
        numeric_cols = ['nodes_expanded', 'decision_time', 'pruned_nodes']
        for col in numeric_cols:
            if col in self.moves_df.columns:
                z_scores = np.abs((self.moves_df[col] - self.moves_df[col].mean()) / self.moves_df[col].std())
                outliers = self.moves_df[z_scores > threshold]
                outliers_info[f'moves_{col}'] = {
                    'count': len(outliers),
                    'indices': outliers.index.tolist()
                }
                print(f"  {col}: {len(outliers)} outliers detected")
        
        return outliers_info
    
    def handle_outliers(self, method='cap', threshold=3):
        """
        Handle outliers using specified method
        
        Args:
            method: 'cap' (cap at threshold) or 'remove' (remove outliers)
            threshold: Z-score threshold
        """
        print(f"\nHandling outliers using {method} method...")
        
        # Handle outliers in games data
        numeric_cols = ['total_moves', 'game_duration']
        for col in numeric_cols:
            z_scores = np.abs((self.games_df[col] - self.games_df[col].mean()) / self.games_df[col].std())
            if method == 'cap':
                # Cap outliers at threshold
                upper_bound = self.games_df[col].mean() + threshold * self.games_df[col].std()
                lower_bound = self.games_df[col].mean() - threshold * self.games_df[col].std()
                self.games_df[col] = self.games_df[col].clip(lower=lower_bound, upper=upper_bound)
            elif method == 'remove':
                self.games_df = self.games_df[z_scores <= threshold]
        
        # Handle outliers in moves data
        numeric_cols = ['nodes_expanded', 'decision_time', 'pruned_nodes']
        for col in numeric_cols:
            if col in self.moves_df.columns:
                z_scores = np.abs((self.moves_df[col] - self.moves_df[col].mean()) / self.moves_df[col].std())
                if method == 'cap':
                    upper_bound = self.moves_df[col].mean() + threshold * self.moves_df[col].std()
                    lower_bound = self.moves_df[col].mean() - threshold * self.moves_df[col].std()
                    self.moves_df[col] = self.moves_df[col].clip(lower=lower_bound, upper=upper_bound)
                elif method == 'remove':
                    self.moves_df = self.moves_df[z_scores <= threshold]
        
        print("Outliers handled")
    
    def extract_board_features(self, board_state: str) -> Dict:
        """
        Extract features from board state
        
        Args:
            board_state: JSON string of board state
        
        Returns:
            Dictionary of extracted features
        """
        try:
            board = json.loads(board_state)
            features = {}
            
            # Count pieces
            player1_pieces = sum(row.count(1) for row in board)
            player2_pieces = sum(row.count(2) for row in board)
            empty_cells = sum(row.count(0) for row in board)
            
            features['player1_pieces'] = player1_pieces
            features['player2_pieces'] = player2_pieces
            features['empty_cells'] = empty_cells
            features['total_pieces'] = player1_pieces + player2_pieces
            
            # Center control
            center_col = 3
            center_pieces_p1 = sum(board[row][center_col] == 1 for row in range(6))
            center_pieces_p2 = sum(board[row][center_col] == 2 for row in range(6))
            features['center_control_p1'] = center_pieces_p1
            features['center_control_p2'] = center_pieces_p2
            
            # Column heights (how many pieces in each column)
            column_heights = [sum(board[row][col] != 0 for row in range(6)) for col in range(7)]
            for i, height in enumerate(column_heights):
                features[f'col_{i}_height'] = height
            
            # Board density (pieces per row)
            row_densities = [sum(board[row][col] != 0 for col in range(7)) for row in range(6)]
            for i, density in enumerate(row_densities):
                features[f'row_{i}_density'] = density
            
            return features
        
        except:
            return {}
    
    def engineer_features(self):
        """Engineer new features from existing data"""
        print("\nEngineering features...")
        
        # Extract board features from moves data
        if 'board_state' in self.moves_df.columns:
            print("  Extracting board features...")
            board_features = self.moves_df['board_state'].apply(self.extract_board_features)
            board_features_df = pd.DataFrame(board_features.tolist())
            self.moves_df = pd.concat([self.moves_df, board_features_df], axis=1)
        
        # Create game-level features
        print("  Creating game-level features...")
        
        # Algorithm combinations
        self.games_df['algorithm_matchup'] = (
            self.games_df['player1_algorithm'] + '_vs_' + self.games_df['player2_algorithm']
        )
        
        # Depth combinations
        self.games_df['depth_matchup'] = (
            self.games_df['player1_depth'].astype(str) + '_vs_' + 
            self.games_df['player2_depth'].astype(str)
        )
        
        # Winner type
        self.games_df['winner_type'] = self.games_df['winner'].map({
            0: 'draw',
            1: 'player1',
            2: 'player2'
        })
        
        # Game efficiency (moves per second)
        self.games_df['moves_per_second'] = (
            self.games_df['total_moves'] / self.games_df['game_duration']
        )
        
        # Create move-level aggregated features
        print("  Creating move-level aggregated features...")
        move_aggregates = self.moves_df.groupby('game_id').agg({
            'nodes_expanded': ['mean', 'sum', 'max'],
            'pruned_nodes': ['mean', 'sum', 'max'],
            'decision_time': ['mean', 'sum', 'max'],
            'column': ['mean', 'std']
        }).reset_index()
        
        move_aggregates.columns = ['game_id'] + [
            f'move_{col[0]}_{col[1]}' for col in move_aggregates.columns[1:]
        ]
        
        # Merge with games data
        self.games_df = self.games_df.merge(move_aggregates, on='game_id', how='left')
        
        print("Feature engineering complete")
    
    def normalize_data(self, columns_to_normalize=None):
        """
        Normalize numerical columns
        
        Args:
            columns_to_normalize: List of columns to normalize (None = auto-detect)
        """
        print("\nNormalizing data...")
        
        if columns_to_normalize is None:
            # Auto-detect numerical columns
            games_numeric = self.games_df.select_dtypes(include=[np.number]).columns.tolist()
            moves_numeric = self.moves_df.select_dtypes(include=[np.number]).columns.tolist()
            
            # Don't normalize IDs and categorical encodings
            games_numeric = [col for col in games_numeric if col not in ['game_id', 'winner', 'player1_depth', 'player2_depth']]
            moves_numeric = [col for col in moves_numeric if col not in ['game_id', 'move_number', 'player', 'column', 'row', 'depth']]
        
        # Normalize games data
        for col in games_numeric:
            if col in self.games_df.columns:
                mean = self.games_df[col].mean()
                std = self.games_df[col].std()
                if std > 0:
                    self.games_df[f'{col}_normalized'] = (self.games_df[col] - mean) / std
        
        # Normalize moves data
        for col in moves_numeric:
            if col in self.moves_df.columns:
                mean = self.moves_df[col].mean()
                std = self.moves_df[col].std()
                if std > 0:
                    self.moves_df[f'{col}_normalized'] = (self.moves_df[col] - mean) / std
        
        print("Normalization complete")
    
    def clean_data(self):
        """Clean the dataset"""
        print("\nCleaning data...")
        
        # Remove duplicate games
        initial_count = len(self.games_df)
        self.games_df = self.games_df.drop_duplicates(subset=['game_id'])
        removed = initial_count - len(self.games_df)
        if removed > 0:
            print(f"  Removed {removed} duplicate games")
        
        # Remove invalid moves
        initial_moves = len(self.moves_df)
        self.moves_df = self.moves_df[
            (self.moves_df['column'] >= 0) & 
            (self.moves_df['column'] < 7) &
            (self.moves_df['row'] >= 0) &
            (self.moves_df['row'] < 6)
        ]
        removed_moves = initial_moves - len(self.moves_df)
        if removed_moves > 0:
            print(f"  Removed {removed_moves} invalid moves")
        
        # Remove games with too few moves (likely errors)
        game_move_counts = self.moves_df.groupby('game_id').size()
        valid_games = game_move_counts[game_move_counts >= 4].index
        self.games_df = self.games_df[self.games_df['game_id'].isin(valid_games)]
        self.moves_df = self.moves_df[self.moves_df['game_id'].isin(valid_games)]
        
        print("Data cleaning complete")
    
    def preprocess(self, handle_outliers_method='cap', normalize=True):
        """
        Run complete preprocessing pipeline
        
        Args:
            handle_outliers_method: Method to handle outliers ('cap' or 'remove')
            normalize: Whether to normalize numerical features
        """
        print("=" * 60)
        print("Starting Data Preprocessing Pipeline")
        print("=" * 60)
        
        # Load data
        self.load_data()
        
        # Clean data
        self.clean_data()
        
        # Handle missing values
        self.handle_missing_values()
        
        # Detect outliers
        outliers_info = self.detect_outliers()
        
        # Handle outliers
        self.handle_outliers(method=handle_outliers_method)
        
        # Engineer features
        self.engineer_features()
        
        # Normalize data
        if normalize:
            self.normalize_data()
        
        # Store processed data
        self.processed_games_df = self.games_df.copy()
        self.processed_moves_df = self.moves_df.copy()
        
        print("\n" + "=" * 60)
        print("Preprocessing Complete!")
        print("=" * 60)
        print(f"Processed games: {len(self.processed_games_df)}")
        print(f"Processed moves: {len(self.processed_moves_df)}")
        print(f"Games features: {len(self.processed_games_df.columns)}")
        print(f"Moves features: {len(self.processed_moves_df.columns)}")
    
    def save_processed_data(self, games_file=None, moves_file=None):
        """Save processed data to CSV files"""
        data_dir = os.path.dirname(os.path.abspath(__file__))
        if games_file is None:
            games_file = os.path.join(data_dir, 'processed_game_data.csv')
        if moves_file is None:
            moves_file = os.path.join(data_dir, 'processed_move_data.csv')
        
        if self.processed_games_df is not None:
            self.processed_games_df.to_csv(games_file, index=False)
            print(f"Saved processed games data to {games_file}")
        
        if self.processed_moves_df is not None:
            self.processed_moves_df.to_csv(moves_file, index=False)
            print(f"Saved processed moves data to {moves_file}")


def main():
    """Main function to run preprocessing"""
    preprocessor = Connect4Preprocessor()
    
    # Run preprocessing pipeline
    preprocessor.preprocess(handle_outliers_method='cap', normalize=True)
    
    # Save processed data
    preprocessor.save_processed_data()
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("Processed Data Summary")
    print("=" * 60)
    print("\nGames Data:")
    print(preprocessor.processed_games_df.describe())
    print("\nMoves Data:")
    print(preprocessor.processed_moves_df.describe())


if __name__ == '__main__':
    main()

