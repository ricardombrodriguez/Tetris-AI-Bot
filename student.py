import asyncio
import getpass
import json
import os
import websockets
from shape import S, Z, I, O, J, T, L, Shape
from search import *
import time

async def agent_loop(server_address="localhost:8000", agent_name="student"):

    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        initial_info = json.loads(
                    await websocket.recv()
        )  # receive game update, this must be called timely or your game will get out of sync with the server

        shapes_keys = shapesKeys(SHAPES,initial_info)
        print(shapes_keys)


        #random.uniform(-0.005, 0.005)
        A = -0.5315399798301605 
        B = -0.19154935732098807
        C = -0.21347761435267243 
        D = 0.35768437036647033
        variables = [A,B,C,D]

        new_piece = True  #variavel para saber é uma nova peça e, assim, calcular a search tree
        keys = []   # isto pode ser um array de arrays, cada sub-array é o conjunto de chaves para uma das peças especificas no lookahead
        first_piece = True  #quando está é true, temos de usar o search() e calcular as keys consoante o lookahead
        all_keys = []
        
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
                if 'piece' in state:
                    piece = state['piece']
                    next_pieces = state['next_pieces']    # apenas a prineira peça
                else:
                    piece = None
                
                # A peça foi encaixada, não existindo nenhuma nova, por agora
                if piece is None:
                    new_piece = True

                # Nova peça
                elif new_piece:
                    # Caso a peça faça parte do lookahead de uma peça anterior (só verifica se keys existe porque o pop das keys ja acontece acima)
                    if not first_piece:

                        # se todas as chaves/keys do lookahead já foram enviadas, então acabou e a próxima peça recebida vai fazer o search
                        if not all_keys:
                            first_piece = True
                            
                        else:
                            new_piece = False
                            keys = all_keys.pop(0)
                            
                    # Encontrar a melhor solução para a nova peça
                    elif first_piece:

                        current_shape = findShape(piece)
                        next_shapes = [findShape(shape) for shape in next_pieces]
                        # shapes = [current_shape] + next_shapes[:]
                        shapes = [current_shape] + next_shapes[:-2]
                        #shapes = [current_shape] + next_shapes[:-3]
                        s = Search(state,initial_info,shapes,variables,shapes_keys)
                        print("começou o search")
                        start = time.time()
                        s.search()
                        print("--- %s seconds (1 lookeahead) ---" % (time.time() - start))
                        print(s.iter)
                        print()
            
                        all_keys = [sol.keys for sol in s.best_solution.solutions]

                      
                        keys = all_keys.pop(0)

                        new_piece = False
                        first_piece = False

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                with open("pontuações.txt", "a") as file_object:
                    file_object.write("A: " + str(A) + " | ")
                    file_object.write("B: " + str(B) + " | ")
                    file_object.write("C: " + str(C) + " | ")
                    file_object.write("D: " + str(D) + " | ")
                    file_object.write("\n")
                    file_object.close()

                return

def shapesKeys(shapes, initial_info):

    grid = {(tup[0],tup[1]) for tup in initial_info['grid']}
    x = max(grid, key = lambda coord : coord[0])[0] + 1
    y = max(grid, key = lambda coord : coord[1])[1]

    shapekeys = {}    #dict

    for fshape in shapes:

        fshape.set_pos((x - fshape.dimensions.x) / 2, 0) 
            
        for rot in range(0, len(fshape.plan)):
            
            _fs = copy(fshape)
            _fs.rotate(rot)
            
            min_x = min(_fs.positions, key=lambda coords: coords[0])[0]
            max_x = max(_fs.positions, key=lambda coords: coords[0])[0]
            
            # percorrer colunas [1,8]
            for a in range(1, x-1):
                    
                x_differential = a - min_x
                # dispensa soluções não válidas
                if (x_differential + max_x >= x - 1):
                    break

                keys = ["w"]*rot

                keys += ["a"]*abs(x_differential) + ["s"] if x_differential < 0 else ["d"]*abs(x_differential) + ["s"]                
                
                name = _fs.name + str(rot)
                shapekeys.setdefault(name, []).append(keys)    
                 
    return shapekeys

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