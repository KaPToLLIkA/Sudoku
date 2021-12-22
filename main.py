from copy import deepcopy
import sys
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
        self.git = Git(self)

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

        if value < 1 or value > 9:
            print(f'Value must be in range [1; 9]')
            return

        if 0 <= x <= 8 and 0 <= y <= 8:
            if not self.__check_segment(x, y, value) \
                    and not self.__check_row(y, value) \
                    and not self.__check_column(x, value):
                if self.unsolved[y][x] != value:
                    print(f'Set value at x:{x + 1} y:{y + 1}')
                    if self.unsolved[y][x] == 0:
                        self.zeros -= 1
                        self.git.index.stage_zero(-1)
                    self.unsolved[y][x] = value
                    self.git.index.stage_insert([x, y, value])
                else:
                    print(f'No effect')
            else:
                print('Wrong answer')
                print(f'Duplicate at x:{self.duplicate_pos[0] + 1} y:{self.duplicate_pos[1] + 1}')
                self.wrong += 1
                self.git.index.stage_wrong(1)
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
                self.git.index.stage_delete([x, y, 0])
                self.git.index.stage_zero(1)
            else:
                print(f'No effect')
        else:
            print('Wrong indexes')

    def cmd_log(self, args):
        self.git.log(args)

    def cmd_redo(self, args):
        self.git.redo(args)

    def cmd_undo(self, args):
        self.git.undo(args)

    def cmd_commit(self, args):
        self.git.commit(args[0])

    def save(self):
        with open(self.file_name, 'w') as f:
            for row in self.unsolved:
                f.write(f'{",".join(list(map(lambda x: str(x), row)))}\n')
            f.write(f'{self.zeros},{self.wrong}\n')

    def load(self, file_name):
        self.file_name = file_name
        try:
            with open(file_name, 'r') as f:
                self.unsolved = []
                for i in range(0, 9):
                    self.unsolved.append(list(map(lambda x: int(x), f.readline().split(','))))
                other = list(map(lambda x: int(x), f.readline().split(',')))
                self.zeros = other[0]
                self.wrong = other[1]
        except FileNotFoundError:
            pass


def safe_get_int_in_range(min_inclusive: int, max_exclusive: int):
    while True:
        try:
            value = int(input())
            if min_inclusive <= value < max_exclusive:
                return value
            else:
                print(f'Value not in range [{min_inclusive};{max_exclusive})')
        except ValueError:
            print(f'Value must be int')


class Commit:
    def __init__(self, p_id, name: str):
        self.name = name
        self.inserted = []
        self.deleted = []
        self.d_wrong = 0
        self.d_zero = 0
        self.p_id = p_id
        self.c_ids = []

    def stage_insert(self, insert):
        for rem in self.deleted:
            if rem[0] == insert[0] and rem[1] == insert[1]:
                self.deleted.remove(rem)
        for ins in self.inserted:
            if set(ins) == set(insert):
                return
        for ins in self.inserted:
            if ins[0] == insert[0] and ins[1] == insert[1]:
                ins[2] = insert[2]
                return
        self.inserted.append(insert)

    def stage_delete(self, delete):
        for ins in self.inserted:
            if ins[0] == delete[0] and ins[1] == delete[1]:
                self.inserted.remove(ins)
        for rem in self.deleted:
            if set(rem) == set(delete):
                return
        for rem in self.deleted:
            if rem[0] == delete[0] and rem[1] == delete[1]:
                rem[2] = delete[2]
                return
        self.deleted.append(delete)

    def stage_wrong(self, wrong):
        self.d_wrong += wrong

    def stage_zero(self, zero):
        self.d_zero += zero

    def __str__(self):
        return f'Parent: {self.p_id:5} DWrong: {self.d_wrong: 5} DZeros: {self.d_zero:5} ' \
               f'Inserted: {self.inserted} Removed: {self.deleted}'


class Git:
    def __init__(self, game: Game):
        self.commits = [Commit(-1, 'init')]
        self.index = Commit(-1, 'index')
        self.head = 0
        self.game = game
        self.last_state_file = 'state.dt'
        self.git = 'git.dt'
        self.game.load(self.last_state_file)

    def revert_index(self):
        # undo index changes
        for ins in self.index.inserted:
            self.game.unsolved[ins[0]][ins[1]] = 0
        for rem in self.index.deleted:
            self.game.unsolved[rem[0]][rem[1]] = rem[2]
        self.game.wrong -= self.index.d_wrong
        self.game.zeros -= self.index.d_zero
        self.index = Commit(-1, 'index')

    def undo(self, args):
        cur_commit = self.commits[self.head]

        if cur_commit.p_id == -1:
            print(f'Root of tree... head_id {self.head} p_id {cur_commit.p_id}')
            return

        self.revert_index()

        for ins in cur_commit.inserted:
            self.game.unsolved[ins[0]][ins[1]] = 0
        for rem in cur_commit.deleted:
            self.game.unsolved[rem[0]][rem[1]] = rem[2]
        self.game.wrong -= cur_commit.d_wrong
        self.game.zeros -= cur_commit.d_zero

        self.head = self.commits[self.head].p_id

    def log(self, args):
        for commit in self.commits:
            print(f'[{self.commits.index(commit)}] {commit}')
        print(f'HEAD: {self.head}\n'
              f'INDEX:\n====\n{self.index}\n'
              f'====')

    def redo(self, args):
        count = len(self.commits[self.head].c_ids)
        if count > 0:
            if count == 1:
                next_head = self.commits[self.head].c_ids[0]
                next_commit = self.commits[next_head]
            else:
                print(f'You should choose commit... print index to select:')
                for i in range(0, count):
                    print(f'[{i}] commit name: {self.commits[self.commits[self.head].c_ids[i]].name}')
                next_id = safe_get_int_in_range(0, count)
                next_head = self.commits[self.head].c_ids[next_id]
                next_commit = self.commits[next_head]

            self.revert_index()

            # apply commit changes
            for ins in next_commit.inserted:
                self.game.unsolved[ins[0]][ins[1]] = ins[2]
            for rem in next_commit.deleted:
                self.game.unsolved[rem[0]][rem[1]] = 0
            self.game.wrong += next_commit.d_wrong
            self.game.zeros += next_commit.d_zero

            self.head = next_head
        else:
            print(f'End of tree... head_id {self.head} leaf_count: {count}')

    def commit(self, name):
        self.index.p_id = self.head
        self.index.name = name
        self.commits[self.head].c_ids.append(len(self.commits))
        self.commits.append(self.index)
        self.head = len(self.commits) - 1
        self.index = Commit(-1, 'index')
        print(f'Commited:\n====\n{self.commits[self.head]}\n====')


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
            'c': self.game.cmd_commit,
            'u': self.game.cmd_undo,
            'r': self.game.cmd_redo,
            'l': self.game.cmd_log,
        }

        for key, value in commands.items():
            if key == cmd_type:
                value(args)

    def cmd_exit(self, args):
        self.game.save()
        sys.exit(0)


w = Window()
w.run()
