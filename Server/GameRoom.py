import uuid

class GameRoom:
    def __init__(self):
        self.id = str(uuid.uuid4())  # Unique ID for the game room
        self.player1 = {}  # Stores player 1's address and socket
        self.player2 = {}  # Stores player 2's address and socket
        self.gameStarted = False  # Tracks if the game has started

    def __str__(self):
        return f"Room ID: [ {self.id},\n Player 1: {self.player1},\n Player 2: {self.player2},\n Game Started: {self.gameStarted} \n ]"
    