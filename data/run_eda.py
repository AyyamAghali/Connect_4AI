"""
EDA Script for Connect 4 AI
Run this script to perform exploratory data analysis
Can also be converted to Jupyter notebook cells
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from scipy import stats
import warnings
import os

warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def load_data():
    """Load data from CSV files"""
    print("=" * 60)
    print("LOADING DATA")
    print("=" * 60)
    
    # Get data directory (where this script is located)
    data_dir = os.path.dirname(os.path.abspath(__file__))
    games_file = os.path.join(data_dir, 'game_data.csv')
    moves_file = os.path.join(data_dir, 'move_data.csv')
    
    if not os.path.exists(games_file):
        print(f"ERROR: {games_file} not found!")
        print("Please run: python data/data_collection.py")
        return None, None
    
    games_df = pd.read_csv(games_file)
    moves_df = pd.read_csv(moves_file)
    
    print(f"✓ Loaded {len(games_df)} games")
    print(f"✓ Loaded {len(moves_df)} moves")
    return games_df, moves_df

def data_overview(games_df, moves_df):
    """Display data overview and basic statistics"""
    print("\n" + "=" * 60)
    print("DATA OVERVIEW")
    print("=" * 60)
    
    print("\nGames Data:")
    print(f"  Shape: {games_df.shape}")
    print(f"  Columns: {list(games_df.columns)}")
    print(f"  Missing values: {games_df.isnull().sum().sum()}")
    
    print("\nMoves Data:")
    print(f"  Shape: {moves_df.shape}")
    print(f"  Columns: {list(moves_df.columns)}")
    print(f"  Missing values: {moves_df.isnull().sum().sum()}")
    
    print("\nGames Data Info:")
    print(games_df.info())
    
    print("\nMoves Data Info:")
    print(moves_df.info())

def five_number_summary(games_df, moves_df):
    """Calculate five-number summary"""
    print("\n" + "=" * 60)
    print("FIVE-NUMBER SUMMARY")
    print("=" * 60)
    
    print("\nGames Data:")
    numeric_cols = games_df.select_dtypes(include=[np.number]).columns
    numeric_cols = [col for col in numeric_cols if col not in ['game_id', 'winner']]
    
    for col in numeric_cols:
        print(f"\n{col}:")
        print(f"  Min: {games_df[col].min():.2f}")
        print(f"  Q1: {games_df[col].quantile(0.25):.2f}")
        print(f"  Median: {games_df[col].median():.2f}")
        print(f"  Q3: {games_df[col].quantile(0.75):.2f}")
        print(f"  Max: {games_df[col].max():.2f}")
        print(f"  Mean: {games_df[col].mean():.2f}")
        print(f"  Std: {games_df[col].std():.2f}")
    
    print("\nMoves Data:")
    numeric_cols = moves_df.select_dtypes(include=[np.number]).columns
    numeric_cols = [col for col in numeric_cols if col not in ['game_id', 'move_number', 'player', 'column', 'row', 'depth']]
    
    for col in numeric_cols[:5]:  # Limit to first 5 for readability
        print(f"\n{col}:")
        print(f"  Min: {moves_df[col].min():.2f}")
        print(f"  Q1: {moves_df[col].quantile(0.25):.2f}")
        print(f"  Median: {moves_df[col].median():.2f}")
        print(f"  Q3: {moves_df[col].quantile(0.75):.2f}")
        print(f"  Max: {moves_df[col].max():.2f}")
        print(f"  Mean: {moves_df[col].mean():.2f}")
        print(f"  Std: {moves_df[col].std():.2f}")

def detect_outliers(games_df, moves_df):
    """Detect outliers using IQR method"""
    print("\n" + "=" * 60)
    print("OUTLIER DETECTION")
    print("=" * 60)
    
    def detect_outliers_iqr(data, column):
        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = data[(data[column] < lower_bound) | (data[column] > upper_bound)]
        return outliers, lower_bound, upper_bound
    
    # Check games data
    if 'game_duration' in games_df.columns:
        outliers, lb, ub = detect_outliers_iqr(games_df, 'game_duration')
        print(f"\nGame Duration:")
        print(f"  Outliers: {len(outliers)} ({len(outliers)/len(games_df)*100:.2f}%)")
        print(f"  Bounds: [{lb:.2f}, {ub:.2f}]")
    
    if 'total_moves' in games_df.columns:
        outliers, lb, ub = detect_outliers_iqr(games_df, 'total_moves')
        print(f"\nTotal Moves:")
        print(f"  Outliers: {len(outliers)} ({len(outliers)/len(games_df)*100:.2f}%)")
        print(f"  Bounds: [{lb:.2f}, {ub:.2f}]")
    
    # Check moves data
    if 'decision_time' in moves_df.columns:
        outliers, lb, ub = detect_outliers_iqr(moves_df, 'decision_time')
        print(f"\nDecision Time:")
        print(f"  Outliers: {len(outliers)} ({len(outliers)/len(moves_df)*100:.2f}%)")
        print(f"  Bounds: [{lb:.4f}, {ub:.4f}]")
    
    if 'nodes_expanded' in moves_df.columns:
        outliers, lb, ub = detect_outliers_iqr(moves_df, 'nodes_expanded')
        print(f"\nNodes Expanded:")
        print(f"  Outliers: {len(outliers)} ({len(outliers)/len(moves_df)*100:.2f}%)")
        print(f"  Bounds: [{lb:.2f}, {ub:.2f}]")

def create_visualizations(games_df, moves_df):
    """Create all visualizations"""
    print("\n" + "=" * 60)
    print("CREATING VISUALIZATIONS")
    print("=" * 60)
    
    # Create output directory in data folder
    data_dir = os.path.dirname(os.path.abspath(__file__))
    plots_dir = os.path.join(data_dir, 'eda_plots')
    os.makedirs(plots_dir, exist_ok=True)
    
    # 1. Histograms
    print("\n1. Creating histograms...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    if 'game_duration' in games_df.columns:
        axes[0, 0].hist(games_df['game_duration'], bins=30, edgecolor='black')
        axes[0, 0].set_title('Distribution of Game Duration')
        axes[0, 0].set_xlabel('Duration (seconds)')
        axes[0, 0].set_ylabel('Frequency')
    
    if 'total_moves' in games_df.columns:
        axes[0, 1].hist(games_df['total_moves'], bins=30, edgecolor='black')
        axes[0, 1].set_title('Distribution of Total Moves')
        axes[0, 1].set_xlabel('Number of Moves')
        axes[0, 1].set_ylabel('Frequency')
    
    if 'decision_time' in moves_df.columns:
        axes[1, 0].hist(moves_df['decision_time'], bins=50, edgecolor='black')
        axes[1, 0].set_title('Distribution of Decision Time')
        axes[1, 0].set_xlabel('Time (seconds)')
        axes[1, 0].set_ylabel('Frequency')
    
    if 'nodes_expanded' in moves_df.columns:
        axes[1, 1].hist(moves_df['nodes_expanded'], bins=50, edgecolor='black')
        axes[1, 1].set_title('Distribution of Nodes Expanded')
        axes[1, 1].set_xlabel('Nodes')
        axes[1, 1].set_ylabel('Frequency')
    
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, 'histograms.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ Saved histograms.png")
    
    # 2. Box plots
    print("2. Creating box plots...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    if 'game_duration' in games_df.columns:
        axes[0, 0].boxplot(games_df['game_duration'])
        axes[0, 0].set_title('Game Duration Distribution')
        axes[0, 0].set_ylabel('Duration (seconds)')
    
    if 'total_moves' in games_df.columns:
        axes[0, 1].boxplot(games_df['total_moves'])
        axes[0, 1].set_title('Total Moves Distribution')
        axes[0, 1].set_ylabel('Number of Moves')
    
    if 'decision_time' in moves_df.columns:
        axes[1, 0].boxplot(moves_df['decision_time'])
        axes[1, 0].set_title('Decision Time Distribution')
        axes[1, 0].set_ylabel('Time (seconds)')
    
    if 'nodes_expanded' in moves_df.columns:
        axes[1, 1].boxplot(moves_df['nodes_expanded'])
        axes[1, 1].set_title('Nodes Expanded Distribution')
        axes[1, 1].set_ylabel('Nodes')
    
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, 'boxplots.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ Saved boxplots.png")
    
    # 3. Bar charts
    print("3. Creating bar charts...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    if 'winner' in games_df.columns:
        winner_counts = games_df['winner'].value_counts().sort_index()
        winner_labels = ['Draw', 'Player 1', 'Player 2']
        axes[0, 0].bar(winner_labels, winner_counts.values)
        axes[0, 0].set_title('Game Outcomes Distribution')
        axes[0, 0].set_ylabel('Count')
        for i, v in enumerate(winner_counts.values):
            axes[0, 0].text(i, v, str(v), ha='center', va='bottom')
    
    if 'player1_algorithm' in games_df.columns:
        alg_counts = games_df['player1_algorithm'].value_counts()
        axes[0, 1].bar(alg_counts.index, alg_counts.values)
        axes[0, 1].set_title('Player 1 Algorithm Distribution')
        axes[0, 1].set_ylabel('Count')
        axes[0, 1].tick_params(axis='x', rotation=45)
    
    if 'player1_depth' in games_df.columns:
        depth_counts = games_df['player1_depth'].value_counts().sort_index()
        axes[1, 0].bar(depth_counts.index.astype(str), depth_counts.values)
        axes[1, 0].set_title('Player 1 Depth Distribution')
        axes[1, 0].set_xlabel('Depth')
        axes[1, 0].set_ylabel('Count')
    
    if 'column' in moves_df.columns:
        col_counts = moves_df['column'].value_counts().sort_index()
        axes[1, 1].bar(col_counts.index.astype(str), col_counts.values)
        axes[1, 1].set_title('Column Selection Distribution')
        axes[1, 1].set_xlabel('Column')
        axes[1, 1].set_ylabel('Count')
    
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, 'barcharts.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ Saved barcharts.png")
    
    # 4. Correlation heatmaps
    print("4. Creating correlation heatmaps...")
    
    # Games data correlation
    numeric_games = games_df.select_dtypes(include=[np.number])
    numeric_games = numeric_games.drop(['game_id'], axis=1, errors='ignore')
    
    if len(numeric_games.columns) > 1:
        corr_matrix = numeric_games.corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=1, cbar_kws={"shrink": 0.8})
        plt.title('Correlation Matrix - Games Data')
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, 'correlation_games.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ Saved correlation_games.png")
    
    # Moves data correlation
    numeric_moves = moves_df.select_dtypes(include=[np.number])
    numeric_moves = numeric_moves.drop(['game_id', 'move_number'], axis=1, errors='ignore')
    
    if len(numeric_moves.columns) > 1:
        corr_matrix = numeric_moves.corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=1, cbar_kws={"shrink": 0.8})
        plt.title('Correlation Matrix - Moves Data')
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, 'correlation_moves.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ Saved correlation_moves.png")
    
    # 5. Scatter plots
    print("5. Creating scatter plots...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    if 'game_duration' in games_df.columns and 'total_moves' in games_df.columns:
        axes[0, 0].scatter(games_df['total_moves'], games_df['game_duration'], alpha=0.5)
        axes[0, 0].set_xlabel('Total Moves')
        axes[0, 0].set_ylabel('Game Duration (seconds)')
        axes[0, 0].set_title('Game Duration vs Total Moves')
    
    if 'decision_time' in moves_df.columns and 'nodes_expanded' in moves_df.columns:
        axes[0, 1].scatter(moves_df['nodes_expanded'], moves_df['decision_time'], alpha=0.3)
        axes[0, 1].set_xlabel('Nodes Expanded')
        axes[0, 1].set_ylabel('Decision Time (seconds)')
        axes[0, 1].set_title('Decision Time vs Nodes Expanded')
    
    if 'depth' in moves_df.columns and 'nodes_expanded' in moves_df.columns:
        axes[1, 0].scatter(moves_df['depth'], moves_df['nodes_expanded'], alpha=0.3)
        axes[1, 0].set_xlabel('Search Depth')
        axes[1, 0].set_ylabel('Nodes Expanded')
        axes[1, 0].set_title('Nodes Expanded vs Search Depth')
    
    if 'pruned_nodes' in moves_df.columns and 'nodes_expanded' in moves_df.columns:
        axes[1, 1].scatter(moves_df['nodes_expanded'], moves_df['pruned_nodes'], alpha=0.3)
        axes[1, 1].set_xlabel('Nodes Expanded')
        axes[1, 1].set_ylabel('Pruned Nodes')
        axes[1, 1].set_title('Pruned Nodes vs Nodes Expanded')
    
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, 'scatterplots.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ Saved scatterplots.png")
    
    # 6. Algorithm performance
    print("6. Creating algorithm performance plots...")
    if 'player1_algorithm' in games_df.columns and 'winner' in games_df.columns:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        alg_win_rates = games_df.groupby('player1_algorithm').apply(
            lambda x: (x['winner'] == 1).sum() / len(x)
        ).sort_values(ascending=False)
        
        axes[0].bar(alg_win_rates.index, alg_win_rates.values)
        axes[0].set_title('Win Rate as Player 1 by Algorithm')
        axes[0].set_ylabel('Win Rate')
        axes[0].set_ylim([0, 1])
        axes[0].tick_params(axis='x', rotation=45)
        
        if 'game_duration' in games_df.columns:
            alg_avg_duration = games_df.groupby('player1_algorithm')['game_duration'].mean()
            axes[1].bar(alg_avg_duration.index, alg_avg_duration.values)
            axes[1].set_title('Average Game Duration by Algorithm')
            axes[1].set_ylabel('Duration (seconds)')
            axes[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, 'algorithm_performance.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ Saved algorithm_performance.png")

def correlation_analysis(games_df, moves_df):
    """Perform correlation analysis"""
    print("\n" + "=" * 60)
    print("CORRELATION ANALYSIS")
    print("=" * 60)
    
    # Games data correlations
    numeric_games = games_df.select_dtypes(include=[np.number])
    numeric_games = numeric_games.drop(['game_id'], axis=1, errors='ignore')
    
    if len(numeric_games.columns) > 1:
        corr_matrix = numeric_games.corr()
        print("\nTop Correlations (Games Data):")
        corr_pairs = corr_matrix.unstack().sort_values(ascending=False)
        corr_pairs = corr_pairs[corr_pairs != 1.0]
        print(corr_pairs.head(10))
    
    # Moves data correlations
    numeric_moves = moves_df.select_dtypes(include=[np.number])
    numeric_moves = numeric_moves.drop(['game_id', 'move_number'], axis=1, errors='ignore')
    
    if len(numeric_moves.columns) > 1:
        corr_matrix = numeric_moves.corr()
        print("\nTop Correlations (Moves Data):")
        corr_pairs = corr_matrix.unstack().sort_values(ascending=False)
        corr_pairs = corr_pairs[corr_pairs != 1.0]
        print(corr_pairs.head(10))

def summary_insights(games_df, moves_df):
    """Generate summary insights"""
    print("\n" + "=" * 60)
    print("SUMMARY INSIGHTS")
    print("=" * 60)
    
    print("\n1. GAME OUTCOMES:")
    if 'winner' in games_df.columns:
        winner_dist = games_df['winner'].value_counts().sort_index()
        total_games = len(games_df)
        print(f"   Total games: {total_games}")
        print(f"   Player 1 wins: {winner_dist.get(1, 0)} ({winner_dist.get(1, 0)/total_games*100:.1f}%)")
        print(f"   Player 2 wins: {winner_dist.get(2, 0)} ({winner_dist.get(2, 0)/total_games*100:.1f}%)")
        print(f"   Draws: {winner_dist.get(0, 0)} ({winner_dist.get(0, 0)/total_games*100:.1f}%)")
    
    print("\n2. GAME LENGTH:")
    if 'total_moves' in games_df.columns:
        print(f"   Average moves per game: {games_df['total_moves'].mean():.2f}")
        print(f"   Median moves per game: {games_df['total_moves'].median():.2f}")
        print(f"   Min moves: {games_df['total_moves'].min()}")
        print(f"   Max moves: {games_df['total_moves'].max()}")
    
    print("\n3. PERFORMANCE METRICS:")
    if 'nodes_expanded' in moves_df.columns:
        print(f"   Average nodes expanded per move: {moves_df['nodes_expanded'].mean():.2f}")
        print(f"   Median nodes expanded: {moves_df['nodes_expanded'].median():.2f}")
    
    if 'decision_time' in moves_df.columns:
        print(f"   Average decision time: {moves_df['decision_time'].mean():.4f} seconds")
        print(f"   Median decision time: {moves_df['decision_time'].median():.4f} seconds")
    
    if 'pruned_nodes' in moves_df.columns:
        total_pruned = moves_df['pruned_nodes'].sum()
        total_nodes = moves_df['nodes_expanded'].sum()
        if total_nodes > 0:
            pruning_rate = total_pruned / total_nodes * 100
            print(f"   Pruning rate: {pruning_rate:.2f}%")
    
    print("\n4. ALGORITHM COMPARISON:")
    if 'player1_algorithm' in games_df.columns:
        for alg in games_df['player1_algorithm'].unique():
            alg_games = games_df[games_df['player1_algorithm'] == alg]
            win_rate = (alg_games['winner'] == 1).sum() / len(alg_games) if len(alg_games) > 0 else 0
            print(f"   {alg}: {len(alg_games)} games, {win_rate*100:.1f}% win rate as Player 1")

def main():
    """Main EDA function"""
    print("=" * 60)
    print("EXPLORATORY DATA ANALYSIS - CONNECT 4 AI")
    print("=" * 60)
    
    # Load data
    games_df, moves_df = load_data()
    if games_df is None:
        return
    
    # Run EDA steps
    data_overview(games_df, moves_df)
    five_number_summary(games_df, moves_df)
    detect_outliers(games_df, moves_df)
    create_visualizations(games_df, moves_df)
    correlation_analysis(games_df, moves_df)
    summary_insights(games_df, moves_df)
    
    print("\n" + "=" * 60)
    print("EDA COMPLETE!")
    print("=" * 60)
    data_dir = os.path.dirname(os.path.abspath(__file__))
    plots_dir = os.path.join(data_dir, 'eda_plots')
    print(f"All visualizations saved to '{plots_dir}/' directory")

if __name__ == '__main__':
    main()

