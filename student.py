import asyncio
import getpass
import json
import os
import websockets
from shape import SHAPES

async def agent_loop(server_address="localhost:8000", agent_name="student"):

    # Guardar variáveis:
    current_shape = None        #Tipo de forma

    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

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
                    current_shape = None
                elif current_shape is not None:
                    continue
                else:
                    current_shape = findShape(piece)


                print("PIECE:")
                print(piece)
                print("GAME:")
                print(game)
                print("=====================")
                

                # Verificar se mudou a forma. Caso isto se verifique, procurar qual é a peça correspondente e guardar numa variável e, depois disso
                # procurar uma solução para a peça.


                solution(state)
                key = searchKey()
                key = "s"
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
        if shape.positions == piece_coords:
            return shape


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
