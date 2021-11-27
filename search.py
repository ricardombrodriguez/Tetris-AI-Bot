from collections import Counter
from copy import deepcopy
from shape import *

# uma das soluções
class Solution:

    def __init__(self, shape, pieces): 

        self.shape = shape
        self.keys = []
        self.pieces = pieces


class Search:

    def __init__(self, state, shape, initial_info, next_shapes): 

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

        self.shape = shape 
        self.shape.set_pos((self.x - self.shape.dimensions.x) / 2, 0) 
        self.next_shapes = next_shapes
        for next_shape in next_shapes:
            next_shape.set_pos((self.x - self.shape.dimensions.x) / 2, 0) 
        self.shapes = [self.shape] + self.next_shapes    # peça atual + 3 próximas

        self.possible_solutions = []
        self.valid_solutions = []
        self.best_solution = None

        # começa no 0, ou seja, vai começar a ver a peça atual (mas depois é incrementado até chegar ao lookahead)
        self.current_iteration = 0
        self.lookahead = 4

        print("[SEARCH] Search inicializada")
        for s in self.shapes:
            print(s)
        print("=============================")


    # no inicio, o valor de solution é None
    def search(self, solution=None):

        # percorrer cada rotação possível primeiro. Porque, por exemplo, se tivermos a peça I deitada no inicio encostada à esquerda 
        # e rodarmos a mesma, esta não fica encostada logo à esquerda.

        self.current_iteration += 1

        # current -> instância do objeto que vamos manipular agora
        current = None
        game = None
        previous_keys = []
        if solution is None:
            print("solution is none")
            current = deepcopy(self.shape)  # primeira shape que recebemos, ainda não há soluções
            game = self.grid[:]
        else:
            print("solution exists")
            current = deepcopy(solution.pieces[0])  # guardar a primeira peça existente na lista
            game = solution.game[:]
            previous_keys = solution.keys[:]

        print("current shape")
        print(current)
        if solution:
            print("remaining pieces: " + str(len(solution.pieces[1:])))
            print("=== INFO ===")
            print("game")
            print(solution.game)
            print("keys")
            print(solution.keys)

        for i in range(0,len(current.plan)):

            step = i

            # para calcular o numero de keys para chegar a uma determinada coluna
            min_x = min(current.positions, key=lambda coords: coords[0])[0]

            # percorrer colunas [1,8]
            for x in range(1, self.x-1):

                # nova instância para cada solução numa coluna duma rotação específica
                solution = Solution(deepcopy(current), self.shapes[1:]) if solution is None else Solution(deepcopy(current), solution.pieces[1:])
                solution.shape.rotate(step) 
                solution.game = game



                # diferença entre a coluna atual e o min_x, para depois saber se ele vai para a esquerda, fica no meio ou vai para a direita
                x_differential = x - min_x

                keys = []
                solution.keys = previous_keys[:]

                print("solution.keys [BEFORE - AFTER]:")
                print(solution.keys)

                solution.keys += ["w"]*step

                if x_differential < 0:
                    solution.keys += ["a"]*abs(x_differential)
                    keys += ["a"]*abs(x_differential)
                elif x_differential > 0:
                    solution.keys += ["d"]*abs(x_differential)
                    keys += ["d"]*abs(x_differential)

                # depois de obter as keys, a ultima é sempre o "s"
                solution.keys += ["s"]
                keys += ["s"]

                print(solution.keys)

                # enquanto há keys para serem premidas
                valid = True
                while True:

                    # verificar se elimina linhas -> se sim, tirar do solution.game as coordenadas

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

                        solution.shape.y += 1

                        if key in ["a", "d"]:
                            solution.shape.translate(shift, 0)
                            if not self.valid(solution):
                                valid = False
                                break

                        if not keys:
                            break


                # agora a peça já está repousada

                if valid:

                    # temos que adicionar as soluções ao solution.game

                    solution.game += solution.shape.positions
                
                    #chegou ao final
                    if not solution.pieces:

                        
                    
                        # Pontuação ganha
                        self.checkScore(solution)

                        # A altura média do jogo depois de colocar essa peças
                        self.checkHeight(solution)

                        # A pontuação do peso dos buracos depois da solução
                        self.checkHoleWeight(solution)

                        #self.checkOpenHolesWeight(solution, self)

                        # A pontuação 'bumpiness' que calcula a diferença de altura em colunas adjacentes à solução
                        self.checkBumpiness(solution)

                        self.checkLowestSolution(solution)
                        
                        self.valid_solutions.append(solution)

                        """
                        print("PEÇAS DA SOLUÇÃO & KEYS:")
                        print(solution.shape.positions)
                        print(solution.keys)
                        """

                        # update best solution if it's the new best solution
                        s = sorted([self.best_solution, solution], key = lambda x: (-x.score, x.hole_weight, x.average_height, x.bumpiness, x.sum_height)) if self.best_solution else [solution]
                        self.best_solution = s[0]
                        print("best solution keys")
                        print(self.best_solution.keys)
                        print()


                    else:

                        new_solution = deepcopy(solution)
                        #new_solution.pieces.pop(0)
                        print("vai chamar nova função:")
                        self.search(new_solution)


                        # IMPORTANTE

                        # ATUALIZAR O SOLUTION.GAME, SE AS LINHAS FOREM REMOVIDAS, AS COORDENADAS DAS MESMAS TEM DE SER REMOVIDAS



                    # verificar: 
                        # se a solução está na ultima peça da solution.pieces:
                            # -> calcular heuristicas
                            # -> adicionar a uma lista de valid_solutions
                        # caso contrário
                            # passar para a próxima iteração AKA chamar a função recustiva com solution.pieces[1:] (apesar de passar a solution como parâmetro)



    # DONE
    def checkScore(self, solution):
        
        solution.score = 0
        lines = 0

        for item, count in Counter(y for _, y in solution.game).most_common():
            if count == self.x - 2:
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
            for y in range(height+1,self.y):
                # espaço vazio
                if ((x,y) not in column_coords):
                    hole_weight += 1

            """
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
            """

        solution.hole_weight = hole_weight
        #Nota: quanto maior a hole_weight, pior a solução

    """
    def checkOpenHolesWeight(self, solution, search):

        open_hole_weight = 0

        for x in range(1, self.x-1):
            column_coords = []
            for coord in solution.game:
                if coord[0] == x:
                    column_coords.append(coord)

            # verificar se tem, nas colunas adjacentes, blocos que estão ao seu lado
            for y in range(0,self.y):
                # se é um bloco vazio / buraco, verificar se existem blocos ao seu lado esquerdo e ao lado direito
                if not ((x,y) in column_coords):
                    # à esquerda
                    if ((x-1,y) in solution.game or (x-1,y) in search.grid) and ((x+1,y) in solution.game or (x+1,y) in search.grid):
                        open_hole_weight += 1


        solution.open_hole_weight = open_hole_weight
    """

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