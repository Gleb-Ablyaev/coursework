from tkinter import Canvas, Event, messagebox
from PIL import Image, ImageTk
from random import choice
from pathlib import Path
from time import sleep
from math import inf
from typing import List

from checkers.field import Field
from checkers.enums import CheckerType, SideType

from checkers.point import Point
from checkers.enums import CheckerType, SideType
from PIL import Image, ImageTk, ImageDraw
from pathlib import Path


import random

class Move:
    def __init__(self, from_x: int = -1, from_y: int = -1, to_x: int = -1, to_y: int = -1):
        self.__from_x = from_x
        self.__from_y = from_y
        self.__to_x = to_x
        self.__to_y = to_y

    @property
    def from_x(self) -> int:
        return self.__from_x

    @property
    def from_y(self) -> int:
        return self.__from_y

    @property
    def to_x(self) -> int:
        return self.__to_x
        
    @property
    def to_y(self) -> int:
        return self.__to_y

    def __repr__(self) -> str:
        return f'{self.from_x}-{self.from_y} -> {self.to_x}-{self.to_y}'

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return (
                self.from_x == other.from_x and
                self.from_y == other.from_y and
                self.to_x == other.to_x and
                self.to_y == other.to_y
            )
        return NotImplemented

    def clone(self) -> 'Move':
        return self.__class__(self.from_x, self.from_y, self.to_x, self.to_y)


# Генерируем случайное значение
PLAYER_SIDE = random.choice([SideType.WHITE, SideType.BLACK])

# Размер поля
X_SIZE = 10
Y_SIZE = 8

CELL_SIZE = 90


ANIMATION_SPEED = 5
MAX_PREDICTION_DEPTH = 3

BORDER_WIDTH = 6
FIELD_COLORS = ['#EEEEEE', '#111111']
HOVER_BORDER_COLOR = '#111111'
SELECT_BORDER_COLOR = '#00FF00'
POSIBLE_MOVE_CIRCLE_COLOR = '#00FF00'

# Возможные смещения ходов шашек
MOVE_OFFSETS = [
    Point(-1, -1),
    Point( 1, -1),
    Point(-1,  1),
    Point( 1,  1)
]

# Массивы типов белых и чёрных шашек [Обычная пешка, дамка]
WHITE_CHECKERS = [CheckerType.WHITE_REGULAR, CheckerType.WHITE_QUEEN]
BLACK_CHECKERS = [CheckerType.BLACK_REGULAR, CheckerType.BLACK_QUEEN]

