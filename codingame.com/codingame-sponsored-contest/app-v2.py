import sys


KEY = {' ': 'A', 'A': 'B', 'B': 'C', 'C': 'D', 'D': 'E', 'E': 'E'}


def debug(message: str):
    print(message, file=sys.stderr)


def pretty_board(board: []):
    s = ''
    for row in board:
        s += '    ' + str(''.join(row)) + '\n'
    return s


def create_board(w: int, h: int, value, border=None) -> []:
    board = []
    for i in range(h):
        if i == 0 and border:
            board.append([border] * w)
        elif i == h - 1 and border:
            board.append([border] * w)
        else:
            if border:
                row = []
                row.append(border)
                row.extend([value] * (w-2))
                row.append(border)
                board.append(row)
            else:
                board.append([value] * w)
    return board


def main():
    width = int(input())
    height = int(input())
    third_init_input = int(input())

    board = create_board(width, height, ' ', border=' ')
    debug(f'board={len(board[0])}x{len(board)}')

    new_move = 'E'
    turn = 0
    while True:
        i1 = input()
        i2 = input()
        i3 = input()
        i4 = input()

        i_s = f'{i1}{i2}{i3}{i4}'

        p = [[0, 0]] * third_init_input
        d = [('', 0)] * (third_init_input - 1)
        which_move = 4
        valid_moves = []
        valid_c = '_'
        if i1 == valid_c:
            which_move = 0
            valid_moves.append('A')
        elif i2 == valid_c:
            which_move = 1
            valid_moves.append('B')
        elif i3 == valid_c:
            which_move = 2
            valid_moves.append('C')
        elif i4 == valid_c:
            which_move = 3
            valid_moves.append('D')

        for i in range(third_init_input):
            p[i] = [int(j) for j in input().split()]
            y, x = p[i]
            if i == which_move:
                new_move = KEY[board[y][x]]
                board[y][x] = new_move
            else:
                board[y][x] = KEY[board[y][x]]

        min_move = 4, 99999
        max_move = 4, -1
        for i in range(third_init_input - 1):
            d[i] = 'ABCDE'[i], abs(p[i][0] - p[4][0]) + abs(p[i][1] - p[4][1])
            if d[i][1] < min_move[1]:
                min_move = i, d[i][1]
            if d[i][1] > max_move[1]:
                max_move = i, d[i][1]

        d.sort(key=lambda t: t[1], reverse=True)

        choice = 'E'
        if d[3][1] != 1 or i_s == '#__#':
            choice_int = 4
            for x in d:
                # if x[0] in valid_moves:
                if x[0]:
                    choice = x[0]
                    # choice_int = x[0]
                    break

        # choice = 'ABCDE'[choice_int]

        debug(i_s)
        debug(f'choice={choice}')
        debug(f'd={d}')
        debug(f'board=\n{pretty_board(board)}')

        print(choice)
        # print(new_move)
        # print('ABCDE'[turn % 5])
        turn += 1


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # e = sys.exc_info()[0]
        debug(f'e={e}')
        debug(f'e={repr(e)}')
    finally:
        debug(f'STOP')




