actions = ["s","a","d","w"]

"""
Nós de uma arvore de pesquisa (uma dos possíveis estados das coordenadas)

self.coordinates -> Coordenadas onde a peça vai repousar nesta solução
self.score -> Pontos obtidos por esta solução (linhas completadas)
self.keys -> 'keys' precisas até chegar até esta solução (array de keys)
self.average_height -> Soma da altura de todas as colunas / num. de colunas (é uma boa heurística uma vez que smaller is better)
self.bumpiness -> Serve para medir as diferenças em altura com as colunas adjacentes
self.hole_weight -> Cada 'bloco' que é um buraco vai ter uma medida para calcular a sua dificuldade de remoção. Assim, quanto menor for este parâmetro,
                    mais fáceis são de remover os buracos na grid
"""

from collections import Counter
from copy import deepcopy
import sys


class SearchNode:

    def __init__(self,shape,score,keys):
        self.shape = shape  # copia da instância do shape pai (tem coordenadas e isso tudo)
        self.score = score
        self.keys = keys



"""
Árvore de pesquisa para encontrar a melhor solução

self.state -> Estado do jogo (atributos 'game','piece','next_pieces' e 'game_speed')
self.shape -> Instância Shape da forma atual da 'piece'
self.solution -> Para guardar a solução (um SearchNode)
self.open_nodes -> Lista que guarda todas as soluções para depois ver qual é a melhor
"""

