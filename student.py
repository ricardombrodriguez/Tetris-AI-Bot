import asyncio
import time
import getpass
import json
import os
import websockets
from shape import S, Z, I, O, J, T, L, Shape
from search import *

async def agent_loop(server_address="localhost:8000", agent_name="student"):

    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        initial_info = json.loads(
                    await websocket.recv()
        )  # receive game update, this must be called timely or your game will get out of sync with the server

        print(initial_info)
        #print("INICIO")

        new_piece = True  #variavel para saber é uma nova peça e, assim, calcular a search tree
        keys = []


        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server

                if keys:
                    #print(keys[0])
                    await websocket.send(
                        json.dumps({"cmd": "key", "key": keys.pop(0)})
                    )
                
                # Peça recebida
                piece = state['piece']
                next_piece = state['next_pieces'][0]    # apenas a prineira peça
                
                # A peça foi encaixada, não existindo nenhuma nova, por agora
                if piece is None:
                    new_piece = True
                else:

                    # Encontrar a melhor solução para a nova peça
                    if new_piece is True:

                        current_shape = findShape(piece)
                        next_shape = findShape(next_piece)
                        s = Search(state,current_shape,initial_info, next_shape)
                        #s = Search(state,current_shape,initial_info)
                        s.search()
                        keys = s.solution.keys
                        new_piece = False

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

# Search the shape 
# SHAPES = [Shape(s) for s in [S, Z, I, O, J, T, L]]
def findShape(piece):

    #S (done)
    if piece[0][0] == piece[1][0] and piece[1][1] == piece[2][1] and piece[2][0] == piece[3][0]:
        return Shape(S)

    elif piece[0][1] == piece[1][1] and piece[0][0] == piece[3][0] and piece[2][1] == piece[3][1]:
        s = Shape(S)
        s.rotate(1)
        return s

    #Z (dá erro)
    elif piece[0][0] == piece[2][0] and piece[1][1] == piece[2][1] and piece[1][0] == piece[3][0]:
        return Shape(Z)

    elif piece[0][1] == piece[1][1] and piece[1][0] == piece[2][0] and piece[2][1] == piece[3][1]:
        z = Shape(Z)
        z.rotate(1)
        return z

    #I (done)
    elif piece[0][1] == piece[1][1] and piece[1][1] == piece[2][1] and piece[2][1] == piece[3][1]:
        return Shape(I)
   
    elif piece[0][0] == piece[1][0] and piece[1][0] == piece[2][0] and piece[2][0] == piece[3][0]:
        i = Shape(I)
        i.rotate(1)
        return i

    #O (done)
    elif piece[0][0] == piece[2][0] and piece[0][1] == piece[1][1] and piece[1][0] == piece[3][0] and piece[2][1] == piece[3][1]:
        return Shape(O)

    #J (done acho)
    elif piece[0][1] == piece[1][1] and piece[0][0] == piece[2][0] and piece[2][0] == piece[3][0]:
        return Shape(J)

    elif piece[0][1] == piece[1][1] and piece[1][1] == piece[2][1] and piece[2][0] == piece[3][0]:
        j = Shape(J)
        j.rotate(1)
        return j

    #T (done acho)
    elif piece[0][0] == piece[1][0] and piece[1][1] == piece[2][1] and piece[1][0] == piece[3][0]:
        return Shape(T)

    elif piece[0][1] == piece[1][1] and piece[1][1] == piece[2][1] and piece[1][0] == piece[3][0]:
        t = Shape(T)
        t.rotate(1)
        return t

    #L
    elif piece[0][0] == piece[1][0] and piece[1][0] == piece[2][0] and piece[2][1] == piece[3][1]:
        return Shape(L)

    elif piece[0][1] == piece[1][1] and piece[1][1] == piece[2][1] and piece[0][0] == piece[3][0]:
        l = Shape(L)
        l.rotate(1)
        return l

# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))