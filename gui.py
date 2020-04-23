from itertools import product

import pygame
from pygame import Surface

from src.ai import AI, PositionEvaluation
from src.boardstate import BoardState


def draw_board(screen: Surface, pos_x: int, pos_y: int, elem_size: int, board: BoardState):
    dark = (0, 0, 0)
    white = (200, 200, 200)

    for y, x in product(range(8), range(8)):
        color = white if (x + y) % 2 == 0 else dark
        position = pos_x + x * elem_size, pos_y + y * elem_size, elem_size, elem_size
        pygame.draw.rect(screen, color, position)

        figure = board.board[y, x]

        if figure == 0:
            continue

        if figure > 0:
            figure_color = 255, 255, 255
        else:
            figure_color = 100, 100, 100
        r = elem_size // 2 - 10

        pygame.draw.circle(screen, figure_color, (position[0] + elem_size // 2, position[1] + elem_size // 2), r)
        if abs(figure) == 2:
            r = 5
            negative_color = [255 - e for e in figure_color]
            pygame.draw.circle(screen, negative_color, (position[0] + elem_size // 2, position[1] + elem_size // 2), r)


def equal_boards(board_a:BoardState, board_b: BoardState) -> 'bool':
    for i in range(0, 8):
        for j in range(0, 8):
            if board_a.board[i, j] != board_b.board[i, j] and board_a.board[i, j] * board_a.current_player > 0:
                return False
    return True


def verify_loop(start_board: BoardState, finish_board: BoardState, from_x, from_y) -> 'BoardState':
    states = start_board.unit_move(from_x, from_y)
    for state in states:
        if equal_boards(finish_board, state):
            return state
    return None


def save_state(state: BoardState):
    f = open('savegame.txt', 'w')
    for i in range(8):
        for j in range(8):
            f.write(str(state.board[i, j]) + " ")
        f.write('\n')
    f.write(str(state.current_player) + " " + str(state.cnt_white) + " " +
            str(state.cnt_white))
    f.close()


def get_state() -> BoardState:
    f = open("savegame.txt", 'r')
    result = BoardState.initial_state()
    cur = f.read().split('\n')
    for i in range(8):
        line = cur[i].split(' ')
        for j in range(8):
            result.board[i, j] = int(line[j])
    line = cur[8].split(' ')
    f.close()
    result.current_player = int(line[0])
    result.cnt_white = int(line[1])
    result.cnt_black = int(line[2])
    return result


def game_loop(screen: Surface, board: BoardState, ai: AI):
    grid_size = screen.get_size()[0] // 8
    states = []
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click_position = event.pos

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                new_x, new_y = [p // grid_size for p in event.pos]
                old_x, old_y = [p // grid_size for p in mouse_click_position]

                new_board = board.do_move(old_x, old_y, new_x, new_y)
                if new_board is not None:
                    next_state = verify_loop(board, new_board, old_x, old_y)
                    if next_state is not None:
                        states.append(board)
                        board = next_state
                        board.current_player *= -1

            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                x, y = [p // grid_size for p in event.pos]
                board.board[y, x] = (board.board[y, x] + 1 + 2) % 5 - 2  # change figure

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    board = states.pop()

                if event.key == pygame.K_s:
                    save_state(board)

                if event.key == pygame.K_l:
                    board = get_state()

                if event.key == pygame.K_r:
                    board = board.inverted()

                if event.key == pygame.K_SPACE:
                    new_board = ai.next_move(board)
                    if new_board is not None:
                        states.append(board)
                        board = new_board
                        board.current_player *= -1

        draw_board(screen, 0, 0, grid_size, board)
        pygame.display.flip()
        if board.is_game_finished:
            print("White win") if board.get_winner == 1 else print("Black win")
            return


pygame.init()

screen: Surface = pygame.display.set_mode([512, 512])
ai = AI(PositionEvaluation(), search_depth=4)

game_loop(screen, BoardState.initial_state(), ai)

pygame.quit()
