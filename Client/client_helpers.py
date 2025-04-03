def has_game_ended(board):
    h_counter = 0
    MAX_NUMBER_OF_X = 20
    # MAX_NUMBER_OF_X = 3
    for row in board:
        for place in row:
            if place == "H":
                h_counter += 1

    return h_counter == MAX_NUMBER_OF_X


def update_board(board, shot_x, shot_y, result):
    board[shot_y - 1][shot_x - 1] = result
    return board


def is_ship_hit(board, x_coord, y_coord):
    if board[y_coord - 1][x_coord - 1] == "X":
        return True
    return False