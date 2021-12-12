import asyncio
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

        shapes_keys = shapesKeys(SHAPES,initial_info)

        A = -0.510066
        B = -0.184483
        C = -0.35663
        D = 0.760666

        variables = [A,B,C,D]

        new_piece = True  #variavel para saber é uma nova peça e, assim, calcular a search tree
        keys = []   # isto pode ser um array de arrays, cada sub-array é o conjunto de chaves para uma das peças especificas no lookahead
        first_piece = True  #quando está é true, temos de usar o search() e calcular as keys consoante o lookahead
        all_keys = []
  
        # grid = {(tup[0],tup[1]) for tup in initial_info['grid']}
        # x = max(grid, key = lambda coord : coord[0])[0] + 1
        # y = max(grid, key = lambda coord : coord[1])[1]
        # print(x,y)

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
                    game_speed = state['game_speed']
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

                        shapes = None
                        if game_speed <= 25:
                            # lookahead 3
                            shapes = [current_shape] + next_shapes[:]

                        elif game_speed > 25 and game_speed < 32:
                            #lookahead 2
                            shapes = [current_shape] + next_shapes[:-1]

                        elif game_speed >= 32:
                            #lookahead 1
                            shapes = [current_shape] + next_shapes[:-2]

                        #shapes = [current_shape] + next_shapes[:-2]

                        s = Search(state,initial_info,shapes,variables,shapes_keys)
                        s.search()

                        all_keys = None
                        try:
                            all_keys = [sol.keys for sol in s.best_solution.solutions]
                        except:
                            all_keys = [["s"]]*len(shapes)

                        keys = all_keys.pop(0)

                        new_piece = False
                        first_piece = False

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

def shapesKeys(shapes, initial_info):

    grid = {(tup[0],tup[1]) for tup in initial_info['grid']}
    x = max(grid, key = lambda coord : coord[0])[0] + 1         

    shapekeys = dict()    #dicionario q guarda shape+rotation e todas as teclas possiveis no tabuleiro deça peça para essa rotaçao

    for fshape in shapes:   # para cada shape existente vai descobrir TODAS as combinaçoes de teclas q podem ser premidas

        fshape.set_pos((x - fshape.dimensions.x) / 2, 0)
            
        for rot in range(0, len(fshape.plan)):  # loop para fazer cada rotaçao da peça atual
            
            _fs = copy(fshape)
            _fs.rotate(rot)

            min_x = min(_fs.positions, key=lambda coords: coords[0])[0]
            max_x = max(_fs.positions, key=lambda coords: coords[0])[0]

            name = _fs.name + str(rot)
            
            # percorrer colunas [1,8]
            for a in range(1, x-1):
                    
                x_differential = a - min_x
                # dispensa soluções não válidas
                if (x_differential + max_x >= x - 1):
                    break

                keys = ["w"]*rot
                keys += ["a"]*abs(x_differential) + ["s"] if x_differential < 0 else ["d"]*abs(x_differential) + ["s"]                
                shapekeys.setdefault(name, []).append(keys)    
                 
    return shapekeys

    
def findShape(piece):
    
    #S (done)
    if piece[0][0] == piece[1][0] and piece[1][1] == piece[2][1] and piece[2][0] == piece[3][0]:
        fshape = Shape(S)

    #Z (done)
    elif piece[0][0] == piece[2][0] and piece[1][1] == piece[2][1] and piece[1][0] == piece[3][0]:
        fshape = Shape(Z)

    #I (done)
    elif piece[0][1] == piece[1][1] and piece[1][1] == piece[2][1] and piece[2][1] == piece[3][1]:
        fshape = Shape(I)

    #O (done)
    elif piece[0][0] == piece[2][0] and piece[0][1] == piece[1][1] and piece[1][0] == piece[3][0] and piece[2][1] == piece[3][1]:
        fshape = Shape(O)

    #J (done)
    elif piece[0][1] == piece[1][1] and piece[0][0] == piece[2][0] and piece[2][0] == piece[3][0]:
        fshape = Shape(J)

    #T (done)
    elif piece[0][0] == piece[1][0] and piece[1][1] == piece[2][1] and piece[1][0] == piece[3][0]:
        fshape = Shape(T)

    #L (done)
    elif piece[0][0] == piece[1][0] and piece[1][0] == piece[2][0] and piece[2][1] == piece[3][1]:
        fshape = Shape(L)
        
    return fshape
    

# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))