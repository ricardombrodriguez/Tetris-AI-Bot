import asyncio
import getpass
import json
import os
import websockets
from shape import SHAPES
from tree_search import SearchTree
import random

async def agent_loop(server_address="localhost:8000", agent_name="student"):

    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        new_piece = True  #variavel para saber é uma nova peça e, assim, calcular a search tree

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server

                # Dados recebidos
                game = state['game']
                piece = state['piece']
                next_pieces = state['next_pieces']
                game_speed = state['game_speed']

                if piece is None:
                    print("nova!")
                    new_piece = True
                elif new_piece is True:
                    print("calculando")
                    #t = SearchTree(game, piece)
                    #t.search()
                    new_piece = False
                elif new_piece is False:
                    print("mesma!")
                    # operações para mudar a key

                print(piece)

                key = random.choice(["w","a","d"])

                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )  # send key command to server - you must implement this send in the AI agent

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

# Esta função tem como objetivo encontrar qual é a melhor posição para a peça atual encaixar no jogo. 
# Ela guarda esta informação para depois, por cada iteração, saber qual é a key que deve ser pressionada.
def solution(state):
    pass

# A partir da solução obtida, retornar a key que é preciso premir para chegar à solução
def searchKey():
    pass



# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
