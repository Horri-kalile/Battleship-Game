import os
import client_boardsets as boards
import client_make_board as myboard

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
    
def choose_board():
    print("Create your board, you can use predefined layouts or create your own:")
    print("Write 1 - if you want to create your own")
    print("Write 2 - if you want to choose predefined set number 1")
    print("Write 3 - if you want to choose predefined set number 2")
    option = input("Your choice: ")
    try:
        option = int(option)
        if option == 1:
            board = myboard.make_user_board()
        elif option == 2:
            board = boards.board1
        else:
            board = boards.board2

        return board
    except ValueError:
        print("Enter a number from 1 to 3")
        choose_board()


def generate_shots_board(rows, cols):
    board = [['-' for _ in range(cols)] for _ in range(rows)]
    return board

def print_board(board, shot_board):
    separator = "=" * 80
    print(separator, "\n")
    print("Your board", "\t" * 4, "Your shots")
    print("  1 2 3 4 5 6 7 8 9 10 			       1 2 3 4 5 6 7 8 9 10")
    for rowB, rowS in zip(board, shot_board):
        print(board.index(rowB) + 1, " ".join(rowB), "\t" * 3, board.index(rowB) + 1, " ".join(rowS))
    print(separator, "\n")


def show_rules():
    print("LET'S START THE GAME")
    print("RULES")
    print("\tWrite 'end' to finish the game")
    print("Your board")
    print("\tThe 'X' sign represents a part of your ship")
    print("\tThe 'H' sign indicates that a part of the ship has been hit")
    print("\tThe 'M' sign indicates that the shot hit the water")
    print("Your shots board")
    print("\tThe 'H' sign indicates a successful shot")
    print("\tThe 'M' sign indicates an unsuccessful shot")
    input("Press ENTER to continue: ")
    clear_console()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')
