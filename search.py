from collections import Counter
from copy import copy
from shape import *

import math

# uma das soluções
class Solution:

    def __init__(self, shape):

        self.shape = shape

class Search:

    def __init__(self, state, initial_info, shapes): 

        self.game = {(tup[0],tup[1]) for tup in state['game']}
        self.grid = {(tup[0],tup[1]) for tup in initial_info['grid']}

        self.x = max(self.grid, key = lambda coord : coord[0])[0] + 1
        self.y = max(self.grid, key = lambda coord : coord[1])[1]

        self.shapes = shapes
        for shape in self.shapes:
            shape.set_pos((self.x - shape.dimensions.x) / 2, 0) 
            print(shape)

        self.best_solution = None
        self.iter = 0

        self.best_nodes = []    # soluções finais
        self.max_nodes = 5

    # Breadth-first
    def search(self, solutions=[]):

        iteration = 0 if not solutions else len(solutions)  # numero da peça que estamos a ver agora

        best_nodes = []

        for rot in range(0, len(self.shapes[iteration].plan)):
            
            piece = copy(self.shapes[iteration])
            piece.rotate(rot)
            
            # para calcular o numero de keys para chegar a uma determinada coluna
            min_x = min(piece.positions, key=lambda coords: coords[0])[0]
            max_x = max(piece.positions, key=lambda coords: coords[0])[0]

            # percorrer colunas [1,8]
            for x in range(1, self.x-1):
                
                x_differential = x - min_x

                # dispensa soluções não válidas
                if (x_differential + max_x >= self.x - 1):
                    break

                keys = ["w"]*rot

                # keys += ["a"]*abs(x_differential) + ["s"] if x_differential > 0 else ["d"]*(abs(x_differential)+1) + ["s"]
                keys += ["a"]*abs(x_differential) + ["s"] if x_differential > 0 else ["d"]*abs(x_differential) + ["s"]
                
                # obter a shape com o estado inicial
                solution = Solution(copy(self.shapes[iteration]))

                # guardar as keys para chegar ao estado especifico dessa solução
                solution.keys = [*keys]
                solution.solutions = [*solutions]

                valid_solution = False
                while self.valid(solution):

                    solution.shape.y += 1

                    key = keys.pop(0)
                                                
                    if key == "s":
                        while self.valid(solution):
                            solution.shape.y +=1
                            
                        solution.shape.y -= 1

                    elif key == "w":
                        solution.shape.rotate()

                    elif key == "a":
                        solution.shape.translate(-1, 0)

                    elif key == "d":
                        solution.shape.translate(+1, 0)
                    
                    if not keys:
                        valid_solution = True
                        break
                    
                if valid_solution:
                
                    last_solution_game = solutions[-1].game if solutions else self.game
                    solution.game = set(last_solution_game).union(set(solution.shape.positions))
                    
                    solution.solutions.append(solution)
                    solution.heuristic = self.checkHeight(solution) * -0.510066 + self.checkBumpiness(solution) * -0.184483 + self.checkHoles(solution)* -0.35663 + self.checkScore(solution) * 0.555 
                    best_nodes.append(solution)
                    
                    self.iter += 1

                    if len(solution.solutions) == len(self.shapes):

                        all_heuristics = [ sol.heuristic for sol in solution.solutions]
                        solution.heuristic = sum(all_heuristics)
                        
                        # solution.heuristic = all_heuristics[0]
                        
                        print("AAAAAAAAAAAAAAAAAAAA", solution.keys)
                        print("A PUTA DA HEURISTICA", solution.heuristic)
                        print("CCCCCCCCCCCCCCCCCCCC", solution.shape)
                        print()
                        
                        self.best_nodes.append(solution)    # adicionar nó terminal à lista de soluções possíveis

        if len(solution.solutions) != len(self.shapes) - 1:   

            best_nodes = sorted(best_nodes, key=lambda node: node.heuristic, reverse=True)[:self.max_nodes]

            for node in best_nodes:
                """ print("AAAAAAAAAAAAAAAAAAAA", node.keys)
                print("BBBBBBBBBBBBBBBBBBBB", node.heuristic)
                print("CCCCCCCCCCCCCCCCCCCC", node.shape)
                print() """
                self.search(node.solutions)
        
        if not solutions:
            print("CALCULAR MELHOR SOLUÇÃO")
            self.best_solution = max(self.best_nodes, key = lambda sol : sol.heuristic)


    def biggestHeight(self,solution):
        return self.y - min(list(solution.game), key = lambda coord : coord[1])[1]
    
    def lowestHeight(self, solution):
        return self.y - max(list(solution.game), key = lambda coord : coord[1])[1]
    
    def distance(self, solution):
        return math.sqrt( self.biggestHeight(solution) - self.lowestHeight(solution) )


    def valid(self, solution):
        game = solution.solutions[-1].game if solution.solutions else self.game
        return not any(
            {piece_part in self.grid for piece_part in solution.shape.positions}
        ) and not any(
            {piece_part in game for piece_part in solution.shape.positions}
        )

    def checkLowestSolution(self, solution):
        average_height = 0
        
        for coord in solution.shape.positions:
            average_height += (self.y - coord[1])
            
        average_height /= len(solution.shape.positions)
        return average_height


    def checkHeight(self, solution):
        aggregate_height = 0

        for x in range(1, self.x-1):
            column_coords = {coord for coord in solution.game if coord[0] == x}
            aggregate_height += self.y - min(column_coords, key = lambda coord: coord[1], default = (0,self.y-1))[1]
            
        return aggregate_height


    def checkBumpiness(self,solution):
        bumpiness = 0
        
        for x in range(1, self.x-2):
            this_column_coords = set()
            next_column_coords = set()
            
            for coord in solution.game:
                if coord[0] == x:
                    this_column_coords.add(coord)
                elif coord[0] == x+1:
                    next_column_coords.add(coord)
            
            this_height = min(this_column_coords, key = lambda coord: coord[1], default = (0,self.y-1))[1]  # descobre o topo da coluna
            next_height = min(next_column_coords, key = lambda coord: coord[1], default = (0,self.y-1))[1]  # descobre o topo da coluna

            absolute_difference = abs(next_height - this_height)
            bumpiness += absolute_difference 

        return bumpiness


    def checkHoles(self, solution):
        hole_weight = 0
        height = self.y

        for x in range(1, self.x-1):
            column_coords = set()
            for coord in solution.game: 
                if coord[0] == x:
                    column_coords.add(coord)
            
            height = min(column_coords, key = lambda coord: coord[1], default = (0,self.y-1))[1]  # descobre o topo da coluna

            for y in range(height+1,self.y):
                if ((x,y) not in column_coords):
                        hole_weight += 2

        return hole_weight


    def checkScore(self, solution):
        lines = 0
        
        for item, count in Counter(y for _, y in solution.game).most_common():
            if count == self.x - 2:
                solution.game = {(x, y) for (x, y) in solution.game if y != item}  # remove row
                solution.game = {
                    (x, y + 1) if y < item else (x, y) for (x, y) in solution.game
                }
                lines += 1

        return lines