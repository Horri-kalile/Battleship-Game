import os
import signal
import threading
import time
import client_boardsets as boards
import client_make_board as myboard

class TimeoutError(Exception):
    pass

def timeout_input(prompt, timeout=30):
    """Input with timeout functionality"""
    result = [None]
    
    def get_input():
        try:
            result[0] = input(prompt)
        except:
            pass
    
    input_thread = threading.Thread(target=get_input)
    input_thread.daemon = True
    input_thread.start()
    input_thread.join(timeout)
    
    if input_thread.is_alive():
        raise TimeoutError("Input timeout")
    
    return result[0]

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
        print("Enter your shot (you have 30 seconds)")
        try:
            x_coord = timeout_input("Enter x coordinate: ", 30)
        except TimeoutError:
            print("Time's up! You took too long to enter coordinates.")
            return -1, -1, "timeout"

        if x_coord == "end":
            return -1, -1, True

        try:
            y_coord = timeout_input("Enter y coordinate: ", 30)
        except TimeoutError:
            print("Time's up! You took too long to enter coordinates.")
            return -1, -1, "timeout"

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
    while True:
        print("Create your board, you can use predefined layouts or create your own:")
        print("Write 1 - if you want to create your own")
        print("Write 2 - if you want to choose predefined set number 1")
        print("Write 3 - if you want to choose predefined set number 2")
        option = input("Your choice: ")
        try:
            option = int(option)
            if option == 1:
                board = myboard.make_user_board()
                return board
            elif option == 2:
                board = boards.board1
                return board
            elif option == 3:
                board = boards.board2
                return board
            else:
                print("Invalid choice! Please enter 1, 2, or 3.")
                continue
        except ValueError:
            print("Invalid input! Please enter a number from 1 to 3.")
            continue


def generate_shots_board(rows, cols):
    board = [['-' for _ in range(cols)] for _ in range(rows)]
    return board

def print_board(board, shot_board):
    separator = "=" * 80
    print(separator, "\n")

    print("Your board" + " " * 20 + "Your shots")
    
    # Column headers, with one space in top-left corner
    header_left = "   " + " ".join(str(i) for i in range(1, 11))
    header_right = "  " + " ".join(str(i) for i in range(1, 11))
    print(f"{header_left}     {header_right}")

    for i in range(10):
        left = f"{i+1:>2} " + " ".join(board[i])
        right = f"{i+1:>2} " + " ".join(shot_board[i])
        print(f"{left}     {right}")

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
