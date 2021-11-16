import asyncio
import time
import getpass
import json
import os
import websockets
from shape import S, Z, I, O, J, T, L, Shape
from tree_search import *
from search import *
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
                    print("PIECE IS NONE")

                    new_piece = True
                    keys = None

                else:

                    key = None

                    # Encontrar a melhor solução para a nova peça
                    if new_piece is True:

                        print("NEW PIECE....")
                        current_shape = findShape(piece)

                        #t = SearchTree(state,current_shape)
                        #t.search()
                        #keys = t.solution.keys

                        s = Search(state,current_shape)
                        s.search()

                        key = keys.pop(0)
                        new_piece = False

                    elif new_piece is False:

                        # Usar a próxima 'key' para se chegarem às coordenadas pretendidas
                        if not keys:
                            piece = None
                            key = "a"
                            print("new piece is false and not keys!")
                        else:
                            key = keys.pop(0)
                            print("still have keys left...")
    


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
        print("its O")
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

    else:
        print("n deu")





# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
