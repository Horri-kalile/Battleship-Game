import ast
import socket

from client_helpers import *

global my_room_id
my_room_id = ""


def main():
    global my_room_id
    IP = "127.0.0.1"
    PORT = 5001
    BUF_SIZE = 1024

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (IP, PORT)

    try:
        client_socket.connect(server_address)
        client_address = client_socket.getsockname()

        client_socket.sendto("connect".encode('utf-8'), server_address)

        while True:
            response, _ = client_socket.recvfrom(BUF_SIZE)
            response = response.decode('utf-8')

            if response == "connect":
                print("Connected to server, waiting for the opponent...")
                print("My address: ", client_address)
            elif response.startswith("start"):
                my_room_id = response.split(";")[1]
                action = response.split(';')[2]

                print("Room id:", my_room_id)
                print("GAME BEGINS")

                shots_board = generate_shots_board(10, 10)
                show_rules()
                board = choose_board()
                clear_console()
                print_board(board, shots_board)

                if action == "wait":
                    print("Enemy's turn...")
                elif action == "shoot":
                    print("Your turn")
                    x_coord, y_coord, end_game = get_shot(shots_board)
                    if end_game:
                        print("END, You give up")
                        client_socket.sendto("end_you_won".encode('utf-8'), server_address)
                        play_again()

                    message = "shoots " + "(" + str(x_coord) + "," + str(y_coord) + ");" + str(
                        client_address) + ";" + my_room_id
                    client_socket.sendto(message.encode('utf-8'), server_address)
                else:
                    print("error occurred during message fetching")

            elif response == "wait":
                print("Enemy's turn...")

            elif response == "shoot":
                print("Your turn")
                if not has_game_ended(shots_board):
                    x_coord, y_coord, end_game = get_shot(shots_board)

                    if end_game:
                        print("END, YOU GIVE UP")
                        client_socket.sendto("end_you_won".encode('utf-8'), server_address)
                        play_again()

                    message = "shoots " + "(" + str(x_coord) + "," + str(y_coord) + ");" + str(client_address) + ";" + my_room_id
                    client_socket.sendto(message.encode('utf-8'), server_address)

            elif response.startswith("check"):
                try:
                    coords = response.split(';')[0].removeprefix("check").replace('[', '').replace(']', '').replace("'", "").split(",")
                    x_coord = coords[0]
                    y_coords = coords[1]

                    print("=" * 80)


                    if is_ship_hit(board, int(x_coord), int(y_coords)):
                        clear_console()
                        is_successful = True
                        print("ENEMY HIT YOUR SHIP")
                        update_board(board, int(x_coord), int(y_coords), "H")
                        print_board(board, shots_board)
                    else:
                        clear_console()
                        is_successful = False
                        print("ENEMY MISSED")
                        update_board(board, int(x_coord), int(y_coords), "M")
                        print_board(board, shots_board)

                    print("Enemy shoots on:", x_coord, ',', y_coords)
                    msg = "result;" + str(is_successful) + ';from;' + str(client_address) + ";coord;" + str(coords)
                    client_socket.sendto(msg.encode('utf-8'), server_address)

                    if has_game_ended(board):
                        print("GAME ENDED, DEFEAT")
                        client_socket.sendto("end_you_won".encode('utf-8'), server_address)
                        play_again()
                except UnboundLocalError:
                    continue
            elif response.lower().startswith("update"):
                array = response.split(";")
                coords = array[1]
                result = array[2]

                coords_array = ast.literal_eval(coords)
                clear_console()
                print("=" * 80)


                if result == "True":
                    print("Shoot on", coords_array, "is a HIT!")
                    sign = "H"
                else:
                    print("Shoot on", coords_array, "is a MISS!")
                    sign = "M"

                update_board(shots_board, int(coords_array[0]), int(coords_array[1]), sign)
                print_board(board, shots_board)
            