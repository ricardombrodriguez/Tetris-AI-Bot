import asyncio
import getpass
import json
import os
import websockets
from shape import S, Z, I, O, J, T, L, Shape
from search import *
import timeit

async def agent_loop(server_address="localhost:8000", agent_name="student"):

    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        initial_info = json.loads(
                    await websocket.recv()
        )  # receive game update, this must be called timely or your game will get out of sync with the server

        print("INICIO")

        new_piece = True  #variavel para saber é uma nova peça e, assim, calcular a search tree
        keys = []

        iteracao = 1

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server

                if keys:
                    await websocket.send(
                        json.dumps({"cmd": "key", "key": keys.pop(0)})
                    )

                # Peça recebida
                piece = state['piece']
                next_pieces = state['next_pieces']

                # A peça foi encaixada, não existindo nenhuma nova, por agora
                if piece is None:

                    new_piece = True
                    iteracao += 1

                else:

                    # Encontrar a melhor solução para a nova peça
                    if new_piece is True:

                        current_shape = findShape(piece)
                        next_shapes = [findShape(next_piece) for next_piece in next_pieces]
                        s = Search(state,current_shape,initial_info,next_shapes)
                        print("VAI ENTRAR NO SEARCH")
                        start = timeit.timeit()
                        s.search()
                        end = timeit.timeit()
                        print("TEMPO (EM MILISSEGUNDOS): " + str(end-start))
                        print("SAIU DO SEARCH")
                        print("NUMBER OF ITERATIONS:" + str(s.current_iteration))
                        keys = s.best_solution.keys
                        print("Keys:")
                        print(keys)
                        print("Score")
                        print(s.best_solution.score)
                        print(s.best_solution.sum_height)


                        new_piece = False

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


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
