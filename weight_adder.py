import datetime
import sys
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox
import os

def get_documents_folder() -> Path:
    home = Path.home()

    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes
            CSIDL_PERSONAL = 5
            SHGFP_TYPE_CURRENT = 0
            buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(
                None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf
            )
            path = Path(buf.value)
            if path.exists():
                return path
        except Exception:
            pass
        for name in ("Documents", "Dokumenty"):
            candidate = home / name
            if candidate.exists():
                return candidate
        return home / "Documents"
    else:
        config_file = home / ".config" / "user-dirs.dirs"
        if config_file.exists():
            try:
                content = config_file.read_text(encoding="utf-8")
                for line in content.splitlines():
                    if line.startswith("XDG_DOCUMENTS_DIR"):
                        value = line.split("=", 1)[1].strip().strip('"')
                        value = value.replace("$HOME", str(home))
                        path = Path(value)
                        if path.exists():
                            return path
            except Exception:
                pass

        for name in ("Documents", "Dokumenty"):
            candidate = home / name
            if candidate.exists():
                return candidate
        return home / "Documents"

documents_path = get_documents_folder() / "weight-adder" / "weight-adder-save.txt"
os.makedirs(documents_path.parent, exist_ok=True)

weights = [25, 20, 15, 10, 5, 2.5, 1.25, 0.5, 0.25]
BAR_WEIGHT = 20
loaded = []

def url():
    webbrowser.open("https://github.com/melamann00/weight_adder")

def strength_calculate(weight, reps):
    brzycki = weight / (1.0278 - 0.0278 * reps)
    epley = weight * (1 + 0.0333 * reps)
    oconner = weight * (1 + (0.025 * reps))
    avg_ORM = round((brzycki + epley + oconner) / 3, 2)
    return avg_ORM

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
        loaded.clear()
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


def temp_result():
    return " | ".join(map(str, loaded))


def saveresult():
    calculated_time = datetime.datetime.now()
    with open(documents_path, "a") as was:
        was.write(
            calculated_time.strftime("%c")
            + " "
            + entry.get()
            + "kg"
            + " "
            + temp_result()
            + "\n"
        )


def open_onerep_max():
    new_win = tk.Toplevel(root)
    menu = tk.Menu(new_win)
    new_win.config(menu=menu)
    new_win.title("Kalkulator One Rep Max")
    new_win.geometry("400x300")
    weight_reps = tk.Label(new_win, text="Podaj ciężar (kg):")
    weight_reps.pack()
    entry = tk.Entry(new_win, font=("Arial", 12))
    entry.pack(pady=5)
    weight_reps = tk.Label(new_win, text="Podaj ilość powtórzeń:")
    weight_reps.pack()
    entry_weight = tk.Entry(new_win, font=("Arial", 12))
    entry_weight.pack(pady=5)
    result_label = tk.Label(new_win, text="", font=("Arial", 12), wraplength=350)

    def orm_result():
        try:
            orm = strength_calculate(float(entry.get()), int(entry_weight.get()))
            result_label.config(text=f"One Rep Max: {orm} kg")
        except ValueError:
            messagebox.showerror("Błąd", "Podaj poprawne wartości.")

    calc_button = tk.Button(
        new_win,
        text="Przelicz",
        command=lambda: orm_result(),
    )
    calc_button.pack(pady=10)
    result_label.pack(pady=10)


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
savemenu = tk.Menu(menu)
menu.add_cascade(label="Save", menu=savemenu)
savemenu.add_command(label="Save result", command=saveresult)
othermenu = tk.Menu(menu)
menu.add_cascade(label="Other", menu=othermenu)
othermenu.add_command(label="One Rep Max calculator", command=open_onerep_max)
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
