// Game constants
const COLS = 7;
const ROWS = 6;
const CELL_SIZE = 100;
const RADIUS = 40;
const COLORS = {
    EMPTY: '#1e3a8a',
    RED: '#ff4444',
    YELLOW: '#ffd700'
};

// Game state
let board = [];
let currentPlayer = 1; // 1 = Red, 2 = Yellow
let gameOver = false;
let winner = null;
let isProcessingMove = false; // Prevent multiple simultaneous moves
let gameMode = 'human'; // 'human', 'ai', or 'ai_vs_ai'
let aiPlayer = 2; // AI plays as player 2 (Yellow) in human vs AI
let aiDepth = 5; // Search depth for minimax
let aiAlgorithm = 'minimax_ab'; // 'minimax', 'minimax_ab', 'iterative', 'random'
let ai1Depth = 5;
let ai2Depth = 5;
let ai1Algorithm = 'minimax_ab'; // Only 'minimax', 'minimax_ab', 'iterative' for AI vs AI
let ai2Algorithm = 'minimax_ab'; // Only 'minimax', 'minimax_ab', 'iterative' for AI vs AI
let randomizeFirstPlayer = true;
const AI_MOVE_DELAY_MS = 400; // small delay so UI updates between AI turns
const API_URL = 'http://localhost:5001/api';

function isAITurn() {
    if (gameMode === 'ai') {
        return currentPlayer === aiPlayer;
    }
    if (gameMode === 'ai_vs_ai') {
        return true;
    }
    return false;
}

function scheduleAIMove() {
    if (!gameOver && isAITurn() && !isProcessingMove) {
        setTimeout(() => makeAIMove(), AI_MOVE_DELAY_MS);
    }
}

function currentAISettings() {
    if (gameMode === 'ai_vs_ai') {
        // Ensure random algorithm is not used in AI vs AI mode (fallback to minimax_ab)
        let alg1 = ai1Algorithm === 'random' ? 'minimax_ab' : ai1Algorithm;
        let alg2 = ai2Algorithm === 'random' ? 'minimax_ab' : ai2Algorithm;
        
        if (currentPlayer === 1) {
            return { algorithm: alg1, depth: ai1Depth };
        }
        return { algorithm: alg2, depth: ai2Depth };
    }
    return { algorithm: aiAlgorithm, depth: aiDepth };
}

// Canvas setup
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Initialize board
function initBoard() {
    board = [];
    for (let row = 0; row < ROWS; row++) {
        board[row] = [];
        for (let col = 0; col < COLS; col++) {
            board[row][col] = 0; // 0 = empty, 1 = red, 2 = yellow
        }
    }
    // Randomize starting player for AI vs AI if enabled
    if (gameMode === 'ai_vs_ai' && randomizeFirstPlayer) {
        currentPlayer = Math.random() < 0.5 ? 1 : 2;
    } else {
        currentPlayer = 1;
    }
    gameOver = false;
    winner = null;
    isProcessingMove = false;
    updateUI();
    drawBoard();
    
    scheduleAIMove();
}

