#!/usr/bin/env python3
import itertools
from random import shuffle

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

def chain(lst):
    return itertools.chain(*lst)

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
    def __init__(self, piece, loc, val=0, related=None):
        self.piece, self.loc, self.val = piece, loc, val
        self.related = related

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

    def do_move(self):
        self.piece.move(self)

class Board:
    def __init__(self, size):
        self.b = [row(size) for _ in range(size)]
        self.size = size

    def place_standard(self):
        add = self.add
        piece_locs = {Rook: (0,7), Knight: (1,6), Bishop: (2,5), Queen: (3,), King: (4,)}

        if self.size == 8:
            for x in range(8):
                add(Pawn, WHITE, Loc(x, 1), dir=1)
                add(Pawn, BLACK, Loc(x, 6), dir=-1)
            for pc, x_locs in piece_locs.items():
                for x in x_locs:
                    add(pc, WHITE, Loc(x, 0))
            for pc, x_locs in piece_locs.items():
                for x in x_locs:
                    add(pc, BLACK, Loc(x, 7))

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
        if move.related:
            self.move(move.related)

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

    def add(self, piece_cls, color, loc, dir=None):
        self[loc] = piece_cls(self, color, loc, dir)
        return self[loc]

    def all_pieces(self, color, types=None):
        for r in self.b:
            for tile in r:
                if tile!=blank and (types is None or isinstance(tile, types)) and tile.color==color:
                    yield tile

    def get_loc_val(self, loc):
        pc = self[loc]
        if self.empty(loc):
            return 0
        elif isinstance(pc, King):
            # this is only needed when calculating opponent_moves to determine if we are in check
            return 999
        else:
            return piece_values[self[loc].__class__]

class Piece:
    def __init__(self, board, color, loc, dir=None):
        self.loc = loc
        self.board = board
        self.orig_location = True
        self.color = color
        self.dir = dir

    def move(self, move):
        self.board.move(move)
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

    def moves(self, attacking_only=False):
        l = self.loc
        B = self.board
        moves = []
        if not attacking_only:
            move_len = 2 if self.orig_location else 1
            line = self.line((0, self.dir))[:move_len]
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
                moves.append(Move(self, l, B.get_loc_val(l)))
        return moves

class Knight(Piece):
    char = '♘'

    def moves(self):
        B = self.board
        lst = [self.loc.modified(*mod) for mod in knight_moves]
        lst = self.remove_invalid(lst)
        lst = [Move(self, l, B.get_loc_val(l)) for l in lst]
        return lst


