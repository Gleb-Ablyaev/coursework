from tkinter import Tk, Canvas, Button, Entry, Label, messagebox
import sqlite3
import hashlib
from checkers.game import Game
from checkers.point import Point
from checkers.enums import CheckerType, SideType



# Размер поля
X_SIZE = 10
Y_SIZE = 8
CELL_SIZE = 90

USERS_FILE = "users.txt"

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

def caesar_cipher(password):
    shift = 1
    result = ""
    for char in password:
        if char.isalpha():
            if char.islower():
                result += chr((ord(char) - 97 + shift) % 26 + 97)
            elif char.isupper():
                result += chr((ord(char) - 65 + shift) % 26 + 65)
        else:
            result += char
    return result

def register():
    username = username_entry.get()
    password = password_entry.get()
    if username and password:
        hashed_password = caesar_cipher(password)
        with open(USERS_FILE, "a") as file:
            file.write(f"{username}:{hashed_password}\n")
        messagebox.showinfo("Успех", "Вы успешно зарегистрированы!")
    else:
        messagebox.showerror("Ошибка", "Введите имя пользователя и пароль")

def authenticate(username, password):
    with open(USERS_FILE, "r") as file:
        for line in file:
            stored_username, stored_password = line.strip().split(":")
            if username == stored_username:
                hashed_password = caesar_cipher(password)
                return hashed_password == stored_password
    return False

def run_game():
    main_window.destroy()
    # Создание окна
    game_window = Tk()
    game_window.title('Шашки')
    game_window.resizable(0, 0)

    # Создание холста
    main_canvas = Canvas(game_window, width=CELL_SIZE * X_SIZE, height=CELL_SIZE * Y_SIZE)
    main_canvas.pack()

    game = Game(main_canvas, X_SIZE, Y_SIZE)

    main_canvas.bind("<Button-1>", game.mouse_down)

    game_window.mainloop()

def login():
    username = username_entry.get()
    password = password_entry.get()
    if authenticate(username, password):
        messagebox.showinfo("Успех", "Вы успешно вошли в систему!")
        run_game()
    else:
        messagebox.showerror("Ошибка", "Неправильное имя пользователя или пароль")

main_window = Tk()
main_window.title("Регистрация и вход")

label_username = Label(main_window, text="Имя пользователя:")
label_username.grid(row=0, column=0, padx=5, pady=5)
username_entry = Entry(main_window)
username_entry.grid(row=0, column=1, padx=5, pady=5)

label_password = Label(main_window, text="Пароль:")
label_password.grid(row=1, column=0, padx=5, pady=5)
password_entry = Entry(main_window, show="*")
password_entry.grid(row=1, column=1, padx=5, pady=5)

button_login = Button(main_window, text="Войти", command=login)
button_login.grid(row=2, column=0, padx=5, pady=5)

button_register = Button(main_window, text="Зарегистрироваться", command=register)
button_register.grid(row=2, column=1, padx=5, pady=5)

main_window.mainloop()