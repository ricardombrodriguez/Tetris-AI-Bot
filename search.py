from collections import Counter
from copy import deepcopy
from shape import *

# uma das soluções
class Solution:

    def __init__(self, shape): 

        self.shape = shape
        self.keys = []

class Search:

    def __init__(self, state, shape): 

        self.state = state
        self.game = state['game']
        self.coords = state['piece']  

        self.x = 10
        self.y = 30
        self._bottom = [(i, self.y) for i in range(self.x)]  # bottom
        self._lateral = [(0, i) for i in range(self.y)]  # left
        self._lateral.extend([(self.x - 1, i) for i in range(self.y)])  # right
        self.grid = self._bottom + self._lateral

        self.shape = shape 
        self.shape.set_pos((self.x - self.shape.dimensions.x) / 2, 0) 
        self.possible_solutions = []
        self.best_solution = None

        print("[SEARCH] Search inicializada")


    def search(self):

        print("posições do shape")
        print(self.shape)

        # percorrer cada rotação possível primeiro. Porque, por exemplo, se tivermos a peça I deitada no inicio encostada à esquerda 
        # e rodarmos a mesma, esta não fica encostada logo à esquerda.
        for i in range(0,len(self.shape.plan)):

            step = i

            print(step)

            solution = Solution(deepcopy(self.shape))

            solution.shape.rotate(step)

            solution.keys = ["w"]*step

            # para calcular o numero de keys para chegar a uma determinada coluna
            min_x = min(self.shape.positions, key=lambda coords: coords[0])[0]
            print("min x ", min_x)

            # percorrer colunas [1,8]
            for x in range(1, self.x-1):

                # nova instância para cada solução numa coluna duma rotação específica
                solution = Solution(deepcopy(solution))

                # diferença entre a coluna atual e o min_x, para depois saber se ele vai para a esquerda, fica no meio ou vai para a direita
                x_differential = x - min_x

                solution.keys += ["w"]*step

                if x_differential < 0:
                    solution.keys += ["a"]*abs(x_differential)
                elif x_differential > 0:
                    solution.keys += ["d"]*abs(x_differential)

                # depois de obter as keys, a ultima é sempre o "s"
                solution.keys += ["s"]

                print("SOLUTION KEYS")
                print(solution.keys)

                self.possible_solutions.append(solution)

        # AGORA, DEPOIS DE ADICIONAR TODAS AS SOLUTIONS ÀS POSSIBLE_SOLUTIONS, PODEMOS PERCORRER A LISTA DE KEYS DE CADA SOLUÇÃO
        # SIMULAR O JOGO COM ESSAS KEYS E CALCULAR HEURISTICAS
        print("num de possiveis solutions")
        print(len(self.possible_solutions))

        """
        # check if valid
        valid = self.valid(solution.shape)

        # nao cria nós "filhos" e passa para o proximo open node
        if not valid:
            continue
        """













    # DONE
    def checkScore(self, solution):
        
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
    def checkHeight(self, node):

        node.sum_height = 0

        # das colunas [1,8]
        for x in range(1, self.x-1):
            column_coords = []
            for coord in node.game:
                if coord[0] == x:
                    column_coords.append(coord)
            node.sum_height += self.y - min(column_coords, key = lambda coord: coord[1], default = (0,self.y))[1]

        # Nota: Quanto maior for a coluna, menor vai ser o score. Assim, a solução que tiver colunas menos altas vai ter melhor score, para a heuristica


    """
    Como calcular o peso cumulativo dos buracos no jogo:

    Uma célula/bloco vazio do jogo é um buraco quando:
    - Está bloqueada, no seu topo, por um bloco ocupado ou por um buraco (uma célula vazia que também tem um bloco ocupado em cima dele)
    - Está a uma altura menor ou igual da maior altura da coluna adjacente (seja esta a coluna da esquerda ou da direita)
    - Nota: quanto mais em baixo estiverem os buracos, maior a sua classificação, uma vez que estes são mais dificeis de se remover
    """

    # DONE
    def checkHoleWeight(self, node):
        # Para cada coluna, verificar as heuristicas descritas acima ^^

        hole_weight = 0

        for x in range(1, self.x-1):
            column_coords = []
            for coord in node.game:
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
                    if (x-1,y) in node.game:
                        hole_weight += severity
                    if (x+1,y) in node.game:
                        hole_weight += severity

        node.hole_weight = hole_weight
        #Nota: quanto maior a hole_weight, pior a solução


    # DONE
    def checkBumpiness(self, node):

        node.bumpiness = 0

        # ir de 0 até 8, porque o 8 ja compara com a 9º coluna
        for x in range(1, self.x-1):
            this_column_coords = []
            for coord in node.game:
                if coord[0] == x:
                    this_column_coords.append(coord)
            this_height = min(this_column_coords, key = lambda coord: coord[1], default = (0,self.y))[1]  # descobre o topo da coluna

            next_column_coords = []
            for coord in node.game:
                if coord[0] == x + 1:
                    next_column_coords.append(coord)
            next_height = min(next_column_coords, key = lambda coord: coord[1], default = (0,self.y))[1]  # descobre o topo da coluna

            absolute_difference = abs(next_height - this_height)
            node.bumpiness += absolute_difference
        # Nota: quanto maior a bumpiness, pior a solução


    # Verifica o quão baixo a peça vai ficar
    def checkLowestSolution(self, node):
        node.average_height = 0
        for coord in node.shape.positions:
            node.average_height += (self.y - coord[1])
        node.average_height /= len(node.shape.positions)


    # Podemos usar uma formula que combina todas as heuristicas com um determinado peso (ex: score vale 50%, height vale 10%, etc...)
    # A solução com a maior heuristica é a escolhida
    def checkHeuristic(self, node):
        node.heuristic = 100000 * node.score - 100 * node.sum_height - 10 * node.hole_weight - 200 * node.bumpiness
        node.columns = [node.score, node.bumpiness, node.sum_height, node.hole_weight]

    def valid(self, piece):
        return not any(
            [piece_part in self.grid for piece_part in piece.positions]
        ) and not any(
            [piece_part in self.game for piece_part in piece.positions]
        )

    def collide_lateral(self, piece):
        return any(
            [piece_part in self._lateral for piece_part in piece.positions]
        )

    # Verificar se existe algum bloco ocupado em baixo dele, o que significa que acabou e é uma das soluções
    def isLastNode(self,node):
        for coords in node.shape.positions:
            below_coords = (coords[0], coords[1]+1)
            #ver se bate na grid também
            if (below_coords in self.game or below_coords in self.grid):
                self.possible_solutions.append(node)
                return True
        return False