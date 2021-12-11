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
        keys = []   # isto pode ser um array de arrays, cada sub-array é o conjunto de chaves para uma das peças especificas no lookahead
        first_piece = True  #quando está é true, temos de usar o search() e calcular as keys consoante o lookahead
        all_keys = []
        fs = Fs()
        
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
                    #print(keys[0])
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
                        
                        current_shape = fs.findShape(piece)

                        next_shapes = [fs.findShape(shape) for shape in next_pieces]
                        # shapes = [current_shape] + next_shapes[:]
                        shapes = [current_shape] + [next_shapes[0]]
                        #shapes = [current_shape]
                        s = Search(state,initial_info,shapes)
                        # print("começou o search")
                        start = time.time()
                        s.search()
                        """ print("--- %s seconds ---" % (time.time() - start))
                        print(s.iter)
                        print() """

                        #keys = s.solution.keys
                        # o search() tem de retornar uma lista de listas, em que cada sublista é as keys de uma peça especifica

                        #current_keys = s.solution[0].keys
                        #next_keys = s.solution[1].keys
            
                        all_keys = [sol.keys for sol in s.best_solution.solutions]
                        print("------------ nova peça ------------")
                        print("MELHOR SOLUÇÃO", all_keys[0])
                        print()
                        
                        keys = all_keys.pop(0)

                        new_piece = False
                        first_piece = False



            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return

# Search the shape 
# SHAPES = [Shape(s) for s in [S, Z, I, O, J, T, L]]
class Fs:
    
    # def __init__(self):
        
    #     self.shapekeys = dict()
        
    #     self.x = 10 
    #     self.y = 30
    
    def findShape(self, piece):
        
        #S (done)
        if piece[0][0] == piece[1][0] and piece[1][1] == piece[2][1] and piece[2][0] == piece[3][0]:
            fshape = Shape(S)

        elif piece[0][1] == piece[1][1] and piece[0][0] == piece[3][0] and piece[2][1] == piece[3][1]:
            fshape = Shape(S)
            fshape.rotate(1)

        #Z (dá erro)
        elif piece[0][0] == piece[2][0] and piece[1][1] == piece[2][1] and piece[1][0] == piece[3][0]:
            fshape = Shape(Z)

        elif piece[0][1] == piece[1][1] and piece[1][0] == piece[2][0] and piece[2][1] == piece[3][1]:
            fshape = Shape(Z)
            fshape.rotate(1)

        #I (done)
        elif piece[0][1] == piece[1][1] and piece[1][1] == piece[2][1] and piece[2][1] == piece[3][1]:
            fshape = Shape(I)
    
        elif piece[0][0] == piece[1][0] and piece[1][0] == piece[2][0] and piece[2][0] == piece[3][0]:
            fshape = Shape(I)
            fshape.rotate(1)

        #O (done)
        elif piece[0][0] == piece[2][0] and piece[0][1] == piece[1][1] and piece[1][0] == piece[3][0] and piece[2][1] == piece[3][1]:
            fshape = Shape(O)

        #J (done acho)
        elif piece[0][1] == piece[1][1] and piece[0][0] == piece[2][0] and piece[2][0] == piece[3][0]:
            fshape = Shape(J)

        elif piece[0][1] == piece[1][1] and piece[1][1] == piece[2][1] and piece[2][0] == piece[3][0]:
            fshape = Shape(J)
            fshape.rotate(1)

        #T (done acho)
        elif piece[0][0] == piece[1][0] and piece[1][1] == piece[2][1] and piece[1][0] == piece[3][0]:
            fshape = Shape(T)

        elif piece[0][1] == piece[1][1] and piece[1][1] == piece[2][1] and piece[1][0] == piece[3][0]:
            fshape = Shape(T)
            fshape.rotate(1)

        #L
        elif piece[0][0] == piece[1][0] and piece[1][0] == piece[2][0] and piece[2][1] == piece[3][1]:
            fshape = Shape(L)

        elif piece[0][1] == piece[1][1] and piece[1][1] == piece[2][1] and piece[0][0] == piece[3][0]:
            fshape = Shape(L)
            fshape.rotate(1)
        
        # fshape.set_pos((self.x - fshape.dimensions.x) / 2, 0) 
        
        # print(fshape)
        
        # for rot in range(0, len(fshape.plan)):
            
        #     min_x = min(fshape.positions, key=lambda coords: coords[0])[0]
        #     max_x = max(fshape.positions, key=lambda coords: coords[0])[0]
            
        #     # percorrer colunas [1,8]
        #     for a in range(1, self.x-1):
                    
        #         x_differential = a - min_x
        #         # dispensa soluções não válidas
        #         if (x_differential + max_x >= self.x - 1):
        #             break

        #         keys = ["w"]*rot

        #         keys += ["a"]*abs(x_differential) + ["s"] if x_differential < 0 else ["d"]*abs(x_differential) + ["s"]                
                
        #         #for item in self.shapekeys:      # se shape n está adiciona keys

        #         if fshape not in self.shapekeys:
        #             print("shapes", self.shapekeys.keys())
        #             print("new shape new keys")
        #             self.shapekeys[fshape] = [keys]
        #         else:                                    # se shape está ent atualiza keys   
        #             self.shapekeys[fshape].append(keys)
        
        return fshape
        
    

# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))