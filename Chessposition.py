from enum import Enum, Flag
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
    
    def is_king(self):
        return self==ChessPieces.WhiteKing or self==ChessPieces.BlackKing
    
    def is_knight(self):
        return self==ChessPieces.WhiteKnight or self==ChessPieces.BlackKnight
    
    def is_bishop(self):
        return self==ChessPieces.WhiteBishop or self==ChessPieces.BlackBishop
    
    def is_rook(self):
        return self==ChessPieces.WhiteRook or self==ChessPieces.BlackRook
    
    def is_queen(self):
        return self==ChessPieces.WhiteQueen or self==ChessPieces.BlackQueen
    
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
            
    def pointvalue_in_game(self) -> float:
        sign=1 if self.is_white else -1
        if self.is_rook():
            value=5
        elif self.is_knight():
            value=2.5
        elif self.is_bishop():
            value=3
        elif self.is_king():
            value=0
        elif self.is_queen():
            value=10
        elif self.is_pawn():
            value=1
        else:
            raise ValueError("Seems like I forgot about a type")
        return value*sign

        

    
    def invertcolor(self):
        return ChessPieces(self.value-6 if self.value>6 else self.value+6)
    
class Castling(Flag):
    White=1
    Queenside=2
    def apply_castling_to_rook(self,Board:list[list[ChessPieces|None]]) -> list[list[ChessPieces|None]]:
        rightcoloured_rook=ChessPieces.WhiteRook if Castling.White in self else ChessPieces.BlackRook
        row=-1
        if Castling.White in self:
            row=0
        if Castling.Queenside in self:
            Board[row][0]=None
            Board[row][3]=rightcoloured_rook
        else:
            Board[row][-1]=None
            Board[row][5]=rightcoloured_rook
        return Board

def legalkingmoves(row: int, column: int, Board: list[list], castlingrights:list[bool],castlingcolour: Castling)-> list[tuple[int,int]]:
    castlingmoves=[]
    if castlingrights[(Castling.Queenside|castlingcolour).value] and all(Board[row][i] is None for i in [1,2,3]):
        castlingmoves.append((row,2))
    if castlingrights[castlingcolour.value] and all(Board[row][i] is None for i in [5,6]):
        castlingmoves.append((row,6))
    ammounts=[-1,0,1]
    theoreticalmoves=[(leftstep,rightstep) for leftstep in ammounts for rightstep in ammounts if (leftstep,rightstep)!=(0,0)]
    return [(row+i,column+j) for (i,j) in theoreticalmoves if (0<=row+i<8 and 0<=column+j<8)]+castlingmoves

def eval_by_randomgames(Position: "ChessPosition", numberofgames: int=100) -> float:
    score=0
    #Play random games and figure out and calculate average result.
    for i in range(numberofgames):
        Game=self
        while (moves:=Game.possibleMoves())!=[]:
            Game=random.choice(moves)
        gamevalue=1 if Game.whitesmove else -1
        gamevalue*=0 if Game.reachablesquares()==[] or Game.only_kings_on_board() else 1
        score+=gamevalue
        print(gamevalue)
    return score/numberofgames 

class ChessPosition():
    def __init__(self, Board: list[list[ChessPieces|None]]|None=None,whitesmove: bool= True,enpassantablefile: int|None=None, Castlingright: list[bool]=[True]*4):
        if Board==None:
            Board=[[None]*8 for Row in range(8)]
            Board[0]=[ChessPieces.WhiteRook,ChessPieces.WhiteKnight,ChessPieces.WhiteBishop,ChessPieces.WhiteQueen,ChessPieces.WhiteKing,ChessPieces.WhiteBishop,ChessPieces.WhiteKnight,ChessPieces.WhiteRook]
            Board[-1]=[Piece.invertcolor() for Piece in Board[0]]
            Board[1]=[ChessPieces.WhitePawn]*8
            Board[-2]=[ChessPieces.BlackPawn]*8
        self.Board=Board
        self.whitesmove=whitesmove
        self.enpassantablefile=enpassantablefile
        self.Castlingrights=Castlingright
        """self.white_can_castle=white_can_castle
        self.white_can_castle_queenside=white_can_castle_queenside
        self.black_can_castle=black_can_castle
        self.black_can_castle_queenside=black_can_castle_queenside"""
        #print(f"Initalizing: {str(self)}")
    def __str__(self):
        return tabulate([["" if Piece is None else Piece.symbol() for Piece in row] for row in self.Board[::-1]],tablefmt="grid")
    
    def possibleMoves(self) -> list["ChessPosition"]:
        if self.only_kings_on_board():
            return []
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
                Rawmoves+=legalkingmoves(rowNumber,columnNumber,self.Board, self.Castlingrights,self.castlingcolour())
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
        NewBoard=deepcopy(self.Board)
        movedpiece=self.Board[startrow][startcolumn]

        #Handling en passant
        if enpassanthappened:
            enpassantrow= 3 if self.whitesmove else 4
            NewBoard[enpassantrow][self.enpassantablefile]=None

        newenpassantablefile:int|None=None
        if movedpiece.is_pawn() and abs(startrow-endrow)==2:
            newenpassantablefile=startcolumn

        #Handling Queening
        if movedpiece.is_pawn() and endrow in [0,7]:
            movedpiece=ChessPieces.WhiteQueen if movedpiece==ChessPieces.WhitePawn else ChessPieces.BlackQueen

        NewBoard[endrow][endcolumn]=movedpiece
        NewBoard[startrow][startcolumn]=None

        #Handling Castling
        newCastlingrights=self.Castlingrights
        if movedpiece.is_king():
            for direction in [Castling.Queenside,Castling(0)]:
                newCastlingrights[(self.castlingcolour()|direction).value]=False
            if abs(startcolumn-endcolumn)==2:
                if startcolumn==2:
                    direction=Castling.Queenside
                elif startcolumn==6:
                    direction=Castling(0)
                else:
                    raise ValueError("King castle onto a unexpected square")
                NewBoard=(self.castlingcolour()|direction).apply_castling_to_rook(NewBoard)
            
        if movedpiece.is_rook():
            if startcolumn==0 or startcolumn==7:
                direction=Castling(0)
                if startcolumn==0:
                    direction=Castling.Queenside
                newCastlingrights[(self.castlingcolour()|direction).value]=False
                    
        return ChessPosition(NewBoard,not self.whitesmove,newenpassantablefile,newCastlingrights)
    
    def only_kings_on_board(self) -> bool:
        for i in range(8):
            for j in range(8):
                if self.Board[i][j] not in [ChessPieces.BlackKing,ChessPieces.WhiteKing, None]:
                    return False
        return True
    def eval_by_material(self) -> float:
        return sum(piece.pointvalue_in_game() for row in self.Board for piece in row if piece is not None)

    def eval(self, depth: int, depth0method=eval_by_material) -> float:
        if depth<=0:
            return depth0method(self)
        raise ValueError("deeper level of evals not yet implemented")
    
    def castlingcolour(self) -> Castling:
        if self.whitesmove:
            return Castling.White
        return Castling(0)

           

        
def randomgame():
    Position=ChessPosition()
    while True:
        print(str(Position))
        Position=Position.randommove()
        sleep(1)

def eval_in_randomgame(moves_before_eval,depth=0):
    Position=ChessPosition()
    for i in range(moves_before_eval):
        Position=Position.randommove()
    print(str(Position))
    print(Position.eval(depth))

if __name__=="__main__":
    eval_in_randomgame(100)
    pass