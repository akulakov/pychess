Making a Chess game with Python
---

This guide will show how to make a simple chess implementation in Python.

I will start by making a game board, a few game pieces and allowing them to move according to the
chess rules.

The complete source code (about 600 lines) is here: chess.py

I will also use a class that represents a location on the game board.

Before adding the board class, I will have a few variables for white and black sides, and a
character representing an empty board tile:


```python
WHITE = 'White'
BLACK = 'Black'
blank = '.'
```

And next the Board class and a helper function to create rows:

```python
def row(size):
    return [blank] * size

class Board:
    def __init__(self, size):
        self.b = [row(size) for _ in range(size)]
        self.size = size

    def display(self):
        for r in self.b:
            yield ' ' + ' '.join(str(a) for a in r)

    def __setitem__(self, loc, item):
        self.b[loc.y][loc.x] = item
```

I will start by making a small 3x3 board and displaying it:

```python
b = Board(3)
for row in b.display():
    print(row)
```

It should display:

    . . .
    . . .
    . . .

I will need a Piece class that will have shared logic for all pieces:

```python
class Piece:
    def __init__(self, board, color, loc, dir=None):
        self.loc = loc
        self.board = board
        self.orig_location = True
        self.color = color
        self.dir = dir

def __repr__(self):
    return self.char if self.color==WHITE else piece_chars[self.char]
```

The `dir` attribute is only used by pawns, but it was a bit more convenient to add it to this
class.  The `orig_location` is used by pawns (for the two-space jump) and rooks and the king --
for castling.

I will add `piece_chars` dictionary a bit later for black pieces.

Pieces will use the location objects to keep track of their place:

```python
class Loc:
    def __init__(self, x, y):
        if isinstance(x, str):
            self.x = 'abcdefgh'.index(x)
            self.y = y - 1
        else:
            self.x, self.y = x,y

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self):
        x = 'abcdefgh'[self.x]
        return f'<{x}{self.y+1}>'
```

Location class makes it a bit more convenient to add locations using standard chess notation.
The `__iter__` method yield two values that can be assigned to x,y variables: `x,y = location`.

```python
class Pawn(Piece):
    char = '♙'

board[Loc(0,0)] = Pawn()
```

To print the board to the terminal, I will use a small helper function:

```python
def print_board(self):
    print(' ' + ' '.join('abcdefgh'))
    for r in reversed(list(self.board.display())):
        print(r)
```

I'm reversing the order of rows so that first row starts on the bottom, the way chess boards
are usually displayed. Row numbers can be easily added on the side if you prefer.

I will now add the ability for the pawn to move by adding a new `Move` class that will keep
record of the piece, the target location and value of the move:


```python
class Move:
    def __init__(self, piece, loc, val=0, related=None, en_passant=False, en_passant_capture=False):
        self.piece, self.loc, self.val = piece, loc, val
        self.related = related
        self.en_passant = en_passant
        self.en_passant_capture = en_passant_capture

    def __repr__(self):
        return f'<M {repr(self.loc)[1:-1]}>'

    def do_move(self):
        self.piece.move(self)
```

I will explain various attributes later in the tutorial. At the very least, a move requires the
piece and the target location `loc`.

I will add three methods related to moves: `piece.moves()` returns possible moves;
`piece.move()` performs the move, and `board.move()` makes the move happen on the board:

```python
# Board
def move(self, move):
    a, b = move.piece.loc, move.loc
    self[b] = self[a]
    self[a] = blank
    move.piece.loc = b

# Piece
def move(self, move):
    self.board.move(move)
    self.orig_location = False
```

The `orig_location` is set to `False` to signal that the piece can no longer do special moves
that require original placement location, like pawns being on the 2nd row.

```python
# Loc
def modified(self, x=None, y=None):
    l = Loc(*self)
    if x:
        l.x += x
    if y:
        l.y += y
    return l

# Pawn
def moves(self):
    new = self.loc.modified(y=1)
    return [Move(self, new)]
```

The pawn is moving up one square, which means on the XY coordinates, the `x` will stay the same
and the `y` will be increased by 1. To make this sort of modifications more convenient, I'm
adding the `modified()` method that creates and returns a new location object.

I can now display the board, move the pawn and display it again:

```python
print_board()
move = pawn.moves()[0]
move.do_move()
print_board()
```
    a b c
    . . .
    . . .
    ♙ . .

    a b c
    . . .
    ♙ . .
    . . .

Now we can look at the three pieces that have similar moves: a Rook, a Bishop and a Queen.
Notice how the moves are in a straight line until the end of the board, a friendly or an
opposing piece.

Starting with a Rook, we can see that four move directions can be represented by x and y
modifiers, with four tuples for four cardinal directions:


```python
piece_moves = {
    'Rook': [
            (1, 0), (-1, 0),
            (0, 1), (0, -1)
            ],
}
```

If this doesn't look clear enough, you can also represent directional modifiers with named
variables like so:

```python
class Dir:
    right = 1, 0
    up = 0, 1
    ...
'Rook': [Dir.right, Dir.up, Dir.left, Dir.down]
```

I've used modifier tuples however, and I kept move modifer tuples for all pieces in the same
structure, to keep logic and data nicely separated:

```python
piece_moves = {
    'Knight': [
        (2, 1),
        (2, -1),
        (-2, 1),
        (-2, -1),
        (1, 2),
        (1, -2),
        (-1, 2),
        (-1, -2),
    ],

    'Rook': [
            (1, 0), (-1, 0),
            (0, 1), (0, -1)
            ],

    'King': [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1)
    ],

    'Queen': [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1)
    ],

    'Bishop': [
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1)
        ],
}
```

Bishop, Queen and Rook moves are so similar that they can be done in the same method that will
live in the `Piece` class.

But first I will need to add a method that creates a "line" of moves radiating from the current
piece position. For example, Rook moves will be generated by creating four "lines" of moves in
four cardinal directions:

```python
# Board
def is_valid(self, l):
    return 0 <= l.x < self.size and 0<=l.y<self.size

def empty(self, loc):
    return self[loc]==blank

def get_loc_val(self, loc):
    pc = self[loc]
    if self.empty(loc):
        return 0
    elif isinstance(pc, King):
        # this is only needed when calculating opponent_moves to determine if we are in check
        return 999
    else:
        return piece_values[self[loc].__class__]

def line(self, piece, loc, mod, color, include_defense=False):
    lst = []
    color = self[loc].color
    while 1:
        loc = loc.modified(*mod)
        if not self.is_valid(loc):
            break
        if not self.empty(loc):
            if include_defense or color != self[loc].color:
                lst.append(Move(piece, loc, self.get_loc_val(loc)))     # capture move
            break
        else:
            lst.append(Move(piece, loc))
    return lst
```

A few things to explain here: `include_defense` can be set to include pseudo-moves that defend
our own pieces; this is useful when calculating opponent moves because the opponent may not
want to capture pieces that are defended.

Calculating values of moves that capture pieces relies on this lookup table:

```python
piece_values = {
    Pawn: 1,
    Bishop: 3,
    Knight: 3,
    Rook: 5,
    Queen: 9,
}
```

And finally we can have the `moves()` method that works like a charm for the Rooks, Bishops and
the Queen:

```python
import itertools

def chain(lst):
    return itertools.chain(*lst)

# Piece
def moves(self, include_defense=False):
    mods = piece_moves[self.__class__.__name__]
    return chain(self.line(mod, include_defense=include_defense) for mod in mods)
```


