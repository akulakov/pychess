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
    def __init__(self, board, color, loc):
        self.loc = loc
        self.board = board
        self.orig_location = True
        self.color = color

def __repr__(self):
    char = piece_data[self.__class__][1]
    return char[0 if self.color==WHITE else 1]
```

The `dir` attribute is only used by pawns, but it was a bit more convenient to add it to this
class.  The `orig_location` is used by pawns (for the two-space jump) and rooks and the king --
for castling.

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

I am now ready to add the first piece subclass:

```python
class Pawn(Piece):
    dir = None

    def __init__(self, *args, **kwargs):
        self.dir = kwargs.pop('dir')
        assert self.dir in (1,-1), "Pawns need to have a direction set"
        super().__init__(*args, **kwargs)

board[Loc(0,0)] = Pawn()
```

As only pawns have directional movement based on their color, the `__init__()` method sets
the custom `dir` attribute.

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

Now is a good time to add all data related to pieces: values, display characters and move
modifiers:

```python
piece_data = {
    # piece value, display characters, move modifiers
    Pawn: (1, ('♙', '♟︎'), []),

    Knight: (3,
       ('♘', '♞'),
       [
        (2, 1),
        (2, -1),
        (-2, 1),
        (-2, -1),
        (1, 2),
        (1, -2),
        (-1, 2),
        (-1, -2),
    ]),

    Rook: (5,
           ('♖', '♜'),
            [
            (1, 0), (-1, 0),
            (0, 1), (0, -1)
            ]
          ),

    King: (
        -1,
        ('♔', '♚'),
        [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1)
    ]),


    Queen: (
        9,
        ('♕', '♛'),
        [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1)
    ]),

    Bishop: (
        3,
        ('♗', '♝'),
        [
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1)
        ]),

}
```

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
# piece_data
[
(1, 0), (-1, 0),
(0, 1), (0, -1)
],
```

If this doesn't look clear enough, you can also represent directional modifiers with named
variables like so:

```python
class Dir:
    right = 1, 0
    up = 0, 1
    ...
[Dir.right, Dir.up, Dir.left, Dir.down]
```

I've used modifier tuples however, and I kept move modifer tuples for all pieces in the same
structure, to keep logic and data nicely separated -- see the piece_data structure above.

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
        return piece_data[self[loc].__class__][0]

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

Calculating values of moves that capture pieces relies on `piece_data` structure.

And finally we can add the `moves()` method that works well for the Rooks, Bishops and the
Queen:

```python
import itertools

def chain(lst):
    return itertools.chain(*lst)

# Piece
def moves(self, include_defense=False):
    mods = piece_data[self.__class__][2]
    return chain(self.line(mod, include_defense=include_defense) for mod in mods)
```

The `chain()` method combines multiple iterables into a single iterable; in this case we want
to combine multiple "lines" into a single iterable of all available moves.

Move modifiers are looked up using the name of the piece class.

And now I can add the classes for all three pieces:

```python
class Bishop(Piece):
    pass

class Rook(Piece):
    pass

class Queen(Piece):
    pass
```

The moves are looked up based on the name of the class. I think it's quite neat that all three
pieces can be defined with just a class name!

To prepare for the next, I'll add the `remove_invalid()` methods first:

```python
# Board
def remove_invalid(self, locs):
    return [l for l in locs if self.is_valid(l)]


# Piece
def remove_invalid(self, locs, include_defense=False):
    B = self.board
    locs = B.remove_invalid(locs)
    if include_defense:
        return locs
    else:
        return [l for l in locs if B.empty(l) or self.color != B[l].color]
```

At the level of board, it makes sense to remove everything that doesn't fit into the board, and
at the level of piece, I may also remove locations with my own pieces because I can't move on
top of them.

The knight moves differ from the pieces we've already added in that it jumps over obstacles and
does not move in a line:

```python
class Knight(Piece):
    def moves(self, include_defense=False):
        B = self.board
        lst = [self.loc.modified(*mod) for mod in piece_data[Knight][2]]

        lst = self.remove_invalid(lst, include_defense=include_defense)
        lst = [Move(self, l, B.get_loc_val(l)) for l in lst]
        return lst
```

The logic is similar to `line()`, except that we do the "jump" based on modifiers only once
rather than until bumping into an obstacle.

Of Kings and Pawns
===

If you thought that Kings and Pawns are about as easy to add as the other pieces, prepare to be
surprised! The king is especially tricky, perhaps three times more complicated than all other
pieces combined, -- and so I will start with the Pawns.

As a side note, it's curious that the most complexity in chess rules comes from the weakest
(individually) pieces and the most crucial piece in the game.

I will start by cheating a bit, if you don't mind: I will add queening logic that turns the
fully advanced pawn into a Queen, rather than carefully choosing the best Piece in the
circumstances. In some positions, a Knight may result in checkmate even as a Queen loses the
game. In others, a Queen may result in a draw while a Rook will win you the game.

For now, I will simply create a Queen as that's what you want in vast majority of cases:

```python
# Board
def add(self, piece_cls, color, loc, dir=None):
    kwargs = {'dir':dir} if dir else {}
    self[loc] = piece_cls(self, color, loc, **kwargs)
    return self[loc]

# Piece
def queen(self):
    if self.loc.y in (0,7):
        self.board.add(Queen, self.color, self.loc)
```

Note that adding a piece at a location in effect replaces any existing pieces.

Next I will add the capture moves:


```python
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
    return moves
```

