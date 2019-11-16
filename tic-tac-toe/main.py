import tkinter as tk
import tkinter.ttk as ttk
import random
from constants import *

class Pole:

    def __init__(self, root, num):
        '''
        Функция инициализации
        :param num - номер клетки, w - ширина, h - высота, padx - сдвиг по x,
        pady - сдвиг по y, b - расстояние между клетками
        '''
        self.root = root
        self.num = num
        self.sign = tk.StringVar()
        # поля игры
        self.lbl = tk.Label(self.root, textvariable=self.sign,
                            font="Arial 75", bg="white")
        self.lbl.place(x=padx + (num % field_size) * (pole_w + space),
                       y=pady + (num // field_size) * (pole_h + space), width=pole_w, height=pole_h)

    def mark_pole(self, mark):
        """ Функция помечает клетку """
        self.sign.set(mark)

    def stupid_user_move(self, *args):
        """ Вызывает функцию хода пользователя принажатии кнопки """
        self.root.do_move(self.num, 'X')
        if not self.root.end:
            self.root.turn_pc()

    def change_color(self, color):
        """ Меняетт цвет клетки """
        self.lbl.configure(bg=color)

    def unbind(self):
        """ Отвязывает функцию нажатия кнопки от кнопки """
        self.lbl.unbind("<Button-1>")

    def bind(self):
        """ Привязывает функцию нажатия кнопки к кнопке """
        self.lbl.bind("<Button-1>", self.stupid_user_move)


class Application(tk.Frame):
    def __init__(self, root):
        '''
        Конструктор наследника
        :param root
        Определены константы выйгрыша,
        константы приоритетных угловых полей,
        константы не угловых полей.
        Вызывается функция, конструирующая клетки.
        '''
        super(Application, self).__init__(root, width=field_w, height=field_h)
        self.pack()
        self.board_start = [' '] * field_size**2
        self.start_pole = [x for x in range(field_size**2)]
        self.create_widgets()

    def create_widgets(self):
        '''
        Функция, создающая клетки поля
        arg: -
        Делает заливку фона,
        создает клетки поля,
        создает кнопку старт,
        создает поле с посланием,
        создает выбор хода.
        '''
        self.fill = tk.Label(self, bg='khaki', width=field_w, height=field_h)
        self.fill.place(x=0, y=0)

        # клетки
        self.pole = {}
        for num in range(9):
            self.pole[num] = Pole(self, num)

        # кнопка старт
        self.button_start = tk.Button(self, text="Старт", bg='deep pink')
        self.button_start.bind("<Button-1>", self.start)
        self.button_start.place(x=but_place_x, y=but_plce_y, width=but_width)

        # Статус игры
        self.status = tk.StringVar()
        status_lbl = tk.Label(self, textvariable=self.status, bg='light yellow',
                              bd=2, width=st_width, height=st_height, anchor='center')
        status_lbl.place(x=st_x, y=st_y)
        self.status.set('Чтобы начать игру, нажмите кнопку "Старт"')

        # Выбор хода
        frame = tk.LabelFrame(self, text=" Буду ходить ", width=frame_width, height=frame_height, bg='deep pink', bd=0)
        frame.place(x=frame_x, y=frame_y)
        self.combobox = ttk.Combobox(self, values=[u'Первым', u'Вторым'])
        self.combobox.current(0)
        self.combobox.place(x=comb_x, y=comb_y)
        self.widgets = [self.combobox, self.button_start]

    def start(self, *args):
        '''
        Функция, запускающая игру
        Создает список свободных клеток,
        создаем поле
        :return:
        '''
        # Основные поля
        self.next_moves = None
        self.end = False
        self.free_pos = self.start_pole[:]
        self.board = self.board_start[:]
        self.status.set('GAME ON')
        for i in range(9):
            cur_pole = self.pole[i]
            cur_pole.bind()
            cur_pole.mark_pole('')
            cur_pole.change_color('white')
        if self.combobox.get() == 'Вторым':
            self.turn_pc()
        self.combobox.config(state=tk.DISABLED)
        self.button_start.config(state=tk.DISABLED)
        self.button_start.unbind("<Button-1>")

    def check_win(self, sign, move):
        x, y = move % 3, (move // 3) * 3
        self.wins = []
        if sign == self.board[y] and sign == self.board[y + 1] and sign == self.board[y + 2]:
            self.wins = [y, y + 1, y + 2]
        if sign == self.board[x] and sign == self.board[x + 3] and sign == self.board[x + 6]:
            self.wins = [x, x + 3, x + 6]
        if sign == self.board[0] and sign == self.board[4] and sign == self.board[8]:
            self.wins = [0, 4, 8]
        if sign == self.board[2] and sign == self.board[4] and sign == self.board[6]:
            self.wins = [2, 4, 6]
        return len(self.wins) == 3

    def is_over(self, sign, move):
        '''
        Эта функция, определяющая, закончена игра или нет
        Проверяет, заполнена ли хотя бы одна выйгрышная ситуация одним знаком.
        Если да, то подсвечивает данную конфигурацию соответствующим цветом.
        Если свободных клеток не осталось, то ничья.
        :param sign, move
        '''
        if self.check_win(sign, move):
            color = 'green' if sign == 'X' else 'red'
            for i in self.wins:
                cur_pole = self.pole[i]
                cur_pole.change_color(color)
            for i in self.free_pos:
                self.pole[i].unbind()
            if sign == 'X':
                self.status.set('Woow! You are a champion!')
            else:
                self.status.set('Ooops, you\'re dead. \n Нажмите "Старт", чтобы начать заново')
            self.end = True
            self.combobox.config(state=tk.NORMAL)
            self.button_start.config(state=tk.NORMAL)
            self.button_start.bind("<Button-1>", self.start)
            return
        if not self.free_pos:
            self.status.set('Hmm... We don\'t have a winner')
            self.end = True
            for i in range(9):
                cur_pole = self.pole[i]
                cur_pole.change_color('yellow')
            self.combobox.config(state=tk.NORMAL)
            self.button_start.config(state=tk.NORMAL)
            self.button_start.bind("<Button-1>", self.start)

    def find_win_move(self):
        '''
        Функция, ищущая выгрышный ход.
        Если выйгрышный ход есть, возвращет его, если нет, то None.
        '''
        for sign in ['O', 'X']:
            for move in self.free_pos:
                self.board[move] = sign
                if self.check_win(sign, move):
                    return move
                self.board[move] = ''
        return None

    def turn_pc(self):
        '''
        Эта функция реализует  ход ИИ
        Если возможен ход, ведущий к выйгрышу, то делается он.
        Если возможен ход соперника, ведущий к выйгрышу соперника, то ИИ делает ход туда, чтобы помешать.
        Если таких ходов нет, то делается стандартный ход.
        '''
        move = self.find_win_move()
        if move is None:
            move = random.choice(self.free_pos)
        self.do_move(move, 'O')

    def do_move(self, move, sign):
        '''
        Функция, делающая ход.
        Ставит на клетке знак,
        деактивирует её,
        удаляет из списка свободных клеток,
        проверяет не закончена ли игра.
        :param move:
        :param sign:
        :return:
        '''
        self.pole[move].unbind()
        self.pole[move].mark_pole(sign)
        self.board[move] = sign
        self.free_pos.remove(move)
        self.is_over(sign, move)


def main():
    root = tk.Tk()
    root.title('Игра "Крестики - Нолики"')
    root.geometry('%dx%d' % (field_w, field_h))
    root.resizable(False, False)
    app = Application(root)
    root.mainloop()


if __name__ == '__main__':
    main()