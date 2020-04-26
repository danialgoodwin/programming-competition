"""
If only 'A':
- TC1: score=16, turns=90, init=35,28,5,

If only 'B':
- TC1: score=2, turns=97, init=35,28,5

"""

import sys
import math

board = []

min_1, max_1 = None, None
min_2, max_2 = None, None
min_3, max_3 = None, None
min_4, max_4 = None, None
min_5, max_5 = None, None
min_6, max_6 = None, None

i1s = []
i2s = []
i3s = []
i4s = []
i5s = []
i6s = []


def debug(message: str):
    print(message, file=sys.stderr)


def debug_board(board: []):
    s = ''
    for row in board:
        s += str(row) + '\n'
    print(s, file=sys.stderr)


def main():
    global min_1, min_2, max_6, min_3, min_4, min_5, min_6, max_1, max_2, max_3, max_4, max_5
    first_init_input = int(input())
    second_init_input = int(input())
    third_init_input = int(input())

    debug(f'first_init_input={first_init_input}')
    debug(f'second_init_input={second_init_input}')
    debug(f'third_init_input={third_init_input}')
    board_all = [[''] for x in range(first_init_input)] * second_init_input

    i1s = []
    i2s = []
    i3s = []
    i4s = []
    i5s = [[''] for x in range(third_init_input)]
    i6s = [[''] for x in range(third_init_input)]

    turn = 0
    while True:
        first_input = input()
        second_input = input()
        third_input = input()
        fourth_input = input()
        debug(f'\nturn={turn}')
        for i in range(third_init_input):
            fifth_input, sixth_input = [int(j) for j in input().split()]
            debug(f'fifth_input={fifth_input}, sixth_input={sixth_input}')
            i5s[i].append(fifth_input)
            i6s[i].append(sixth_input)
            min_5 = min(min_5, fifth_input) if min_5 else fifth_input
            min_6 = min(min_6, sixth_input) if min_6 else sixth_input
            max_5 = max(max_5, fifth_input) if max_5 else fifth_input
            max_6 = max(max_6, sixth_input) if max_6 else sixth_input

        # min_1 = min(min_1, first_input) if min_1 else first_input
        # min_2 = min(min_2, second_input) if min_2 else second_input
        # min_3 = min(min_3, third_input) if min_3 else third_input
        # min_4 = min(min_4, fourth_input) if min_4 else fourth_input
        # max_1 = max(max_1, first_input) if min_1 else first_input
        # max_2 = max(max_2, second_input) if min_2 else second_input
        # max_3 = max(max_3, third_input) if min_3 else third_input
        # max_4 = max(max_4, fourth_input) if min_4 else fourth_input

        i1s.append(first_input)
        i2s.append(second_input)
        i3s.append(third_input)
        i4s.append(fourth_input)

        # debug(f'range_1=({max_1}, {max_1})')
        # debug(f'range_2=({max_2}, {max_2})')
        # debug(f'range_3=({max_3}, {max_3})')
        # debug(f'range_4=({max_4}, {max_4})')
        debug(f'range_5=({max_5}, {max_5})')
        debug(f'range_6=({max_6}, {max_6})')
        debug(f'i1s={i1s}')
        debug(f'i2s={i2s}')
        debug(f'i3s={i3s}')
        debug(f'i4s={i4s}')
        debug(f'i5s={debug_board(i5s)}')
        debug(f'i6s={debug_board(i6s)}')

        print("A")

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
