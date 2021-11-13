
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


class SearchNode:

    def __init__(self,shape,score,keys,average_height,bumpiness,hole_weight):
        self.shape = shape  # copia da instância do shape pai (tem coordenadas e isso tudo)
        self.score = score
        self.keys = keys

    # função para verificar se já passamos por esse nó
    def in_parent(self, newstate):
        if self.state == newstate:
            return True
        if not self.parent:
            return False
        return self.parent.in_parent(newstate)


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
        root = SearchNode(shape, 0, [], 0, 0, 0)
        self.open_nodes = [root]
        self.possible_solutions = []

        # Alterar isto depois, para receber o grid de alguma forma
        x = 10
        y = 30
        self._bottom = [(i, y) for i in range(x)]  # bottom
        self._lateral = [(0, i) for i in range(y)]  # left
        self._lateral.extend([(x - 1, i) for i in range(y)])  # right
        self.grid = self._bottom + self._lateral

    def search(self):

        while self.open_nodes != []:

            node = self.open_nodes.pop(0)

            # check if valid and if's the last node
            valid = self.isValid(node)

            # nao cria nós "filhos" epassa para o proximo open node
            if not valid:
                continue

            # verifica se é o ultimo nó, ou seja, se não vai divergir para novos nós (novas soluções)
            lastNode = self.isLastNode(node)

            # Calcular aquelas variaveis todas (score, bumpiness e isso tudo)
            if lastNode:

                # Guardar coordenadas onde a peça repousa e acrescentar ao grid para depois se poderem calcular as heuristicas
                node.game = self.game.extend(node.shape.positions)
                
                # Guardar o score obtido pela colocação dessa peça (ou linhas eliminadas)
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
                node.heuristic = self.calculateHeuristic(node)

                self.possible_solutions.append(node)



            # Caso contrário, ainda dá para expandir este nó em mais possibilidades:

            newnodes = []               #Novos nós que vão ser adicionados
            for key in ["w","a","s","d"]:
            
                newnode = SearchNode(node.shape,0,node.keys,0,0,0)  # criar um novo node para essa action

                # para cada ação possível, fazer as alterações
                    
                if key == "s":
                    while self.valid(newnode.shape):
                        newnode.shape.y +=1
                    newnode.shape.y -= 1
                elif key == "w":
                    newnode.shape.rotate()
                    if not self.valid(newnode.shape):
                        newnode.shape.rotate(-1)
                elif key == "a":
                    shift = -1
                elif key == "d":
                    shift = +1

                if key in ["a", "d"]:
                    newnode.shape.translate(shift, 0)
                    if self.collide_lateral(newnode.shape):
                        newnode.shape.translate(-shift, 0)
                    elif not self.valid(newnode.shape):
                        newnode.shape.translate(-shift, 0)

                newnode.keys.append(key)        # adicionar key à lista de keys introduzidas para chegar a esse estado 

                # maybe calcular a heuristica do newnode aqui!!!

            self.open_nodes.extend(newnodes)
            #self.open_nodes.sort(key=lambda x: x.heuristic + x.cost)

        return None

    # DONE
    def checkScore(self, node):
        
        lines = 0

        for item, count in Counter(y for _, y in self.game).most_common():
            if count == len(self._bottom) - 2:
                self.game = [(x, y) for (x, y) in self.game if y != item]  # remove row
                self.game = [
                    (x, y + 1) if y < item else (x, y) for (x, y) in self.game
                ]
                lines += 1

        self.score += lines ** 2
        

    def checkHeight(self, node):
        #self.average_height = average_height
        pass

    def checkHoleWeight(self, node):
        #self.hole_weight = hole_weight
        pass

    def checkBumpiness(self, node):
        #self.bumpiness = bumpiness
        pass

    # DONE
    def checkCost(self, node):
        return len(node.keys)

    #Podemos usar uma formula que combina todas as heuristicas com um determinado peso (ex: score vale 50%, height vale 10%, etc...)
    def checkHeuristic(self, node):
        pass

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
            if (self.game.contains(below_coords) or self.grid.contains(below_coords)):
                self.possible_solutions.append(node)
                return True
        return False

