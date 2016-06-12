# -*- coding: utf-8 -*-
from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *
from tkinter import messagebox
from ast import literal_eval
from ecdsa import *
import pygubu
from pygubu.builder import ttkstdwidgets
import os
filename = 'main.ui'


class Application:
    # Стартовое окно
    def __init__(self, master=None):
        self._master = master
        self.builder = builder = pygubu.Builder()
        builder.add_from_file(filename)
        self.mainwindow = builder.get_object('mainwindow', master)
        self.ec = None
        self.g_point = None
        self.key = None
        self.order = None

        self.entry_p = self.builder.get_object('entry_p')
        self.entry_a = self.builder.get_object('entry_a')
        self.entry_b = self.builder.get_object('entry_b')

        self.entry_p.tk_focusFollowsMouse()

        builder.connect_callbacks(self)

    def on_button_clear_clicked(self):
        self.entry_p.delete(0, 'end')
        self.entry_a.delete(0, 'end')
        self.entry_b.delete(0, 'end')

    def on_button_ok_clicked(self):
        try:
            p = int(self.builder.get_object('entry_p').get())
            a = int(self.builder.get_object('entry_a').get())
            b = int(self.builder.get_object('entry_b').get())
            if not simple1(p):
                messagebox.showerror('Ошибка', 'p не является простым числом, введите новое', parent=self.mainwindow)
                return
            self.ec = CurveOverFp(a, b, 0, p)
            if not self.ec.check_curve():
                messagebox.showerror('Ошибка', 'Неподходящие параметры ЭЦП, введите новые', parent=self.mainwindow)
                return
            self._master.withdraw()
            self.select_generate_point()

        except ValueError as ex:
            print('error')
            showerror("Ошибка", str(ex))
            return

    # Выбор генерирующей точки
    def select_generate_point(self):
        self.gp_builder = gp_builder = pygubu.Builder()
        gp_builder.add_from_file(filename)
        self.genpoint = gp_builder.get_object('genpoint')

        gp_builder.connect_callbacks(self)
        box_values = StringVar()
        values = tuple(str(x) for x in self.ec.get_points())
        combo = gp_builder.get_object('combo')
        combo['values'] = values

    def on_gpbutton_ok_clicked(self):
        value = self.gp_builder.get_object('combo').get()
        value = eval(value)
        self.g_point = Point(x=value[0], y=value[1])
        self.order = self.ec.order(self.g_point)
        self.genpoint.withdraw()
        self.show_main_widget()

    def on_gpbutton_cancel_clicked(self):
        self.gp_builder.get_object('genpoint').destroy()

    def on_exit(self):
        # check if saving
        # if not:
        root.destroy()

    # Окно для работы с ЭЦП
    def show_main_widget(self):
        self.ec_builder = ec_builder = pygubu.Builder()
        ec_builder.add_from_file(filename)
        self.ecdsamain = ec_builder.get_object('ecdsamain')
        self.ecdsamain.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.ec_builder.get_object('formula_label')['text'] = str(self.ec)

        ec_builder.connect_callbacks(self)

    def open_ecdsa_generation(self):
        self.ecg_builder = pygubu.Builder()
        self.ecg_builder.add_from_file(filename)
        self.ecdsa_gen = self.ecg_builder.get_object('ecdsa_generation')
        self.ecdsa_gen.protocol("WM_DELETE_WINDOW", self.close_ecdsa_generation)

        self.ecg_builder.get_object('FormulaLabel')['text'] = str(self.ec)
        self.ecg_builder.get_object('ECOrderLabelValue')['text'] = str(len(self.ec.get_points()))
        self.ecg_builder.get_object('GenPointLabelValue')['text'] = str(self.g_point)
        self.ecg_builder.get_object('GenPointOrderLabelValue')['text'] = str(self.order)

        self.ecg_builder.connect_callbacks(self)

    def generate_keys(self):
        self.key = generate_keypair(self.ec, self.g_point, self.order)
        self.ecg_builder.get_object('RandomKLabelValue')['text'] = str(self.key[0])
        self.ecg_builder.get_object('OpenKeyLabelValue')['text'] = str(self.key[1])
        print(self.key)

    def close_ecdsa_generation(self):
        self.ecg_builder.get_object('ecdsa_generation').destroy()

    def show_help(self):
        messagebox.showinfo('Руководство',
        """
        После запуска приложения открывается стартовое окно, где
        пользователь вводит параметры для задания эллиптической
        кривой, p, a, b. (p должно быть простым, a<0, b>0 и b<p).
        После ввода данных перед пользователем открывается окно
        с двумя кнопками "Генерация подписи" и "проверка подписи".
        При нажатии "Генерация подписи", перед пользователем
        открывается окно "Генерация ЭЦП". В этом окне пользователь
        может видеть уравнение эллиптической кривой, порядок
        эллиптической кривой,
        генерирующую точку которую выбрал пользователь, порядок
        генерирующей точки, после нажатия "Генерация ключей"
        пользователь видит, что сгенерирован открытый ключ и
        случайное число k.
        При нажатии "Хеширования текста" открывается окно где
        пользователь вводит сообщение, после чего нажимает кнопку
        "Рассчитать хэш" и нажимает "ОК". Нажимая кнопку
        "Генерация подписи", пользователь может видеть подпись
        которая получилась.Если же подпись уже есть, то
        пользователь выбирает кнопку "Проверка подписи". После
        нажатия на соответствующую кнопку открывается окно
        "Проверка ЭЦП", в котором так же можно видеть уравнение
        эллиптической кривой, порядок эллиптической кривой,
        генерирующую точку которую выбрал пользователь, порядок
        генерирующей точки. И кнопки "Хеширование текста" так
        же идет расчет хэша сообщения и после этого пользователь
        проводит проверку подписи, нажимая на данную кнопку
        пользователь видит в открывшемся окне поле, в которое
        нужно ввести текст для проверки, а так же поля для ввода
        открытого ключа и самой подписи.
        """)

    def hashing_text(self):
        self.it_builder = it_builder = pygubu.Builder()
        it_builder.add_from_file(filename)
        self.itmain = it_builder.get_object('input_text')

        self.plain_text_widget = self.it_builder.get_object('text_box')
        self.scrollbar1 = self.it_builder.get_object('scrollbar1')
        self.plain_text_widget.configure(yscrollcommand=self.scrollbar1.set)
        self.scrollbar1.configure(command=self.plain_text_widget.yview)

        # scrollb = Scrollbar(self.itmain, command=self.itmain.yview)
        # scrollb.grid(row=0, column=3, sticky='nsew')
        # self.itmain['yscrollcommand'] = scrollb.set

        it_builder.connect_callbacks(self)

    def text_button_cancel(self):
        self.it_builder.get_object('input_text').destroy()

    def text_generate(self):
        self.plain_text_widget = self.it_builder.get_object('text_box')

        self.hashed_text_widget = self.it_builder.get_object('text_box_hashed')
        text = self.plain_text_widget.get("1.0", END)
        self.hashed_text_widget.delete("1.0", END)
        h_txt, h = hash_and_truncate(text.encode('utf-8'), self.order)
        self.hashed_text_widget.insert("1.0", h_txt)

    def text_hashing(self):
        self.text_to_sign = self.plain_text_widget.get("1.0", END).encode('utf-8')
        print(self.text_to_sign)
        self.itmain.withdraw()

    def generate_sign(self):
        ok = False
        while not ok:
            try:
                self.sign = sign(self.text_to_sign, self.ec, self.g_point, self.order, self.key)
                ok = True
            except ValueError:
                ok = False
        messagebox.showinfo('Подпись', 'R: {0}  \nS: {1}'.format(self.sign[1], self.sign[2]), parent=self.ecdsamain)

    def verify_sign(self):
        self.qvw_builder = qvw_builder = pygubu.Builder()
        qvw_builder.add_from_file(filename)
        self.qvwmain = qvw_builder.get_object('ecdsa_verify')

        self.qvw_builder.get_object('FormulaLabel_4')['text'] = str(self.ec)
        self.qvw_builder.get_object('OrderLabelValue')['text'] = str(len(self.ec.get_points()))
        self.qvw_builder.get_object('GenPointLabelValue_7')['text'] = str(self.g_point)
        self.qvw_builder.get_object('GenPointOrderLabelValue_1')['text'] = str(self.order)


        qvw_builder.connect_callbacks(self)

    def open_verify_sign(self):
        self.vw_builder = vw_builder = pygubu.Builder()
        vw_builder.add_from_file(filename)
        self.vwmain = vw_builder.get_object('verify_sign')

        vw_builder.connect_callbacks(self)

    def do_verify_sign(self):
        sign = []

        t = literal_eval((self.vw_builder.get_object('open_key_value_1').get()))
        Q = Point(t[0], t[1])

        sign.append(Q)
        sign.append(int(self.vw_builder.get_object('r_value').get()))
        sign.append(int(self.vw_builder.get_object('s_value').get()))


        try:
            if verify(self.text_to_sign, self.ec, self.g_point, self.order, tuple(sign)):
                messagebox.showinfo('Информация', 'ЭЦП правильная', parent=self.ecdsamain)
            else:
                messagebox.showerror('Ошибка', 'ЭЦП фальшивая', parent=self.ecdsamain)
        except ValueError as err:
            print(err)
            messagebox.showerror('Ошибка', 'ЭЦП фальшивая', parent=self.ecdsamain)

    def close_virify_widget(self):
        self.vw_builder.get_object('verify_sign').destroy()


root = Tk()
if hasattr(sys, '_MEIPASS'):
    filename = os.path.join(sys._MEIPASS, filename)
root.wm_title("Выбор параметров кривой")
app = Application(master=root)
root.mainloop()



