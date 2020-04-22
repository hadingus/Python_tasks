import numpy as np
from typing import Optional, List
from queue import Queue


def val_pos(x, y) -> 'bool':
    if x < 0 or y < 0 or x > 7 or y > 7:
        return False
    return True


def normalize(x) -> 'int':
    if x == 0:
        return x
    return x / abs(x)


class BoardState:
    directions = [[-1, -1, ], [-1, 1],
                  [1, -1], [1, 1]]

    def __init__(self, board: object, current_player: object = 1) -> object:
        self.board: np.ndarray = board
        self.current_player: int = current_player
        self.cnt_black = 12
        self.cnt_white = 12

    def inverted(self) -> 'BoardState':
        return BoardState(board=self.board[::-1, ::-1] * -1, current_player=self.current_player * -1)

    def copy(self) -> 'BoardState':
        result = BoardState(self.board.copy(), self.current_player)
        result.cnt_white = self.cnt_white
        result.cnt_black = self.cnt_black
        return result

    def do_move(self, from_x, from_y, to_x, to_y) -> Optional['BoardState']:
        """
        :return: new BoardState or None for invalid move
        """
        if from_x == to_x and from_y == to_y:
            return None  # invalid move

        if (to_x + to_y) % 2 == 0:
            return None

        if not (val_pos(to_x, to_y)):
            return None

        if self.board[to_y, to_x] != 0:
            return None

        if abs(self.board[from_y, from_x]) == 1:
            if ((self.current_player == 1 and to_y == from_y + 1) or
                    (self.current_player == -1 and to_y == from_y - 1)):
                return None

        result = self.copy()
        result.board[to_y, to_x] = result.board[from_y, from_x]
        result.board[from_y, from_x] = 0

        if abs(result.board[to_y, to_x]) == 1:
            if ((result.board[to_y, to_x] > 0 and to_y == 0) or
                    (result.board[to_y, to_x] < 0 and to_y == 7)):
                result.board[to_y, to_x] *= 2

        return result

    def diag_move(self, from_x, from_y, to_x, to_y, id_dir):
        killed_white = 0
        killed_black = 0
        dx = self.directions[id_dir][0]
        dy = self.directions[id_dir][1]
        cur_x = from_x + dx
        cur_y = from_y + dy
        res_state = self.do_move(from_x, from_y, to_x, to_y)
        if res_state is None:
            return None
        while cur_x != to_x and cur_y != to_y:
            if self.board[cur_y, cur_x] < 0:
                if self.current_player == -1:
                    return None
                killed_black += 1
                res_state.cnt_black -= 1
            elif self.board[cur_y, cur_x] > 0:
                if self.current_player == 1:
                    return None
                killed_white += 1
                res_state.cnt_white -= 1
            res_state.board[cur_y, cur_x] = 0
            cur_x += dx
            cur_y += dy
        if self.current_player == 1:
            killed = killed_black
        else:
            killed = killed_white
        return [res_state, killed, to_x, to_y]

    def once_unit_move(self, from_x, from_y, dif):
        result = []

        for length in range(1, dif + 1):
            for d in range(0, 4):
                dx = length * self.directions[d][0]
                dy = length * self.directions[d][1]

                to_x = from_x + dx
                to_y = from_y + dy
                cur = self.diag_move(from_x, from_y, to_x, to_y, d)
                if cur is None:
                    continue
                result.append(cur)
        return result

    def unit_move(self, from_x, from_y) -> List['BoardState']:
        result = []
        states_q = Queue()
        states_q.put((self.copy(), from_x, from_y, True))
        while not states_q.empty() != 0:
            current = states_q.get()
            current_state: BoardState = current[0]
            cur_x = current[1]
            cur_y = current[2]
            valid = current[3]
            new_states = []
            unit_id = abs(current_state.board[cur_y, cur_x])
            if unit_id == 2:
                new_states.extend(current_state.once_unit_move(cur_x, cur_y, 9))
            else:
                new_states.extend(current_state.once_unit_move(cur_x, cur_y, 2))
            cnt_added = 0
            for state in new_states:
                if (unit_id == 1) and (state[1] == 0) and (abs(state[2] - cur_x) > 1):
                    continue
                if valid and state[1] == 0:
                    result.append(state[0])
                if state[1] > 0:
                    states_q.put([state[0], state[2], state[3], False])
                    cnt_added += 1
            if not valid and (cnt_added == 0):
                result.append(current_state)
        return result

    def get_possible_moves(self) -> List['BoardState']:
        result = []
        for y in range(0, 8):
            for x in range(0, 8):
                if self.board[y, x] * self.current_player > 0:
                    current_states = self.unit_move(x, y)
                    if current_states is None:
                        continue
                    for state in current_states:
                        result.append(state)
        return result

    @property
    def is_game_finished(self) -> bool:
        if self.cnt_black == 0 or self.cnt_white == 0:
            return True
        else:
            return False

    @property
    def get_winner(self) -> Optional[int]:
        if self.cnt_black == 0:
            return 1
        else:
            return -1

    @staticmethod
    def initial_state() -> 'BoardState':
        board = np.zeros(shape=(8, 8), dtype=np.int8)

        for x in range(3):
            for y in range(8):
                if (x + y) % 2 is 0:
                    board[x + 5, y] = 1
                else:
                    board[x, y] = -1

        return BoardState(board, 1)