// Draw the game board
function drawBoard() {
    // Clear canvas
    ctx.fillStyle = COLORS.EMPTY;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw board background with grid
    ctx.strokeStyle = '#0f1f4a';
    ctx.lineWidth = 2;
    for (let row = 0; row < ROWS; row++) {
        for (let col = 0; col < COLS; col++) {
            const x = col * CELL_SIZE + CELL_SIZE / 2;
            const y = row * CELL_SIZE + CELL_SIZE / 2;
            
            // Draw circle for each cell
            ctx.beginPath();
            ctx.arc(x, y, RADIUS, 0, Math.PI * 2);
            ctx.fillStyle = COLORS.EMPTY;
            ctx.fill();
            ctx.stroke();
        }
    }

    // Draw pieces
    for (let row = 0; row < ROWS; row++) {
        for (let col = 0; col < COLS; col++) {
            if (board[row][col] !== 0) {
                const x = col * CELL_SIZE + CELL_SIZE / 2;
                const y = row * CELL_SIZE + CELL_SIZE / 2;
                
                ctx.beginPath();
                ctx.arc(x, y, RADIUS - 2, 0, Math.PI * 2);
                ctx.fillStyle = board[row][col] === 1 ? COLORS.RED : COLORS.YELLOW;
                ctx.fill();
                
                // Add shine effect
                ctx.beginPath();
                ctx.arc(x - 15, y - 15, RADIUS / 3, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                ctx.fill();
            }
        }
    }
}

// Get the column from mouse click
function getColumnFromClick(event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const col = Math.floor(x / CELL_SIZE);
    // Ensure column is within valid range
    if (col < 0 || col >= COLS) return -1;
    return col;
}

// Drop a piece in the specified column
function dropPiece(col) {
    if (gameOver || col < 0 || col >= COLS || isProcessingMove) return false;
    
    isProcessingMove = true;

    // Find the lowest empty row in the column (from bottom to top)
    // In Connect 4, pieces fall to the bottom, so we check from bottom row (ROWS-1) upward
    for (let row = ROWS - 1; row >= 0; row--) {
        if (board[row][col] === 0) {
            // Place the piece in this specific row and column
            board[row][col] = currentPlayer;
            
            // Redraw immediately to show the piece
            drawBoard();
            
            // Check for win
            if (checkWin(row, col)) {
                gameOver = true;
                winner = currentPlayer;
                updateUI();
                recordGameEnd();
                isProcessingMove = false;
                return true;
            }
            
            // Check for draw
            if (isBoardFull()) {
                gameOver = true;
                winner = 0; // 0 = draw
                updateUI();
                recordGameEnd();
                isProcessingMove = false;
                return true;
            }
            
            // Switch player
            currentPlayer = currentPlayer === 1 ? 2 : 1;
            updateUI();
            isProcessingMove = false;
            
            // Trigger AI move(s) when appropriate (covers human vs AI and AI vs AI)
            scheduleAIMove();
            
            return true;
        }
    }
    
    isProcessingMove = false;
    return false; // Column is full
}

// Check if the board is full
function isBoardFull() {
    for (let col = 0; col < COLS; col++) {
        if (board[0][col] === 0) {
            return false;
        }
    }
    return true;
}

// Check for win condition
function checkWin(row, col) {
    const player = board[row][col];
    
    // Check horizontal
    let count = 1;
    // Check left
    for (let c = col - 1; c >= 0 && board[row][c] === player; c--) count++;
    // Check right
    for (let c = col + 1; c < COLS && board[row][c] === player; c++) count++;
    if (count >= 4) return true;
    
    // Check vertical
    count = 1;
    // Check up
    for (let r = row - 1; r >= 0 && board[r][col] === player; r--) count++;
    // Check down
    for (let r = row + 1; r < ROWS && board[r][col] === player; r++) count++;
    if (count >= 4) return true;
    
    // Check diagonal (top-left to bottom-right)
    count = 1;
    // Check top-left
    for (let r = row - 1, c = col - 1; r >= 0 && c >= 0 && board[r][c] === player; r--, c--) count++;
    // Check bottom-right
    for (let r = row + 1, c = col + 1; r < ROWS && c < COLS && board[r][c] === player; r++, c++) count++;
    if (count >= 4) return true;
    
    // Check diagonal (top-right to bottom-left)
    count = 1;
    // Check top-right
    for (let r = row - 1, c = col + 1; r >= 0 && c < COLS && board[r][c] === player; r--, c++) count++;
    // Check bottom-left
    for (let r = row + 1, c = col - 1; r < ROWS && c >= 0 && board[r][c] === player; r++, c--) count++;
    if (count >= 4) return true;
    
    return false;
}

// Helper functions for UI feedback
function showLoading() {
    document.getElementById('loadingOverlay').classList.add('show');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('show');
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.classList.add('show');
    setTimeout(() => {
        errorDiv.classList.remove('show');
    }, 5000);
}

function showSuccess(message) {
    const successDiv = document.getElementById('successMessage');
    successDiv.textContent = message;
    successDiv.classList.add('show');
    setTimeout(() => {
        successDiv.classList.remove('show');
    }, 3000);
}

function addThinkingIndicator(element) {
    if (!element.querySelector('.thinking-indicator')) {
        const indicator = document.createElement('span');
        indicator.className = 'thinking-indicator';
        indicator.innerHTML = '<span></span><span></span><span></span>';
        element.appendChild(indicator);
    }
}

function removeThinkingIndicator(element) {
    const indicator = element.querySelector('.thinking-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Update UI elements
function updateUI() {
    const currentPlayerDiv = document.getElementById('currentPlayer');
    const winnerMessageDiv = document.getElementById('winnerMessage');
    
    if (gameOver) {
        currentPlayerDiv.style.display = 'none';
        winnerMessageDiv.style.display = 'block';
        removeThinkingIndicator(currentPlayerDiv);
        
        if (winner === 0) {
            winnerMessageDiv.textContent = "🤝 It's a Draw!";
            winnerMessageDiv.className = 'winner-message winner-draw';
        } else if (winner === 1) {
            winnerMessageDiv.textContent = '🎉 Player 1 (Red) Wins! 🎉';
            winnerMessageDiv.className = 'winner-message winner-red';
        } else {
            winnerMessageDiv.textContent = '🎉 Player 2 (Yellow) Wins! 🎉';
            winnerMessageDiv.className = 'winner-message winner-yellow';
        }
    } else {
        currentPlayerDiv.style.display = 'inline-block';
        winnerMessageDiv.style.display = 'none';
        
        const isAIThinking = isAITurn() && isProcessingMove;
        if (currentPlayer === 1) {
            if (isAIThinking && gameMode !== 'human') {
                currentPlayerDiv.textContent = "AI 1 is thinking (Red)";
                currentPlayerDiv.className = 'current-player player-red pulsing';
                addThinkingIndicator(currentPlayerDiv);
            } else {
                currentPlayerDiv.textContent = "Player 1's Turn (Red)";
                currentPlayerDiv.className = 'current-player player-red';
                removeThinkingIndicator(currentPlayerDiv);
            }
        } else {
            const yellowLabel = gameMode === 'ai' && currentPlayer === aiPlayer
                ? "AI's Turn (Yellow)"
                : (gameMode === 'ai_vs_ai' ? "AI 2's Turn (Yellow)" : "Player 2's Turn (Yellow)");
            
            if (isAIThinking) {
                currentPlayerDiv.textContent = yellowLabel;
                currentPlayerDiv.className = 'current-player player-yellow pulsing';
                addThinkingIndicator(currentPlayerDiv);
            } else {
                currentPlayerDiv.textContent = yellowLabel;
                currentPlayerDiv.className = 'current-player player-yellow';
                removeThinkingIndicator(currentPlayerDiv);
            }
        }
    }
}

// Handle canvas click
canvas.addEventListener('click', (event) => {
    if (!gameOver && !isProcessingMove) {
        // Don't allow clicks if it's AI's turn
        if (isAITurn()) {
            showError('Please wait for the AI to make its move.');
            return;
        }
        const col = getColumnFromClick(event);
        if (col >= 0) {
            // Check if column is full
            let hasSpace = false;
            for (let row = 0; row < ROWS; row++) {
                if (board[row][col] === 0) {
                    hasSpace = true;
                    break;
                }
            }
            if (!hasSpace) {
                showError('This column is full! Choose another column.');
                return;
            }
            dropPiece(col);
        }
    } else if (gameOver) {
        showError('Game is over! Click "New Game" to start a new game.');
    }
});

// Add hover effect to show which column will be selected
let hoverColumn = -1;
canvas.addEventListener('mousemove', (event) => {
    if (!gameOver) {
        const col = getColumnFromClick(event);
        if (col !== hoverColumn) {
            hoverColumn = col;
            drawBoard();
            // Draw hover indicator
            if (hoverColumn >= 0 && hoverColumn < COLS) {
                // Check if column has space
                let hasSpace = false;
                for (let row = 0; row < ROWS; row++) {
                    if (board[row][hoverColumn] === 0) {
                        hasSpace = true;
                        break;
                    }
                }
                
                if (hasSpace) {
                    const x = hoverColumn * CELL_SIZE + CELL_SIZE / 2;
                    const y = 50; // Top of the board
                    ctx.beginPath();
                    ctx.arc(x, y, RADIUS - 2, 0, Math.PI * 2);
                    ctx.fillStyle = currentPlayer === 1 ? COLORS.RED : COLORS.YELLOW;
                    ctx.globalAlpha = 0.5;
                    ctx.fill();
                    ctx.globalAlpha = 1.0;
                }
            }
        }
    }
});

canvas.addEventListener('mouseleave', () => {
    hoverColumn = -1;
    if (!gameOver) {
        drawBoard();
    }
});

// ==================== AI IMPLEMENTATION (Python Backend) ====================

// Make AI move by calling Python backend
async function makeAIMove() {
    if (gameOver || isProcessingMove || !isAITurn()) {
        console.log('makeAIMove: Skipping - gameOver:', gameOver, 'isProcessingMove:', isProcessingMove, 'currentPlayer:', currentPlayer, 'aiPlayer:', aiPlayer, 'gameMode:', gameMode);
        return;
    }
    
    console.log('makeAIMove: Starting AI move request...');
    isProcessingMove = true;
    updateUI(); // Update to show "Thinking..."
    drawBoard(); // Redraw to show updated UI
    
    try {
        // Add timeout to prevent hanging
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
        
        const aiConfig = currentAISettings();
        
        // Ensure depth is a number, not a string
        const depthValue = typeof aiConfig.depth === 'string' ? parseInt(aiConfig.depth, 10) : aiConfig.depth;
        
        const requestData = {
            board: board,
            player: currentPlayer,
            algorithm: String(aiConfig.algorithm).trim(), // Ensure it's a clean string
            depth: depthValue,
            time_limit: 5.0
        };
        
        console.log('makeAIMove: Sending request to', `${API_URL}/move`, requestData);
        console.log('makeAIMove: Algorithm value:', requestData.algorithm, 'Type:', typeof requestData.algorithm);
        
        const response = await fetch(`${API_URL}/move`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        console.log('makeAIMove: Response status:', response.status, response.statusText);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('makeAIMove: Response error:', errorText);
            throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('makeAIMove: Received data:', data);
        
        // Display metrics in console
        console.log(`✅ AI Move: Column ${data.move}`);
        console.log(`   Nodes Expanded: ${data.nodes_expanded}`);
        console.log(`   Pruned Nodes: ${data.pruned_nodes}`);
        console.log(`   Decision Time: ${data.decision_time.toFixed(3)}s`);
        console.log(`   Search Depth: ${data.depth}`);
        
        if (data.move !== null && data.move >= 0) {
            console.log('makeAIMove: Dropping piece in column', data.move);
            // Reset isProcessingMove so dropPiece can execute
            isProcessingMove = false;
            const success = dropPiece(data.move);
            if (!success) {
                console.error('makeAIMove: dropPiece returned false - column may be full or invalid');
                showError('AI made an invalid move. Please start a new game.');
                isProcessingMove = false;
                updateUI();
            }
        } else {
            console.error('makeAIMove: AI returned invalid move:', data);
            showError('AI could not determine a valid move. Please try again.');
            isProcessingMove = false;
            updateUI();
        }
    } catch (error) {
        console.error('❌ Error getting AI move:', error);
        if (error.name === 'AbortError') {
            showError('AI move request timed out. Try reducing the search depth.');
        } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            showError('Failed to connect to AI server. Make sure the Python server is running on port 5001.');
        } else {
            showError('Error getting AI move: ' + error.message);
        }
        isProcessingMove = false;
        updateUI(); // Reset UI state
        drawBoard();
    }
}

// Record game end result
async function recordGameEnd() {
    if ((gameMode === 'ai' || gameMode === 'ai_vs_ai') && winner !== null) {
        try {
            await fetch(`${API_URL}/game/end`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    winner: winner,
                    game_mode: gameMode  // Send game mode so server knows how to track stats
                })
            });
        } catch (error) {
            console.error('Error recording game end:', error);
        }
    }
}

