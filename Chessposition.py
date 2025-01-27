from enum import Enum, Flag
from tabulate import tabulate
from LegalPieceMoves import *
import random
from time import sleep
from copy import deepcopy
import math


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
    
    def is_white(self)->bool:
        return self.value <= 6

    def is_pawn(self)->bool:
        return self==ChessPieces.WhitePawn or self==ChessPieces.BlackPawn
    
    def is_king(self)->bool:
        return self==ChessPieces.WhiteKing or self==ChessPieces.BlackKing
    
    def is_knight(self)->bool:
        return self==ChessPieces.WhiteKnight or self==ChessPieces.BlackKnight
    
    def is_bishop(self)->bool:
        return self==ChessPieces.WhiteBishop or self==ChessPieces.BlackBishop
    
    def is_rook(self)->bool:
        return self==ChessPieces.WhiteRook or self==ChessPieces.BlackRook
    
    def is_queen(self)->bool:
        return self==ChessPieces.WhiteQueen or self==ChessPieces.BlackQueen
    
    def moves_diagonal(self)->bool:
        return self.is_bishop() or self.is_queen()
    
    def moves_straight(self)->bool:
        return self.is_rook() or self.is_queen()
    
    def white_version_of_self(self)->"ChessPieces":
        return self if self.is_white() else self.invertcolor()
    
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
        sign=1 if self.is_white() else -1
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
    def invertcolor(self)->"ChessPieces":
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
    
    def Castlinglegal(self,Position:"ChessPosition")->bool:
        if not Position.Castlingrights[self.value]:
            return False
        if Position.whitesmove!=(Castling.White in self):
            return False
        row=0 if Castling.White in self else 7
        rookcol=0 if Castling.Queenside in self else 7
        increment=-1 if Castling.Queenside in self else 1
        for col in range(4+increment,rookcol,increment):
            if Position.Board[row][col] is not None:
                return False
            if Position.square_attacked(row,col):
                return False
        return True
    
    def squares(self)->tuple[tuple[int,int],tuple[int,int]]:
        """Returns: (Startrow,Startcolumn),(Endrow,endcolumn) of king"""
        row=0 if Castling.White in self else 7
        startcol=4
        finalcol=2 if Castling.Queenside else 6
        return (row,startcol),(row,finalcol)
    
    def final_king_col(self):
        return 2 if Castling.Queenside in self else 6

def castlingcolor(white:bool)->Castling:
    return Castling.White if white else Castling(0)

def castlingdirection(queenside: bool)->Castling:
    return Castling.Queenside if queenside else Castling(0)

def enumCastling():
    for i in [Castling(0),Castling.Queenside]:
        for j in [Castling(0),Castling.White]:
            yield i|j

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
        Game=Position
        while (moves:=Game.possibleMoves())!=[]:
            Game=random.choice(moves)
        gamevalue=1 if Game.whitesmove else -1
        gamevalue*=0 if Game.reachablesquares()==[] or Game.only_kings_on_board() else 1
        score+=gamevalue
        print(gamevalue)
    return score/numberofgames 

