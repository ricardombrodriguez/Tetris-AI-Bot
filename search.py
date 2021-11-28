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
        for i in range(0,len(self.shape.plan)):

            step = i

            original = Solution(deepcopy(self.shape))

            original.shape.rotate(step)

            #original.keys = ["w"]*step

            # para calcular o numero de keys para chegar a uma determinada coluna
            min_x = min(self.shape.positions, key=lambda coords: coords[0])[0]

            # percorrer colunas [1,8]
            for x in range(1, self.x-1):

                # nova instância para cada solução numa coluna duma rotação específica
                solution = Solution(deepcopy(original))

                # diferença entre a coluna atual e o min_x, para depois saber se ele vai para a esquerda, fica no meio ou vai para a direita

                """ 
                ATENÇÃO

                O I vertical deve estar mal porque não vai para colunas que estão vazias no lado esquerdo!!!!!!!!!!!!!!!!!!!!
                """

                x_differential = x - min_x

                solution.keys += ["w"]*step

                if x_differential < 0:
                    solution.keys += ["a"]*abs(x_differential)
                elif x_differential > 0:
                    solution.keys += ["d"]*abs(x_differential)

                # depois de obter as keys, a ultima é sempre o "s"
                solution.keys += ["s"]

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
                solution.game = deepcopy(self.game)
                self.valid_solutions.append(solution)

        for valid_solution in self.valid_solutions:

            height = self.aggregate_height(valid_solution)
            score = self.score(valid_solution)
            hole = self.holes(valid_solution)
            bumpiness = self.bumpiness(valid_solution)
            
            valid_solution.heuristic = -0.510066 * height + 0.760666 * score + -0.35663 * hole + -0.184483 * bumpiness
            print(valid_solution.heuristic)
            # valid_solution.heuristic= 0.50 * height + 0.30 * -score + 0.15 * hole + 0.05 * bumpiness
            
            # Pontuação ganha
            self.checkScore(valid_solution)

            # A altura média do jogo depois de colocar essa peças
            self.checkHeight(valid_solution)

            # A pontuação do peso dos buracos depois da solução
            self.checkHoleWeight(valid_solution)

            # A pontuação 'bumpiness' que calcula a diferença de altura em colunas adjacentes à solução
            self.checkBumpiness(valid_solution)

            self.checkLowestSolution(valid_solution)


        print("chegou ao final")

        #  solution.columns = [solution.score, solution.bumpiness, solution.sum_height, solution.hole_weight, solution.average_height]
    

        # self.solution = min(self.valid_solutions, key = lambda x : x.average_height)
        self.solution = sorted(self.valid_solutions, key = lambda x: ( x.average_height, x.hole_weight, -x.score, x.bumpiness, x.sum_height))[0]
        # self.solution = sorted(self.valid_solutions, key = lambda x: x.heuristic)[0]



    # DONE
    def checkScore(self, solution):
        
        solution.score = 0
        lines = 0

        for item, count in Counter(y for _, y in solution.game).most_common():
            if count == len(self._bottom) - 2:
                solution.game = [(x, y) for (x, y) in solution.game if y != item]  # remove row
                solution.game = [
                    (x, y + 1) if y < item else (x, y) for (x, y) in solution.game
                ]
                lines += 1

        solution.score += lines ** 2


    # DONE
    def checkHeight(self, solution):

        solution.sum_height = 0

        # das colunas [1,8]
        for x in range(1, self.x-1):
            column_coords = []
            for coord in solution.game:
                if coord[0] == x:
                    column_coords.append(coord)
            solution.sum_height += self.y - min(column_coords, key = lambda coord: coord[1], default = (0,self.y))[1]

        # Nota: Quanto maior for a coluna, menor vai ser o score. Assim, a solução que tiver colunas menos altas vai ter melhor score, para a heuristica


    """
    Como calcular o peso cumulativo dos buracos no jogo:
    Uma célula/bloco vazio do jogo é um buraco quando:
    - Está bloqueada, no seu topo, por um bloco ocupado ou por um buraco (uma célula vazia que também tem um bloco ocupado em cima dele)
    - Está a uma altura menor ou igual da maior altura da coluna adjacente (seja esta a coluna da esquerda ou da direita)
    - Nota: quanto mais em baixo estiverem os buracos, maior a sua classificação, uma vez que estes são mais dificeis de se remover
    """

    # DONE
    def checkHoleWeight(self, solution):
        # Para cada coluna, verificar as heuristicas descritas acima ^^

        hole_weight = 0

        for x in range(1, self.x-1):
            column_coords = []
            for coord in solution.game:
                if coord[0] == x:
                    column_coords.append(coord)
            height = min(column_coords, key = lambda coord: coord[1], default = (0,self.y-1))[1]  # descobre o topo da coluna

            # verificar se está bloqueado acima
            severity = 3
            for y in range(height+1,self.y):
                # espaço ocupado
                if ((x,y) in column_coords):
                    severity += 3
                # espaço vazio (é buraco)
                else:
                    hole_weight += severity

            severity = 1
            # verificar se tem, nas colunas adjacentes, blocos que estão ao seu lado
            for y in range(0,self.y):
                # se é um bloco vazio / buraco, verificar se existem blocos ao seu lado esquerdo e ao lado direito
                if not ((x,y) in column_coords):
                    # à esquerda
                    if (x-1,y) in solution.game:
                        hole_weight += severity
                    if (x+1,y) in solution.game:
                        hole_weight += severity

        solution.hole_weight = hole_weight
        #Nota: quanto maior a hole_weight, pior a solução


    # DONE
    def checkBumpiness(self, solution):

        solution.bumpiness = 0

        # ir de 0 até 8, porque o 8 ja compara com a 9º coluna
        for x in range(1, self.x-1):
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
            solution.bumpiness += absolute_difference
        # Nota: quanto maior a bumpiness, pior a solução