// Get and display metrics
async function updateMetrics() {
    try {
        showLoading();
        const response = await fetch(`${API_URL}/metrics`);
        if (response.ok) {
            const data = await response.json();
            console.log('Game Metrics:', data);
            
            // Display Human vs AI metrics
            document.getElementById('gamesPlayed').textContent = data.games_played || 0;
            document.getElementById('aiWins').textContent = data.ai_wins || 0;
            document.getElementById('humanWins').textContent = data.human_wins || 0;
            document.getElementById('draws').textContent = data.draws || 0;
            document.getElementById('winRate').textContent = 
                ((data.win_rate || 0) * 100).toFixed(1) + '%';
            
            // Display AI vs AI metrics
            document.getElementById('aiVsAiGamesPlayed').textContent = data.ai_vs_ai_games_played || 0;
            document.getElementById('aiVsAiPlayer1Wins').textContent = data.ai_vs_ai_player1_wins || 0;
            document.getElementById('aiVsAiPlayer2Wins').textContent = data.ai_vs_ai_player2_wins || 0;
            document.getElementById('aiVsAiDraws').textContent = data.ai_vs_ai_draws || 0;
            document.getElementById('aiVsAiPlayer1WinRate').textContent = 
                ((data.ai_vs_ai_player1_win_rate || 0) * 100).toFixed(1) + '%';
            document.getElementById('aiVsAiPlayer2WinRate').textContent = 
                ((data.ai_vs_ai_player2_win_rate || 0) * 100).toFixed(1) + '%';
            
            // Display performance metrics
            document.getElementById('avgNodes').textContent = 
                Math.round(data.average_nodes_expanded) || 0;
            document.getElementById('avgTime').textContent = 
                (data.average_decision_time || 0).toFixed(3) + 's';
            document.getElementById('avgPruned').textContent = 
                Math.round(data.average_pruned_nodes) || 0;
            document.getElementById('totalMoves').textContent = data.total_moves || 0;
            
            // Show metrics panel
            const metricsPanel = document.getElementById('metricsPanel');
            metricsPanel.classList.add('show');
            
            hideLoading();
            showSuccess('Metrics loaded successfully!');
        } else {
            throw new Error('Failed to fetch metrics');
        }
    } catch (error) {
        console.error('Error fetching metrics:', error);
        hideLoading();
        showError('Failed to fetch metrics. Make sure the Python server is running.');
    }
}

