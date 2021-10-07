#!/usr/bin/env python3
import itertools
from random import shuffle, random, choice

"""
Chess

En passant:
    - move is created to move 2 tiles and has en_passant attr set
    - move is performed and pawn en_passant attr is also set
    - other pawn checks to right and left for en passant pawns
    - capture move en_passant_capture is created
    - if capture move is performed, tile in the opposite direction of pawn is checked and captured pawn is removed from
    there
    - at the end of loop (i.e. after any move is done), reset en passant state of all opposing pawns
"""


WHITE = 'White'
BLACK = 'Black'
blank = '.'

PAWN_ODDS = 1
DBG = 0
RANDOMIZED_CHESS = 0

piece_chars = {
    '♖': '♜',
    '♔': '♚',
    '♘': '♞',
    '♙': '♟︎',
    '♗': '♝',
    '♕': '♛',
}

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

def chain(lst):
    return itertools.chain(*lst)

def x_col(color):
    return WHITE if color==BLACK else BLACK

def row(size):
    return [blank] * size

def getrand(locs):
    val = choice(locs)
    locs.remove(val)
    return val


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
            a, b = (a, b) if a<b else (b, a)
            return [Loc(self.x,y) for y in range(a+1,b+1)]
        if self.y==loc.y:
            a, b = self.x, loc.x
            a, b = (a, b) if a<b else (b, a)
            return [Loc(x,self.y) for x in range(a+1,b+1)]
        # diagonal
        x1, y1 = self
        x2, y2 = loc
        if x1>x2:
            x1,x2 = x2,x1
            y1,y2 = y2,y1

        lst = []
        ymod = 1 if y1<y2 else -1
        for x in range(x1+1, x2):
            y1 += ymod
            lst.append(Loc(x,y1))

        return lst

class Move:
    def __init__(self, piece, loc, val=0, related=None, en_passant=False, en_passant_capture=False):
        self.piece, self.loc, self.val = piece, loc, val
        self.related = related
        self.en_passant = en_passant
        self.en_passant_capture = en_passant_capture

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
        if self.en_passant:
            self.piece.en_passant = True
        if self.en_passant_capture:
            self.piece.do_en_passant_capture()
        if self.piece.is_pawn:
            self.piece.queen()


class Board:
    def __init__(self, size):
        self.b = [row(size) for _ in range(size)]
        self.size = size

    def place_standard(self):
        add = self.add
        piece_locs = {Rook: (0,7), Knight: (1,6), Bishop: (2,5), Queen: (3,), King: (4,)}

        if RANDOMIZED_CHESS:
            locs = list(range(8))
            rook = getrand(locs), getrand(locs)
            knight = getrand(locs), getrand(locs)
            bishop = getrand(locs), getrand(locs)
            queen = (getrand(locs),)
            king = (locs[0],)
            piece_locs = {Rook: rook, Knight: knight, Bishop: bishop, Queen: queen, King: king}

        if self.size == 8:
            for x in range(8):
                if not DBG:
                    if random() < PAWN_ODDS:
                        add(Pawn, WHITE, Loc(x, 1), dir=1)
                    if random() < PAWN_ODDS:
                        add(Pawn, BLACK, Loc(x, 6), dir=-1)
            if DBG:
                add(King, BLACK, Loc(0, 0))

                add(King, WHITE, Loc(3, 2))
                add(Pawn, WHITE, Loc(6, 3), dir=-1)
                add(Pawn, BLACK, Loc(5, 1), dir=1)
            else:
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

    def line(self, piece, loc, mod, color, include_defense=False):
        lst = []
        color = self[loc].color
        while 1:
            loc = loc.modified(*mod)
            if not self.is_valid(loc):
                break
            if not self.empty(loc):
                target = self[loc]
                if include_defense or color != target.color:
                    lst.append(Move(piece, loc, self.get_loc_val(loc)))     # capture move
                    if target.is_king:
                        loc = loc.modified(*mod)
                        if self.is_valid(loc):
                            lst.append(Move(piece, loc))
                break
            else:
                lst.append(Move(piece, loc))
        return lst

    def add(self, piece_cls, color, loc, dir=None):
        kwargs = {'dir':dir} if dir else {}
        self[loc] = piece_cls(self, color, loc, **kwargs)
        return self[loc]

    def all_pieces(self, color, types=None):
        for r in self.b:
            for tile in r:
                if tile!=blank and (types is None or isinstance(tile, types)) and tile.color==color:
                    yield tile

    def get_pawns(self, color):
        return self.all_pieces(color, (Pawn,))

    def get_king(self, color):
        return next(self.all_pieces(color, (King,)))

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
    def __init__(self, board, color, loc):
        self.loc = loc
        self.board = board
        self.orig_location = True
        self.color = color

    def move(self, move):
        self.board.move(move)
        self.orig_location = False

    def __repr__(self):
        return self.char if self.color==WHITE else piece_chars[self.char]

    def line(self, dir, include_defense=False):
        return self.board.line(self, self.loc, dir, self.color, include_defense=include_defense)

    def remove_invalid(self, locs, include_defense=False):
        B = self.board
        locs = B.remove_invalid(locs)
        if include_defense:
            return locs
        else:
            return [l for l in locs if B.empty(l) or self.color != B[l].color]

    @property
    def value(self):
        return self.board.get_loc_val(self.loc)

    def moves(self, include_defense=False):
        mods = piece_moves[self.__class__.__name__]
        return chain(self.line(mod, include_defense=include_defense) for mod in mods)

    @property
    def is_pawn(self):
        return isinstance(self, Pawn)

    @property
    def is_king(self):
        return isinstance(self, King)