class SearchTree:

    # Construtor (recebe o parâmetro 'state' que tem toda a informação que precisamos para obter a melhor solução)
    def __init__(self, state, shape): 
        self.state = state
        self.game = state['game']
        self.coords = state['piece']  
        self.shape = shape  
        self.solution = None
        root = SearchNode(shape, 0, [])
        self.open_nodes = [root]
        self.possible_solutions = []
        print("INCIO DA SEARCH TREE")

        # Alterar isto depois, para receber o grid de alguma forma
        self.x = 10
        self.y = 30
        self._bottom = [(i, self.y) for i in range(self.x)]  # bottom
        self._lateral = [(0, i) for i in range(self.y)]  # left
        self._lateral.extend([(self.x - 1, i) for i in range(self.y)])  # right
        self.grid = self._bottom + self._lateral

    def search(self):

        numero_iteracoes = 0

        while self.open_nodes != []:

            node = self.open_nodes.pop(0)

            numero_iteracoes += 1
            print(numero_iteracoes)

            # check if valid and if's the last node
            valid = self.valid(node.shape)

            # nao cria nós "filhos" e passa para o proximo open node
            if not valid:
                continue

            # verifica se é o ultimo nó, ou seja, se não vai divergir para novos nós (novas soluções)
            lastNode = self.isLastNode(node)

            # Calcular aquelas variaveis todas (score, bumpiness e isso tudo)
            if lastNode:

                # Guardar coordenadas onde a peça repousa e acrescentar ao grid para depois se poderem calcular as heuristicas
                node.game = self.game + node.shape.positions

                # Guardar o score obtido pela colntocação dessa peça (ou linhas eliminadas)
                self.checkScore(node)

                # A altura média do jogo depois de colocar essa peças
                self.checkHeight(node)

                # A pontuação do peso dos buracos depois da solução
                self.checkHoleWeight(node)

                # A pontuação 'bumpiness' que calcula a diferença de altura em colunas adjacentes à solução
                self.checkBumpiness(node)

                # As 'keys' necessárias (em array) para chegar às coordenadas da solução
                self.checkCost(node)

                #Maybe uma formula para calcular heuristica
                self.checkHeuristic(node)

                self.possible_solutions.append(node)

                print(" ==== HEURISTICS ===")
                print("SCORE")
                print(node.score)
                print("sum_height")
                print(node.sum_height)
                print("hole")
                print(node.hole_weight)
                print("bumpiness")
                print(node.bumpiness)
                print("cost")
                print(node.keys)
                print(node.cost)

                print("........")


            # Caso contrário, ainda dá para expandir este nó em mais possibilidades:

            node.shape.y += 1

            newnodes = []               #Novos nós que vão ser adicionados
            for keypress in actions:
            
                newnode = SearchNode(deepcopy(node.shape),0,node.keys[:])  # criar um novo node para essa action

                # para cada ação possível, fazer as alterações
                    
                if keypress == "s":
                    while self.valid(newnode.shape):
                        newnode.shape.y +=1
                    newnode.shape.y -= 1
                elif keypress == "w":
                    newnode.shape.rotate()
                    if not self.valid(newnode.shape):
                        newnode.shape.rotate(-1)
                elif keypress == "a":
                    shift = -1
                elif keypress == "d":
                    shift = +1

                if keypress in ["a", "d"]:
                    newnode.shape.translate(shift, 0)
                    if self.collide_lateral(newnode.shape):
                        newnode.shape.translate(-shift, 0)
                    elif not self.valid(newnode.shape):
                        newnode.shape.translate(-shift, 0)

                newnodes.append(newnode)

                # maybe calcular a heuristica do newnode aqui!!!

            # a* search
            self.open_nodes.extend(newnodes)
            #self.open_nodes.sort(key=lambda node: node.heuristic)

        print("chegou ao final")
        print("Numero de iterações: " + str(numero_iteracoes))
        # Calcular a solução com a melhor heuristica da self.possible_solutions
        self.solution = max(self.possible_solutions,key=lambda node: node.heuristic)


    # DONE
    def checkScore(self, node):
        
        lines = 0

        for item, count in Counter(y for _, y in node.game).most_common():
            if count == len(self._bottom) - 2:
                node.game = [(x, y) for (x, y) in node.game if y != item]  # remove row
                node.game = [
                    (x, y + 1) if y < item else (x, y) for (x, y) in node.game
                ]
                lines += 1

        node.score += lines ** 2


    # DONE
    def checkHeight(self, node):

        node.sum_height = 0

        for x in range(0, self.x):
            column_coords = [coord for coord in node.game if coord[0] == x]
            node.sum_height += min(column_coords, key = lambda coord: coord[1], default = (0,self.y - 1))[1]
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

        for x in range(0, self.x):
            column_coords = [coord for coord in node.game if coord[0] == x]
            height = min(column_coords, key = lambda coord: coord[1], default = (0,self.y - 1))[1]  # descobre o topo da coluna

            # verificar se está bloquado acima
            severity = 1
            for y in range(height+1,self.y):
                # espaço ocupado
                if ((x,y) in column_coords):
                    severity += 1
                # espaço vazio (é buraco)
                else:
                    hole_weight += severity

            # verificar se tem, nas colunas adjacentes, blocos que estão ao seu lado
            for y in range(0,self.y):
                # se é um bloco vazio / buraco, verificar se existem blocos ao seu lado esquerdo e ao lado direito
                if not ((x,y) in column_coords):
                    # à esquerda
                    if (x-1,y) in node.game:
                        hole_weight += 1
                    if (x+1,y) in node.game:
                        hole_weight += 1

        node.hole_weight = hole_weight
        #Nota: quanto maior a hole_weight, pior a solução


    # DONE
    def checkBumpiness(self, node):

        node.bumpiness = 0

        # ir de 0 até 8, porque o 8 ja compara com a 9º coluna
        for x in range(0, self.x-1):
            this_column_coords = [coord for coord in node.game if coord[0] == x]
            this_height = min(this_column_coords, key = lambda coord: coord[1], default = (0,self.y - 1))[1]  # descobre o topo da coluna

            next_column_coords = [coord for coord in node.game if coord[0] == x+1]
            next_height = min(next_column_coords, key = lambda coord: coord[1], default = (0,self.y - 1))[1]  # descobre o topo da coluna

            absolute_difference = abs(next_height - this_height)
            node.bumpiness += absolute_difference

        # Nota: quanto maior a bumpiness, pior a solução


    # DONE
    def checkCost(self, node):
        node.cost = len(node.keys)


    # Podemos usar uma formula que combina todas as heuristicas com um determinado peso (ex: score vale 50%, height vale 10%, etc...)
    # A solução com a maior heuristica é a escolhida
    def checkHeuristic(self, node):
        node.heuristic = 50 * node.score - 10 * (node.sum_height - node.hole_weight - node.bumpiness - node.cost)

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

