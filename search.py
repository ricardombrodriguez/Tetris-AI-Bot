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
        self.possible_solutions = []
        self.valid_solutions = []
        self.best_solution = None

        print("[SEARCH] Search inicializada")


    def search(self):

        # percorrer cada rotação possível primeiro. Porque, por exemplo, se tivermos a peça I deitada no inicio encostada à esquerda 
        # e rodarmos a mesma, esta não fica encostada logo à esquerda.

        self.iter = 0

        print()

        for i in range(0,len(self.shape.plan)):


            step = i

            original = Solution(deepcopy(self.shape))

            print("shape inicial:")
            print(original.shape.positions)

            original.shape.rotate(step)

            print("shape:")
            print(original.shape)

            # para calcular o numero de keys para chegar a uma determinada coluna
            min_x = min(original.shape.positions, key=lambda coords: coords[0])[0]

            # percorrer colunas [1,8]
            for x in range(1, self.x-1):

                # nova instância para cada solução numa coluna duma rotação específica
                solution = Solution(deepcopy(original))

                x_differential = x - min_x

                solution.keys += ["w"]*step

                if x_differential < 0:
                    solution.keys += ["a"]*abs(x_differential)
                elif x_differential > 0:
                    solution.keys += ["d"]*abs(x_differential)

                # depois de obter as keys, a ultima é sempre o "s"
                solution.keys += ["s"]

                print(solution.keys)

                self.possible_solutions.append(solution)

        # AGORA, DEPOIS DE ADICIONAR TODAS AS SOLUTIONS ÀS POSSIBLE_SOLUTIONS, PODEMOS PERCORRER A LISTA DE KEYS DE CADA SOLUÇÃO
        # SIMULAR O JOGO COM ESSAS KEYS E CALCULAR HEURISTICAS
        for sol in self.possible_solutions:

            keys = deepcopy(sol.keys)

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
                self.valid_solutions.append(solution)

        for valid_solution in self.valid_solutions:
            
            state = valid_solution.game
            valid_solution.heuristic = (self.checkHeight(state) * -0.510066) + (self.checkBumpiness(state) * -0.184483) + (self.checkHoles(state)* -0.35663) + (self.checkScore(state) * 0.555)


        self.solution = max(self.valid_solutions, key = lambda x : x.heuristic)



    def valid(self, solution):
        return not any(
            [piece_part in self.grid for piece_part in solution.shape.positions]
        ) and not any(
            [piece_part in self.game for piece_part in solution.shape.positions]
        )
        
        
    def columns_height(self, state):
        high = [0]*8
        for x, y in state:
            if 30 - y > high[x - 1]:
                high[x - 1] = 30 - y
        return high
        
    def checkHeight(self, state):
        return sum(self.columns_height(state))


    def checkBumpiness(self,state):
        bumpiness = 0
        high = self.columns_height(state)
        
        for i in range(len(high) - 1):
            bumpiness += abs(high[i] - high[i+1])
            
        return bumpiness

    def checkHoles(self, state):
        heights = self.columns_height(state)
        holes = 0
        
        for i in range(8):
            for y in range(30 - heights[i], 30):
                if [i + 1, y] not in state:
                    holes += 1
                    
        return holes

    def checkScore(self, state):
        highest = max(self.columns_height(state))
        score = 0
        y = 30 - highest
        x = 1
        for i in range(y * 8):
            coord_tmp = [x , y]
            if coord_tmp in state:
                x += 1
            else:
                y += 1
                x = 1
            if x == 8:
                score += 1
                x = 1
                y += 1
        return score
