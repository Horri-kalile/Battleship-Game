def print_board(board):
    print("Your board")
    print("  0 1 2 3 4 5 6 7 8 9")
    for i, rowB in enumerate(board):
        print(i, " ".join(rowB))

def is_valid_position(board, x, y, ship_size, orientation):
    if orientation.lower() == "h":
        if y + ship_size > 10:
            return False
        for i in range(ship_size):
            if board[x][y + i] != "-" or (x > 0 and board[x - 1][y + i] != "-") or (
                    x < 9 and board[x + 1][y + i] != "-"):
                return False
    elif orientation.lower() == "v":
        if x + ship_size > 10:
            return False
        for i in range(ship_size):
            if board[x + i][y] != "-" or (y > 0 and board[x + i][y - 1] != "-") or (
                    y < 9 and board[x + i][y + 1] != "-"):
                return False
    return True

def convert_to_x(board):
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j].isdigit():
                board[i][j] = "X"
    return board