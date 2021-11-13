# Notas sobre o projeto

## shapes.py

Contem todos os tipos de formas

Um Shape() tem um atributo de entrada (plan) que é o tipo da forma, um de rotação da peça (começa a 0), uma subclasse Dimensions com x=5 e y=5. Os atributos privados 'x' e 'y' começam ambos a 0 e chama-se o metodo rotate().

O rotate() tem um parametro de entrada (step = numero de pedidos de rotação da peça).

self.rotation = (self.rotation + step) % len(self.plan):

Se a peça for o quadrado, este sempre que rodar fica exatamente na mesma posição, a len(self.plan) dele é 1, portanto o self.rotation vai ser sempre o mesmo.

No caso do 'I', este tanto pode ficar na horizontal como na vertical, por isso o seu len(self.plan) é 2 e ele pode ter 2 valores possiveis para o self.rotation. Por aí adiante para o T (4), Z (2), S(2).

O shape 'I' tem duas listas, uma para cada representação possível.

O enumerate() é um metodo que retorna, numa lista, os tuplos com (indice do elemento, elemento)

Exemplo:

lista = [a,b,c]

```
>>> for count, value in enumerate(lista):
...     print(count, value)
...
0 a
1 b
2 c
```

Assim, o self.plan[self.rotation] vai retornar a forma na posição especificada.

O y vai ser sempre igual e o line vai ser o valor que queremos (a lista da forma na posição devida).

O enumerate(line) faz o mesmo mas percorre cada pixel da lista e se for igual a 1, ou seja, se tiver um bloco preenchido, então guarda no self.positions a posição atual do x e do y incrementado com os valores de x e y que tem '1'. Ou seja, o rotate() atualiza toda a posição atual da forma consoante o numero de rotações pedidos, atualizando o self.positions.

O translate(x,y) vai pegar no x=shift e no y=0 e vai estabelecer a nova posição ao invocar o set_pos(x,y).

O set_pos(x,y) vai guardar o novo valor de x,y da peça e vai atualizar o self.positions consoante o shift dado.

## game.py

Construtor tem os parâmetros: x (default 10), y (default 30)

O que é o dimensions?

collections.namedtuple(*typename*, *field_names*)

Returns a new tuple subclass named *typename*. The new subclass is used to create tuple-like objects that have fields accessible by attribute lookup as well as being indexable and iterable. (in this case 'x' and 'y' attributes)

No inicio a current_piece é None e o self.next_pieces vai obter 3 random shapes da lista SHAPES.

Self.bottom: preenche a ultima linha (y=30) com valores de 0 ate x

Self.lateral: Preenche a primeira coluna (com x=0 e 0<=y<=30).

self.lateral.extend(): Preenche a ultima coluna (x=30 e 0<=y<=30)

self.grid é o resultado da soma das duas listas anteriores, formando uma grid 10x30.

metodo info(): retorna informação sobre a grid (self.grid), a peça atual (self.current_piece.positions), as proximas peças e a velocidade do jogo.

metodo clear_rows():

permite eliminar linhas quando estas são todas preenchidas.

Percorre cada linha no self.game em pares de tuplos ('1',8),('.',2).

Se o count for igual a len(self.bottom) - 2: a linha deve ser eliminada e todas acima devem ser "dropadas".

Quando as linhas são eliminadas, a velocidade do jogo aumenta.

método loop():

aqui é onde vai correr o jogo.

Tem um tempo de espera entre cada tempo do jogo (1/game_speed).

Se a peça atual n existir: retira-se a primeira da lista de peças seguintes e adiciona-se uma nova

A posição desta peça é sempre centrada no x e com y=0 (inicio)

Se a peça n for valida no inicio, é porque já fez stack até ao final e o jogo acaba.

A cada iteração o y da peça aumenta (current_piece.y).

Depois do y ser reduzido, verifica-se se a peça é valida ou não.

Se for valid, é porque ainda não chegou ao chão. Se o 's' for pressionado, a peça vai descendo rapido. Se for 'w', é para fazer o rotate. Se for 'a' ou 'd', é para deslocar-se para a esquerda ou direita, respetivamente. Convém mencionar que o collide_lateral() verifica se a peça está a colidir com uma das margens, corrigindo a posição se necessário. Também se verifica se está a colidir lateralmente com outras peças

 Se não for valid, é porque chegou ao chão. O self.game é atualizado com a posição da peça que foi encaixada, verifica-se se há linhas que podem ser eliminadas e a peça atual volta a ser None, pronto para ser outra peça a entrar no jogo.