// ==================== EVENT HANDLERS ====================

// Handle reset button
document.getElementById('resetButton').addEventListener('click', () => {
    initBoard();
});

// Handle game mode change
document.getElementById('gameMode').addEventListener('change', (e) => {
    gameMode = e.target.value;
    const aiVsAiBlock = document.getElementById('aiVsAiConfig');
    const aiSettingsGroup = document.getElementById('aiSettingsGroup');
    const aiDepthGroup = document.getElementById('aiDepthGroup');
    
    if (gameMode === 'ai_vs_ai') {
        aiVsAiBlock.classList.add('show');
        aiSettingsGroup.style.display = 'none';
        aiDepthGroup.style.display = 'none';
    } else {
        aiVsAiBlock.classList.remove('show');
        aiSettingsGroup.style.display = 'block';
        aiDepthGroup.style.display = 'block';
    }
    
    initBoard();
});

// Handle AI depth change
document.getElementById('aiDepth').addEventListener('change', (e) => {
    aiDepth = parseInt(e.target.value);
});

// Handle AI algorithm change
document.getElementById('aiAlgorithm').addEventListener('change', (e) => {
    aiAlgorithm = e.target.value;
});

// AI vs AI controls
document.getElementById('ai1Algorithm').addEventListener('change', (e) => {
    ai1Algorithm = e.target.value;
});
document.getElementById('ai2Algorithm').addEventListener('change', (e) => {
    ai2Algorithm = e.target.value;
});
document.getElementById('ai1Depth').addEventListener('change', (e) => {
    ai1Depth = parseInt(e.target.value);
});
document.getElementById('ai2Depth').addEventListener('change', (e) => {
    ai2Depth = parseInt(e.target.value);
});
document.getElementById('randomStartCheckbox').addEventListener('change', (e) => {
    randomizeFirstPlayer = e.target.checked;
});

