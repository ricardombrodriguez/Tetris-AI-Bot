from collections import Counter
from copy import deepcopy
from shape import *

# uma das soluções
class Solution:

    def __init__(self, shape): 

        self.shape = shape
        self.keys = []
        self.heuristic = 0


class Search:

    def __init__(self, state, shape, initial_info): 

        self.state = state
        self.game = []
        for tup in state['game']:
            self.game.append((tup[0], tup[1]))
        self.coords = state['piece']  

        self.grid = []
        for coord in initial_info['grid']:
           self.grid.append((coord[0], coord[1]))

        self.x = 10
        self.y = 30

        self._bottom = [(i, 30) for i in range(10)]  # bottom
        self._lateral = [(0, i) for i in range(30)]  # left
        self._lateral.extend([(10 - 1, i) for i in range(30)])  # right

        self.shape = shape 
        self.shape.set_pos((self.x - self.shape.dimensions.x) / 2, 0) 
        self.solution = None

        print("[SEARCH] Search inicializada")


    def search(self):

        # percorrer cada rotação possível primeiro. Porque, por exemplo, se tivermos a peça I deitada no inicio encostada à esquerda 
        # e rodarmos a mesma, esta não fica encostada logo à esquerda.
        for i in range(0,len(self.shape.plan)):

            step = i

            original = Solution(deepcopy(self.shape))

            original.shape.rotate(step)

            # para calcular o numero de keys para chegar a uma determinada coluna
            min_x = min(original.shape.positions, key=lambda coords: coords[0])[0]

            # percorrer colunas [1,8]
            for x in range(1, self.x-1):

                # nova instância para cada solução numa coluna duma rotação específica
                solution = Solution(deepcopy(original.shape))

                x_differential = x - min_x

                solution.keys += ["w"]*step

                if x_differential < 0:
                    solution.keys += ["a"]*abs(x_differential)
                elif x_differential > 0:
                    solution.keys += ["d"]*abs(x_differential)

                # depois de obter as keys, a ultima é sempre o "s"
                solution.keys += ["s"]

                keys = solution.keys[:]

                # obter a shape com o estado inicial
                solution = Solution(deepcopy(self.shape))

                # guardar as keys para chegar ao estado especifico dessa solução
                solution.keys = deepcopy(keys)

                # enquanto há keys para serem premidas
                valid = True
                while valid:

                    solution.shape.y += 1

                    if self.valid(solution):

                        key = keys.pop(0)

                        if key == "s":

                            while self.valid(solution):
                                solution.shape.y +=1
                                if solution.shape.y > 30:
                                    valid = False
                                    break
                            solution.shape.y -= 1

                        elif key == "w":
                            solution.shape.rotate()
                            if not self.valid(solution):
                                solution.shape.rotate(-1)

                        elif key == "a":
                            shift = -1

                        elif key == "d":
                            shift = +1

                        if key in ["a", "d"]:
                            solution.shape.translate(shift, 0)
                            if not self.valid(solution):
                                valid = False

                        if not keys:
                            break

                # agora a peça já está repousada

                if valid:
                    solution.game = deepcopy(self.game) + solution.shape.positions
                    solution.heuristic = (self.checkHeight(solution) * -0.510066) + (self.checkBumpiness(solution) * -0.184483) + (self.checkHoles(solution)* -0.35663) + (self.checkScore(solution) * 0.555)
                    self.solution = max([self.solution, solution], key = lambda x : x.heuristic) if self.solution else solution


    def valid(self, solution):
        # print(solution.shape.positions)
        return not any(
            [piece_part in self.grid for piece_part in solution.shape.positions]
        ) and not any(
            [piece_part in self.game for piece_part in solution.shape.positions]
        )
        
        
    def checkHeight(self, solution):

        aggregate_height = 0

        # das colunas [1,8]
        for x in range(1, self.x-1):
            column_coords = [coord for coord in solution.game if coord[0] == x]
            aggregate_height += self.y - min(column_coords, key = lambda coord: coord[1], default = (0,self.y))[1]

        return aggregate_height

    def checkBumpiness(self,solution):
        
        bumpiness = 0

        # ir de 0 até 8, porque o 8 ja compara com a 9º coluna
        for x in range(1, self.x-2):
            this_column_coords = []
            for coord in solution.game:
                if coord[0] == x:
                    this_column_coords.append(coord)
            this_height = min(this_column_coords, key = lambda coord: coord[1], default = (0,self.y))[1]  # descobre o topo da coluna

            next_column_coords = []
            for coord in solution.game:
                if coord[0] == x + 1:
                    next_column_coords.append(coord)
            next_height = min(next_column_coords, key = lambda coord: coord[1], default = (0,self.y))[1]  # descobre o topo da coluna

            absolute_difference = abs(next_height - this_height)
            bumpiness += absolute_difference

        return bumpiness
        # Nota: quanto maior a bumpiness, pior a solução

    def checkHoles(self, solution):

        hole_weight = 0

        for x in range(1, self.x-1):
            column_coords = []
            for coord in solution.game:
                if coord[0] == x:
                    column_coords.append(coord)
            height = min(column_coords, key = lambda coord: coord[1], default = (0,self.y-1))[1]  # descobre o topo da coluna

            # verificar se está bloqueado acima
            for y in range(height+1,self.y):
                if ((x,y) not in column_coords):
                    hole_weight += 1

        return hole_weight

    def checkScore(self, solution):

        lines = 0

        for item, count in Counter(y for _, y in solution.game).most_common():
            if count == len(self._bottom) - 2:
                solution.game = [(x, y) for (x, y) in solution.game if y != item]  # remove row
                solution.game = [
                    (x, y + 1) if y < item else (x, y) for (x, y) in solution.game
                ]
                lines += 1

        return lines