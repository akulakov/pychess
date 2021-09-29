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

def x_col(color):
    return WHITE if color==BLACK else BLACK

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

    def is_adjacent(self, loc):
        return abs(self.x-loc.x)<=1 and abs(self.y-loc.y)<=1

    def between(self, loc):
        if self.x==loc.x:
            a, b = self.y, loc.y
            a, b = a, b if a<b else b, a
            return [Loc(self.x,y) for y in range(a+1,b+1)]
        if self.y==loc.y:
            a, b = self.x, loc.x
            a, b = a, b if a<b else b, a
            return [Loc(x,self.y) for x in range(a+1,b+1)]
        # diagonal
        a, b = self.x, loc.x
        a, b = a, b if a<b else b, a
        return [Loc(n,n) for n in range(a+1,b+1)]

class Move:
    def __init__(self, piece, loc, val=0):
        self.piece, self.loc, self.val = loc, val

    def __lt__(self, o):
        if not isinstance(o, Move):
            raise TypeError(f'{o} is not a move')
        return o.val < self.val

    def __hash__(self):
        return hash((self.piece, self.loc))

    def __eq__(self, o):
        if isinstance(o, Move):
            return self.loc==o.loc and self.piece is o.piece

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

    def move(self, move):
        a, b = move.piece.loc, move.loc
        self[b] = self[a]
        self[a] = blank
        move.piece.loc = b

    def is_valid(self, l):
        return 0 <= l.x < self.size and 0<=l.y<self.size

    def remove_invalid(self, locs):
        return [l for l in locs if self.is_valid(l)]

    def remove_occupied(self, locs):
        locs = self.remove_invalid(locs)
        return [l for l in locs if self[l[1]]==blank]

    def empty(self, loc):
        return self[loc]==blank

    def line(self, piece, loc, mod, color):
        lst = []
        color = self[loc].color
        while 1:
            loc = loc.modified(*mod)
            if not self.is_valid(loc):
                break
            if not self.empty(loc):
                if color != self[loc].color:
                    lst.append(Move(piece, loc, self.get_loc_val(loc)))     # capture move
                break
            else:
                lst.append(Move(piece, loc))
        return lst

    def add(self, piece_cls, color, loc):
        self[loc] = piece_cls(self, color, loc)
        return self[loc]

    def all_pieces(self, color, types=None):
        for r in self.b:
            for tile in r:
                if (types is None or isinstance(tile, types)) and tile.color==color:
                    yield tile

    def get_loc_val(self, loc):
        if self.empty(loc):
            return 0
        else:
            return piece_values[self[loc].__class__]

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
        return self.board.line(self, self.loc, dir, self.color)

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
                moves.append(Move(self, l, get_loc_val(l)))
        return moves

class Knight(Piece):
    char = '♘'

    def moves(self):
        B = self.board
        lst = [self.loc.modified(mod) for mod in knight_moves]
        lst = self.remove_invalid(lst)
        lst = [Move(self, l, B.get_loc_val(l)) for l in lst]
        return lst

from random import shuffle

class King(Piece):
    char = '♔'

    def all_moves(self, color, include_king=True):
        pc = B.all_pieces(color, (Knight, Bishop, Rook, Queen))
        pawns = B.all_pieces(color, (Pawn,))
        moves = chain(a.moves() for a in pc)
        pwn_moves = chain(pwn.moves() for pwn in pawns)
        all_moves = set(moves) | set(pwn_moves)
        if include_king:
            king = next(B.all_pieces(color, (King,)))
            all_moves |= self.get_king_moves(self)
        return all_moves

    def get_king_moves(self, king):
        king_moves = [king.loc.modified(*mod) for mod in piece_moves['King']]
        king_moves = king.remove_invalid(king_moves)
        king_moves = [Move(king, m) for m in king_moves]
        return set(king_moves)

    def opponent_moves(self):
        return self.all_moves(x_col(self.color))

    def in_check(self):
        checks = [m.loc for m in self.opponent_moves()]
        return [m for m in checks if m.loc==self.loc]

    def moves(self):
        l = self.loc
        B = self.board
        lst = [l.modified(*mod) for mod in piece_moves['King']]
        lst = self.remove_invalid(lst)
        lst = [Move(self, l, B.get_loc_val(l)) for l in lst]
        unavailable = self.opponent_moves()

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
                lst.append(Move(self, l.modified(-2,0)))

        b = Loc(7, self.loc.y)
        rook = self.board[a]
        isrook = isinstance(rook, Rook)
        line = self.line((1,0))
        if not set(line) & unavailable:
            last = line[-1].loc.x
            if isrook and rook.orig_location and last==6:
                lst.append(Move(self, l.modified(2,0)))
        return lst


class Chess:
    current = WHITE
    n = 0
    n_max = 300

    def __init__(self, board):
        self.board = board
        w_king = list(board.all_pieces(WHITE, (King,)))[0]
        b_king = list(board.all_pieces(BLACK, (King,)))[0]
        self.kings = {WHITE: w_king, BLACK: b_king}

    def handle_check(self, king, in_check, moves):
        """
        capture: single attacker, by any piece
        block: single attacker, not a knight, at least one tile between; any piece except for king
        king move: always
        -
        multi attack: only king move
        """
        # try capture
        if len(in_check) == 1:
            all_moves = self.all_moves(self.current)
            capture = [m for m in all_moves if m.loc==in_check[0].loc]
            if capture:
                return capture[0]

        # try block
        if len(in_check) == 1:
            ok = True
            if isinstance(in_check[0].piece, Knight):
                ok = False
            if self.loc.is_adjacent(in_check[0].loc):
                ok = False
            if ok:
                all_moves = self.all_moves(self.current, include_king=False)
                blocking = set(self.loc.between(in_check[0].loc))
                blocking = [m for m in all_moves if m.loc in blocking]
                if blocking:
                    return blocking[0]

        # only king moves left
        k_moves = king.moves()
        if k_moves:
            return k_moves[0]
        else:
            curc = 'White' if current==WHITE else 'Black'
            print(f'{curc} is checkmated')
            return

    def loop(self):
        B = self.board
        while self.n <= self.n_max:
            pieces = B.all_pieces(self.current)
            moves = []
            for p in pieces:
                for m in p.moves():
                    moves.append((m, p))
            king = self.kings[self.current]
            in_check = king.in_check()
            if in_check:
                move = self.handle_check(king, in_check, moves)
                if not move:
                    break
                moves = [move]
            else:
                shuffle(moves)
            moves.sort()
            B.move(moves[0])
            self.n += 1
            self.current = x_col(self.current)


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
