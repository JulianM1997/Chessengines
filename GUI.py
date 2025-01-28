import pygame
import Chessposition
from typing import Iterable
import time

pygame.init()
size = 400
rows, cols = 8, 8
cell_size = size // rows
screen = pygame.display.set_mode((size, size))
font = pygame.font.Font(None, 36)
WHITE = (200, 200, 200)
BLACK = (100, 100, 100)
DARK_BLACK = (0, 0, 0)
RED_TINGE_AMMOUNT = 50
LIGHT_RED_TINGE_AMMOUNT = 30
BLUE_TINGE_AMMOUNT = 50
FRAMETHICKNESS_WHEN_MARKED = 5
Piece_Images= {Chessposition.ChessPieces.BlackBishop: pygame.image.load('Schachfiguren\Chess_bdt45.svg'),
               Chessposition.ChessPieces.BlackQueen: pygame.image.load('Schachfiguren\Chess_qdt45.svg'),
               Chessposition.ChessPieces.BlackKing: pygame.image.load('Schachfiguren\Chess_kdt45.svg'),
               Chessposition.ChessPieces.WhiteKing: pygame.image.load('Schachfiguren\Chess_klt45.svg'),
               Chessposition.ChessPieces.WhiteBishop: pygame.image.load('Schachfiguren\Chess_blt45.svg'),
               Chessposition.ChessPieces.BlackKnight: pygame.image.load('Schachfiguren\Chess_ndt45.svg'),
               Chessposition.ChessPieces.WhiteKnight: pygame.image.load('Schachfiguren\Chess_nlt45.svg'),
               Chessposition.ChessPieces.BlackPawn: pygame.image.load('Schachfiguren\Chess_pdt45.svg'),
               Chessposition.ChessPieces.WhitePawn: pygame.image.load('Schachfiguren\Chess_plt45.svg'),
               Chessposition.ChessPieces.WhiteQueen: pygame.image.load('Schachfiguren\Chess_qlt45.svg'),
               Chessposition.ChessPieces.BlackRook: pygame.image.load('Schachfiguren\Chess_rdt45.svg'),
               Chessposition.ChessPieces.WhiteRook: pygame.image.load('Schachfiguren\Chess_rlt45.svg'),}


def draw_cell(row,col,marked=False,lightlymarked=False,markedblue=False):
    if marked and lightlymarked:
        raise SyntaxError("Can't mark a cell and fully and only lightly at the same time")
    if marked or lightlymarked:
        markedblue=False
    red_tinge=RED_TINGE_AMMOUNT if marked else LIGHT_RED_TINGE_AMMOUNT if lightlymarked else 0
    blue_tinge=BLUE_TINGE_AMMOUNT if markedblue else 0
    color = (200+red_tinge-blue_tinge, 200-blue_tinge, 200+blue_tinge) if (row + col) % 2 == 0 else (100+red_tinge, 100, 100+blue_tinge)
    pygame.draw.rect(screen, color, (col * cell_size, row * cell_size, cell_size, cell_size))

def draw_board(
        cellmarked:bool, markedrow:int, markedcol:int, 
        othersquares_to_highlight: list[tuple[int,int]], 
        squares_to_highlight_blue: tuple[tuple[int,int],tuple[int,int]]
        )->None:
    if squares_to_highlight_blue is None:
        squares_to_highlight_blue=tuple()
    for row in range(rows):
        for col in range(cols):
            marked=cellmarked and markedrow==row and markedcol==col
            lightlymarked=cellmarked and ((row,col) in othersquares_to_highlight)
            markedblue=((row,col) in squares_to_highlight_blue)
            draw_cell(row,col,marked, lightlymarked,markedblue)

def draw_text(row: float, col: float, text: str) -> None:
    TEXT_COLOR=DARK_BLACK
    text_surface = font.render(text, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(col * cell_size + cell_size // 2, row * cell_size + cell_size // 2))
    screen.blit(text_surface, text_rect)

def draw_piece(row: int, col: int, piece: Chessposition.ChessPieces|None) -> None:
    if piece is None:
        return
    screen.blit(Piece_Images[piece], (col * cell_size, row * cell_size))
    

def draw_position(Position:Chessposition.ChessPosition) -> None:
    for row in range(8):
        for col in range(8):
            draw_piece(row, col, Position.Board[row][col])

def main(number_of_players:int, engine_depth:float=0, player_white:bool=True,delay:float=3):
    Position=Chessposition.ChessPosition()

    running = True
    PIECE_SELECTED=False
    selected_row=0
    selected_col=0
    Possible_Moves=[]
    lastmove:tuple[tuple[int,int],tuple[int,int]]=None
    Best_move_functions=[Chessposition.ChessPosition.eval_by_material,
                         Chessposition.ChessPosition.eval_by_placement,
                         Chessposition.ChessPosition.eval_without_depth]
    
    match number_of_players:
        case 2:
            Players_Turn=True
        case 1:
            Players_Turn=player_white
        case 0:
            Players_Turn=False
        case _:
            raise ValueError(f"number_of_players must be 0, 1 or 2.")
    time_of_last_move=time.perf_counter()
    game_active=True
    Result="Result not in yet"
    def makemove(startrow,startcol,endrow,endcol):
        nonlocal Position, lastmove, Players_Turn, time_of_last_move, game_active, Result
        Position=Position.applymove(startrow,startcol,endrow,endcol)
        lastmove=((startrow,startcol),(endrow,endcol))
        if number_of_players==1:
            Players_Turn=not Players_Turn
        time_of_last_move=time.perf_counter()
        if Position.is_game_over():
            game_active=False
            Result="CHECKMATE" if Position.is_check() else "DRAW"
        
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and Players_Turn and game_active:
                x, y = event.pos
                row, col = y // cell_size, x // cell_size
                piece=Position.Board[row][col]
                print(f"Clicked on {row}, {col}. Found a {piece}")
                if PIECE_SELECTED:
                    PIECE_SELECTED=False
                    if not (row==selected_row and col==selected_col):
                        if Position.move_is_legal(selected_row,selected_col,row,col,False):
                            makemove(selected_row,selected_col,row,col)
                        else:
                            print("not a legal move")
                    pass
                elif piece is not None:
                    selected_row=row
                    selected_col=col
                    PIECE_SELECTED=True
                    Possible_Moves=Position.new_pieces_possible_moves(selected_row,selected_col,False)
                    Possible_Moves=list(Possible_Moves)
        if not Players_Turn and time.perf_counter()-time_of_last_move>delay and game_active:
            #Position=Position.bestmove(engine_depth)
            lastmove=Position.bestmove(engine_depth)
            makemove(*lastmove[0],*lastmove[1])
        screen.fill((0, 0, 0))
        draw_board(PIECE_SELECTED,selected_row,selected_col,Possible_Moves,lastmove)
        draw_position(Position)
        if not game_active:
            draw_text(3.5,3.5,Result)
        pygame.display.flip()

    

if __name__=="__main__":
    main(1,engine_depth=1.9,delay=0.1)

pygame.quit()