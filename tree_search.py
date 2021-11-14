
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

class SearchNode:

    def __init__(self,shape,score,keys,average_height,bumpiness,hole_weight):
        self.shape = shape  # copia da instância do shape pai (tem coordenadas e isso tudo)
        self.score = score
        self.keys = keys
        self.average_height = average_height
        self.bumpiness = bumpiness
        self.hole_weight = hole_weight


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
        root = SearchNode(state['piece'], 0, [], 0, 0, 0)
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

            # check if valid
            # isValid = self.isValid(node)
            lastNode = self.checkMoreActions(node)

            # Calcular aquelas variaveis todas (score, bumpiness e isso tudo)
            # if lastNode and isValid:

                # Guardar coordenadas onde a peça repousa
                

                # Guardar o score obtido pela colocação dessa peça (ou linhas eliminadas)


                # A altura média do jogo depois de colocar essa peças


                # A pontuação do peso dos buracos depois da solução


                # A pontuação 'bumpiness' que calcula a diferença de altura em colunas adjacentes à solução


                # As 'keys' necessárias (em array) para chegar às coordenadas da solução



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

                # maybe calcular a heuristica do newnode aqui!!!

            self.open_nodes.extend(newnodes)
            #self.open_nodes.sort(key=lambda x: x.heuristic + x.cost)

        return None

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
    def checkMoreActions(self,node):
        for coords in node.shape.positions:
                below_coords = [coords[0], coords[1]-1]
                if (below_coords in self.game):
                    print("Open node!")
                    self.possible_solutions.append(node)
                    return True
        return False

