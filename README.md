# Connect 4 AI Game

A web-based Connect 4 game featuring an AI opponent with multiple algorithms (Minimax, Alpha-Beta Pruning, and Iterative Deepening).

## Features

- 🎮 **Interactive Web Interface** - Beautiful, modern UI built with HTML5 Canvas
- 🤖 **AI Opponent** - Play against an intelligent AI with multiple difficulty levels
- 📊 **Game Statistics** - Track wins, losses, and AI performance metrics
- 🔧 **Multiple Algorithms** - Choose from different AI algorithms:
  - Minimax (without pruning)
  - Minimax with Alpha-Beta Pruning
  - Iterative Deepening
- ⚙️ **Customizable Difficulty** - Adjust AI search depth (Easy to Expert)

## Prerequisites

- **Python 3.7 or higher** (Python 3.8+ recommended)
- **pip** (Python package installer)

To check if you have Python installed, open a terminal/command prompt and run:
```bash
python --version
```
or
```bash
python3 --version
```

## Quick Start

### Step 1: Install Dependencies

Open a terminal/command prompt in the project directory and run:

**On macOS/Linux:**
```bash
pip3 install -r requirements.txt
```

**On Windows:**
```bash
pip install -r requirements.txt
```

If you encounter permission errors, use:
```bash
pip3 install --user -r requirements.txt
```

### Step 2: Start the Server

**Option A: Using the Python run script (Recommended - Works on all platforms)**
```bash
python run.py
```
or
```bash
python3 run.py
```

**Option B: Using platform-specific scripts**

**On macOS/Linux:**
```bash
chmod +x run.sh
./run.sh
```

**On Windows:**
Double-click `run.bat` or run:
```bash
run.bat
```

**Option C: Manual start**
```bash
python app.py
```
or
```bash
python3 app.py
```

You should see:
```
Starting Connect Four AI server...
API endpoints:
  POST /api/move - Get AI move
  GET /api/metrics - Get game metrics
  POST /api/metrics/reset - Reset metrics
  POST /api/game/end - Record game end
 * Running on http://127.0.0.1:5001
```

### Step 3: Open the Game

1. Open your web browser (Chrome, Firefox, Safari, or Edge)
2. Navigate to: **http://localhost:5001**
3. The game will load automatically!

**That's it!** The server serves both the game interface and the API, so everything works seamlessly.

## How to Play

1. **Select Game Mode:**
   - **Human vs Human**: Play with a friend on the same computer
   - **Human vs AI**: Challenge the AI opponent

2. **Configure AI Settings** (if playing against AI):
   - **Algorithm**: Choose the AI algorithm
   - **Difficulty**: Select search depth (higher = harder)

3. **Make Your Move:**
   - Click on any column to drop your piece
   - Red pieces are Player 1, Yellow pieces are Player 2/AI

4. **View Statistics:**
   - Click "View Metrics" to see game statistics
   - Click "Reset Metrics" to clear statistics

5. **Start New Game:**
   - Click "New Game" to reset the board

## Project Structure

```
connect4_AI/
├── app.py                 # Flask API server
├── index.html             # Web interface
├── game.js                # Game logic and UI
├── requirements.txt       # Python dependencies
├── ai/                    # AI algorithms module
│   ├── __init__.py
│   ├── game_state.py     # Board state management
│   ├── heuristic.py      # Evaluation functions
│   ├── minimax.py         # Minimax algorithms
│   └── iterative_deepening.py  # Iterative deepening
├── run.sh                 # Unix/Mac startup script
├── run.bat                # Windows startup script
└── README.md              # This file
```

## Troubleshooting

### Port Already in Use
If you see an error about port 5001 being in use:
- Close any other instances of the server
- Or modify `app.py` line 203 to use a different port (e.g., `port=5002`)
- Update `game.js` line 22 to match the new port

### Import Errors
If you see import errors:
```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
# or on Windows:
# Delete all __pycache__ folders manually

# Reinstall dependencies
pip3 install --force-reinstall -r requirements.txt
```

### CORS Errors
Make sure you're accessing the game through `index.html` or `http://localhost:5001`. The server must be running for the API to work.

### Python Not Found
- **macOS/Linux**: Use `python3` instead of `python`
- **Windows**: Make sure Python is installed and added to PATH
- Install Python from [python.org](https://www.python.org/downloads/)

## API Endpoints

The server provides the following REST API endpoints:

- `POST /api/move` - Get AI's next move
- `GET /api/metrics` - Get game statistics
- `POST /api/metrics/reset` - Reset statistics
- `POST /api/game/end` - Record game end result

## Development

To modify the AI behavior, edit files in the `ai/` directory:
- `heuristic.py` - Adjust evaluation function
- `minimax.py` - Modify minimax algorithm
- `iterative_deepening.py` - Change iterative deepening parameters

## License

This project is open source and available for educational purposes.

## Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed correctly
3. Verify Python version is 3.7 or higher
4. Check that port 5001 is not in use by another application
