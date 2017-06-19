from piece import *
from graphic import *
from copy import deepcopy

WHITE = (255, 255, 255)
GREY = (119, 136, 153)


class Board:

    def __init__(self):
        self.board = []
        self.previousMove = None

    def getTypeAndColor(self, x, y):
        return (self.board[x][y].Type, self.board[x][y].color)

    def setPiece(self, Type, color, x, y):
        if Type == pType.King:
            self.board[x][y] = King(color, (x, y))
        elif Type == pType.Knight:
            self.board[x][y] = Knight(color, (x, y))
        elif Type == pType.Rook:
            self.board[x][y] = Rook(color, (x, y))
        elif Type == pType.Bishop:
            self.board[x][y] = Bishop(color, (x, y))
        elif Type == pType.Queen:
            self.board[x][y] = Queen(color, (x, y))
        elif Type == pType.Pawn:
            self.board[x][y] = Pawn(color, (x, y))

    def setPieceToPlay(self, row, color):
        self.setPiece(pType.Rook, color, row, 0)
        self.setPiece(pType.Knight, color, row, 1)
        self.setPiece(pType.Bishop, color, row, 2)
        self.setPiece(pType.Queen, color, row, 3)
        self.setPiece(pType.King, color, row, 4)
        self.setPiece(pType.Bishop, color, row, 5)
        self.setPiece(pType.Knight, color, row, 6)
        self.setPiece(pType.Rook, color, row, 7)
        if color == pColor.Black:
            row += 1
        else:
            row -= 1
        for j in range(8):
            self.setPiece(pType.Pawn, color, row, j)

    def initBoard(self):
        for i in range(8):
            self.board.append([])
            for j in range(8):
                self.board[i].append('.')
        self.setPieceToPlay(0, pColor.Black)
        self.setPieceToPlay(7, pColor.White)

    def isNotBlank(self, x, y):
        return self.board[x][y] != '.'

    def draw(self):
        for i in range(8):
            for j in range(8):
                color = GREY
                if (i + j) % 2 == 0:
                    color = WHITE
                drawTile(i, j, color)
                if self.board[i][j] != '.':
                    c = 'black'
                    if self.board[i][j].color == pColor.White:
                        c = 'white'
                    if self.board[i][j].Type == pType.King:
                        displayImage(i, j, './' + c + '/King.png')
                    elif self.board[i][j].Type == pType.Knight:
                        displayImage(i, j, './' + c + '/Knight.png')
                    elif self.board[i][j].Type == pType.Rook:
                        displayImage(i, j, './' + c + '/Rook.png')
                    elif self.board[i][j].Type == pType.Bishop:
                        displayImage(i, j, './' + c + '/Bishop.png')
                    elif self.board[i][j].Type == pType.Queen:
                        displayImage(i, j, './' + c + '/Queen.png')
                    elif self.board[i][j].Type == pType.Pawn:
                        displayImage(i, j, './' + c + '/Pawn.png')

    def isCollide(self, from_x, from_y, to_x, to_y):
        if self.board[from_x][from_y].Type != pType.Knight:
            dx = to_x - from_x
            dy = to_y - from_y
            if dx != 0:
                dx = dx / abs(dx)
            if dy != 0:
                dy = dy / abs(dy)
            x = int(from_x + dx)
            y = int(from_y + dy)
            while x != to_x or y != to_y:
                if self.board[x][y] != '.':
                    return True
                x += int(dx)
                y += int(dy)
        return False

    def moveToAlly(self, from_x, from_y, to_x, to_y):
        if self.board[to_x][to_y] != '.':
            if self.board[to_x][to_y].color == self.board[from_x][from_y].color:
                return True
        return False

    def promote(self, x, y, Type):
        self.setPiece(Type, self.board[x][y].color, x, y)

    def makeMove(self, from_x, from_y, to_x, to_y):
        self.board[to_x][to_y] = self.board[from_x][from_y]
        self.board[to_x][to_y].pos = (to_x, to_y)
        self.board[to_x][to_y].moved = True
        self.board[from_x][from_y] = '.'
        self.previousMove = (
            self.board[to_x][to_y].Type, from_x, from_y, to_x, to_y)

    def getMovePosForPawn(self, from_x, from_y):
        pos = []
        # Check move
        validMoves = self.board[from_x][from_y].validMoves()
        if self.board[from_x][from_y].color == pColor.Black and from_x == 1:
            if self.board[from_x + 2][from_y] == '.':
                validMoves.append((from_x + 2, from_y))
        if self.board[from_x][from_y].color == pColor.White and from_x == 6:
            if self.board[from_x - 2][from_y] == '.':
                validMoves.append((from_x - 2, from_y))
        for move in validMoves:
            if self.isCollide(from_x, from_y, move[0], move[1]):
                continue
            if self.moveToAlly(from_x, from_y, move[0], move[1]):
                continue
            pos.append(move)
        # Check capture
        validCaptures = self.board[from_x][from_y].validCaptures()
        for capture in validCaptures:
            if self.moveToAlly(from_x, from_y, capture[0], capture[1]):
                continue
            # en passant
            if self.board[capture[0]][capture[1]] == '.':
                if self.board[from_x][from_y].color == pColor.White:
                    if from_x != 3 or self.previousMove != \
                       (pType.Pawn, capture[0] - 1, capture[1], capture[0] + 1, capture[1]):
                        continue
                if self.board[from_x][from_y].color == pColor.Black:
                    if from_x != 4 or self.previousMove != \
                       (pType.Pawn, capture[0] + 1, capture[1], capture[0] - 1, capture[1]):
                        continue
            pos.append(capture)
        return pos

    def getMovePosForKing(self, from_x, from_y):
        pos = []
        # Check castling
        validCastling = self.board[from_x][from_y].validCastling()
        if self.board[from_x][from_y].moved is False:
            for cast in validCastling:
                if self.isCollide(from_x, from_y, cast[0], cast[1]):
                    continue
                if self.moveToAlly(from_x, from_y, cast[0], cast[1]):
                    continue
                if (cast[1] != from_y + 2 or self.board[cast[0]][cast[1] + 1].moved is True) \
                   and (cast[1] != from_y - 2 or self.board[cast[0]][cast[1] - 2].moved is True):
                    continue
                pos.append(cast)
        # Check move
        validMoves = self.board[from_x][from_y].validMoves()
        for move in validMoves:
            if self.isCollide(from_x, from_y, move[0], move[1]):
                continue
            if self.moveToAlly(from_x, from_y, move[0], move[1]):
                continue
            pos.append(move)
        return pos

    def getMovePosForPiece(self, from_x, from_y):
        pos = []
        validMoves = self.board[from_x][from_y].validMoves()
        for move in validMoves:
            if self.isCollide(from_x, from_y, move[0], move[1]):
                continue
            if self.moveToAlly(from_x, from_y, move[0], move[1]):
                continue
            pos.append(move)
        return pos

    def move(self, from_x, from_y, to_x, to_y):
        cellFrom = self.board[from_x][from_y]
        # Pawn pieces
        if cellFrom.Type == pType.Pawn:
            if (to_x, to_y) in self.getMovePosForPawn(from_x, from_y):
                # en passant
                if from_x == 3 and self.board[from_x][from_y].color == pColor.White \
                   and self.previousMove == (pType.Pawn, to_x - 1, to_y, to_x + 1, to_y):
                    self.board[to_x + 1][to_y] = '.'
                if from_x == 4 and self.board[from_x][from_y].color == pColor.Black \
                   and self.previousMove == (pType.Pawn, to_x + 1, to_y, to_x - 1, to_y):
                    self.board[to_x - 1][to_y] = '.'

                self.makeMove(from_x, from_y, to_x, to_y)
                return True
        # King pieces
        elif cellFrom.Type == pType.King:
            if (to_x, to_y) in self.getMovePosForKing(from_x, from_y):
                # castling
                if cellFrom.moved is False:
                    if to_y == from_y + 2 and self.board[to_x][to_y + 1].moved is False:
                        self.makeMove(to_x, to_y + 1, from_x, from_y + 1)
                    if to_y == from_y - 2 and self.board[to_x][to_y - 2].moved is False:
                        self.makeMove(to_x, to_y - 2, from_x, from_y - 1)

                self.makeMove(from_x, from_y, to_x, to_y)
                return True
        # Other pieces
        elif (to_x, to_y) in self.getMovePosForPiece(from_x, from_y):
            self.makeMove(from_x, from_y, to_x, to_y)
            return True
        return False

    def getSuccessors(self):
        successors = []
        pieces = []
        for i in range(8):
            for j in range(8):
                if self.isNotBlank(i, j):
                    pieces.append(self.board[i][j])
        for piece in pieces:
            from_x = piece.pos[0]
            from_y = piece.pos[1]
            if piece.Type == pType.Pawn:
                moves = self.getMovePosForPawn(from_x, from_y)
            elif piece.Type == pType.King:
                moves = self.getMovePosForKing(from_x, from_y)
            else:
                moves = self.getMovePosForPiece(from_x, from_y)

            for move in moves:
                cp = deepcopy(self)
                to_x = move[0]
                to_y = move[1]
                if piece.Type == pType.Pawn:
                    if from_x == 3 and cp.board[from_x][from_y].color == pColor.White \
                       and cp.previousMove == (pType.Pawn, to_x - 1, to_y, to_x + 1, to_y):
                        cp.board[to_x + 1][to_y] = '.'
                    if from_x == 4 and cp.board[from_x][from_y].color == pColor.Black \
                       and cp.previousMove == (pType.Pawn, to_x + 1, to_y, to_x - 1, to_y):
                        cp.board[to_x - 1][to_y] = '.'
                elif piece.Type == pType.King:
                    if cp.board[from_x][from_y].moved is False:
                        if to_y == from_y + 2 and cp.board[to_x][to_y + 1].moved is False:
                            cp.makeMove(to_x, to_y + 1, from_x, from_y + 1)
                        if to_y == from_y - 2 and cp.board[to_x][to_y - 2].moved is False:
                            cp.makeMove(to_x, to_y - 2, from_x, from_y - 1)
                cp.makeMove(from_x, from_y, to_x, to_y)
                if piece.Type == pType.Pawn \
                    and ((piece.color == pColor.White and to_x == 0)
                         or (piece.color == pColor.Black and to_x == 7)):
                    tmp = deepcopy(cp)
                    tmp.promote(to_x, to_y, pType.Queen)
                    successors.append(tmp)

                    tmp = deepcopy(cp)
                    tmp.promote(to_x, to_y, pType.Knight)
                    successors.append(tmp)

                    tmp = deepcopy(cp)
                    tmp.promote(to_x, to_y, pType.Rook)
                    successors.append(tmp)

                    tmp = deepcopy(cp)
                    tmp.promote(to_x, to_y, pType.Bishop)
                    successors.append(tmp)
                else:
                    successors.append(cp)
        return successors