class Game:
    def __init__(self, canvas: Canvas, x_field_size: int, y_field_size: int):
        self.__canvas = canvas
        self.__field = Field(x_field_size, y_field_size)

        self.__player_turn = True

        self.__hovered_cell = Point()
        self.__selected_cell = Point()
        self.__animated_cell = Point()

        self.__init_images()
        
        self.__draw()

        # Если игрок играет за чёрных, то совершить ход противника
        if (PLAYER_SIDE == SideType.BLACK):
            self.__handle_enemy_turn()

    def __init_images(self):
        self.__images = {
            CheckerType.WHITE_REGULAR: ImageTk.PhotoImage(Image.open(Path('assets', 'white.png')).resize((CELL_SIZE, CELL_SIZE))),
            CheckerType.BLACK_REGULAR: ImageTk.PhotoImage(Image.open(Path('assets', 'black.png')).resize((CELL_SIZE, CELL_SIZE))),
            CheckerType.WHITE_QUEEN: ImageTk.PhotoImage(Image.open(Path('assets', 'white-q.png')).resize((CELL_SIZE, CELL_SIZE))),
            CheckerType.BLACK_QUEEN: ImageTk.PhotoImage(Image.open(Path('assets', 'black-q.png')).resize((CELL_SIZE, CELL_SIZE))),
        }

    def __animate_move(self, move: Move):
        self.__animated_cell = Point(move.from_x, move.from_y)
        self.__draw()

        # Создание шашки для анимации
        animated_checker = self.__canvas.create_image(move.from_x * CELL_SIZE, move.from_y * CELL_SIZE, image=self.__images.get(self.__field.type_at(move.from_x, move.from_y)), anchor='nw', tag='animated_checker')
        
        # Вектора движения
        dx = 1 if move.from_x < move.to_x else -1
        dy = 1 if move.from_y < move.to_y else -1

        # Анимация
        for distance in range(abs(move.from_x - move.to_x)):
            for _ in range(100 // ANIMATION_SPEED):
                self.__canvas.move(animated_checker, ANIMATION_SPEED / 100 * CELL_SIZE * dx, ANIMATION_SPEED / 100 * CELL_SIZE * dy)
                self.__canvas.update()
                sleep(0.01)

        self.__animated_cell = Point()

    def __draw(self):
        self.__canvas.delete('all')
        self.__draw_field_grid()
        self.__draw_checkers()

    def __draw_field_grid(self):
        for y in range(self.__field.y_size):
            for x in range(self.__field.x_size):
                self.__canvas.create_rectangle(x * CELL_SIZE, y * CELL_SIZE, x * CELL_SIZE + CELL_SIZE, y * CELL_SIZE + CELL_SIZE, fill=FIELD_COLORS[(y + x) % 2], width=0, tag='boards')
          
                if (self.__selected_cell):
                    player_moves_list = self.__get_moves_list(PLAYER_SIDE)
                    for move in player_moves_list:
                        if (self.__selected_cell.x == move.from_x and self.__selected_cell.y == move.from_y):
                            self.__canvas.create_oval(move.to_x * CELL_SIZE + CELL_SIZE / 3, move.to_y * CELL_SIZE + CELL_SIZE / 3, move.to_x * CELL_SIZE + (CELL_SIZE - CELL_SIZE / 3), move.to_y * CELL_SIZE + (CELL_SIZE - CELL_SIZE / 3), fill=POSIBLE_MOVE_CIRCLE_COLOR, width=0, tag='posible_move_circle' )

    def __draw_checkers(self):     
        for y in range(self.__field.y_size):
            for x in range(self.__field.x_size):
                # Не отрисовывать пустые ячейки и анимируемую шашку
                if (self.__field.type_at(x, y) != CheckerType.NONE and not (x == self.__animated_cell.x and y == self.__animated_cell.y)):
                    self.__canvas.create_image(x * CELL_SIZE, y * CELL_SIZE, image=self.__images.get(self.__field.type_at(x, y)), anchor='nw', tag='checkers')


    def mouse_down(self, event: Event):
        if not (self.__player_turn): return

        x, y = (event.x) // CELL_SIZE, (event.y) // CELL_SIZE

        if not (self.__field.is_within(x, y)): return

        if (PLAYER_SIDE == SideType.WHITE):
            player_checkers = WHITE_CHECKERS
        elif (PLAYER_SIDE == SideType.BLACK):
            player_checkers = BLACK_CHECKERS
        else: return

        # Если нажатие по шашке игрока, то выбрать её
        if (self.__field.type_at(x, y) in player_checkers):
            self.__selected_cell = Point(x, y)
            self.__draw()
        elif (self.__player_turn):
            move = Move(self.__selected_cell.x, self.__selected_cell.y, x, y)

            # Если нажатие по ячейке, на которую можно походить
            if (move in self.__get_moves_list(PLAYER_SIDE)):
                self.__handle_player_turn(move)

                # Если не ход игрока, то ход противника
                if not (self.__player_turn):
                    self.__handle_enemy_turn()

    def __handle_move(self, move: Move, draw: bool = True) -> bool:
        if (draw): self.__animate_move(move)

        # Изменение типа шашки, если она дошла до края
        if (move.to_y == 0 and self.__field.type_at(move.from_x, move.from_y) == CheckerType.WHITE_REGULAR):
            self.__field.at(move.from_x, move.from_y).change_type(CheckerType.WHITE_QUEEN)
        elif (move.to_y == self.__field.y_size - 1 and self.__field.type_at(move.from_x, move.from_y) == CheckerType.BLACK_REGULAR):
            self.__field.at(move.from_x, move.from_y).change_type(CheckerType.BLACK_QUEEN)

        # Изменение позиции шашки
        self.__field.at(move.to_x, move.to_y).change_type(self.__field.type_at(move.from_x, move.from_y))
        self.__field.at(move.from_x, move.from_y).change_type(CheckerType.NONE)

        # Вектора движения
        dx = -1 if move.from_x < move.to_x else 1
        dy = -1 if move.from_y < move.to_y else 1

        # Удаление съеденных шашек
        has_killed_checker = False
        x, y = move.to_x, move.to_y
        while (x != move.from_x or y != move.from_y):
            x += dx
            y += dy
            if (self.__field.type_at(x, y) != CheckerType.NONE):
                self.__field.at(x, y).change_type(CheckerType.NONE)
                has_killed_checker = True

        if (draw): self.__draw()

        return has_killed_checker

    def __handle_player_turn(self, move: Move):
        self.__player_turn = False

        has_killed_checker = self.__handle_move(move)

        required_moves_list = list(filter(lambda required_move: move.to_x == required_move.from_x and move.to_y == required_move.from_y, self.__get_required_moves_list(PLAYER_SIDE)))
        
        if (has_killed_checker and required_moves_list):
            self.__player_turn = True

        self.__selected_cell = Point()

    def __handle_enemy_turn(self):
        self.__player_turn = False

        optimal_moves_list = self.__predict_optimal_moves(SideType.opposite(PLAYER_SIDE))

        for move in optimal_moves_list:
            self.__handle_move(move)
            
        self.__player_turn = True
        
        self.__check_for_game_over()

    def __check_for_game_over(self):
        game_over = False

        white_moves_list = self.__get_moves_list(SideType.WHITE)
        if not (white_moves_list):
            # Белые проиграли
            answer = messagebox.showinfo('Конец игры', 'Чёрные выиграли')
            game_over = True

        black_moves_list = self.__get_moves_list(SideType.BLACK)
        if not (black_moves_list):
            # Чёрные проиграли
            answer = messagebox.showinfo('Конец игры', 'Белые выиграли')
            game_over = True
        
        if (game_over):
            # Новая игра
            self.__init__(self.__canvas, self.__field.x_size, self.__field.y_size)

    def __predict_optimal_moves(self, side: SideType) -> List[Move]:
        best_result = float('-inf')
        optimal_moves = []
        predicted_moves_list = self.__get_predicted_moves_list(side)

        if predicted_moves_list:
            field_copy = Field.copy(self.__field)
            for moves in predicted_moves_list:
                for move in moves:
                    self.__handle_move(move, draw=False)

                try:
                    if side == SideType.WHITE:
                        result = self.__field.white_score / self.__field.black_score
                    elif side == SideType.BLACK:
                        result = self.__field.black_score / self.__field.white_score
                except ZeroDivisionError:
                    result = float('inf')
                
                if result > best_result:
                    best_result = result
                    optimal_moves = [moves]
                elif result == best_result:
                    optimal_moves.append(moves)

                self.__field = Field.copy(field_copy)

        optimal_move = []
        if optimal_moves:
            # Фильтрация хода
            for move in choice(optimal_moves):
                if (side == SideType.WHITE and self.__field.type_at(move.from_x, move.from_y) in BLACK_CHECKERS) or \
                (side == SideType.BLACK and self.__field.type_at(move.from_x, move.from_y) in WHITE_CHECKERS):
                    break

                optimal_move.append(move)

        return optimal_move

    def __get_predicted_moves_list(self, side: SideType, current_prediction_depth: int = 0, all_moves_list: List[List[Move]] = None, current_moves_list: List[Move] = None, required_moves_list: List[Move] = None) -> List[List[Move]]:      
        if all_moves_list is None:
            all_moves_list = []

        if current_moves_list is None:
            current_moves_list = []

        if required_moves_list is None:
            required_moves_list = []

        if current_moves_list:
            all_moves_list.append(current_moves_list)
        else:
            all_moves_list.clear()

        moves_list = self.__get_moves_list(side) if not required_moves_list else required_moves_list

        if moves_list and current_prediction_depth < MAX_PREDICTION_DEPTH:
            field_copy = Field.copy(self.__field)
            for move in moves_list:
                has_killed_checker = self.__handle_move(move, draw=False)
                required_moves_list = [required_move for required_move in self.__get_required_moves_list(side) if move.to_x == required_move.from_x and move.to_y == required_move.from_y]

                # Если есть ещё ход этой же шашкой
                if has_killed_checker and required_moves_list:
                    self.__get_predicted_moves_list(side, current_prediction_depth, all_moves_list, current_moves_list + [move], required_moves_list)
                else:
                    self.__get_predicted_moves_list(SideType.opposite(side), current_prediction_depth + 1, all_moves_list, current_moves_list + [move])

                self.__field = Field.copy(field_copy)

        return all_moves_list

    def __get_moves_list(self, side: SideType) -> list[Move]:
        moves_list = self.__get_required_moves_list(side)
        if not (moves_list):
            moves_list = self.__get_optional_moves_list(side)
        return moves_list

    def __get_required_moves_list(self, side: SideType) -> list[Move]:
        moves_list = []

        # Определение типов шашек
        if (side == SideType.WHITE):
            friendly_checkers = WHITE_CHECKERS
            enemy_checkers = BLACK_CHECKERS
        elif (side == SideType.BLACK):
            friendly_checkers = BLACK_CHECKERS
            enemy_checkers = WHITE_CHECKERS
        else: return moves_list

        for y in range(self.__field.y_size):
            for x in range(self.__field.x_size):

                # Для обычной шашки
                if (self.__field.type_at(x, y) == friendly_checkers[0]):
                    for offset in MOVE_OFFSETS:
                        if not (self.__field.is_within(x + offset.x * 2, y + offset.y * 2)): continue

                        if self.__field.type_at(x + offset.x, y + offset.y) in enemy_checkers and self.__field.type_at(x + offset.x * 2, y + offset.y * 2) == CheckerType.NONE:
                            moves_list.append(Move(x, y, x + offset.x * 2, y + offset.y * 2))

                # Для дамки
                elif (self.__field.type_at(x, y) == friendly_checkers[1]):
                    for offset in MOVE_OFFSETS:
                        if not (self.__field.is_within(x + offset.x * 2, y + offset.y * 2)): continue

                        has_enemy_checker_on_way = False

                        for shift in range(1, self.__field.size):
                            if not (self.__field.is_within(x + offset.x * shift, y + offset.y * shift)): continue

                            # Если на пути не было вражеской шашки
                            if (not has_enemy_checker_on_way):
                                if (self.__field.type_at(x + offset.x * shift, y + offset.y * shift) in enemy_checkers):
                                    has_enemy_checker_on_way = True
                                    continue
                                # Если на пути союзная шашка - то закончить цикл
                                elif (self.__field.type_at(x + offset.x * shift, y + offset.y * shift) in friendly_checkers):
                                    break
                            
                            # Если на пути была вражеская шашка
                            if (has_enemy_checker_on_way):
                                if (self.__field.type_at(x + offset.x * shift, y + offset.y * shift) == CheckerType.NONE):
                                    moves_list.append(Move(x, y, x + offset.x * shift, y + offset.y * shift))
                                else:
                                    break
                            
        return moves_list

    def __get_optional_moves_list(self, side: SideType) -> list[Move]:
        moves_list = []

        # Определение типов шашек
        if (side == SideType.WHITE):
            friendly_checkers = WHITE_CHECKERS
        elif (side == SideType.BLACK):
            friendly_checkers = BLACK_CHECKERS
        else: return moves_list

        for y in range(self.__field.y_size):
            for x in range(self.__field.x_size):
                # Для обычной шашки
                if (self.__field.type_at(x, y) == friendly_checkers[0]):
                    for offset in MOVE_OFFSETS[:2] if side == SideType.WHITE else MOVE_OFFSETS[2:]:
                        if not (self.__field.is_within(x + offset.x, y + offset.y)): continue

                        if (self.__field.type_at(x + offset.x, y + offset.y) == CheckerType.NONE):
                            moves_list.append(Move(x, y, x + offset.x, y + offset.y))

                # Для дамки
                elif (self.__field.type_at(x, y) == friendly_checkers[1]):
                    for offset in MOVE_OFFSETS:
                        if not (self.__field.is_within(x + offset.x, y + offset.y)): continue

                        for shift in range(1, self.__field.size):
                            if not (self.__field.is_within(x + offset.x * shift, y + offset.y * shift)): continue

                            if (self.__field.type_at(x + offset.x * shift, y + offset.y * shift) == CheckerType.NONE):
                                moves_list.append(Move(x, y, x + offset.x * shift, y + offset.y * shift))
                            else:
                                break
        return moves_list