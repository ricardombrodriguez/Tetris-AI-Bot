from collections import Counter
from copy import copy
from shape import *

# uma das soluções
class Solution:

    def __init__(self, shape, heuristic): 

        self.shape = shape
        self.keys = []
        self.heuristic = heuristic


class Search:

    def __init__(self, state, shape, initial_info, next_shapes): 

        self.game = set()
        for tup in state['game']:
            self.game.add((tup[0], tup[1]))
        
        self.coords = state['piece']  

        self.grid = set()
        for coord in initial_info['grid']:
           self.grid.add((coord[0], coord[1]))

        self.x = max(self.grid, key = lambda coord : coord[0])[0] + 1
        self.y = max(self.grid, key = lambda coord : coord[1])[1]

        self.shape = shape 
        self.shape.set_pos((self.x - self.shape.dimensions.x) / 2, 0) 
        
        self.next_shapes = next_shapes
        for next_shape in next_shapes:
            next_shape.set_pos((self.x - self.shape.dimensions.x) / 2, 0) 
        
        self.solution = None
        self.heuristic = 0


    def search(self, shape=None, sol=None):
    
        # print("Begin shape")
        # print(self.shape)
        # print("Next shapes:", self.next_shapes)

        # faz todas as hipoteses e retorna melhor solution para aquela shape ou num universo perfeito a melhor soluçao da soma de todas as peças

        while self.next_shapes != []:
            for rot in range(0, len(self.shape.plan)):
        
                original = Solution(copy(self.shape), self.heuristic)
                original.shape.rotate(rot)
                
                # para calcular o numero de keys para chegar a uma determinada coluna
                min_x = min(original.shape.positions, key=lambda coords: coords[0])[0]
                max_x = max(original.shape.positions, key=lambda coords: coords[0])[0]

                # percorrer colunas [1,8]
                for x in range(1, self.x-1):

                    x_differential = x - min_x

                    # dispensa soluções não válidas
                    if (x_differential + max_x >= self.x - 1):
                        break

                    keys = []

                    keys += ["w"]*rot

                    if x_differential < 0:
                        keys += ["a"]*abs(x_differential)
                    elif x_differential > 0:
                        keys += ["d"]*abs(x_differential)

                    # depois de obter as keys, a ultima é sempre o "s"
                    keys += ["s"]

                    # obter a shape com o estado inicial
                    solution = Solution(copy(self.shape), self.heuristic)

                    # guardar as keys para chegar ao estado especifico dessa solução
                    solution.keys = [*keys]
                    
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
                            shift = -1

                        elif key == "d":
                            shift = +1

                        if key in ["a", "d"]:
                            solution.shape.translate(shift, 0)
                        
                        if not keys:
                            break
                        

                    solution.game = set(self.game).union(set(solution.shape.positions))


                    if self.biggestHeight(solution) > 15:
                        solution.heuristic += (-1.02 * self.checkLowestSolution(solution) + self.checkHeight(solution) * -0.710066) + (self.checkBumpiness(solution) * -0.784483) + (self.checkHoles(solution)* - 0.35663) + (self.checkScore(solution) * 0.855)
                    else:
                        solution.heuristic += (self.checkHeight(solution) * -0.510066) + (self.checkBumpiness(solution) * -0.184483) + (self.checkHoles(solution)* -0.35663) + (self.checkScore(solution) * 0.555)

                    #solution.heuristic = (self.checkHeight(solution) * -0.510066) + (self.checkBumpiness(solution) * -0.184483) + (self.checkHoles(solution)* -0.35663) + (self.checkScore(solution) * 0.555)
                    #solution.heuristic = (self.checkHeight(solution) * -0.798752914564018) + (self.checkBumpiness(solution) * -0.164626498034284) + (self.checkHoles(solution)* -0.24921408023878) + (self.checkScore(solution) * 0.522287506868767)
                    
                    self.solution = max([self.solution, solution], key = lambda x : x.heuristic) if self.solution else solution

            #print("End shape")
            new_solution = copy(solution.heuristic)
            self.search(self.next_shapes.pop(0), new_solution)
        else:
            pass

        # para cada shape ele calcula uma solution q vai ser a melhor, com lookahead ele tem de calcular essa solution da peça 1
        # e depois calcular as solutions da 2º peça e ver qual é a melhor combinaçao entre 1º + 2º peça e o mm p 3ª
    
        # AINDA N TA A FAZWER NADA fds
                            
                
                    
    
    def biggestHeight(self,solution):
        return self.y - min(list(solution.game), key = lambda coord : coord[1])[1]

    def valid(self, solution):
        
        return not any(
            {piece_part in self.grid for piece_part in solution.shape.positions}
        ) and not any(
            {piece_part in self.game for piece_part in solution.shape.positions}
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
            
            # if absolute_difference > 4:
            #     absolute_difference *= 50
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