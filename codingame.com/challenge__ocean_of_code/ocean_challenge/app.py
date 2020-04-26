import logging
# import math
import random
import sys
from collections import Counter
from typing import Optional

logging.basicConfig(level=logging.DEBUG)

STARTING_HEALTH = 6
MAX_RECURSION = 7  # Arbitrary-ish
TORPEDO_RANGE = 4
shootable_torpedo_distances = [*range(-TORPEDO_RANGE, -1), *range(2, TORPEDO_RANGE + 1)]

SILENCE_RANGE = 4

POWER_TORPEDO = 'TORPEDO'
POWER_SONAR = 'SONAR'
POWER_MINE = 'MINE'
POWER_SILENCE = 'SILENCE'
ACTION_TRIGGER = 'TRIGGER'
ACTION_SURFACE = 'SURFACE'
ACTION_MOVE = 'MOVE'


def test_1():
    return 1


def move_via_direction(start_x, start_y, direction: str, range) -> (int, int):
    if direction == 'N': return start_x, start_y - range
    if direction == 'S': return start_x, start_y + range
    if direction == 'E': return start_x + range, start_y
    return start_x, start_y


class Tree:
    def __init__(self, height: int = 1):
        self.x = None
        self.y = None
        self.height: int = height
        self.north: Optional[Tree] = None
        self.south: Optional[Tree] = None
        self.east: Optional[Tree] = None
        self.west: Optional[Tree] = None

    def __str__(self):
        return f'\n{" " * (MAX_RECURSION - self.height)}Tree(x={self.x}, y={self.y}, height={self.height}, north={self.north}, south={self.south}, east={self.east}, west={self.west})'


class Dan:
    def __init__(self, water: [], x, y):
        tree = Tree()
        tree.x = x
        tree.y = y
        self.position = tree
        self.water = water
        self.available = copy_board(water)
        self.available[self.position.y][self.position.x] = False
        self.torpedo_position = None
        self.health = STARTING_HEALTH
        self.torpedo_cooldown = -1
        self.sonar_cooldown = -1
        self.silence_cooldown = -1
        self.mine_cooldown = -1
        self.is_used_sonar = False
        self.is_hit = False

    def move(self, x, y):
        self.position.x = x
        self.position.y = y
        self.available[y][x] = False

    def surface(self):
        self.available = copy_board(self.water)
        self.available[self.position.y][self.position.x] = False

    def is_move_available(self, x, y):
        return self.available[y][x]

    def torpedo(self, x, y):
        self.torpedo_position = (x, y)

    def choose_power_to_charge(self) -> str:
        if not self.is_used_sonar and self.sonar_cooldown: return POWER_SONAR
        if self.torpedo_cooldown: return POWER_TORPEDO
        if self.silence_cooldown: return POWER_SILENCE
        return POWER_MINE

    def maybe_silence(self, opp_potential_positions: []) -> (str, int):
        if self.silence_cooldown: return None, None
        if not self.is_hit: return None, None
        # TODOv2: Maybe improve - move towards opponent
        opp_position = opp_potential_positions[0]
        x_distance = abs(self.position.x - opp_position[0])
        opp_direction = 'W' if self.position.x > opp_position[0] else 'E'
        y_distance = abs(self.position.y - opp_position[1])
        if y_distance > x_distance:
            opp_direction = 'S' if self.position.y > opp_position[1] else 'N'
        # TODOv2: Maybe improve - moving always SILENCE_RANGE
        return opp_direction, SILENCE_RANGE

    # TODO: Improve
    def maybe_sonar(self, opp_potential_positions: []) -> Optional[int]:
        if self.sonar_cooldown: return None
        if len(opp_potential_positions) > 4: return None  # Arbitrary value
        # counts = Counter()
        opp_position = opp_potential_positions[0]
        return get_sector(opp_position[0], opp_position[1])


