import asyncio
import time
import getpass
import json
import os
import websockets
from shape import S, Z, I, O, J, T, L, Shape
from tree_search import *
import random

async def agent_loop(server_address="localhost:8000", agent_name="student"):

    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        print("INICIO")

        new_piece = True  #variavel para saber é uma nova peça e, assim, calcular a search tree
        keys = []

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server

                # Peça recebida
                piece = state['piece']

                # A peça foi encaixada, não existindo nenhuma nova, por agora
                if piece is None:

                    new_piece = True

                # Encontrar a melhor solução para a nova peça
                elif new_piece is True:

                    current_shape = findShape(piece)
                    print(current_shape)

                    t = SearchTree(state,current_shape)
                    t.search()
                    keys = t.solution.keys
                    print(keys)
                    new_piece = False

                # Usar a próxima 'key' para se chegarem às coordenadas pretendidas
                key = "s" if not keys else keys.pop(0)

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

# Search the shape (FUNÇÃO ESTÁ MAL)
# SHAPES = [Shape(s) for s in [S, Z, I, O, J, T, L]]
# ESTE MÉTODO N FUNCIONA PORQUE VARIAS SHAPES TEM A DIFERENÇA IGUAL, CORRIGIR ISTO AMANHÃ
def findShape(piece):

    S_piece = Shape(S)
    piece_coords = []
    piece_coords = [(coord[0] - 2, coord[1] - 1) for coord in piece]
    if S_piece.positions.sort(key=lambda coords: (coords[0], coords[1])) == piece_coords.sort(key=lambda coords: (coords[0], coords[1])):
        return S_piece

    Z_piece = Shape(Z)
    piece_coords = []
    piece_coords = [(coord[0] - 2, coord[1] - 1) for coord in piece]
    if Z_piece.positions.sort(key=lambda coords: (coords[0], coords[1])) == piece_coords.sort(key=lambda coords: (coords[0], coords[1])):
        return Z_piece

    I_piece = Shape(I)
    piece_coords = []
    piece_coords = [(coord[0] - 3, coord[1] - 1) for coord in piece]
    if I_piece.positions.sort(key=lambda coords: (coords[0], coords[1])) == piece_coords.sort(key=lambda coords: (coords[0], coords[1])):
        return I_piece

    O_piece = Shape(O)
    piece_coords = []
    piece_coords = [(coord[0] - 3, coord[1] - 1) for coord in piece]
    if O_piece.positions.sort(key=lambda coords: (coords[0], coords[1])) == piece_coords.sort(key=lambda coords: (coords[0], coords[1])):
        return O_piece

    J_piece = Shape(J)
    piece_coords = []
    piece_coords = [(coord[0] - 3, coord[1] - 1) for coord in piece]
    if J_piece.positions.sort(key=lambda coords: (coords[0], coords[1])) == piece_coords.sort(key=lambda coords: (coords[0], coords[1])):
        return J_piece

    T_piece = Shape(T)
    piece_coords = []
    piece_coords = [(coord[0] - 3, coord[1] - 1) for coord in piece]
    if T_piece.positions.sort(key=lambda coords: (coords[0], coords[1])) == piece_coords.sort(key=lambda coords: (coords[0], coords[1])):
        return T_piece

    L_piece = Shape(L)
    piece_coords = []
    piece_coords = [(coord[0] - 2, coord[1] - 1) for coord in piece]
    if L_piece.positions.sort(key=lambda coords: (coords[0], coords[1])) == piece_coords.sort(key=lambda coords: (coords[0], coords[1])):
        return L_piece




# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
