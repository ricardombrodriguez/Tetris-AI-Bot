from collections import Counter
from copy import copy
from shape import *

# uma das soluções
class Solution:

    def __init__(self, shape): 

        self.shape = shape
        self.keys = []
        self.heuristic = 0


class Search:

    def __init__(self, state, shape, initial_info, next_shape): 

        #self.state = state
        
        # talvez mudar a estrutura para suportar listas e ser mais rapido

        # OPERAÇÕES COM SETS SÃO MAIS RÁPIDAS DO QUE COM LISTAS NORMAIS (EX: O "IN")
        self.game = set()
        for tup in state['game']:
            self.game.add((tup[0], tup[1]))
        
        self.coords = state['piece']  

        self.grid = set()
        for coord in initial_info['grid']:
           self.grid.add((coord[0], coord[1]))

        self.x = max(self.grid, key = lambda coord : coord[0])[0] + 1
        self.y = max(self.grid, key = lambda coord : coord[1])[1]

        self.shape = shape 
        self.shape.set_pos((self.x - self.shape.dimensions.x) / 2, 0) 
        
        self.next_shape = next_shape        # só com lookahead de 1 peça
        self.next_shape.set_pos((self.x - self.next_shape.dimensions.x) / 2, 0) 
        
        self.solution = None


    def search(self):

        for rot in range(0, len(self.shape.plan)):

            original = Solution(copy(self.shape))
            original.shape.rotate(rot)
            
            # para calcular o numero de keys para chegar a uma determinada coluna
            min_x = min(original.shape.positions, key=lambda coords: coords[0])[0]
            max_x = max(original.shape.positions, key=lambda coords: coords[0])[0]

            # percorrer colunas [1,8]
            for x in range(1, self.x-1):

                x_differential = x - min_x

                # dispensa soluções não válidas
                if (x_differential + max_x >= self.x - 1):
                    break

                keys = []

                keys += ["w"]*rot

                if x_differential < 0:
                    keys += ["a"]*abs(x_differential)
                elif x_differential > 0:
                    keys += ["d"]*abs(x_differential)

                # depois de obter as keys, a ultima é sempre o "s"
                keys += ["s"]

                # obter a shape com o estado inicial
                solution = Solution(copy(self.shape))

                # guardar as keys para chegar ao estado especifico dessa solução
                solution.keys = [*keys]

                # enquanto há keys para serem premidas
                
                while self.valid(solution):

                    solution.shape.y += 1

                    key = keys.pop(0)
                                                
                    if key == "s":

                        # usar outra função mais rapida que evite um loop
                        
                        while self.valid(solution): # fica stuck aqui 
                            solution.shape.y +=1
                            
                        solution.shape.y -= 1

                    elif key == "w":
                        solution.shape.rotate()

                    elif key == "a":
                        shift = -1

                    elif key == "d":
                        shift = +1

                    if key in ["a", "d"]:
                        solution.shape.translate(shift, 0)
                    
                    if not keys:
                        break
                    
                 
                # agora a peça já está repousada
                solution.game = [*self.game] + solution.shape.positions
                solution.heuristic = (self.checkHeight(solution) * -0.510066) + (self.checkBumpiness(solution) * -0.184483) + (self.checkHoles(solution)* -0.35663) + (self.checkScore(solution) * 0.555)
                self.solution = max([self.solution, solution], key = lambda x : x.heuristic) if self.solution else solution

                # calcular outras heuristicas para outros thresholds

        #print("end")

    # verificar se há uma forma mais rapida de fazer esta verificação 
    def valid(self, solution):
        
        return not any(
            {piece_part in self.grid for piece_part in solution.shape.positions}
        ) and not any(
            {piece_part in self.game for piece_part in solution.shape.positions}
        )

    def checkHeight(self, solution):

        aggregate_height = 0

        # das colunas [1,8]
        for x in range(1, self.x-1):
            column_coords = {coord for coord in solution.game if coord[0] == x}
            aggregate_height += self.y - min(column_coords, key = lambda coord: coord[1], default = (0,self.y-1))[1]
            
        return aggregate_height

    def checkBumpiness(self,solution):
        
        bumpiness = 0
        
        # ir de 0 até 8, porque o 8 ja compara com a 9º coluna
        #start = time.time()
        for x in range(1, self.x-2):
            this_column_coords = set()
            next_column_coords = set()
            
            for coord in solution.game:
                if coord[0] == x:
                    this_column_coords.add(coord)
                elif coord[0] == x+1:
                    next_column_coords.add(coord)
                #this_height = coord[1] if coord[1] > height else height  # descobre o topo da coluna
            
            this_height = min(this_column_coords, key = lambda coord: coord[1], default = (0,self.y-1))[1]  # descobre o topo da coluna
            next_height = min(next_column_coords, key = lambda coord: coord[1], default = (0,self.y-1))[1]  # descobre o topo da coluna

            absolute_difference = abs(next_height - this_height)
            bumpiness += absolute_difference 
            
        #end = time.time()
        #print(round((end-start)/(10**-6)))
        return bumpiness
        # Nota: quanto maior a bumpiness, pior a solução

    def checkHoles(self, solution):

        hole_weight = 0
        height = self.y

        #start = time.time()
        for x in range(1, self.x-1):
            column_coords = set()
            for coord in solution.game: 
                if coord[0] == x:
                    column_coords.add(coord)
            #    height = coord[1] if coord[1] > height else height  # descobre o topo da coluna
            
            height = min(column_coords, key = lambda coord: coord[1], default = (0,self.y-1))[1]  # descobre o topo da coluna
            # verificar se está bloqueado acima
            for y in range(height+1,self.y):
                if ((x,y) not in column_coords):
                        hole_weight += 2
        # end = time.time()
        # print(round((end-start)/(10**-6)))
        return hole_weight

    def checkScore(self, solution):

        lines = 0
        
        for item, count in Counter(y for _, y in solution.game).most_common():
            if count == self.x - 2:
                solution.game = {(x, y) for (x, y) in solution.game if y != item}  # remove row
                solution.game = {
                    (x, y + 1) if y < item else (x, y) for (x, y) in solution.game
                }
                lines += 1

        return lines