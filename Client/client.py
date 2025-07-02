import ast
import platform
import socket
import threading
import time

from client_helpers import *

global my_room_id, client_socket, server_address, heartbeat_running, game_ready, is_my_turn
my_room_id = ""
heartbeat_running = False
game_ready = False
is_my_turn = False


def main():
    global my_room_id, client_socket, server_address, heartbeat_running, game_ready, is_my_turn
    IP = "127.0.0.1"
    PORT = 5001
    BUF_SIZE = 1024

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (IP, PORT)
    client_socket.settimeout(60)  # Longer timeout since input timeout is handled separately

    try:
        if platform.system() == "Windows":
            client_socket.connect(server_address)
        client_address = client_socket.getsockname()

        client_socket.sendto("connect".encode('utf-8'), server_address)

        while True:
            try:
                response, _ = client_socket.recvfrom(BUF_SIZE)
            except socket.timeout:
                # Socket timeout only happens for real connection issues now
                print("Connection lost. Server might be unavailable. Exiting...")
                break
            response = response.decode('utf-8')

            if response == "connect":
                print("Connected to server, waiting for the opponent...")
                print("My address: ", client_address)
                
            elif response.startswith("prepare_game"):
                my_room_id = response.split(";")[1]
                print("Room id:", my_room_id)
                print("Opponent found! Prepare your board...")
                
                # Start heartbeat once connected to a room
                start_heartbeat()
                
                # Let player set up their board
                shots_board = generate_shots_board(10, 10)
                show_rules()
                board = choose_board()
                clear_console()
                print_board(board, shots_board)
                
                print("Board setup complete! Waiting for opponent to be ready...")
                
                # Send ready signal to server
                ready_message = f"ready;{my_room_id}"
                client_socket.sendto(ready_message.encode('utf-8'), server_address)
                game_ready = True
                
            elif response.startswith("start"):
                my_room_id = response.split(";")[1]
                action = response.split(';')[2]

                print("Both players ready! GAME BEGINS")

                if action == "wait":
                    print("Enemy's turn...")
                    is_my_turn = False
                elif action == "shoot":
                    print("Your turn")
                    is_my_turn = True
                    x_coord, y_coord, end_game = get_shot(shots_board)
                    if end_game == "timeout":
                        print("You took too long to make your move. You lose by timeout!")
                        client_socket.sendto("timeout_loss".encode('utf-8'), server_address)
                        stop_heartbeat()
                        play_again()
                        return
                    elif end_game:
                        print("END, You give up")
                        client_socket.sendto("end_you_won".encode('utf-8'), server_address)
                        stop_heartbeat()
                        play_again()
                        return

                    message = "shoots " + "(" + str(x_coord) + "," + str(y_coord) + ");" + str(
                        client_address) + ";" + my_room_id
                    client_socket.sendto(message.encode('utf-8'), server_address)
                    is_my_turn = False  # After shooting, it's not my turn anymore
                else:
                    print("error occurred during message fetching")

            elif response.startswith("opponent_disconnected"):
                stop_heartbeat()
                disconnect_type = response.split(";")[1]
                
                if disconnect_type == "waiting_room":
                    print("Your opponent has disconnected! You will be returned to the waiting room...")
                    time.sleep(2)
                    # Restart the connection process
                    main()
                    return
                else:  # game_in_progress
                    print("Your opponent has disconnected during the game! You win by default.")
                    play_again()
                    return

            elif response == "opponent_timeout_win":
                stop_heartbeat()
                print("Your opponent has lost by time. You win!")
                play_again()
                return

            elif response == "wait":
                print("Enemy's turn...")
                is_my_turn = False

            elif response == "shoot":
                print("Your turn")
                is_my_turn = True
                if not has_game_ended(shots_board):
                    x_coord, y_coord, end_game = get_shot(shots_board)

                    if end_game == "timeout":
                        print("You took too long to make your move. You lose by timeout!")
                        client_socket.sendto("timeout_loss".encode('utf-8'), server_address)
                        stop_heartbeat()
                        play_again()
                        return
                    elif end_game:
                        print("END, YOU GIVE UP")
                        client_socket.sendto("end_you_won".encode('utf-8'), server_address)
                        stop_heartbeat()
                        play_again()
                        return

                    message = "shoots " + "(" + str(x_coord) + "," + str(y_coord) + ");" + str(client_address) + ";" + my_room_id
                    client_socket.sendto(message.encode('utf-8'), server_address)
                    is_my_turn = False  # After shooting, it's not my turn anymore

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
                        stop_heartbeat()
                        play_again()
                except (UnboundLocalError, IndexError, ValueError):
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
            elif response.lower() == "winner":
                stop_heartbeat()
                print("YOU WON!!!")
                play_again()
            elif response == "end":
                stop_heartbeat()
                play_again()
            else:
                print("Waiting...")
    except socket.error as e:
        print(f"Socket error: {e}")
    finally:
        stop_heartbeat()
        client_socket.close()

def start_heartbeat():
    """Start sending heartbeat messages to server"""
    global heartbeat_running
    heartbeat_running = True
    heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
    heartbeat_thread.start()

def stop_heartbeat():
    """Stop sending heartbeat messages"""
    global heartbeat_running
    heartbeat_running = False

def send_heartbeat():
    """Send periodic heartbeat messages to server"""
    global heartbeat_running, client_socket, server_address, my_room_id
    while heartbeat_running:
        try:
            time.sleep(10)  # Send heartbeat every 10 seconds
            if heartbeat_running and my_room_id:
                heartbeat_msg = f"heartbeat;{my_room_id}"
                client_socket.sendto(heartbeat_msg.encode('utf-8'), server_address)
        except socket.error:
            break
        except Exception:
            break

def play_again():
    global heartbeat_running, game_ready, my_room_id, is_my_turn
    
    # Clean up current game state
    stop_heartbeat()
    game_ready = False
    my_room_id = ""
    is_my_turn = False
    
    print("Do you want to play again?")
    res = input("Enter Y or N: ")

    if res.lower() in ['y', 'yes', 'continue']:
        main()
    elif res.lower() in ['n','no', 'dont', 'exit', 'e', 'q']:
        exit()
    else:
        print("Invalid input!")
        play_again()


if __name__ == "__main__":
    main()