// Handle metrics button
document.getElementById('metricsButton').addEventListener('click', () => {
    updateMetrics();
});

// Handle reset metrics button
document.getElementById('resetMetricsButton').addEventListener('click', async () => {
    if (!confirm('Are you sure you want to reset all statistics? This cannot be undone.')) {
        return;
    }
    
    try {
        showLoading();
        await fetch(`${API_URL}/metrics/reset`, { method: 'POST' });
        console.log('Metrics reset');
        
        // Update displayed metrics (reset all)
        document.getElementById('gamesPlayed').textContent = '0';
        document.getElementById('aiWins').textContent = '0';
        document.getElementById('humanWins').textContent = '0';
        document.getElementById('draws').textContent = '0';
        document.getElementById('winRate').textContent = '0%';
        document.getElementById('aiVsAiGamesPlayed').textContent = '0';
        document.getElementById('aiVsAiPlayer1Wins').textContent = '0';
        document.getElementById('aiVsAiPlayer2Wins').textContent = '0';
        document.getElementById('aiVsAiDraws').textContent = '0';
        document.getElementById('aiVsAiPlayer1WinRate').textContent = '0%';
        document.getElementById('aiVsAiPlayer2WinRate').textContent = '0%';
        document.getElementById('avgNodes').textContent = '0';
        document.getElementById('avgTime').textContent = '0.000s';
        document.getElementById('avgPruned').textContent = '0';
        document.getElementById('totalMoves').textContent = '0';
        
        hideLoading();
        showSuccess('Statistics reset successfully!');
    } catch (error) {
        console.error('Error resetting metrics:', error);
        hideLoading();
        showError('Failed to reset metrics. Make sure the Python server is running.');
    }
});

// Initialize UI on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeGame);
} else {
    initializeGame();
}

function initializeGame() {
    // Set initial visibility of AI settings
    const gameModeSelect = document.getElementById('gameMode');
    if (gameModeSelect) {
        const currentMode = gameModeSelect.value;
        if (currentMode === 'ai_vs_ai') {
            document.getElementById('aiVsAiConfig').classList.add('show');
            document.getElementById('aiSettingsGroup').style.display = 'none';
            document.getElementById('aiDepthGroup').style.display = 'none';
        }
    }
    
    // Initialize game
    initBoard();
    
    // Show welcome message
    setTimeout(() => {
        if (gameMode === 'human') {
            showSuccess('Welcome! Click on a column to drop your piece.');
        }
    }, 500);
}

