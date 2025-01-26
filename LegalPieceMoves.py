from time import sleep

def legalPawnmoves(row: int, column: int, WhitePawn:bool, Board: list[list],enpassantablefile: int|None)-> list[tuple[int,int,bool]]:
    """Returns: list of legal moves containing row, column and wether enpassant happened.
     
     List of legal Moves includes the moves which are physically possible. The moves might leave the king hanging or capture own pieces.
    """
    #print(f"{row = }, {column = }, {WhitePawn = }")
    if not WhitePawn:
        MirroredMoves: list[tuple[int,int,bool]]=legalPawnmoves(7-row,column,True, Board, enpassantablefile)
        return [(7-Row, Column,enpassanthappened) for (Row,Column,enpassanthappened) in MirroredMoves]
    Moves=[]
    #Straightmoves
    if Board[row+1][column] is None:
        Moves.append((row+1,column,False))
        if row==1:
            if Board[row+2][column] is None:
                Moves.append((row+2,column,False))
    #En passant
    if enpassantablefile is not None and row==4:
        if abs(enpassantablefile-column)==1:
            Moves.append((5,enpassantablefile,True))
    #Normal captures
    if column+1<8:
        if Board[row+1][column+1] is not None:
            #print(f"I found something to eat on {(row+1,column+1)}. It's a {Board[row+1][column+1]}")
            #sleep(3)
            Moves.append((row+1,column+1,False))
    if column-1>=0:
        if Board[row+1][column-1] is not None:
            #print(f"I found something to eat on {(row+1,column-1)}. It's a {Board[row+1][column-1]}")
            #sleep(3)
            Moves.append((row+1,column-1,False))
    #print(Moves)
    #sleep(20)
    return Moves

def legalstraightmoves(row: int, column: int, Board: list[list])-> list[tuple[int,int]]:
    """Returns: list of legal moves containing row and column.
     
     List of legal Moves includes the moves which are physically possible. The moves might leave the king hanging or capture own pieces.
    """
    #Upward moves
    Moves=movesincertaindirection(row,column,Board,1,0)
    #Downward moves
    Moves+=movesincertaindirection(row,column,Board,-1,0)
    #Rightward moves
    Moves+=movesincertaindirection(row,column,Board,0,1)
    #Leftward moves
    Moves+=movesincertaindirection(row,column,Board,0,-1)
    return Moves
    """Moves=[]
    #Upward moves
    if Row!=7:
        newrow=Row+1
        Moves.append((newrow, Column))
        while newrow+1<8 and Board[newrow, Column] is None:
            Moves.append((newrow+1, Column))
            newrow+=1
    #Downward moves
    if Row!=0:
        newrow=Row-1
        Moves.append((newrow, Column))
        while newrow-1>=0 and Board[newrow, Column] is None:
            Moves.append((newrow-1, Column))
            newrow-=1
    
    #Leftward moves
    if Column!=0:
        newcol=Column-1
        Moves.append((Row, newcol))
        while newcol-1>=0 and Board[Row, newcol] is None:
            Moves.append((Row, newcol-1))
            newcol-=1
    #Upward moves
    if Column!=7:
        newcol=Column+1
        Moves.append((Row, newcol))
        while newcol+1>=0 and Board[Row, newcol] is None:
            Moves.append((Row, newcol+1))
            newcol+=1
        return Moves"""
def movesincertaindirection(row: int, column: int, Board: list[list],rowincrement: int,columnincrement: int) -> list[tuple[int,int]]:
        Moves=[]
        newrow=row
        newcol=column
        while 0<=newrow+rowincrement<8 and 0<=newcol+columnincrement<8 and ((Board[newrow][newcol] is None) or (row,column)==(newrow,newcol)):
            newcol+=columnincrement
            newrow+=rowincrement
            Moves.append((newrow,newcol))
        return Moves

def legaldiagonalmoves(row: int, column: int, Board: list[list])-> list[tuple[int,int]]:
    """Returns: list of legal moves containing row and column.
     
     List of legal Moves includes the moves which are physically possible. The moves might leave the king hanging or capture own pieces.
    """
    Moves=movesincertaindirection(row,column,Board,1,1)
    Moves+=movesincertaindirection(row,column,Board,-1,1)
    Moves+=movesincertaindirection(row,column,Board,1,-1)
    Moves+=movesincertaindirection(row,column,Board,-1,-1)
    return Moves

def legalknightmoves(row: int, column: int, Board: list[list])-> list[tuple[int,int]]:
    Vectors=[(2,1),(1,2)]
    Factors=[-1,1]
    theoreticalmoves=[(factorrow*i,factorcol*j) for i,j in Vectors for factorcol in Factors for factorrow in Factors]
    return [(row+i,column+j) for (i,j) in theoreticalmoves if (0<=row+i<8 and 0<=column+j<8)]

def legalkingmoves(row: int, column: int, Board: list[list])-> list[tuple[int,int]]:
    ammounts=[-1,0,1]
    theoreticalmoves=[(leftstep,rightstep) for leftstep in ammounts for rightstep in ammounts if (leftstep,rightstep)!=(0,0)]
    return [(row+i,column+j) for (i,j) in theoreticalmoves if (0<=row+i<8 and 0<=column+j<8)]
