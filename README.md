# Battleship Game

## Overview

The Battleship Game is a two-player game where the objective is to destroy all opponent ships. The game begins with a randomly selected player, determined at the start of the game.
Players take turns making shots by entering coordinates on their respective shooting boards. After each shot, the player's shooting board is updated with the result,
and the opponent's ship board is also updated accordingly. If a shot hits, the same player gets another turn.

## Communication Scheme

The communication in the game is based on Socket and UDP (User Datagram Protocol) technologies, following a client-server architecture.

Connection Establishment:

The client sends a "connect" message to the server, indicating an attempt to establish a connection.
The server responds with "connect" to confirm the connection. A new room is created, or the user is added to an existing one.

Game Start:

The server notifies the client about the game start by sending a message "start;room_id;action."
The client receives this information, displays relevant messages, and initializes shooting and ship boards.

Player Moves:

While in "wait" mode, the client receives a "wait" message from the server, indicating the opponent's turn.
While in "shoot" mode, the client receives a "shoot" message, indicating it's the player's turn to shoot.
Shots:

A player sends a shot information to the server in the form of "shoot (x,y);player_address;room_id."
The server forwards the shot information to the other player, who checks whether the shot hits.
Results of shots are communicated between players in the format "result;True/False;from;player_address;coord;(x,y)."

Game End:

If one of the players wins, the opponent sends an "end_you_won" message to the server. The server then sends a "winner" message to the victorious player and an "end" message to the losing player.
Both players are subsequently offered the option to play again.

Additional Messages:

Other messages regarding board updates, opponent moves, victory, or surrender are also transmitted and handled by both sides.
If the server receives an unexpected message, it responds with an error to the sender.

## Usage Description

The client connects and waits until there are two players in the room.
Upon the start of the game, the player receives information about the game rules and the meaning of symbols on the board.
The user can set up their ships on the board or choose from predefined layouts.
One player enters coordinates to make a shot, and the other player waits for their turn.
If the user inputs a string, a number outside the board size, or already used coordinates, the system prompts for a valid entry.
If a player enters 'end' in a field, the game ends, and a message is sent to the opponent that the player surrendered.
After each shot, the result is verified by the opponent's client and displayed on the console and the shots board.
Players continue attacking each other until one of them destroys all opponent ships.
In case a player decides to surrender, the other player is informed.
The game concludes with information about victory/defeat, and the option for a rematch is displayed.

## Running the Battleship Game

## Server Setup

1. Navigate to the server folder.
2. Open a terminal in the server directory.
3. Run the following command to start the server: `python server.py`
4. The server will start, and you will see messages indicating successful initialization.

## Client Setup

1. Navigate to the client folder.
2. Open a terminal in the client directory.
3. Run the following command to start a client: `python client.py`
4. Repeat this step for each additional player/client you want to connect to the game.

Follow the on-screen instructions to set up your ships and participate in the game.

Notes:
The server must be running before clients connect to ensure proper communication.
We have used Python version 3.13 (just in case there are any issues caused by using a different version)
