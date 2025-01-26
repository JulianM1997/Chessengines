from enum import Enum
from tabulate import tabulate
from LegalPieceMoves import *
import random
from time import sleep
from copy import deepcopy

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

    def is_pawn(self):
        return self==ChessPieces.WhitePawn or self==ChessPieces.BlackPawn
    
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
        

class ChessPosition():
    def __init__(self, Board: list[list[ChessPieces|None]]|None=None,whitesmove: bool= True,enpassantablefile: int|None=None):
        if Board==None:
            Board=[[None]*8 for Row in range(8)]
            Board[0]=[ChessPieces.WhiteRook,ChessPieces.WhiteKnight,ChessPieces.WhiteBishop,ChessPieces.WhiteQueen,ChessPieces.WhiteKing,ChessPieces.WhiteBishop,ChessPieces.WhiteKnight,ChessPieces.WhiteRook]
            Board[-1]=[Piece.invertcolor() for Piece in Board[0]]
            Board[1]=[ChessPieces.WhitePawn]*8
            Board[-2]=[ChessPieces.BlackPawn]*8
        self.Board=Board
        self.whitesmove=whitesmove
        self.enpassantablefile=enpassantablefile
        #print(f"Initalizing: {str(self)}")
    def __str__(self):
        return tabulate([["" if Piece is None else Piece.symbol() for Piece in row] for row in self.Board[::-1]],tablefmt="grid")
    
    def possibleMoves(self) -> list["ChessPosition"]:
        ReachablePositions=[]
        for rownumber in range(8):
            for columnnumber in range(8):
                piece_on_current_square=self.Board[rownumber][columnnumber]
                #print(piece_on_current_square)
                if piece_on_current_square!=None:
                    if piece_on_current_square.is_white()==self.whitesmove:
                        piecesmoves=self.piecessemilegalmoves(rownumber,columnnumber)
                        resulting_positions=[self.applymove(rownumber,columnnumber,*move) for move in piecesmoves]
                        ReachablePositions.extend([position for position in resulting_positions if not position.nonmovingPlayerinCheck()])
        return ReachablePositions
    
    def randommove(self)-> "ChessPosition":
        return random.choice(self.possibleMoves())


    def findnonMovingPlayersKing(self):
        searchedKing=ChessPieces.WhiteKing if not self.whitesmove else ChessPieces.BlackKing
        for rownumber in range(8):
            for columnnumber in range(8):
                if self.Board[rownumber][columnnumber]==searchedKing:
                    return rownumber,columnnumber
                
    def nonmovingPlayerinCheck(self):
        kingssquare: tuple[int,int]=self.findnonMovingPlayersKing()
        return kingssquare in self.reachablesquares()

    def reachablesquares(self) -> list[tuple[int,int]]:
        """Returns: All possible moves any piece can make. Move might be illegal if own king hangs afterwards.
        
        Check, if pawn queened or enpassant happened before applying."""
        ReachableSquares=[]
        for rownumber in range(8):
            for columnnumber in range(8):
                piece_on_current_square=self.Board[rownumber][columnnumber]
                if piece_on_current_square is not None:
                    if piece_on_current_square.is_white()==self.whitesmove:
                        CurrentPiecesMoves=self.piecessemilegalmoves(rownumber,columnnumber)
                        ReachableSquares+=[newsquare[:2] for newsquare in CurrentPiecesMoves]
        return ReachableSquares
        


    def piecessemilegalmoves(self, rowNumber: int, columnNumber: int)-> list:
        """Returns: All possible moves a piece on a certain square can make. Move might be illegal if own king hangs afterwards.
        
        Check, if pawn queened or enpassant happened before applying."""
        piece=self.Board[rowNumber][columnNumber]
        if piece.is_white()!=self.whitesmove:
            raise ValueError("piecessemilegalmoves is not supposed to be called with pieces of the other colour!")
        Rawmoves:list[tuple[int,int]|tuple[int,int,bool]]=[]
        match piece:
            case None:
                raise ValueError(f"There is no piece on {(rowNumber,columnNumber)}")
            case ChessPieces.BlackPawn:
                #print(str(self))
                Rawmoves=legalPawnmoves(rowNumber,columnNumber,False,self.Board,self.enpassantablefile)
            case ChessPieces.WhitePawn:
                #print(str(self))
                Rawmoves=legalPawnmoves(rowNumber,columnNumber,True,self.Board,self.enpassantablefile)
            case ChessPieces.BlackKnight|ChessPieces.WhiteKnight:
                Rawmoves=legalknightmoves(rowNumber,columnNumber,self.Board)
            case ChessPieces.WhiteBishop|ChessPieces.BlackBishop|ChessPieces.BlackQueen|ChessPieces.WhiteQueen:
                Rawmoves+=(legaldiagonalmoves(rowNumber,columnNumber,self.Board))
            case ChessPieces.WhiteRook|ChessPieces.BlackRook|ChessPieces.BlackQueen|ChessPieces.WhiteQueen:
                Rawmoves+=(legalstraightmoves(rowNumber,columnNumber,self.Board))
            case ChessPieces.WhiteKing | ChessPieces.BlackKing:
                Rawmoves+=legalkingmoves(rowNumber,columnNumber,self.Board)
            case _:
                ValueError(f"Did not expect {piece =}")
        Actualmoves=[]
        for move in Rawmoves:
            newrow=move[0]
            newcol=move[1]
            Beatenpiece=self.Board[newrow][newcol]
            if Beatenpiece is None:
                Actualmoves.append((newrow,newcol))
            elif Beatenpiece.is_white()!=piece.is_white():
                Actualmoves.append((newrow,newcol))
        #print(str(self))
        #print(f"Legal moves of piece on {(rowNumber,columnNumber)} = {Actualmoves}")
        #sleep(5)
        return Actualmoves
    def applymove(self, startrow: int, startcolumn: int, endrow: int, endcolumn: int, enpassanthappened: bool = False):
        """Copyself=deepcopy(self)
        print(str(self))
        print(f"{startrow = }, {startcolumn = }, {endrow = }, {endcolumn = }, {self.Board[startrow][startcolumn] = }")"""
        NewBoard=deepcopy(self.Board)
        if enpassanthappened:
            enpassantrow= 3 if self.whitesmove else 4
            NewBoard[enpassantrow][self.enpassantablefile]=None
        movedpiece=self.Board[startrow][startcolumn]
        if movedpiece.is_pawn() and endrow in [0,7]:
            movedpiece=ChessPieces.WhiteQueen if movedpiece==ChessPieces.WhitePawn else ChessPieces.BlackQueen
        NewBoard[endrow][endcolumn]=movedpiece
        NewBoard[startrow][startcolumn]=None
        newenpassantablefile:int|None=None
        if movedpiece.is_pawn() and abs(startrow-endrow)==2:
            newenpassantablefile=startcolumn
        return ChessPosition(NewBoard,not self.whitesmove,newenpassantablefile)

        

        
def randomgame():
    Position=ChessPosition()
    while True:
        print(str(Position))
        Position=Position.randommove()
        sleep(3)



    
if __name__=="__main__":
    randomgame()
    pass