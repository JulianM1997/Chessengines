import pygame
import Chessposition

pygame.init()

size = 400
rows, cols = 8, 8
cell_size = size // rows
screen = pygame.display.set_mode((size, size))
font = pygame.font.Font(None, 36)
WHITE = (200, 200, 200)
BLACK = (100, 100, 100)
RED_TINGE=50
FRAMETHICKNESS_WHEN_MARKED=5
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


def draw_cell(row,col,marked=False):
    red_tinge=RED_TINGE if marked else 0
    color = (200+red_tinge, 200, 200) if (row + col) % 2 == 0 else (100+red_tinge, 100, 100)
    pygame.draw.rect(screen, color, (col * cell_size, row * cell_size, cell_size, cell_size))

def draw_board(cellmarked:bool, markedrow:int ,markedcol:int)->None:
    for row in range(rows):
        for col in range(cols):
            draw_cell(row,col,cellmarked and markedrow==row and markedcol==col)

def draw_text(row: int, col: int, text: str) -> None:
    TEXT_COLOR=BLACK
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


Position=Chessposition.ChessPosition()

running = True
PIECE_SELECTED=False
selected_row=0
selected_col=0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            row, col = y // cell_size, x // cell_size
            piece=Position.Board[row][col]
            print(f"Clicked on {row}, {col}. Found a {piece}")
            if PIECE_SELECTED:
                PIECE_SELECTED=False
                pass
            else:
                selected_row=row
                selected_col=col
                PIECE_SELECTED=True
    screen.fill((0, 0, 0))
    draw_board(PIECE_SELECTED,selected_row,selected_col)
    draw_position(Position)
    pygame.display.flip()

pygame.quit()