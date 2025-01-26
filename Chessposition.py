from enum import Enum
from tabulate import tabulate

class ChessPieces(Enum):
    WhitePawn = 1
    WhiteRook = 2
    WhiteKnight = 3
    WhiteBishop = 4
    WhiteQueen = 5
    WhiteKing = 6
    BlackPawn = 7
    BlackRook = 8
    BlackKnight = 9
    BlackBishop = 10
    BlackQueen = 11
    BlackKing = 12
    
    def is_white(self):
        return self.value <= 6

    def is_black(self):
        return self.value > 6
    
    def symbol(self) -> str:
        match self:
            case ChessPieces.WhitePawn: 
                return '♙'
            case ChessPieces.WhiteRook: 
                return '♖'
            case ChessPieces.WhiteKnight: 
                return '♘'
            case ChessPieces.WhiteBishop: 
                return '♗'
            case ChessPieces.WhiteQueen:
                return '♕'
            case ChessPieces.WhiteKing: 
                return '♔'
            case ChessPieces.BlackPawn: 
                return '♟'
            case ChessPieces.BlackRook: 
                return '♜'
            case ChessPieces.BlackKnight: 
                return '♞'
            case ChessPieces.BlackBishop: 
                return '♝'
            case ChessPieces.BlackQueen: 
                return '♛'
            case ChessPieces.BlackKing: 
                return '♚'
    
    def invertcolor(self):
        return ChessPieces(self.value-6 if self.value>6 else self.value+6)
    
    def associateMoves(self):
        pass
        

class ChessPosition():
    def __init__(self, Board: list[list[ChessPieces|None]]|None=None):
        if Board==None:
            Board=[[None]*8 for Row in range(8)]
            Board[0]=[ChessPieces.WhiteRook,ChessPieces.WhiteKnight,ChessPieces.WhiteBishop,ChessPieces.WhiteQueen,ChessPieces.WhiteKing,ChessPieces.WhiteBishop,ChessPieces.WhiteKnight,ChessPieces.WhiteRook]
            Board[-1]=[Piece.invertcolor() for Piece in Board[0]]
            Board[1]=[ChessPieces.WhitePawn]*8
            Board[-2]=[ChessPieces.BlackPawn]*8
        self.Board=Board
    def __str__(self):
        return tabulate([["" if Piece is None else Piece.symbol() for Piece in row] for row in self.Board],tablefmt="grid")
    
if __name__=="__main__":
    print(str(ChessPosition()))