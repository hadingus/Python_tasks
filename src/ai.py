from typing import Optional
from random import randint

from .boardstate import BoardState


class PositionEvaluation:
    def __call__(self, board: BoardState) -> int:
        result = (board.cnt_white - board.cnt_black) * 10
        for x in range(8):
            for y in range(8):
                if abs(board.board[x, y]) == 1:
                    if board.board[x, y] < 0:
                        result += board.board[x, y] * (x + 1)
                    else:
                        result += board.board[x, y] * (8 - x)
                else:
                    result += board.board[x, y] * 8
        return result


class AI:
    def __init__(self, position_evaluation: PositionEvaluation, search_depth: int):
        self.position_evaluation: PositionEvaluation = position_evaluation
        self.depth = search_depth

    def dfs(self, state: BoardState, rec_depth, player):
        if rec_depth == self.depth:
            return [state, self.position_evaluation(state)]
        moves = state.get_possible_moves()
        min_val = 1000
        min_state = None
        max_state = None
        max_val = -1000
        for nxt_state in moves:
            current_res = self.dfs(nxt_state, rec_depth + 1, player)
            if current_res[1] > max_val or (current_res[1] == max_val and randint(0, 1)):
                max_val = current_res[1]
                max_state = nxt_state
            if current_res[1] < min_val or (current_res[1] == min_val and randint(0, 1)):
                min_val = current_res[1]
                min_state = nxt_state
        if player == 1:
            return [max_state, max_val] if rec_depth % 2 == 0 else [min_state, min_val]
        else:
            return [max_state, max_val] if rec_depth % 2 == 1 else [min_state, min_val]

    def next_move(self, board: BoardState) -> Optional[BoardState]:
        moves = board.get_possible_moves()
        if len(moves) == 0:
            return None
        result = self.dfs(board, 0, board.current_player)
        return result[0]