class King(Piece):
    char = '♔'

    def all_moves(self, color, include_king=True):
        B = self.board
        pc = B.all_pieces(color, (Knight, Bishop, Rook, Queen))
        pawns = B.all_pieces(color, (Pawn,))

        moves = list(chain(a.moves() for a in pc))

        # print("moves", moves)
        pwn_moves = chain(pwn.moves() for pwn in pawns)
        all_moves = set(moves) | set(pwn_moves)
        if include_king:
            king = next(B.all_pieces(color, (King,)))
            all_moves |= self.get_king_moves(king)
        return all_moves

    def get_king_moves(self, king):
        king_moves = [king.loc.modified(*mod) for mod in piece_moves['King']]
        king_moves = king.remove_invalid(king_moves)
        king_moves = [Move(king, m) for m in king_moves]
        # print("king_moves", king_moves)
        return set(king_moves)

    def opponent_moves(self):
        return self.all_moves(x_col(self.color))

    def in_check(self):
        # checks = [m.loc for m in self.opponent_moves()]
        # print("checks", checks)
        return [m for m in self.opponent_moves() if m.loc==self.loc]

    def moves(self, dbg=0, add_unavailable=None):
        loc = self.loc
        B = self.board
        lst = [loc.modified(*mod) for mod in piece_moves['King']]
        lst = self.remove_invalid(lst)
        lst = [Move(self, l, self.board.get_loc_val(l)) for l in lst]
        if dbg: print(lst)
        unavailable = self.opponent_moves()
        if dbg: print(unavailable)

        if self.orig_location:
            lst = self.castling_moves(lst, unavailable)
        unavailable_locs = set(m.loc for m in unavailable)
        if add_unavailable:
            unavailable_locs |= add_unavailable
        if dbg: print(unavailable_locs)
        if dbg: print( [m for m in lst if m.loc not in unavailable_locs] )
        return [m for m in lst if m.loc not in unavailable_locs]

    def castling_moves(self, lst, unavailable):
        loc = self.loc
        if loc not in (Loc(4,0), Loc(4,7)):
            # not a standard location, a puzzle game
            return lst
        a = Loc(0, loc.y)
        rook = self.board[a]
        isrook = isinstance(rook, Rook)
        line = self.line((-1,0))
        if line and not set(line) & unavailable:
            last = line[-1].loc.x
            if isrook and rook.orig_location and last==1:
                lst.append(Move(self, loc.modified(-2,0), related=Move(rook, loc.modified(-1,0))))

        b = Loc(7, loc.y)
        rook = self.board[a]
        isrook = isinstance(rook, Rook)
        line = self.line((1,0))
        if line and not set(line) & unavailable:
            last = line[-1].loc.x
            if isrook and rook.orig_location and last==6:
                lst.append(Move(self, loc.modified(2,0), related=Move(rook, loc.modified(1,0))))
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
            all_moves = king.all_moves(self.current)
            capture = [m for m in all_moves if m.loc==in_check[0].loc]
            if capture:
                return capture[0]

        # try block
        if len(in_check) == 1:
            ok = True
            if isinstance(in_check[0].piece, Knight):
                ok = False
            if king.loc.is_adjacent(in_check[0].loc):
                ok = False
            if ok:
                all_moves = king.all_moves(self.current, include_king=False)
                blocking = set(king.loc.between(in_check[0].loc))
                print("blocking", blocking)
                blocking = [m for m in all_moves if m.loc in blocking]
                print("2 blocking", blocking)
                if blocking:
                    return blocking[0]

        # only king moves left
        unavailable = set()
        for mv in in_check:
            piece = mv.piece
            mvloc = mv.loc
            ploc = piece.loc
            if isinstance(piece, (Queen, Rook, Bishop)):
                mod_x = self.envelope(ploc.x - mvloc.x)
                mod_y = self.envelope(ploc.y - mvloc.y)
                unavailable.add(king.loc.modified(mod_x, mod_y))

        k_moves = king.moves(dbg=1, add_unavailable=unavailable)
        print("k_moves", k_moves)
        if k_moves:
            return k_moves[0]
        else:
            curc = 'White' if self.current==WHITE else 'Black'
            print(f'{curc} is checkmated')
            return

    def envelope(self, val, low=-1, high=1):
        return max(low, min(high, val))

    def loop(self):
        B = self.board
        while self.n <= self.n_max:
            pieces = list(B.all_pieces(self.current))

            moves = list(chain(p.moves() for p in pieces))
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
            m = moves[0]
            m.do_move()
            self.n += 1
            self.current = x_col(self.current)
            self.print_board()
            inp = input('continue > ')
            if inp=='q':
                break

    def print_board(self):
        print(' ' + ' '.join('abcdefgh'))
        for r in reversed(list(self.board.display())):
            print(r)

piece_values = {
    Pawn: 1,
    Bishop: 3,
    Knight: 3,
    Rook: 5,
    Queen: 9,
}


if __name__ == "__main__":
    b = Board(8)
    loc = Loc('c',3)
    l2 = Loc('c',5)
    # b.add(King, BLACK, l2.modified(1,0))
    # b.add(Pawn, BLACK, l2, dir=-1)
    # pc = b.add(King, WHITE, loc)
    b.place_standard()
    chess = Chess(b)
    if 1:
        chess.loop()

