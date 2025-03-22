import socket
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

        except socket.error as e:
            print(f"Socket error: {e}")
            exit()

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

if __name__ == "__main__":
    main()