There are a couple of interesting things that happen here: first, I can reuse the `line()`
logic to make either a single or double move depending on the pawn's original location. If I
can do a double move, I take the first two moves of a line, otherwise I take only the first
move.

Second, I have to consider that pawns have three types of moves: normal, capture moves and
defense "pseudo-moves", as described above in the docstring. When I am making a move with my
own pawn, I can choose normal or capture moves and ignore defense moves.

On the other hand, when the opponent is moving, the AI needs to consider capture moves and
defense "pseudo-moves", while ignoring normal moves, as such moves don't offer immediate
threat, and this simple AI does not consider more remote threats.

I've used the term 'pseudo-moves' for defense because it was more convenient to implement them
as moves as they need to record the effective piece and the target location just like the
`Move` class, with the exception that the piece is not allowed to move to that location.

To complete the pawn functionality we need to consider how to approach the /en passant/ rule.
It needs to apply when certain conditions are met over the course of two opposing moves: first
move needs to be a two-space jump, the opposing pawn needs to end up to the right or left of
our pawn, and finally our pawn needs to choose the move that jumps to the normal attack tile
and removes the opposing pawn.

The subtle detail is that it's only a one-time opportunity: if you don't capture, you lose this
option on the next move.

To track en passant state, I will add the state and `do_move()` logic to the `Move` class:

```python
class Board:
    ...

    @property
    def is_pawn(self):
        return isinstance(self, Pawn)

    @property
    def is_king(self):
        return isinstance(self, King)

class Move:
    def __init__(self, piece, loc, val=0, related=None, en_passant=False, en_passant_capture=False):
        self.piece, self.loc, self.val = piece, loc, val
        self.related = related
        self.en_passant = en_passant
        self.en_passant_capture = en_passant_capture

    def do_move(self):
        self.piece.move(self)
        if self.en_passant:
            self.piece.en_passant = True
        if self.en_passant_capture:
            self.piece.do_en_passant_capture()
        if self.piece.is_pawn:
            self.piece.queen()

    ...
```

.. and to the pawn:

```python
class Pawn(Piece):
    en_passant = False
    dir = None

    def do_en_passant_capture(self):
        loc = self.loc.modified(y=-self.dir)
        pawn = self.board[loc]
        if not isinstance(pawn, Pawn) or not pawn.en_passant:
            print(f'Warning: {pawn} at {loc} is not valid for en passant capture')
        else:
            self.board[loc] = blank

    def moves(self, normal=True, capture=True, defense=False):
        ...

        en_passant_locs = self.remove_invalid((l.modified(1,0), l.modified(-1,0)))
        en_passant_pawn = [B[l] for l in en_passant_locs
                if isinstance(B[l], Pawn) and B[l].en_passant]
        if en_passant_pawn:
            loc = en_passant_pawn[0].loc
            moves.append(Move(self, loc.modified(y=self.dir), en_passant_capture=True, val=1))
        return moves

    ...
```

Note that when capturing, the target pawn is "behind" my pawn so I get it by reversing the
direction from my new location.

The King
===

Most of the complexity of this chess program is in the logic related to checks. To start with
something a bit easier, I will add the castling moves first:


```python
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

    ...
```

This method will only run when king is not in check and in the original location. The set of
tiles under attack is provided in `unavailable` and will prevent castling to that side. Note
that you can do `a & b` to check if sets `a` and `b` have any locations in common.

This is a unique type of move that moves a second piece at the same time, which is easily
handled in the `move()` method:

```python
# Piece
def move(self, move):
    ...
    if move.related:
        self.move(move.related)
```

To allow sets of locations to be compared using the `&` operator, I also add these two methods
to `Loc`:

```python
# Loc
def __hash__(self):
    return hash(tuple(self))

def __eq__(self, other):
    return isinstance(other, Loc) and tuple(other) == tuple(self)
```

The first of these allows me to add custom objects to sets and the second treats all locations
with the same x,y coordinates as equal; otherwise two custom objects are considered unequal
and so `Loc(1,1) == Loc(1,1)` would be evaluated as `False`.

The `King.moves()` method is similar to `Knight.moves()`:

```python
def moves(self, include_defense=False, in_check=False):
    loc = self.loc
    lst = [loc.modified(*mod) for mod in piece_data[King][2]]

    lst = self.remove_invalid(lst, include_defense=include_defense)
    lst = [Move(self, l, self.board.get_loc_val(l)) for l in lst]
    unavailable = self.opponent_moves()

    if self.orig_location and not in_check:
        lst = self.castling_moves(lst, unavailable)
    return list(set(lst) - unavailable)
```

The king cannot move under check or capture a defended piece, -- to calculate valid king moves,
I have to look at all opposing moves, including pawn attack moves and opposing king moves.

The following method needs a few extra arguments because it is reused later in other logic.

```python
def x_col(color):
    return WHITE if color==BLACK else BLACK

# King
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

def get_king_moves(self, king, include_defense=False):
    locs = [king.loc.modified(*mod) for mod in piece_data[King][2]]
    locs = king.remove_invalid(moves, include_defense=include_defense)
    moves = {Move(king, m) for m in locs}
    return moves

def opponent_moves(self):
    return self.all_moves(x_col(self.color), include_pawns=False, include_defense=True)
```

Note the logic above that handles pawn moves, discussed in more detail when we were adding
`Pawn.moves()`. It could be implemented by passing `include_defense` directly to `Pawn.moves()`
but that would be confusing because it would be unclear why "forward" moves are not included
with `include_defense=True`.


