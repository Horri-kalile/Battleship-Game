import socket
import random
from GameRoom import GameRoom

global rooms
rooms = []  # List to store all active game rooms

def main():
    global rooms
    IP = "127.0.0.1"  # Server IP address
    PORT = 5001       # Server port
    BUF_SIZE = 1024   # Buffer size for receiving data

    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP, PORT))

    print("Server UDP is active")
    print(f"Waiting for players...")

    while True:
        try:
            # Receive data from clients
            data, address = server_socket.recvfrom(BUF_SIZE)
            mess = data.decode('utf-8')  # Decode the received message

            if mess == "connect":
                print(f"New player joined: {address}")
                can_start = add_player_to_rooms(address)

                # Send a confirmation message to the client
                server_socket.sendto("connect".encode('utf-8'), address)

                # If two players are connected, start the game
                if can_start and find_room(address):
                    found_room, _ = find_room(address)
                    if not found_room.gameStarted:
                        print("Room", found_room.id, "| GAME STARTS")
                        update_game_started(found_room.id, True)

                        first_address = found_room.player1
                        second_address = found_room.player2

                        message = "start;" + found_room.id

                        # Randomly decide which player starts the game
                        if random.randint(0, 1):
                            print("Room", found_room.id, "| Player that begins:", first_address)
                            server_socket.sendto((message + ";shoot").encode('utf-8'), first_address)
                            server_socket.sendto((message + ";wait").encode('utf-8'), second_address)
                        else:
                            print("Room", found_room.id, "| Player that begins:", second_address)
                            server_socket.sendto((message + ";shoot").encode('utf-8'), second_address)
                            server_socket.sendto((message + ";wait").encode('utf-8'), first_address)
            elif mess.lower().startswith("shoots"):

                array = mess.lower().split(';')
                sender_address = address
                coords = array[0].replace(" ", "").removeprefix("shoots").replace("(", "").replace(")", "").split(",")

                room, player_number = find_room(sender_address)
                other_address = find_other_player_address(room, player_number)

                if other_address:
                    print("Room", room.id, "|Player", sender_address, "shoots on coordinates: ", coords)
                    print("Room", room.id, "|Sending shoot verification to:", other_address)

                    mes = "check" + str(coords) + ';' + room.id
                    server_socket.sendto(mes.encode('utf-8'), other_address)

            elif mess.lower().startswith("result"):
                array = mess.split(';')
                result = array[1]
                sender_address = address
                coords = array[5]

                room, player_number = find_room(sender_address)
                other_address = find_other_player_address(room, player_number)

                if other_address:
                    print("Room", room.id, "|Player", address, "verifies shoot as: ", result)
                    print("Room", room.id, "|Updating boards", other_address)

                    mes = "update;" + coords + ";" + str(result) + ";" + room.id
                    server_socket.sendto(mes.encode('utf-8'), other_address)
                if result == "False":
                    server_socket.sendto("wait".encode('utf-8'), other_address)
                    server_socket.sendto("shoot".encode('utf-8'), sender_address)
                else:
                    server_socket.sendto("wait".encode('utf-8'), sender_address)
                    server_socket.sendto("shoot".encode('utf-8'), other_address)

            elif mess.lower() == "end_you_won":

                room, player_number = find_room(address)
                other_address = find_other_player_address(room, player_number)

                if other_address:
                    print("Room", room.id, "|Player", other_address, "wins!")
                    server_socket.sendto("winner".encode('utf-8'), other_address)
                    remove_room_by_id(room.id)

            elif mess.lower() == "end":
                room, player_number = find_room(address)
                other_address = find_other_player_address(room, player_number)
                if other_address:
                    server_socket.sendto("end".encode('utf-8'), other_address)

                print(f"Room", room.id, "|Game has ended by Player {address}.")
                remove_room_by_id(room.id)
            else:
                print("ERROR, Invalid message:",mess)
                server_socket.sendto("ERROR, Invalid message".encode('utf-8'), address)
            
                           
        except socket.error as e:
            print(f"Socket error: {e}")
            exit()

def remove_room_by_id(room_id):
    global rooms
    rooms = [room for room in rooms if room.id != room_id]
    print(f"Game in room ${room_id} ended")

def add_player_to_rooms(player):
    """Add a player to an available room or create a new room."""
    can_start = False
    for room in rooms:
        if not room.gameStarted:
            if not room.player1:
                room.player1 = player
                print(f"Added {player} as player 1 to room {room.id}")
                return can_start

            elif not room.player2:
                room.player2 = player
                can_start = True
                print(f"Added {player} as player 2 to room {room.id}")
                return can_start

    # If no available room, create a new one
    new_room = GameRoom()
    new_room.player1 = player
    rooms.append(new_room)
    print(f"Created new room({new_room.id}) and added {player} as player 1")
    return can_start 
    
def update_game_started(room_id, new_value):
    """Update the gameStarted status of a room."""
    global rooms
    for room in rooms:
        if room.id == room_id:
            room.gameStarted = new_value
            break


def find_other_player_address(room, player_number):
    if room and player_number == 1:
        return room.player2
    elif room and player_number == 2:
        return room.player1
    else:
        print("Error, room doesn't exist!")
        return None
    
    
def find_room(player):
    """Find the room where a player is located."""
    for room in rooms:
        if room.player1 == player:
            return room, 1
        elif room.player2 == player:
            return room, 2
    return None, -1

if __name__ == "__main__":
    main()


