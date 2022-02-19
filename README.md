# AI Tetris Bot

In this project, we developed an intelligent bot capable of playing one of the most popular classic games: **Tetris**.

We used a **breadth-first alpha-beta pruning search algorithm** to seek for both solution optimality and time efficiency, as the game gets faster and faster over time..

Besides the alpha-beta pruning search algorithm, which is a variant of the minimax algorithm made to evaluate less nodes in a search tree, we also implemented **look-ahead** to plan the solutions of the next three tetrominoes (pieces) to find the best moves.

The code implemented for this project is inside the *student.py* and *search.py* files.
