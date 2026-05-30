import tkinter as tk
import webbrowser
from tkinter import messagebox

weights = [25, 20, 15, 10, 5, 2.5, 1.25, 0.5]
BAR_WEIGHT = 20


def url():
    webbrowser.open("https://github.com/melamann00/weight_adder")


def calculate(entry_widget, result_label_widget):
    try:
        wanted = float(entry_widget.get())
        if wanted < BAR_WEIGHT:
            messagebox.showerror("Błąd", "Ciężar musi być większy lub równy 20 kg.")
            return
        elif wanted > 700:
            messagebox.showerror("Błąd", "Podano zbyt duży ciężar.")
        if wanted == BAR_WEIGHT:
            result_label_widget.config(text="Brak ciężaru do załadowania")
            return

        weight_per_side = (wanted - BAR_WEIGHT) / 2
        loaded = []
        for weight in weights:
            while weight_per_side - weight >= -0.001:
                if weight_per_side - weight < -0.001:
                    break
                loaded.append(weight)
                weight_per_side -= weight

        if weight_per_side > 0.001:
            result_label_widget.config(
                text="Nie można dokładnie załadować takiego ciężaru."
            )
        else:
            result_label_widget.config(
                text="Talerze na jedną stronę:\n" + " | ".join(map(str, loaded))
            )
    except ValueError:
        messagebox.showerror("Błąd", "Podaj poprawną liczbę.")


def open_second_window():
    new_win = tk.Toplevel(root)
    menu = tk.Menu(new_win)
    new_win.config(menu=menu)
    filemenu = tk.Menu(menu)
    menu.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="New", command=open_second_window)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=new_win.destroy)

    helpmenu = tk.Menu(menu)
    menu.add_cascade(label="Help", menu=helpmenu)
    helpmenu.add_command(label="About", command=url)

    new_win.title("Kalkulator talerzy na sztangę")
    new_win.geometry("400x300")
    title_label = tk.Label(new_win, text="Kalkulator talerzy", font=("Arial", 16))
    title_label.pack(pady=10)

    entry_label = tk.Label(new_win, text="Podaj ciężar całkowity (kg):")
    entry_label.pack()
    entry = tk.Entry(new_win, font=("Arial", 12))
    entry.pack(pady=5)
    result_label = tk.Label(new_win, text="", font=("Arial", 12), wraplength=350)
    calc_button = tk.Button(
        new_win, text="Przelicz", command=lambda: calculate(entry, result_label)
    )
    calc_button.pack(pady=10)
    result_label.pack(pady=10)


root = tk.Tk()
menu = tk.Menu(root)
root.config(menu=menu)
filemenu = tk.Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="New", command=open_second_window)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
helpmenu = tk.Menu(menu)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="About", command=url)
root.title("Kalkulator talerzy na sztangę")
root.geometry("400x300")
root.resizable(True, True)
title_label = tk.Label(root, text="Kalkulator talerzy", font=("Arial", 16))
title_label.pack(pady=10)
entry_label = tk.Label(root, text="Podaj ciężar całkowity (kg):")
entry_label.pack()
entry = tk.Entry(root, font=("Arial", 12))
entry.pack(pady=5)
result_label = tk.Label(root, text="", font=("Arial", 12), wraplength=350)
calc_button = tk.Button(
    root, text="Przelicz", command=lambda: calculate(entry, result_label)
)
calc_button.pack(pady=10)
result_label.pack(pady=10)
root.mainloop()