###############################################################################################


    def aggregate_height(self, solution):
        
        aggregate_height = 0

        for column in range(1, 9):
            column_coords = [coord for coord in solution.game if coord[0] == column]
            aggregate_height += self.y - min(column_coords, key = lambda coord: coord[1], default = (0,self.y))[1]
                        
        return aggregate_height

        
    def score(self, solution):

        lines = 0

        for item, count in Counter(y for _, y in solution.game).most_common():
            if count == len(self._bottom) - 2:
                lines += 1

        return lines ** 2
 
    def holes(self, solution):
        # Para cada coluna, verificar as heuristicas descritas acima ^^

        hole_weight = 0

        for x in range(1, self.x-1):
            column_coords = [ coord for coord in solution.game if coord[0] == x]
            height = min(column_coords, key = lambda coord: coord[1], default = (0,self.y-1))[1]  # descobre o topo da coluna

            # verificar se está bloqueado acima
            for y in range(height+1,self.y):
                if not ((x,y) in column_coords):
                    hole_weight += 1
            # verificar se tem, nas colunas adjacentes, blocos que estão ao seu lado
            for y in range(0,self.y):
                # se é um bloco vazio / buraco, verificar se existem blocos ao seu lado esquerdo e ao lado direito
                if not ((x,y) in column_coords):
                    # à esquerda
                    if (x-1,y) in solution.game:
                        hole_weight += 1
                    if (x+1,y) in solution.game:
                        hole_weight += 1

        return hole_weight
        #Nota: quanto maior a hole_weight, pior a solução

    def bumpiness(self, solution):

        bumpiness = 0

        # ir de 0 até 8, porque o 8 ja compara com a 9º coluna
        for x in range(1, self.x-1):
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
        
    
    #######################################################################################################

    # Verifica o quão baixo a peça vai ficar
    def checkLowestSolution(self, solution):
        solution.average_height = 0
        for coord in solution.shape.positions:
            solution.average_height += (self.y - coord[1])
        solution.average_height /= len(solution.shape.positions)
        

    def valid(self, solution):
        return not any(
            [piece_part in self.grid for piece_part in solution.shape.positions]
        ) and not any(
            [piece_part in self.game for piece_part in solution.shape.positions]
        )