class Bishop(Piece):
    char = '♗'

class Rook(Piece):
    char = '♖'

class Queen(Piece):
    char = '♕'

class Pawn(Piece):
    char = '♙'
    en_passant = False
    dir = None

    def __init__(self, *args, **kwargs):
        self.dir = kwargs.pop('dir')
        assert self.dir in (1,-1), "Pawns need to have a direction set"
        super().__init__(*args, **kwargs)

    def do_en_passant_capture(self):
        loc = self.loc.modified(y=-self.dir)
        pawn = self.board[loc]
        if not isinstance(pawn, Pawn) or not pawn.en_passant:
            print(f'Warning: {pawn} at {loc} is not valid for en passant capture')
        else:
            self.board[loc] = blank

    def attack_locs(self):
        return self.remove_invalid((
            self.loc.modified(1, self.dir),
            self.loc.modified(-1, self.dir)
            ))

    def moves(self, normal=True, capture=True, defense=False):
        """
        normal - forward moves
        capture - capture opponent piece
        defense - defend friendly piece
        """
        l = self.loc
        B = self.board
        moves = []

        if normal:
            move_len = 2 if self.orig_location else 1
            line = self.line((0, self.dir))[:move_len]
            if line:
                last = line[-1]
                if not B.empty(last.loc):
                    line.pop()
                if len(line) == 2:
                    line[-1].en_passant = True
                moves.extend(line)

        for loc in self.attack_locs():
            piece = B[loc]
            if defense or (piece!=blank and B[loc].color != self.color and capture):
                moves.append(Move(self, loc, B.get_loc_val(loc)))

        en_passant_locs = self.remove_invalid((l.modified(1,0), l.modified(-1,0)))
        en_passant_pawn = [B[l] for l in en_passant_locs if isinstance(B[l], Pawn) and B[l].en_passant]
        if en_passant_pawn:
            loc = en_passant_pawn[0].loc
            moves.append(Move(self, loc.modified(y=self.dir), en_passant_capture=True, val=1))
        return moves

    def queen(self):
        if self.loc.y in (0,7):
            # though sometimes, tactically, it's beneficial to queen to some other piece, the AI is
            # not good enough to make a decision at this level
            self.board.add(Queen, self.color, self.loc)


class Knight(Piece):
    char = '♘'

    def moves(self, include_defense=False):
        B = self.board
        lst = [self.loc.modified(*mod) for mod in piece_moves['Knight']]

        lst = self.remove_invalid(lst, include_defense=include_defense)
        lst = [Move(self, l, B.get_loc_val(l)) for l in lst]
        return lst


