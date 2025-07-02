import uuid
import time

class GameRoom:
    def __init__(self):
        self.id = str(uuid.uuid4())  # Unique ID for the game room
        self.player1 = {}  # Stores player 1's address and socket
        self.player2 = {}  # Stores player 2's address and socket
        self.gameStarted = False  # Tracks if the game has started
        self.player1_ready = False  # Tracks if player 1 has placed ships and is ready
        self.player2_ready = False  # Tracks if player 2 has placed ships and is ready
        self.player1_last_heartbeat = time.time()  # Last heartbeat timestamp for player 1
        self.player2_last_heartbeat = time.time()  # Last heartbeat timestamp for player 2

    def both_players_ready(self):
        """Check if both players are ready to start the game"""
        return self.player1_ready and self.player2_ready

    def is_player_active(self, player_number, timeout=30):
        """Check if a player is still active based on heartbeat"""
        current_time = time.time()
        if player_number == 1:
            return (current_time - self.player1_last_heartbeat) < timeout
        elif player_number == 2:
            return (current_time - self.player2_last_heartbeat) < timeout
        return False

    def update_heartbeat(self, player_number):
        """Update the last heartbeat time for a player"""
        current_time = time.time()
        if player_number == 1:
            self.player1_last_heartbeat = current_time
        elif player_number == 2:
            self.player2_last_heartbeat = current_time

    def __str__(self):
        return f"Room ID: [ {self.id},\n Player 1: {self.player1},\n Player 2: {self.player2},\n Game Started: {self.gameStarted},\n Player1 Ready: {self.player1_ready},\n Player2 Ready: {self.player2_ready} \n ]"
    