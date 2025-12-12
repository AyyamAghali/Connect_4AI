"""
Game state management for Connect Four
"""
COLS = 7
ROWS = 6

def create_empty_board():
    """Create an empty Connect Four board"""
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]

def copy_board(board):
    """Create a deep copy of the board"""
    return [row[:] for row in board]

def get_valid_moves(board):
    """Get list of valid column indices (columns that are not full)"""
    return [col for col in range(COLS) if board[0][col] == 0]

def get_drop_row(board, col):
    """Get the row where a piece would land in the given column"""
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == 0:
            return row
    return -1

def drop_piece(board, col, player):
    """Drop a piece in the specified column. Returns (row, new_board) or None if invalid"""
    if col < 0 or col >= COLS:
        return None
    
    row = get_drop_row(board, col)
    if row == -1:
        return None
    
    new_board = copy_board(board)
    new_board[row][col] = player
    return (row, new_board)

def check_win(board, row, col, player):
    """Check if placing a piece at (row, col) results in a win for the player"""
    if row < 0 or row >= ROWS or col < 0 or col >= COLS:
        return False
    
    # Check horizontal
    count = 1
    for c in range(col - 1, -1, -1):
        if board[row][c] == player:
            count += 1
        else:
            break
    for c in range(col + 1, COLS):
        if board[row][c] == player:
            count += 1
        else:
            break
    if count >= 4:
        return True
    
    # Check vertical
    count = 1
    for r in range(row - 1, -1, -1):
        if board[r][col] == player:
            count += 1
        else:
            break
    for r in range(row + 1, ROWS):
        if board[r][col] == player:
            count += 1
        else:
            break
    if count >= 4:
        return True
    
    # Check diagonal (top-left to bottom-right)
    count = 1
    r, c = row - 1, col - 1
    while r >= 0 and c >= 0 and board[r][c] == player:
        count += 1
        r -= 1
        c -= 1
    r, c = row + 1, col + 1
    while r < ROWS and c < COLS and board[r][c] == player:
        count += 1
        r += 1
        c += 1
    if count >= 4:
        return True
    
    # Check diagonal (top-right to bottom-left)
    count = 1
    r, c = row - 1, col + 1
    while r >= 0 and c < COLS and board[r][c] == player:
        count += 1
        r -= 1
        c += 1
    r, c = row + 1, col - 1
    while r < ROWS and c >= 0 and board[r][c] == player:
        count += 1
        r += 1
        c -= 1
    if count >= 4:
        return True
    
    return False

def is_board_full(board):
    """Check if the board is completely full"""
    return all(board[0][col] != 0 for col in range(COLS))

def is_terminal(board):
    """Check if the game is over (win or draw).
    Returns (is_terminal, winner) where winner is 1, 2, 0 (draw), or None (not terminal)
    """
    # Check for wins
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] != 0:
                if check_win(board, row, col, board[row][col]):
                    return True, board[row][col]  # Return True and winner
    # Check for draw
    if is_board_full(board):
        return True, 0  # Draw
    return False, None

