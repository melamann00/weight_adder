import os
import sys
import customtkinter as ctk
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import messagebox
from CTkMenuBarPlus import CTkMenuBar, CustomDropdownMenu

MB_BAR_COLOR = ("#dbdbdb", "#242424")           # menu bar background
MB_TEXT_COLOR = ("black", "white")              # button/option text
MB_HOVER_COLOR = ("#c6c6c6", "#333333")         # hover highlight
MB_DROPDOWN_BG = ("#ebebeb", "#2b2b2b")         # dropdown panel background
MB_SEPARATOR_COLOR = ("#bfbfbf", "#3f3f3f")     # separator line in dropdown

def new_menu_bar(win):
    return CTkMenuBar(master=win, bg_color=MB_BAR_COLOR)

def new_dropdown(button):
    return CustomDropdownMenu(
        widget=button,
        bg_color=MB_DROPDOWN_BG,
        fg_color=MB_DROPDOWN_BG,
        text_color=MB_TEXT_COLOR,
        hover_color=MB_HOVER_COLOR,
        separator_color=MB_SEPARATOR_COLOR,
        font=("JetBrains Mono", 10),
    )

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

documents_path = get_documents_folder() / "weight-adder"
os.makedirs(documents_path.parent, exist_ok=True)
weights = [25, 20, 15, 10, 5, 2.5, 1.25, 0.5, 0.25]
BAR_WEIGHT = 20
loaded = []

def url():
    webbrowser.open("https://github.com/melamann00/weight_adder")

def strength_calculator(weight, reps):
    brzycki = weight / (1.0278 - 0.0278 * reps)
    epley = weight * (1 + 0.0333 * reps)
    oconner = weight * (1 + (0.025 * reps))
    avg_ORM = round((brzycki + epley + oconner) / 3, 2)
    return avg_ORM

def calculate(entry_widget, result_label_widget, state):
    try:
        wanted = float(entry_widget.get())
        if wanted < BAR_WEIGHT:
            messagebox.showerror("Błąd", "Ciężar musi być większy lub równy 20 kg.")
            return
        elif wanted > 700:
            messagebox.showerror("Błąd", "Podano zbyt duży ciężar.")
            return
        if wanted == BAR_WEIGHT:
            result_label_widget.configure(text="Brak ciężaru do załadowania")
            state["loaded"] = []
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
            result_label_widget.configure(
                text="Nie można dokładnie załadować takiego ciężaru."
            )
            state["loaded"] = []
        else:
            result_label_widget.configure(
                text="Talerze na jedną stronę:\n" + " | ".join(map(str, loaded))
            )
            state["loaded"] = loaded

    except ValueError:
        messagebox.showerror("Błąd", "Podaj poprawną liczbę.")
        state["loaded"] = []

def temp_result(state):
    return " | ".join(map(str, state["loaded"]))

def saveresult(entry_widget, state):
    calculated_time = datetime.now()
    with open(documents_path  / "weight-adder-save-plates.txt", "a") as was:
        was.write(
            calculated_time.strftime("%c")
            + " "
            + entry_widget.get()
            + "kg"
            + " "
            + " | ".join(map(str, state.get("loaded", [])))
            + "\n"
        )

def save_result_orm(orm, entry, entry_weight):
    calculated_time = datetime.now()
    with open(documents_path / "weight-adder-save-orm.txt", "a") as was2:
        was2.write(
            calculated_time.strftime("%c")
            + " "
            + str(orm)
            + " kg "
            +entry_weight.get()
            +" kg | "
            +entry.get()
            +" reps\n"
        )


def open_onerep_max():
    new_win = ctk.CTkToplevel(root)
    state = {"orm": None}

    menu_bar = new_menu_bar(new_win)

    file_btn = menu_bar.add_cascade("File")
    file_dd = new_dropdown(file_btn)
    file_dd.add_option(option="New", command=open_second_window)
    file_dd.add_separator()
    file_dd.add_option(option="Exit", command=new_win.destroy)

    save_btn = menu_bar.add_cascade("Save")
    save_dd = new_dropdown(save_btn)
    save_dd.add_option(option="Save result", command=lambda: save_result_orm(state["orm"], entry_weight, entry))

    other_btn = menu_bar.add_cascade("Other")
    other_dd = new_dropdown(other_btn)
    other_dd.add_option(option="One Rep Max calculator", command=open_onerep_max)

    help_btn = menu_bar.add_cascade("Help")
    help_dd = new_dropdown(help_btn)
    help_dd.add_option(option="About", command=url)

    new_win.title("Kalkulator One Rep Max")
    new_win.geometry("600x400")
    title = ctk.CTkLabel(new_win, text="Kalkulator One Rep Max", font=("JetBrains Mono", 16))
    title.pack(pady=10)
    weight_reps = ctk.CTkLabel(new_win, text="Podaj ciężar (kg):", font=("JetBrains Mono", 16))
    weight_reps.pack()
    entry = ctk.CTkEntry(new_win, font=("JetBrains Mono", 16))
    entry.pack(pady=5)
    weight_reps = ctk.CTkLabel(new_win, text="Podaj ilość powtórzeń:", font=("JetBrains Mono", 16))
    weight_reps.pack()
    entry_weight = ctk.CTkEntry(new_win, font=("JetBrains Mono", 16))
    entry_weight.pack(pady=5)
    result_label = ctk.CTkLabel(new_win, text="", font=("JetBrains Mono", 16), wraplength=350)

    def orm_result():
        try:
            orm = strength_calculator(float(entry.get()), int(entry_weight.get()))
            state["orm"] = orm
            result_label.configure(text=f"One Rep Max: {orm} kg")
        except ValueError:
            state["orm"] = None
            messagebox.showerror("Błąd", "Podaj poprawne wartości.")

    calc_button = ctk.CTkButton(
        new_win,
        text="Przelicz",
        command=lambda: orm_result(),
        font=("JetBrains Mono", 16),
        hover_color="green"
    )
    calc_button.pack(pady=10)
    result_label.pack(pady=10)
    dark_mode_switch(new_win)
    save_button = ctk.CTkButton(new_win, text="Save", command=lambda: save_result_orm(state["orm"], entry_weight, entry), font=("JetBrains Mono", 16))
    save_button.pack(pady=10, side="top")


