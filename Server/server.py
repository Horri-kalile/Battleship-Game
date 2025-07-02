import socket
import random
import threading
import time
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

    # Start background thread for monitoring disconnections
    monitor_thread = threading.Thread(target=monitor_disconnections, args=(server_socket,), daemon=True)
    monitor_thread.start()

    while True:
        try:
            # Receive data from clients
            data, address = server_socket.recvfrom(BUF_SIZE)
            mess = data.decode('utf-8')  # Decode the received message

            if mess == "connect":
                print(f"New player joined: {address}")
                can_start = add_player_to_rooms(address)

                # Send a confirmation message to the client
                try:
                    server_socket.sendto("connect".encode('utf-8'), address)
                except socket.error:
                    print(f"Failed to send connect confirmation to {address}")
                    continue

                # If two players are connected, send prepare message
                if can_start and find_room(address):
                    found_room, _ = find_room(address)
                    if not found_room.gameStarted:
                        print("Room", found_room.id, "| Both players connected, preparing game")

                        first_address = found_room.player1
                        second_address = found_room.player2

                        message = "prepare_game;" + found_room.id

                        try:
                            server_socket.sendto(message.encode('utf-8'), first_address)
                            server_socket.sendto(message.encode('utf-8'), second_address)
                        except socket.error as e:
                            print(f"Failed to send prepare_game message: {e}")

            elif mess.startswith("ready"):
                # Player has placed ships and is ready to start
                array = mess.split(';')
                room_id = array[1] if len(array) > 1 else None
                
                room, player_number = find_room(address)
                if room and room.id == room_id:
                    if player_number == 1:
                        room.player1_ready = True
                        print(f"Room {room.id} | Player 1 is ready")
                    elif player_number == 2:
                        room.player2_ready = True
                        print(f"Room {room.id} | Player 2 is ready")

                    # Check if both players are ready
                    if room.both_players_ready() and not room.gameStarted:
                        print("Room", room.id, "| GAME STARTS")
                        update_game_started(room.id, True)

                        first_address = room.player1
                        second_address = room.player2

                        message = "start;" + room.id

                        # Randomly decide which player starts the game
                        if random.randint(0, 1):
                            print("Room", room.id, "| Player that begins:", first_address)
                            try:
                                server_socket.sendto((message + ";shoot").encode('utf-8'), first_address)
                                server_socket.sendto((message + ";wait").encode('utf-8'), second_address)
                            except socket.error as e:
                                print(f"Failed to send start messages: {e}")
                        else:
                            print("Room", room.id, "| Player that begins:", second_address)
                            try:
                                server_socket.sendto((message + ";shoot").encode('utf-8'), second_address)
                                server_socket.sendto((message + ";wait").encode('utf-8'), first_address)
                            except socket.error as e:
                                print(f"Failed to send start messages: {e}")

            elif mess.startswith("heartbeat"):
                # Update player's heartbeat
                room, player_number = find_room(address)
                if room:
                    room.update_heartbeat(player_number)

            elif mess == "timeout_loss":
                # Player timed out during their turn
                room, player_number = find_room(address)
                if room:
                    room.update_heartbeat(player_number)
                    
                other_address = find_other_player_address(room, player_number)

                if other_address:
                    print("Room", room.id, "|Player", address, "lost by timeout")
                    try:
                        server_socket.sendto("opponent_timeout_win".encode('utf-8'), other_address)
                    except socket.error:
                        print(f"Could not notify winner {other_address}")
                    remove_room_by_id(room.id)

            elif mess.lower().startswith("shoots"):
                array = mess.lower().split(';')
                sender_address = address
                coords = array[0].replace(" ", "").removeprefix("shoots").replace("(", "").replace(")", "").split(",")

                room, player_number = find_room(sender_address)
                if room:
                    # Update heartbeat when player makes a move
                    room.update_heartbeat(player_number)
                    
                other_address = find_other_player_address(room, player_number)

                if other_address:
                    print("Room", room.id, "|Player", sender_address, "shoots on coordinates: ", coords)
                    print("Room", room.id, "|Sending shoot verification to:", other_address)

                    mes = "check" + str(coords) + ';' + room.id
                    try:
                        server_socket.sendto(mes.encode('utf-8'), other_address)
                    except socket.error:
                        print(f"Player {other_address} seems disconnected during shoot verification")
                        handle_player_disconnect(server_socket, room, 2 if player_number == 1 else 1)

            elif mess.lower().startswith("result"):
                array = mess.split(';')
                result = array[1]
                sender_address = address
                coords = array[5]

                room, player_number = find_room(sender_address)
                if room:
                    # Update heartbeat when player responds
                    room.update_heartbeat(player_number)
                    
                other_address = find_other_player_address(room, player_number)

                if other_address:
                    print("Room", room.id, "|Player", address, "verifies shoot as: ", result)
                    print("Room", room.id, "|Updating boards", other_address)

                    mes = "update;" + coords + ";" + str(result) + ";" + room.id
                    try:
                        server_socket.sendto(mes.encode('utf-8'), other_address)
                    except socket.error:
                        print(f"Player {other_address} seems disconnected during board update")
                        handle_player_disconnect(server_socket, room, 2 if player_number == 1 else 1)
                        continue

                if result == "False":
                    try:
                        server_socket.sendto("wait".encode('utf-8'), other_address)
                        server_socket.sendto("shoot".encode('utf-8'), sender_address)
                    except socket.error:
                        print(f"Failed to send turn messages")
                else:
                    try:
                        server_socket.sendto("wait".encode('utf-8'), sender_address)
                        server_socket.sendto("shoot".encode('utf-8'), other_address)
                    except socket.error:
                        print(f"Failed to send turn messages")

            elif mess.lower() == "end_you_won":
                room, player_number = find_room(address)
                if room:
                    room.update_heartbeat(player_number)
                    
                other_address = find_other_player_address(room, player_number)

                if other_address:
                    print("Room", room.id, "|Player", other_address, "wins!")
                    try:
                        server_socket.sendto("winner".encode('utf-8'), other_address)
                    except socket.error:
                        print(f"Could not notify winner {other_address}")
                    remove_room_by_id(room.id)

            elif mess.lower() == "end":
                room, player_number = find_room(address)
                if room:
                    room.update_heartbeat(player_number)
                    
                other_address = find_other_player_address(room, player_number)
                if other_address:
                    try:
                        server_socket.sendto("end".encode('utf-8'), other_address)
                    except socket.error:
                        print(f"Could not notify end to {other_address}")

                print(f"Room", room.id, "|Game has ended by Player {address}.")
                remove_room_by_id(room.id)
            else:
                print("ERROR, Invalid message:",mess)
                try:
                    server_socket.sendto("ERROR, Invalid message".encode('utf-8'), address)
                except socket.error:
                    print(f"Could not send error message to {address}")
            
                           
        except socket.error as e:
            print(f"Socket error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

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

def monitor_disconnections(server_socket):
    """Monitor for player disconnections and handle them appropriately"""
    global rooms
    while True:
        time.sleep(5)  # Check every 5 seconds
        rooms_to_remove = []
        
        for room in rooms[:]:  # Copy list to avoid modification during iteration
            try:
                # Check if players are still active
                if room.player1 and not room.is_player_active(1):
                    print(f"Room {room.id} | Player 1 disconnected")
                    handle_player_disconnect(server_socket, room, 1)
                    continue
                    
                if room.player2 and not room.is_player_active(2):
                    print(f"Room {room.id} | Player 2 disconnected")
                    handle_player_disconnect(server_socket, room, 2)
                    continue
                    
            except Exception as e:
                print(f"Error monitoring room {room.id}: {e}")

def handle_player_disconnect(server_socket, room, disconnected_player):
    """Handle when a player disconnects"""
    global rooms
    
    if disconnected_player == 1:
        remaining_player = room.player2
        disconnected_address = room.player1
    else:
        remaining_player = room.player1
        disconnected_address = room.player2
    
    if remaining_player:
        try:
            if room.gameStarted:
                # Game was in progress - player disconnected
                server_socket.sendto("opponent_disconnected;game_in_progress".encode('utf-8'), remaining_player)
            else:
                # Game hadn't started yet, return to waiting room
                server_socket.sendto("opponent_disconnected;waiting_room".encode('utf-8'), remaining_player)
        except socket.error:
            print(f"Could not notify remaining player {remaining_player} of disconnection")
    
    # Remove the room
    remove_room_by_id(room.id)
    print(f"Room {room.id} removed due to player {disconnected_address} disconnection")

if __name__ == "__main__":
    main()


