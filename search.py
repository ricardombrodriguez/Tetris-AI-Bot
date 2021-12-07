from collections import Counter
from copy import copy
from shape import *

# uma das soluções
class Solution:

    def __init__(self, shape): 

        self.shape = shape

class Search:

    def __init__(self, state, initial_info, shapes): 

        self.game = set()
        for tup in state['game']:
            self.game.add((tup[0], tup[1]))
        
        self.coords = state['piece']  

        self.grid = set()
        for coord in initial_info['grid']:
           self.grid.add((coord[0], coord[1]))

        self.x = max(self.grid, key = lambda coord : coord[0])[0] + 1
        self.y = max(self.grid, key = lambda coord : coord[1])[1]

        self.shapes = shapes
        for shape in self.shapes:
            shape.set_pos((self.x - shape.dimensions.x) / 2, 0) 

        self.solutions = None

        self.iter = 0

        print(self.shapes[0])
        print(self.shapes[1])

    # solutions -> array de soluções-pai
    def search(self, solutions=[]):

        iteration = 0 if not solutions else len(solutions)  # numero da peça que estamos a ver agora
        print(iteration)

        for rot in range(0, len(self.shapes[iteration].plan)):

            print("rotação", rot)

            piece = copy(self.shapes[iteration])
            piece.rotate(rot)
            
            # para calcular o numero de keys para chegar a uma determinada coluna
            min_x = min(piece.positions, key=lambda coords: coords[0])[0]
            max_x = max(piece.positions, key=lambda coords: coords[0])[0]

            # percorrer colunas [1,8]
            for x in range(1, self.x-1):

                print("x: ", x)

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
                        shift = -1

                    elif key == "d":
                        shift = +1

                    if key in ["a", "d"]:
                        solution.shape.translate(shift, 0)
                    
                    if not keys:
                        valid_solution = True
                        break
                    
                if valid_solution:

                    last_solution_game = solutions[-1].game if solutions else self.game
                    """
                    print("last solution:")
                    print(last_solution_game)
                    """
                    solution.game = set(last_solution_game).union(set(solution.shape.positions))
                    """
                    print("now:")
                    print(solution.game)
                    print()
                    """
                    solution.score = self.checkScore(solution)

                    solution.solutions.append(solution)

                    if len(solution.solutions) == len(self.shapes):
                        # acabou, ver as heuristicas todas

                        #print("ACABOU!!!!!")

                        #sum_rows = sum([self.checkScore(sol) for sol in solution.solutions])
                        #solution.heuristic = (self.checkHeight(solution) * -0.510066) + (self.checkBumpiness(solution) * -0.184483) + (self.checkHoles(solution)* -0.35663) + (self.checkScore(solution) * 0.555)
                        solution.heuristic = sum([self.checkHeight(sol) * -0.510066 + self.checkBumpiness(sol) * -0.184483 + \
                                                  self.checkHoles(sol)* -0.35663 + self.checkScore(sol) * 0.555 \
                                                  for sol in solution.solutions])
                        self.solution = max([self.solutions, solution], key = lambda sol : sol.heuristic ) if self.solutions else solution
                    else:
                        print("===")
                        self.search(solution.solutions)


    def biggestHeight(self,solution):
        return self.y - min(list(solution.game), key = lambda coord : coord[1])[1]


    def valid(self, solution):
        game = solution.solutions[-1].game if solution.solutions else self.game
        return not any(
            {piece_part in self.grid for piece_part in solution.shape.positions}
        ) and not any(
            {piece_part in game for piece_part in solution.shape.positions}
        )
        
    def next_valid(self, game, solution):
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