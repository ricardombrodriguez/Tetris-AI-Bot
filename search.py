from collections import Counter
from copy import copy
import time
from shape import *
import time

class Solution:

    def __init__(self, shape):

        self.shape = shape

class Search:

    def __init__(self, state, initial_info, shapes, variables, shapes_keys): 

        # inicializaçao dos dados obtidos do servidor e chamados do student.py
        
        self.game = {(tup[0],tup[1]) for tup in state['game']}
        self.grid = {(tup[0],tup[1]) for tup in initial_info['grid']}
        self.game_speed = state['game_speed']
        self.shapes_keys = shapes_keys

        self.A, self.B, self.C, self.D = variables[0], variables[1], variables[2], variables[3]
        self.x = max(self.grid, key = lambda coord : coord[0])[0] + 1
        self.y = max(self.grid, key = lambda coord : coord[1])[1]

        self.shapes = shapes
        for shape in self.shapes:
            shape.set_pos((self.x - shape.dimensions.x) / 2, 0) 

        self.best_solution = None
        self.best_nodes = [] 


    # Breadth-first
    def search(self, solutions=[]):

        iteration = 0 if not solutions else len(solutions)
        best_nodes = []

        if iteration < len(self.shapes):

            for rot in range(0, len(self.shapes[iteration].plan)):
                
                piece = copy(self.shapes[iteration])
                piece.rotate(rot)
                name = piece.name + str(rot)

                for keys in self.shapes_keys[name]:

                    keys = [*keys]  

                    solution = Solution(copy(self.shapes[iteration]))
                    solution.keys = [*keys]
                    solution.solutions = [*solutions]

                    valid_solution = False
                    while self.valid(solution): # simulaçao do jogo com as soluçoes validas

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
                        solution.heuristic = (self.checkHeight(solution) * self.A) + (self.checkBumpiness(solution) * self.B) + (self.checkHoles(solution)* self.C) + (self.checkScore(solution) * self.D)

                        best_nodes.append(solution)

                        if len(solution.solutions) == len(self.shapes):

                            solution.heuristic = sum([sol.heuristic for sol in solution.solutions])                            
                            self.best_nodes.append(solution) 

            
            if len(solution.solutions) != len(self.shapes):  

                #lookahead 3
                if self.game_speed <= 15:
                    max_nodes = 2  # todos
                elif self.game_speed > 15:
                    max_nodes = 1
            
                
                best_nodes = sorted(best_nodes, key=lambda node: node.heuristic, reverse=True)[:max_nodes]
                [self.search(node.solutions) for node in best_nodes]
            
            if not solutions and len(self.best_nodes) != 0:
                self.best_solution = max(self.best_nodes, key = lambda sol : sol.heuristic)


    def valid(self, solution): 
        
        game = solution.solutions[-1].game if solution.solutions else self.game
        return not any(
            {piece_part in self.grid for piece_part in solution.shape.positions}
        ) and not any(
            {piece_part in game for piece_part in solution.shape.positions}
        )


    def checkHeight(self, solution): # soma da altura de todas as colunas do jogo
        aggregate_height = 0

        for x in range(1, self.x-1):
            column_coords = {coord for coord in solution.game if coord[0] == x}
            aggregate_height += self.y - min(column_coords, key = lambda coord: coord[1], default = (0,self.y-1))[1]
        return aggregate_height


    def checkBumpiness(self,solution):  # verifica a diferença de altura de uma coluna com a sua seguinte, nao queremos que seja muito diferente senao significa que está a fazer "torres"
        bumpiness = 0
        
        for x in range(1, self.x-2):

            this_column_coords = {coord for coord in solution.game if coord[0] == x}
            next_column_coords = {coord for coord in solution.game if coord[0] == x+1}
        
            this_height = min(this_column_coords, key = lambda coord: coord[1], default = (0,self.y))[1]  # descobre o topo da coluna
            next_height = min(next_column_coords, key = lambda coord: coord[1], default = (0,self.y))[1]  # descobre o topo da coluna

            absolute_difference = abs(next_height - this_height)
            
            if absolute_difference > 6:
                bumpiness += absolute_difference * 10 
            else:
                bumpiness += absolute_difference 
            

        return bumpiness


    def checkHoles(self, solution): # verifica os buracos deixados no jogo pela colocaçao das peças, queremos o mínimo de buracos possivel

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
                        hole_weight += 1
        
        return hole_weight


    def checkScore(self, solution): # score é atualizado sempre que uma linha inteira é completada

        lines = 0
        
        for item, count in Counter(y for _, y in solution.game).most_common():
            if count == self.x - 2:
                solution.game = {(x, y) for (x, y) in solution.game if y != item}  # remove row
                solution.game = {(x, y + 1) if y < item else (x, y) for (x, y) in solution.game}
                lines += 1

        return lines