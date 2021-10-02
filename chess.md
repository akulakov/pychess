Making a Chess game with Python
---

This guide will show how to make a simple chess implementation in Python.

I will start by making a game board, a few game pieces and allowing them to move according to the
chess rules.

The complete source code (about 600 lines) is here: chess.py

I will also use a class that represents a location on the game board.

Before adding the board class, I will have a few variables for white and black sides, and a
character representing an empty board tile:


    WHITE = 'White'
    BLACK = 'Black'
    blank = '.'

And next the Board class and a helper function to create rows:

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

I will start by making a small 3x3 board and displaying it:

    b = Board(3)
    for row in b.display():
        print(row)

It should display:

    . . .
    . . .
    . . .

I will need a Piece class that will have shared logic for all pieces:

    class Piece:
        def __init__(self, board, color, loc, dir=None):
            self.loc = loc
            self.board = board
            self.orig_location = True
            self.color = color
            self.dir = dir

    def __repr__(self):
        return self.char if self.color==WHITE else piece_chars[self.char]

The `dir` attribute is only used by pawns, but it was a bit more convenient to add it to this
class.  The `orig_location` is used by pawns (for the two-space jump) and rooks and the king --
for castling.

I will add `piece_chars` dictionary a bit later for black pieces.

Pieces will use the location objects to keep track of their place:

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

Location class makes it a bit more convenient to add locations using standard chess notation.
The `__iter__` method makes it possible to get x,y values: `x,y = location`.

    class Pawn(Piece):
        char = '♙'

    board[Loc(0,0)] = Pawn()

To print the board to the terminal, I will use a small helper function:

    def print_board(self):
        print(' ' + ' '.join('abcdefgh'))
        for r in reversed(list(self.board.display())):
            print(r)

