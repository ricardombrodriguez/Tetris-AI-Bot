
"""
Nós de uma arvore de pesquisa (uma das n possíveis soluções)

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

    # função para verificar se já passamos por esse nó (pode dar jeito para evitar rotações repetidas!!!!!!!!)
    def in_parent(self, newstate):
        if self.state == newstate:
            return True
        if not self.parent:
            return False
        return self.parent.in_parent(newstate)

    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + ")"
    def __repr__(self):
        return str(self)

"""
Árvore de pesquisa para encontrar a melhor solução

self.state -> Estado do jogo (atributos 'game','piece','next_pieces' e 'game_speed')
self.shape -> Instância Shape da forma atual da 'piece'
self.solution -> Para guardar a solução (um SearchNode)
self.nodes -> Lista que guarda todas as soluções para depois ver qual é a melhor
"""

class SearchTree:

    # Construtor (recebe o parâmetro 'state' que tem toda a informação que precisamos para obter a melhor solução)
    def __init__(self, state, shape): 
        self.state = state      
        self.shape = shape  
        self.solution = None
        self.nodes = []

    """
    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return(path)
    """

    def search(self):

        possible_rotations = len(self.shape.plan)       # Guardar o número possíveis de rotação para esse shape

        # Nota: No 'game', a primeira coluna da grid começa no 1 e a ultima linha acaba na 29

        # Para cada rotação, verificar a solução por cada coluna
        for rotation in range(0,possible_rotations):

            # mudar o numero '10' para uma variavel qualquer que obtenha o nº de colunas
            for column in range(1,11):

                # Guardar coordenadas onde a peça repousa
                

                # Guardar o score obtido pela colocação dessa peça (ou linhas eliminadas)


                # A altura média do jogo depois de colocar essa peças


                # A pontuação do peso dos buracos depois da solução


                # A pontuação 'bumpiness' que calcula a diferença de altura em colunas adjacentes à solução


                # As 'keys' necessárias (em array) para chegar às coordenadas sa solução

                pass

        # Calcular a melhor solução
        self.solution = None
        return



    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
        if self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == 'depth':
            self.open_nodes[:0] = lnewnodes
        elif self.strategy == 'greedy':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda x: x.heuristic)
        elif self.strategy == 'uniform':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda x: x.cost)
        elif self.strategy == 'a*':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key=lambda x: x.heuristic + x.cost)