class Opponent:
    def __init__(self, water):
        self.water = water
        self.w = len(water[0])
        self.h = len(water)
        self.health = STARTING_HEALTH
        positions = []
        for j in range(len(water)):
            for i in range(len(water[0])):
                if water[j][i]:
                    positions.append((i, j))
        self.possible_positions = positions

    def is_water(self, x, y):
        if x < 0 or x >= self.w or y < 0 or y >= self.h:
            return False
        return self.water[y][x]

    def moved(self, direction):
        new_possible_positions = []
        if direction == 'N':
            for p in self.possible_positions:
                y = p[1] - 1
                if y >= 0 and self.water[y][p[0]]:
                    new_possible_positions.append((p[0], y))
        elif direction == 'S':
            for p in self.possible_positions:
                y = p[1] + 1
                if y < self.h and self.water[y][p[0]]:
                    new_possible_positions.append((p[0], y))
        elif direction == 'E':
            for p in self.possible_positions:
                x = p[0] + 1
                if x < self.w and self.water[p[1]][x]:
                    new_possible_positions.append((x, p[1]))
        elif direction == 'W':
            for p in self.possible_positions:
                x = p[0] - 1
                if x >= 0 and self.water[p[1]][x]:
                    new_possible_positions.append((x, p[1]))
        self.possible_positions = new_possible_positions

    def surfaced(self, sector):
        sector = int(sector)
        valid_x_min = ((sector - 1) % 3) * 5
        valid_x_max = valid_x_min + 4
        valid_y_min = ((sector - 1) // 3) * 5
        valid_y_max = valid_y_min + 4
        positions = []
        for p in self.possible_positions:
            if p[0] < valid_x_min or p[0] > valid_x_max or p[1] < valid_y_min or p[1] > valid_y_max:
                continue
            positions.append(p)
        self.possible_positions = positions

    def used_torpedo(self, x, y):
        positions = []
        for p in self.possible_positions:
            if distance(x, y, p[0], p[1]) <= TORPEDO_RANGE:
                positions.append(p)
        self.possible_positions = positions

    def silenced(self):
        def silenced_possibilities(x, y) -> []:
            possibilities = []
            ranges = range(-SILENCE_RANGE, SILENCE_RANGE + 1)
            for i in ranges:
                for j in ranges:
                    if self.is_water(x + i, y + j):
                        possibilities.append((x + i, y + j))
            return possibilities

        positions = []
        for p in self.possible_positions:
            positions.extend(silenced_possibilities(p[0], p[1]))
        self.possible_positions = positions

    def is_possible_position(self, x, y):
        for p in self.possible_positions:
            if p[0] == x and p[1] == y:
                return True
        return False

    def direct_hit(self, x, y, direction):
        self.possible_positions = [(x, y)]
        self.moved(direction)

    def indirect_hit(self, x, y, direction):
        positions = []
        for p in self.possible_positions:
            pass
        # TODO
        return positions

    def get_possible_positions_in_torpedo_range(self, x, y) -> []:
        positions = []
        for p in self.possible_positions:
            if distance(p[0], p[1], x, y) <= TORPEDO_RANGE:
                positions.append(p)
        positions.sort(key=lambda p: distance(p[0], p[1], x, y), reverse=True)
        return positions


class Game:
    def __init__(self, water, x, y):
        self.water = water
        self.dan = Dan(water, x, y)
        self.opp = Opponent(water)
        self.width = len(water[0])
        self.height = len(water)

    def debug(self, message: str):
        print(f'({self.dan.position.x}, {self.dan.position.y}): {message}', file=sys.stderr)

    def update_opponent_position(self, opponent_orders: str, water_board, is_opp_direct_hit, is_opp_hit):
        opp_actions = opponent_orders.split('|')
        direction = None
        sector = None
        is_use_mine = False
        is_initial_move = False
        if len(opp_actions) == 1 and len(opp_actions[0]) == 3:
            is_initial_move = True
        for action in opp_actions:
            tokens = action.split()
            if tokens[0] == ACTION_MOVE:
                direction = tokens[1]
            elif tokens[0] == ACTION_SURFACE:
                sector = tokens[1]
            elif tokens[0] == ACTION_TRIGGER:
                trigger_x = tokens[1]
                trigger_y = tokens[2]
            elif tokens[0] == POWER_TORPEDO:
                opp_torpedo_x = tokens[1]
                opp_torpedo_y = tokens[2]
                self.opp.used_torpedo(opp_torpedo_x, opp_torpedo_y)
            elif tokens[0] == POWER_SONAR:
                sonar_sector = tokens[1]
            elif tokens[0] == POWER_SILENCE:
                self.opp.silenced()
            elif tokens[0] == POWER_MINE:
                is_use_mine = True

        if is_opp_direct_hit:
            torpedo_x = self.dan.torpedo_position[0]
            torpedo_y = self.dan.torpedo_position[1]
            self.opp.direct_hit(torpedo_x, torpedo_y, direction)
        elif is_opp_hit:
            torpedo_x = self.dan.torpedo_position[0]
            torpedo_y = self.dan.torpedo_position[1]
            self.opp.indirect_hit(torpedo_x, torpedo_y, direction)
        elif sector:
            self.opp.surfaced(int(sector))
        elif direction:
            self.opp.moved(direction)
        elif is_initial_move:
            # Do nothing
            pass
        else:  # TODO: Did another action besides moving?
            # self.opp.surfaced(int(sector))
            pass

    def get_shot(self) -> (int, int):
        if self.dan.torpedo_cooldown is not 0: return None, None
        self.debug('Torpedo ready...')

        target_positions = self.opp.get_possible_positions_in_torpedo_range(self.dan.position.x, self.dan.position.y)
        self.debug(f'target_positions={target_positions}')
        if not target_positions:
            return None, None
        # Option 1: Shoot furthest target (eventually, depending on dan.health)
        if len(target_positions) == 1:
            return target_positions[0]
        # TODO: Option 2: Shoot largest grouping of targets
        # return target_positions[0]
        return None, None

    def debug_board(self, board: []):
        s = ''
        for row in board:
            s += f'\n    {row}'
        self.debug(f'{s}')

    @staticmethod
    def copy_board(board: []) -> []:
        if not board: return '<empty board>'
        return [x[:] for x in board]

    @staticmethod
    def is_invalid_position(board_width, board_height, x, y):
        return x < 0 or x >= board_width or y < 0 or y >= board_height

    @staticmethod
    def generate_moves(availability_board: [], start_x: int, start_y: int, max_recursion) -> Optional[Tree]:
        if max_recursion <= 0: return None
        if Game.is_invalid_position(len(availability_board[0]), len(availability_board), start_x, start_y): return None
        if not availability_board[start_y][start_x]: return None
        new_availability_board = Game.copy_board(availability_board)
        new_availability_board[start_y][start_x] = False
        tree = Tree()
        tree.north = Game.generate_moves(new_availability_board, start_x, start_y - 1, max_recursion - 1)
        tree.south = Game.generate_moves(new_availability_board, start_x, start_y + 1, max_recursion - 1)
        tree.east = Game.generate_moves(new_availability_board, start_x + 1, start_y, max_recursion - 1)
        tree.west = Game.generate_moves(new_availability_board, start_x - 1, start_y, max_recursion - 1)
        tree.x = start_x
        tree.y = start_y
        tree.height = max(
            tree.north.height if tree.north else 0,
            tree.south.height if tree.south else 0,
            tree.east.height if tree.east else 0,
            tree.west.height if tree.west else 0) + 1
        return tree

    def get_move(self) -> (Tree, str):
        available = copy_board(self.dan.available)
        available[self.dan.position.y][self.dan.position.x] = True  # Workaround for generate_moves(...) checking for availability
        current_position = Game.generate_moves(available, self.dan.position.x, self.dan.position.y, MAX_RECURSION)
        # self.debug(f'current_position={current_position}')
        max_height = 0
        next_position = current_position
        direction = None
        if current_position.north and current_position.north.height > max_height: max_height = current_position.north.height; next_position = current_position.north; direction = 'N'
        if current_position.east and current_position.east.height > max_height: max_height = current_position.east.height; next_position = current_position.east; direction = 'E'
        if current_position.south and current_position.south.height > max_height: max_height = current_position.south.height; next_position = current_position.south; direction = 'S'
        if current_position.west and current_position.west.height > max_height: max_height = current_position.west.height; next_position = current_position.west; direction = 'W'
        return next_position, direction

    def start(self):
        while True:
            x, y, my_life, opp_life, torpedo_cooldown, sonar_cooldown, silence_cooldown, mine_cooldown = [int(i) for i in input().split()]
            sonar_result = input()
            opponent_orders = input()
            is_opponent_direct_hit = self.opp.health - 2 == opp_life
            is_opponent_hit = self.opp.health - 1 == opp_life

            self.dan.health = my_life
            self.dan.position.x = x
            self.dan.position.y = y
            self.dan.torpedo_cooldown = torpedo_cooldown
            self.dan.sonar_cooldown = sonar_cooldown
            self.dan.silence_cooldown = silence_cooldown
            self.dan.mine_cooldown = mine_cooldown

            self.opp.health = opp_life
            self.update_opponent_position(opponent_orders, self.water, is_opponent_direct_hit, is_opponent_hit)

            self.debug(f'opp.possible_positions={self.opp.possible_positions}')

            dan_actions = []

            sonar_sector = self.dan.maybe_sonar(self.opp.possible_positions)
            if sonar_sector:
                perform_sonar_action = f'{POWER_SONAR} {sonar_sector}'
                dan_actions.append(perform_sonar_action)

            shot_x, shot_y = self.get_shot()
            if shot_x:
                self.dan.torpedo(shot_x, shot_y)
                perform_torpedo_action = f'{POWER_TORPEDO} {shot_x} {shot_y} | '
                # TODOv2: torpedo_action = f' | TORPEDO {shot_x} {shot_y}'
                dan_actions.append(perform_torpedo_action)

            silence_direction, silence_range = self.dan.maybe_silence(self.opp.possible_positions)
            if silence_direction:
                perform_silence_action = f'{POWER_SILENCE} {silence_direction} {silence_range}'
                dan_actions.append(perform_silence_action)
                self.dan.move(move_via_direction(self.dan.position.x, self.dan.position.y, silence_direction, silence_range))

            next_position, direction = self.get_move()
            if direction:
                self.dan.move(next_position.x, next_position.y)
                perform_move_action = f'{ACTION_MOVE} {direction} {self.dan.choose_power_to_charge()}'
                dan_actions.append(perform_move_action)
            else:
                self.dan.surface()
                self.debug(f'No moves available')
                perform_move_action = ACTION_SURFACE
                dan_actions.append(perform_move_action)

            print(' | '.join(dan_actions))


def create_water_board() -> []:
    board = []
    width, height, my_id = [int(i) for i in input().split()]
    for i in range(height):
        line = input()
        row = []
        for c in line:
            row.append(c == '.')
        board.append(row)
    return board


def get_initial_position(water_board: []) -> (int, int):
    for i in range(10):
        x = random.randrange(len(water_board[0]))
        y = random.randrange(len(water_board))
        if water_board[y][x]:
            return x, y
    for x in range(len(water_board[0])):
        for y in range(len(water_board)):
            if water_board[y][x]:
                return x, y


def main():
    # water_board = create_water_board()
    # start_x, start_y = get_initial_position(water_board)
    # print(f'{start_x} {start_y}')
    pass
    # game = Game(water_board, start_x, start_y)
    # game.start()


main()
