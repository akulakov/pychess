#!/usr/bin/env python3
from itertools import chain

WHITE = 1
BLACK = 2
blank = '.'

piece_chars = {
    '♖': '♜',
    '♔': '♚',
    '♘': '♞',
    '♙': '♟︎',
    '♗': '♝',
    '♕': '♛',
}

knight_moves = [
    (2, 1),
    (2, -1),
    (-2, 1),
    (-2, -1),
    (1, 2),
    (1, -2),
    (-1, 2),
    (-1, -2),
]

piece_moves = {
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

def row(size):
    return [blank] * size

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

    def __hash__(self):
        return hash(tuple(self))

    def __eq__(self, other):
        return isinstance(other, Loc) and tuple(other) == tuple(self)

    def modified(self, x=None, y=None):
        l = Loc(*self)
        if x:
            l.x += x
        if y:
            l.y += y
        return l

class Move:
    def __init__(self, loc, val=0):
        self.loc, self.val = loc, val

    def __hash__(self):
        return hash(self.loc)

    def __eq__(self, o):
        if isinstance(o, Move):
            return self.loc == o.loc

    def __repr__(self):
        return f'<M {repr(self.loc)[1:-1]}>'

class Board:
    def __init__(self, size):
        self.b = [row(size) for _ in range(size)]
        self.size = size

    def display(self):
        for r in self.b:
            yield ' ' + ' '.join(str(a) for a in r)

    def __getitem__(self, loc):
        return self.b[loc.y][loc.x]

    def __setitem__(self, loc, item):
        self.b[loc.y][loc.x] = item

    def move(self, a, b):
        self[b] = self[a]
        self[a] = blank

    def is_valid(self, l):
        return 0 <= l.x < self.size and 0<=l.y<self.size

    def remove_invalid(self, locs):
        return [l for l in locs if self.is_valid(l)]

    def remove_occupied(self, locs):
        locs = self.remove_invalid(locs)
        return [l for l in locs if self[l[1]]==blank]

    def empty(self, loc):
        return self[loc]==blank

    def line(self, loc, mod, color):
        lst = []
        color = self[loc].color
        while 1:
            loc = loc.modified(*mod)
            if not self.is_valid(loc):
                break
            if not self.empty(loc):
                if color != self[loc].color:
                    lst.append(Move(loc, self.get_loc_val(loc)))     # capture move
                break
            else:
                lst.append(Move(loc))
        return lst

    def add(self, piece_cls, color, loc):
        self[loc] = piece_cls(self, color, loc)
        return self[loc]

    def all_pieces(self, color, types):
        for r in self.b:
            for tile in r:
                if isinstance(tile, types) and tile.color==color:
                    yield tile

    def get_loc_val(self, loc):
        if self.empty(loc):
            return 0
        else:
            return piece_values[self[loc].__class__]

def x_col(color):
    return WHITE if color==BLACK else BLACK

def difference(a, b):
    b = get_locs(b)
    return [val for val in a if val[1] not in b]

class Piece:
    def __init__(self, board, color, loc):
        self.loc = loc
        self.board = board
        self.orig_location = True
        self.color = color

    def move(self, loc):
        self.board.move(self.loc, loc)
        self.orig_location = False

    def __repr__(self):
        return self.char if self.color==WHITE else piece_chars[self.char]

    def line(self, dir):
        return self.board.line(self.loc, dir, self.color)

    def remove_invalid(self, locs):
        B = self.board
        locs = B.remove_invalid(locs)
        return [l for l in locs if B.empty(l) or self.color != B[l].color]


class Bishop(Piece):
    char = '♗'

    def moves(self):
        return chain(self.line(mod) for mod in piece_moves['Bishop'])

class Rook(Piece):
    char = '♖'

    def moves(self):
        return chain(self.line(mod) for mod in piece_moves['Rook'])

class Queen(Piece):
    char = '♕'

    def moves(self):
        return chain(self.line(mod) for mod in piece_moves['Queen'])

class King(Piece):
    char = '♔'

    def moves(self):
        l = self.loc
        B = self.board
        lst = [l.modified(*mod) for mod in piece_moves['King']]
        lst = self.remove_invalid(lst)
        lst = [Move(l, B.get_loc_val(l)) for l in lst]

        opp_pc = B.all_pieces(x_col(self.color), (Knight, Bishop, Rook, Queen))
        opp_pawns = B.all_pieces(x_col(self.color), (Pawn,))
        opp_king = list(B.all_pieces(x_col(self.color), (King,)))[0]

        moves = chain(pc.moves() for pc in opp_pc)
        pwn_moves = chain(pwn.moves(attacking_only=True) for pwn in opp_pawns)
        # note I don't care about captures because those tiles are not available for me anyway
        king_moves = [opp_king.loc.modified(*mod) for mod in piece_moves['King']]
        king_moves = self.remove_invalid(king_moves)
        king_moves = [Move(m) for m in king_moves]

        unavailable = set(moves) | set(pwn_moves) | set(king_moves)

        if self.orig_location:
            lst = self.castling_moves(lst, unavailable)
        return list(set(lst) - unavailable)

    def castling_moves(self, lst, unavailable):
        a = Loc(0, self.loc.y)
        rook = self.board[a]
        isrook = isinstance(rook, Rook)
        line = self.line((-1,0))
        if not set(line) & unavailable:
            last = line[-1].loc.x
            if isrook and rook.orig_location and last==1:
                lst.append(Move(l.modified(-2,0)))

        b = Loc(7, self.loc.y)
        rook = self.board[a]
        isrook = isinstance(rook, Rook)
        line = self.line((1,0))
        if not set(line) & unavailable:
            last = line[-1].loc.x
            if isrook and rook.orig_location and last==6:
                lst.append(Move(l.modified(2,0)))
        return lst

def get_locs(moves):
    return set(m[1] for m in moves)

class Knight(Piece):
    char = '♘'

    def moves(self):
        B = self.board
        lst = [self.loc.modified(mod) for mod in knight_moves]
        lst = self.remove_invalid(lst)
        lst = [Move(l, B.get_loc_val(l)) for l in lst]
        return lst

class Pawn(Piece):
    char = '♙'
    dir = 1     # up board or down board

    def moves(self, attacking_only=False):
        l = self.loc
        B = self.board
        moves = []
        if not attacking_only:
            line = self.line((0, self.dir))
            if line:
                last = line[-1]
                if not B.empty(last.loc):
                    line.pop()
                moves.extend(line)

        lst = l.modified(1, self.dir), l.modified(-1, self.dir)
        lst = self.remove_invalid(lst)
        for l in lst:
            piece = B[l]
            if piece!=blank and B[l].color != self.color:
                moves.append(Move(l, get_loc_val(l)))
        return moves

piece_values = {
    Pawn: 1,
    Bishop: 3,
    Knight: 3,
    Rook: 5,
    Queen: 9,
}


if __name__ == "__main__":
    b = Board(5)
    loc = Loc('c',3)
    l2 = Loc('c',5)
    b.add(King, BLACK, l2)
    pc = b.add(King, WHITE, loc)
    print(' ' + ' '.join('abcde'))
    for r in reversed(list(b.display())):
        print(r)
    print("piece moves()", pc.moves())
