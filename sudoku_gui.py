from copy import deepcopy
import sys
import os
import random


def generate():
    solved = [
        [4, 6, 3, 1, 8, 2, 9, 7, 5],
        [5, 8, 7, 4, 6, 9, 1, 2, 3],
        [9, 2, 1, 3, 5, 7, 8, 6, 4],
        [2, 4, 8, 6, 7, 1, 3, 5, 9],
        [7, 5, 9, 2, 4, 3, 6, 1, 8],
        [1, 3, 6, 5, 9, 8, 7, 4, 2],
        [3, 7, 5, 9, 2, 6, 4, 8, 1],
        [8, 1, 4, 7, 3, 5, 2, 9, 6],
        [6, 9, 2, 8, 1, 4, 5, 3, 7],
    ]

    unsolved = deepcopy(solved)

    for i in range(0, 60):
        while True:
            y = random.randint(0, 8)
            x = random.randint(0, 8)
            if unsolved[y][x] != 0:
                unsolved[y][x] = 0
                break

    return solved, unsolved


def count_zeros(field):
    count = 0
    for y in range(0, 9):
        for x in range(0, 9):
            if field[y][x] == 0:
                count += 1
    return count


class Game:
    def __init__(self):
        boards = generate()
        self.solved = boards[0]
        self.unsolved = boards[1]
        self.wrong = 0
        self.zeros = count_zeros(self.unsolved)
        self.duplicate_pos = [0, 0]

    def __check_segment(self, ix, iy, value: int):
        sx = ix // 3
        sy = iy // 3
        for y in range(sy * 3, sy * 3 + 3):
            for x in range(sx * 3, sx * 3 + 3):
                if self.unsolved[y][x] == value:
                    self.duplicate_pos = [x, y]
                    return True
        return False

    def __check_row(self, iy, value: int):
        for x in range(0, 9):
            if self.unsolved[iy][x] == value:
                self.duplicate_pos = [x, iy]
                return True
        return False

    def __check_column(self, ix, value: int):
        for y in range(0, 9):
            if self.unsolved[y][ix] == value:
                self.duplicate_pos = [ix, y]
                return True
        return False

    def draw(self):
        h = '-'
        v = '|'
        b = self.unsolved
        print(f'Y \\ X '
              f'{" ".join(map(lambda s: str(s), range(1,4)))}   '
              f'{" ".join(map(lambda s: str(s), range(4,7)))}   '
              f'{" ".join(map(lambda s: str(s), range(7,10)))}')
        for y in range(0, 9):
            if y % 3 == 0:
                print(f'{" " * 4}{h * 25}')
            print(f'[{y + 1}] ', end='')
            for x in range(0, 9):
                if x % 3 == 0:
                    print(f'{v} ', end='')
                print(f'{" " if b[y][x] == 0 else b[y][x]} ', end='')
            print(f'{v}')
        print(f'{" " * 4}{h * 25}')
        print('Info: ')
        print(f'Wrong: {self.wrong}')
        print(f'Empty: {self.zeros}')

    def cmd_set_value_at(self, args):
        if len(args) != 3:
            print('Wrong command')
            return
        int_args = None
        try:
            int_args = list(map(lambda x: int(x), args))
        except ValueError:
            print('Wrong indexes')
            return

        x = int_args[0] - 1
        y = int_args[1] - 1
        value = int_args[2]

        if 0 <= x <= 8 and 0 <= y <= 8:
            if not self.__check_segment(x, y, value) \
                    and not self.__check_row(y, value) \
                    and not self.__check_column(x, value):
                if self.unsolved[y][x] == 0:
                    print(f'Set value at x:{x + 1} y:{y + 1}')
                    self.unsolved[y][x] = value
                    self.zeros -= 1
                else:
                    print(f'No effect')
            else:
                print('Wrong answer')
                print(f'Duplicate at x:{self.duplicate_pos[0] + 1} y:{self.duplicate_pos[1] + 1}')
                self.wrong += 1
        else:
            print('Wrong indexes')

    def cmd_del_value_at(self, args):
        if len(args) != 2:
            print('Wrong command')
            return
        int_args = None
        try:
            int_args = list(map(lambda x: int(x), args))
        except ValueError:
            print('Wrong indexes')
            return

        x = int_args[0] - 1
        y = int_args[1] - 1

        if 0 <= x <= 8 and 0 <= y <= 8:
            if self.unsolved[y][x] != 0:
                self.unsolved[y][x] = 0
                self.zeros += 1
            else:
                print(f'No effect')
        else:
            print('Wrong indexes')


class Window:
    def __init__(self):
        self.game = Game()

    def run(self):
        while True:
            self.game.draw()
            self.check_win()
            self.cmd_parse(input("Command: "))
            print('\n'*5)

    def check_win(self):
        if self.game.zeros == 0:
            print('You win!')

    def cmd_parse(self, cmd: str):
        seq = cmd.split(' ')
        cmd_type = seq[0]
        args = seq[1:]
        
        commands = {
            's': self.game.cmd_set_value_at,
            'd': self.game.cmd_del_value_at,
            'e': self.cmd_exit,
        }

        for key, value in commands.items():
            if key == cmd_type:
                value(args)

    def cmd_exit(self, args):
        sys.exit(0)


w = Window()
w.run()
