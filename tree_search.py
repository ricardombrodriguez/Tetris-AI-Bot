
# Nos de uma arvore de pesquisa
class SearchNode:
    def __init__(self,state,parent,depth,cost): 
        self.state = state
        self.parent = parent
        self.depth = depth
        self.cost = cost
        self.heuristic = 0

    # função para verificar se já passamos por esse nó
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

# Arvores de pesquisa
class SearchTree:

    # Construtor (coordenadas do 'game' e a peça atual)
    def __init__(self, game, piece): 
        root = SearchNode()
        self.open_nodes = [root]
        self.solution = None
        self.length = 0
        self.cost = None

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return(path)

    # procurar a solucao
    # verificar se um nó já faz parte da solução para prevenir um ciclo

    def search(self,limit = None):

        self.non_terminals = 0
        self.terminals = 0

        while self.open_nodes != []:

            node = self.open_nodes.pop(0)

            if self.problem.goal_test(node.state):
                self.solution = node
                self.length = self.solution.depth
                self.terminals = len(self.open_nodes) + 1
                self.avg_branching = round((self.non_terminals + self.terminals - 1) / self.non_terminals,2)
                self.cost = node.cost
                self.average_depth = sum(self.all_node_depth)/len(self.all_node_depth)
                return self.get_path(node)

            self.non_terminals += 1

            if limit and node.depth >= limit:
                continue
            
            lnewnodes = []
            for a in self.problem.domain.actions(node.state):
                
                newstate = self.problem.domain.result(node.state,a)
                newnode = SearchNode(newstate,node,node.depth+1, node.cost + self.problem.domain.cost(node.state,(node.state,newstate)))
                newnode.heuristic = self.problem.domain.heuristic(newnode.state,self.problem.goal)

                if (newnode.cost > self.highest_cost_nodes[0].cost):
                    self.highest_cost_nodes = [newnode]*5
                elif (newnode.cost == self.highest_cost_nodes[0].cost and newnode not in self.highest_cost_nodes):
                    self.highest_cost_nodes.append(newnode)
                    self.highest_cost_nodes = self.highest_cost_nodes[1:]
                if not node.in_parent(newstate):
                    lnewnodes.append(newnode)

                self.all_node_depth.append(newnode.depth)

            self.add_to_open(lnewnodes)

        return None

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