def open_second_window():
    new_win = ctk.CTkToplevel(root)
    state = {"loaded": []}

    menu_bar = new_menu_bar(new_win)

    file_btn = menu_bar.add_cascade("File")
    file_dd = new_dropdown(file_btn)
    file_dd.add_option(option="New", command=open_second_window)
    file_dd.add_separator()
    file_dd.add_option(option="Exit", command=new_win.destroy)

    save_btn = menu_bar.add_cascade("Save")
    save_dd = new_dropdown(save_btn)
    save_dd.add_option(option="Save result", command=lambda: saveresult(entry, state))

    other_btn = menu_bar.add_cascade("Other")
    other_dd = new_dropdown(other_btn)
    other_dd.add_option(option="One Rep Max calculator", command=open_onerep_max)

    help_btn = menu_bar.add_cascade("Help")
    help_dd = new_dropdown(help_btn)
    help_dd.add_option(option="About", command=url)

    new_win.title("Kalkulator talerzy na sztangę")
    new_win.geometry("600x400")
    title_label = ctk.CTkLabel(new_win, text="Kalkulator talerzy", font=("JetBrains Mono", 16))
    title_label.pack(pady=10)

    entry_label = ctk.CTkLabel(new_win, text="Podaj ciężar całkowity (kg):", font=("JetBrains Mono", 16))
    entry_label.pack()
    entry = ctk.CTkEntry(new_win, font=("JetBrains Mono", 16))
    entry.pack(pady=5)
    result_label = ctk.CTkLabel(new_win, text="", font=("JetBrains Mono", 16), wraplength=350)
    calc_button = ctk.CTkButton(
        new_win, text="Przelicz",
        command=lambda: calculate(entry, result_label, state),
        font=("JetBrains Mono", 16),
        hover_color="green"
    )
    calc_button.pack(pady=10)
    result_label.pack(pady=10)
    dark_mode_switch(new_win)
    save_button = ctk.CTkButton(new_win, text="Save", command=lambda: saveresult(entry, root_state), font=("JetBrains Mono", 16))
    save_button.pack(pady=10, side="top")




def apperance_mode(switch_value):
    if switch_value == "on":
        ctk.set_appearance_mode("dark")
    elif switch_value == "off":
        ctk.set_appearance_mode("light")
    else:
        ctk.set_appearance_mode("System")

ctk.set_default_color_theme("blue")

root = ctk.CTk()
root_state = {"loaded": []}

root_menu_bar = new_menu_bar(root)

root_file_btn = root_menu_bar.add_cascade("File")
root_file_dd = new_dropdown(root_file_btn)
root_file_dd.add_option(option="New", command=open_second_window)
root_file_dd.add_separator()
root_file_dd.add_option(option="Exit", command=root.quit)

root_save_btn = root_menu_bar.add_cascade("Save")
root_save_dd = new_dropdown(root_save_btn)
root_save_dd.add_option(option="Save result", command=lambda: saveresult(entry, root_state))

root_other_btn = root_menu_bar.add_cascade("Other")
root_other_dd = new_dropdown(root_other_btn)
root_other_dd.add_option(option="One Rep Max calculator", command=open_onerep_max)

root_help_btn = root_menu_bar.add_cascade("Help")
root_help_dd = new_dropdown(root_help_btn)
root_help_dd.add_option(option="About", command=url)

root.title("Kalkulator talerzy na sztangę")
root.geometry("600x400")
root.resizable(True, True)
title_label = ctk.CTkLabel(root, text="Kalkulator  talerzy", font=("JetBrains Mono", 16))
title_label.pack(pady=10)
entry_label = ctk.CTkLabel(root, text="Podaj ciężar całkowity (kg):", font=("JetBrains Mono", 16))
entry_label.pack()
entry = ctk.CTkEntry(root, font=("JetBrains Mono", 16))
entry.pack(pady=5)
result_label = ctk.CTkLabel(root, text="", font=("JetBrains Mono", 16), wraplength=350)
calc_button = ctk.CTkButton(
    root, text="Przelicz", command=lambda: calculate(entry, result_label, root_state), hover=True, hover_color="green", font=("JetBrains Mono", 16)
)
calc_button.pack(pady=10)
result_label.pack(pady=10)
def dark_mode_switch(window):
    def switch_event():
        apperance_mode(switch_var.get())
        window.update()

    switch_var = ctk.StringVar(value="on")
    switch = ctk.CTkSwitch(window, text="Tryb ciemny", command=switch_event, variable=switch_var, onvalue="on", offvalue="off")
    switch.pack(pady=10)
    apperance_mode("on")
    window.update()

dark_mode_switch(root)
save_button = ctk.CTkButton(root, text="Save", command=lambda: saveresult(entry, root_state), font=("JetBrains Mono", 16))
save_button.pack(pady=10, side="top")
root.mainloop()