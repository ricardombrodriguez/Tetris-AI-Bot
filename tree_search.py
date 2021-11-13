
actions = ["w","a","s","d"]


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

    def __init__(self,coordinates,score,keys,average_height,bumpiness,hole_weight): 
        self.coordinates = coordinates
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

    def search(self):

        while self.open_nodes != []:

            node = self.open_nodes.pop(0)

            lastNode = self.chechMoreActions(node)

            # Calcular aquelas variaveis todas (score, bumpiness e isso tudo)
            # if lastNode:

                # Guardar coordenadas onde a peça repousa
                

                # Guardar o score obtido pela colocação dessa peça (ou linhas eliminadas)


                # A altura média do jogo depois de colocar essa peças


                # A pontuação do peso dos buracos depois da solução


                # A pontuação 'bumpiness' que calcula a diferença de altura em colunas adjacentes à solução


                # As 'keys' necessárias (em array) para chegar às coordenadas da solução

            # Caso contrário, ainda dá para expandir este nó em mais possibilidades:

            newnodes = []   #Novos nós que vão ser adicionados
            for key in actions:
            
                
                # para cada ação possível, fazer as alterações
                if self.valid(self.current_piece):
                    if key == "s":
                        while self.valid(self.current_piece):
                            self.current_piece.y +=1
                        self.current_piece.y -= 1
                    elif key == "w":
                        self.current_piece.rotate()
                        if not self.valid(self.current_piece):
                            self.current_piece.rotate(-1)
                    elif key == "a":
                        shift = -1
                    elif key == "d":
                        shift = +1

                    if self._lastkeypress in ["a", "d"]:
                        self.current_piece.translate(shift, 0)
                        if self.collide_lateral(self.current_piece):
                            self.current_piece.translate(-shift, 0)
                        elif not self.valid(self.current_piece):
                            self.current_piece.translate(-shift, 0) 


            """

                
                    #coordinates,score,keys,average_height,bumpiness,hole_weight
                    newnode = SearchNode(newstate,node,node.depth+1, node.cost + self.problem.domain.cost(node.state,(node.state,newstate)))
                    newnode.heuristic = self.problem.domain.heuristic(newnode.state,self.problem.goal)

                

            self.open_nodes.extend(newnodes)
            #self.open_nodes.sort(key=lambda x: x.heuristic + x.cost)
            """

        return None

    def valid(self, piece):
        return not any(
            [piece_part in self.grid for piece_part in piece.positions]
        ) and not any(
            [piece_part in self.game for piece_part in piece.positions]
        )

    
    # Verificar se existe algum bloco ocupado em baixo dele, o que significa que acabou e é uma das soluções
    def checkMoreActions(self,node):
        for coords in node.coords:
                below_coords = (coords[0], coords[1]-1)
                if (self.game.contains(below_coords)):
                    print("Open node!")
                    self.possible_solutions.append(node)
                    return True
        return False