class ChessPosition():
    def __init__(self, Board: list[list[ChessPieces|None]]|None=None,whitesmove: bool= True,enpassantablefile: int|None=None, Castlingright: list[bool]=[True]*4):
        if Board == None:
            Board = [[None]*8 for Row in range(8)]
            Board[0] = [ChessPieces.WhiteRook,ChessPieces.WhiteKnight,ChessPieces.WhiteBishop,ChessPieces.WhiteQueen,ChessPieces.WhiteKing,ChessPieces.WhiteBishop,ChessPieces.WhiteKnight,ChessPieces.WhiteRook]
            Board[-1] = [Piece.invertcolor() for Piece in Board[0]]
            Board[1] = [ChessPieces.WhitePawn]*8
            Board[-2] = [ChessPieces.BlackPawn]*8
        self.Board:list[list[ChessPieces|None]] = Board
        self.whitesmove:bool = whitesmove
        self.enpassantablefile:int|None = enpassantablefile
        self.Castlingrights:list[bool] = Castlingright
        """self.white_can_castle=white_can_castle
        self.white_can_castle_queenside=white_can_castle_queenside
        self.black_can_castle=black_can_castle
        self.black_can_castle_queenside=black_can_castle_queenside"""
        #print(f"Initalizing: {str(self)}")
    def __str__(self):
        return tabulate([["" if Piece is None else Piece.symbol() for Piece in row] for row in self.Board[::-1]],tablefmt="grid")
    
    def move_is_legal(self,startrow,startcol,endrow,endcol):
        print(startrow,startcol,endrow,endcol)
        if (startrow,startcol)==(endrow,endcol):
            return False
        piece=self.Board[startrow][startcol]
        print(piece)
        if piece is None:
            return False
        if piece.is_white()!=self.whitesmove:
            return False
        def legal_diagonalmove() -> bool:
            if not abs(startrow-endrow)==abs(startcol-endcol):
                return False
            rowsign=1 if endrow>startrow else -1
            colsign=1 if endcol>startcol else -1
            intermediate_row=startrow+rowsign
            intermediate_col=startcol+colsign
            while intermediate_row!=endrow:
                intermediate_square_occupant=self.Board[intermediate_row][intermediate_col]
                if intermediate_square_occupant is not None:
                    return False
                intermediate_row+=rowsign
                intermediate_col+=colsign
            return self.square_empty_or_containing_opponent(endrow,endcol)
        def legal_straightmove() -> bool:
            if startcol!=endcol and startrow!=endrow:
                return False
            rowsign=(startrow!=endrow)*(1 if endrow>startrow else -1)
            colsign=(startcol!=endcol)*(1 if endcol>startcol else -1)
            intermediate_row=startrow+rowsign
            intermediate_col=startcol+colsign
            while (intermediate_row,intermediate_col)!=(endrow,endcol):
                intermediate_square_occupant=self.Board[intermediate_row][intermediate_col]
                if intermediate_square_occupant is not None:
                    return False
                intermediate_row+=rowsign
                intermediate_col+=colsign
            return self.square_empty_or_containing_opponent(endrow,endcol)
        def legal_knightmove()->bool:
            if (abs(startrow-endrow),abs(startcol-endcol)) in [(2,1),(1,2)]:
                return self.square_empty_or_containing_opponent(endrow,endcol)
            return False
        def legal_kingmove()->bool:
            if abs(startrow-endrow)<=1 and abs(startcol-endcol)<=1:
                return self.square_empty_or_containing_opponent(endrow,endcol)
            for i in enumCastling():
                print(f"{i = }, {i.Castlinglegal(self) = }, {i.final_king_col() = }")
                if i.Castlinglegal(self) and endcol==i.final_king_col():
                    return True
            return False

        def legal_pawnmove()->bool:
            if abs(startcol-endcol)>=2:
                return False
            if startcol==endcol:#Straight pawn moves
                if startrow+1==endrow:
                    return self.Board[endrow][endcol] is None
                expected_startrow=1 if self.whitesmove else 6
                increments=1 if self.whitesmove else -1#sign of the direction in which players pawns move
                Wrong_direction=(endrow-startrow)*increments<0
                if Wrong_direction or abs(endrow-startrow)>2 or startrow!=expected_startrow:
                    return False
                return (self.Board[startrow+increments][startcol] is None) and (self.Board[startrow+(2*increments)][startcol] is None)
            #Diagonal pawn moves
            if abs(startcol-endcol)!=1:
                return False
            if self.square_containing_opponent(endrow,endcol):
                return True
            enpassantrow=4 if self.whitesmove else 3
            if self.enpassantablefile is None or startrow!=enpassantrow:
                return False
            return self.enpassantablefile==endcol

        match piece.white_version_of_self():
            case ChessPieces.WhiteKnight:
                return legal_knightmove()
            case ChessPieces.WhiteRook:
                return legal_straightmove()
            case ChessPieces.WhiteBishop:
                return legal_diagonalmove()
            case ChessPieces.WhiteQueen:
                return legal_diagonalmove() or legal_straightmove()
            case ChessPieces.WhiteKing:
                return legal_kingmove()
            case ChessPieces.WhitePawn:
                return legal_pawnmove()
            case _:
                raise ValueError("Unexpected Piecetype")
        #Missing:
        #-->Avoiding Check
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
        if piece is None:
            raise ValueError("piecessemilegalmoves is not supposed to be called on empty squares!")
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
        """Returns: Position after the inserted move.
        
        Only use after checking move with move_is_legal"""
        NewBoard=deepcopy(self.Board)
        movedpiece=self.Board[startrow][startcolumn]
        if movedpiece is None:
            raise ValueError("applymove is not meant to be called from squares without pieces")
        if movedpiece.is_white()!=self.whitesmove:
            strpiececolor="white" if movedpiece.is_white() else "black"
            raise ValueError(f"It's not {strpiececolor}'s move")

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
                if endcolumn==2:
                    direction=Castling.Queenside
                elif endcolumn==6:
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
    
    def eval_by_placement(self) -> float:
        return sum((abs(3.5-i)+abs(3.5-j))*(piece.is_white()-0.5)/500 for i in range(8) for j in range(8) if (piece:=self.Board[i][j]) is not None)
    
    def eval_without_depth(self) -> float:
        return self.eval_by_material()+self.eval_by_placement()

    def is_check(self):
        ChessPosition(self.Board,not self.whitesmove,None,self.Castlingrights)

    def eval(self, depth: int, depth0method=eval_by_material) -> tuple[float,"ChessPosition"]:
        """Returns: Evaluation of the position and the best move"""
        moves=self.possibleMoves()
        if len(moves)==0:
            #Player is out of moves so he either lost or it's a draw
            sign=-1 if self.whitesmove else 1
            value=float('inf') if self.is_check() else 0
            return sign*value, self
        if depth<=0:
            return depth0method(self),self.randommove()
        
        cost=math.log(len(moves))#Incentivizing forcing moves
        eval_and_move=[]
        for move in moves:
            directgain:float =abs(self.eval_by_material()-move.eval_by_material())#incentivizing captures
            evaluation,_=move.eval(depth-(cost/(1+directgain)),depth0method)
            eval_and_move.append((evaluation,move))
        if self.whitesmove:
            return max(eval_and_move, key=lambda x: x[0])
        return min(eval_and_move, key=lambda x: x[0])
    
    def bestmove(self,*args):
        return self.eval(*args)[1]
    
    def castlingcolour(self) -> Castling:
        if self.whitesmove:
            return Castling.White
        return Castling(0)
    
    def square_empty_or_containing_opponent(self,row,col):
        piece=self.Board[row][col]
        if piece is None:
            return True
        return piece.is_white()!=self.whitesmove
    
    def square_containing_opponent(self,row,col):
        piece=self.Board[row][col]
        if piece is None:
            return False
        return piece.is_white()!=self.whitesmove
    
    def square_attacked(self,row,col):
        print("square_attacked not yet implemented!")
        return False

           

        
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

def Game_of_bestmoves(depth):
    Position=ChessPosition()
    while True:
        print(str(Position))
        print(len(Position.possibleMoves()))
        Position=Position.bestmove(depth)


if __name__=="__main__":
    Game_of_bestmoves(5)
    pass