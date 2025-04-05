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

    

def get_shot(shot_board):
    try:
        print("Enter your shot")
        x_coord = input("Enter x coordinate: ")

        if x_coord == "end":
            return -1, -1, True

        y_coord = input("Enter y coordinate: ")

        if y_coord == "end":
            return -1, -1, True

        x_coord = int(x_coord)
        y_coord = int(y_coord)

        if 1 <= x_coord <= 10 and 1 <= y_coord <= 10:
            if shot_board[y_coord-1][x_coord-1] == "-":
                return x_coord, y_coord, False
            else:
                print("This place has already been shot! Enter new data.")
                return get_shot(shot_board)

        print("Enter a value in the range of 1-10!")
        return get_shot(shot_board)
    except ValueError:
        print("Enter a numerical value in the range of 1-10!")
        return get_shot(shot_board)