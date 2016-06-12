# -*- coding: utf-8 -*-
from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *
from ecdsa import *


class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.ec = None
        self.g_point = None

        self.label_p = Label(root, text="Параметр p:")
        self.label_a = Label(root, text="Параметр a:")
        self.label_b = Label(root, text="Параметр b:")

        self.param_p = Entry(root)
        self.param_a = Entry(root)
        self.param_b = Entry(root)

        self.button_ok = Button(root, text="Ok", command=self.create_curve)
        self.button_cancel = Button(root, text="Отмена", command=root.destroy)

        self.create_widgets()

    def create_curve(self):
        try:
            p = int(self.param_p.get())
            a = int(self.param_a.get())
            b = int(self.param_b.get())
            self.ec = CurveOverFp(0, a, b, p)
        except ValueError as ex:
            showerror("Ошибка", str(ex))
            return

        self.select_generate_point()

    def show_main_widget(self):
        t = Toplevel(self)
        t.wm_title("Работа с ЭЦП")

        l = Label(t, text="{0}".format(str(self.ec)))
        l.grid(row=0, column=0, padx=5, pady=5)

        button_keygen = Button(t, text="Генерация ключей", command=self.generate_keys)
        button_hashing = Button(t, text="Хэширование текста", command=self.hashing_text)
        button_create_sign = Button(t, text="Генерация подписи", command=self.generate_sign)
        button_verify_sign = Button(t, text="Проверка подписи", command=self.verify_sign)

        button_keygen.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)
        button_hashing.grid(row=2, column=0, padx=5, pady=5, sticky=N + S + E + W)
        button_create_sign.grid(row=3, column=0, padx=5, pady=5, sticky=N + S + E + W)
        button_verify_sign.grid(row=4, column=0, padx=5, pady=5, sticky=N + S + E + W)

    def generate_keys(self):
        key = generate_keypair(self.ec, self.g_point, self.ec.order(self.g_point))
        print(key)

    def hashing_text(self):
        pass

    def generate_sign(self):
        #sig = sign(msg, C, P, 131, key)
        pass

    def verify_sign(self):
        #verify('this is an important message', C, P, 131, sig)
        pass

    def select_generate_point(self):
        t = Toplevel(self)
        t.wm_title("Выбор генерирующей точки")

        l = Label(t, text="Выберите точку из списка: ")
        l.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        box_values = StringVar()
        values = tuple(str(x) for x in self.ec.get_points())
        self.combo = Combobox(t, textvariable=box_values, state='readonly')
        self.combo['values'] = values
        self.combo.current(0)
        self.combo.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        button_ok = Button(t, text="Ok", command=self.generate_point_selected)
        button_cancel = Button(t, text="Отмена", command=t.destroy)

        button_ok.grid(row=3, column=0, padx=5, pady=5, sticky=N + S + E + W)
        button_cancel.grid(row=3, column=1, padx=5, pady=5, sticky=N + S + E + W)

    def generate_point_selected(self):
        value = self.combo.get()
        value = eval(value)
        self.g_point = Point(x=value[0], y=value[1])
        self.show_main_widget()

    def create_widgets(self):
        self.label_p.grid(row=0, column=0, padx=5, pady=5)
        self.label_a.grid(row=1, column=0, padx=5, pady=5)
        self.label_b.grid(row=2, column=0, padx=5, pady=5)
        self.button_ok.grid(row=3, column=0, padx=5, pady=5, sticky=N+S+E+W)

        self.param_p.grid(row=0, column=1, padx=5, pady=5)
        self.param_a.grid(row=1, column=1, padx=5, pady=5)
        self.param_b.grid(row=2, column=1, padx=5, pady=5)
        self.button_cancel.grid(row=3, column=1, padx=5, pady=5, sticky=N+S+E+W)

root = Tk()
root.wm_title("Выбор параметров кривой")
app = Application(master=root)
app.mainloop()


