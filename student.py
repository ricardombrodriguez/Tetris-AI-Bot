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

                # Peça recebida
                piece = state['piece']
                print(state['game'])

                # A peça foi encaixada, não existindo nenhuma nova, por agora
                if piece is None:
                    new_piece = True

                # Encontrar a melhor solução para a nova peça
                elif new_piece is True:
                    print(piece)
                    current_shape = findShape(piece)
                    print(current_shape)
                    #t = SearchTree(state,current_shape)
                    #t.search()
                    new_piece = False

                # Usar a próxima 'key' para se chegarem às coordenadas pretendidas
                elif new_piece is False:
                    pass
                    # operações para mudar a key

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

# Search the shape
def findShape(piece):

    piece_coords = []
    for coord in piece:
        piece_coords.append((coord[0] - 2, coord[1] - 1))

    for shape in SHAPES:
        if shape.positions.sort(key=lambda coords: (coords[0], coords[1])) == piece_coords.sort(key=lambda coords: (coords[0], coords[1])):
            print("Found shape")
            return shape
    
    return None




# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