class King(Piece):
    char = '♔'

    def all_moves(self, color, include_king=True, include_pawns=True, include_defense=False):
        B = self.board
        pc = B.all_pieces(color, (Knight, Bishop, Rook, Queen))

        all_moves = set(chain(a.moves(include_defense=include_defense) for a in pc))

        if include_pawns:
            pawn_moves = []
            for pawn in B.get_pawns(color):
                if include_defense:
                    moves = pawn.moves(normal=False, capture=True, defense=True)
                else:
                    moves = pawn.moves(normal=True, capture=True, defense=False)
                pawn_moves.extend(moves)
            all_moves |= set(pawn_moves)

        if include_king:
            all_moves |= self.get_king_moves(B.get_king(color), include_defense=include_defense)
        return all_moves

    def pawn_attack_locs(self, color):
        pawns = self.board.get_pawns(color)
        return set(chain(p.attack_locs() for p in pawns))

    def get_king_moves(self, king, include_defense=False):
        moves = [king.loc.modified(*mod) for mod in piece_moves['King']]
        moves = king.remove_invalid(moves, include_defense=include_defense)
        moves = {Move(king, m) for m in moves}
        return moves

    def opponent_moves(self):
        return self.all_moves(x_col(self.color), include_pawns=False, include_defense=True)

    def in_check(self):
        return [m for m in self.opponent_moves() if m.loc==self.loc]

    def moves(self, dbg=0, include_defense=False, in_check=False):
        loc = self.loc
        B = self.board
        lst = [loc.modified(*mod) for mod in piece_moves['King']]

        lst = self.remove_invalid(lst, include_defense=include_defense)
        lst = [Move(self, l, self.board.get_loc_val(l)) for l in lst]
        if dbg: print(lst)
        unavailable = self.opponent_moves()

        if self.orig_location and not in_check:
            lst = self.castling_moves(lst, unavailable)
        unavailable_locs = set(m.loc for m in unavailable)
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
        w_king = board.get_king(WHITE)
        b_king = board.get_king(BLACK)
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
            all_moves = king.all_moves(self.current, include_king=False)
            all_moves |= set(king.moves())
            capture = [m for m in all_moves if m.loc==in_check[0].piece.loc]
            if capture:
                return capture[0]

        # try block
        if len(in_check) == 1:
            ok = True
            piece = in_check[0].piece
            if isinstance(piece, Knight):
                ok = False
            if king.loc.is_adjacent(piece.loc):
                ok = False
            if ok:
                all_moves = king.all_moves(self.current, include_king=False)
                blocking = set(king.loc.between(piece.loc))
                blocking = [m for m in all_moves if m.loc in blocking]
                if blocking:
                    return blocking[0]

        k_moves = king.moves(in_check=True)
        if k_moves:
            return k_moves[0]
        else:
            print(f'{self.current} is Checkmated!')
            return

    def envelope(self, val, low=-1, high=1):
        return max(low, min(high, val))

    def loop(self):
        B = self.board
        self.print_board()
        inp = input('continue > ')
        if inp=='q': return

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
            shuffle(moves)
            opp_moves = king.opponent_moves()
            opp_move_locs = set(m.loc for m in opp_moves)
            opp_move_locs |= king.pawn_attack_locs(x_col(self.current))
            for m in moves:
                if m.loc in opp_move_locs:
                    m.val -= m.piece.value

            moves.sort()
            for m in moves:
                # we don't need this check if king is moving because king would not move under check
                # and also don't need it if king is in check because then the move is blocking the check
                # (otherwise the blocking move would be skipped when we test for `in_check()` below)
                if not isinstance(m.piece, King) and not king.in_check():
                    # determine if the move exposes the king
                    B[m.piece.loc] = blank
                    if king.in_check():
                        B[m.piece.loc] = m.piece
                        continue
                    B[m.piece.loc] = m.piece
                m.do_move()
                break
            else:
                print('Draw: no moves available')
                return

            # check for insufficient material
            a = list(B.all_pieces(self.current))
            b = list(B.all_pieces(x_col(self.current)))
            a,b = (a,b) if len(a)<=len(b) else (b,a)
            if len(a)==1 and len(b) <= 3:
                piece_types = [p.__class__ for p in b]
                piece_types.remove(King)
                if piece_types==[Knight] or piece_types==[Knight, Knight] or piece_types==[Bishop]:
                    print('Draw: insufficient material')
                    return

            # we had a chance to capture with en passant in this move; if we did not, reset en passant
            opp_pawns = B.get_pawns(x_col(self.current))
            for p in opp_pawns:
                p.en_passant = False

            self.n += 1
            self.current = x_col(self.current)
            self.print_board()
            inp = input('continue > ')
            if inp=='q': return

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
    board = Board(8)
    board.place_standard()
    chess = Chess(board)
    chess.loop()

