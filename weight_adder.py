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

current_language = "pl"

translations = {
    "pl": {
        "app_title_plates": "Kalkulator talerzy na sztangę",
        "title_plates": "Kalkulator talerzy",
        "enter_total_weight": "Podaj ciężar całkowity (kg):",
        "btn_calc": "Przelicz",
        "btn_save": "Zapisz",
        "dark_mode": "Tryb ciemny",
        "app_title_orm": "Kalkulator One Rep Max",
        "title_orm": "Kalkulator One Rep Max",
        "enter_weight": "Podaj ciężar (kg):",
        "enter_reps": "Podaj ilość powtórzeń:",
        "orm_result_prefix": "One Rep Max: ",
        "menu_file": "Plik",
        "menu_new": "Nowy",
        "menu_exit": "Zakończ",
        "menu_save": "Zapisz",
        "menu_save_result": "Zapisz wynik",
        "menu_other": "Inne",
        "menu_orm_calc": "Kalkulator One Rep Max",
        "menu_help": "Pomoc",
        "menu_about": "O programie",
        "menu_language": "Język",
        "error_title": "Błąd",
        "err_weight_too_low": "Ciężar musi być większy lub równy 20 kg.",
        "err_weight_too_high": "Podano zbyt duży ciężar.",
        "err_invalid_number": "Podaj poprawną liczbę.",
        "err_invalid_values": "Podaj poprawne wartości.",
        "msg_no_weight": "Brak ciężaru do załadowania",
        "msg_cannot_load_exact": "Nie można dokładnie załadować takiego ciężaru.",
        "msg_plates_per_side": "Talerze na jedną stronę:\n"
    },
    "en": {
        "app_title_plates": "Barbell Plates Calculator",
        "title_plates": "Plates Calculator",
        "enter_total_weight": "Enter total weight (kg):",
        "btn_calc": "Calculate",
        "btn_save": "Save",
        "dark_mode": "Dark mode",
        "app_title_orm": "One Rep Max Calculator",
        "title_orm": "One Rep Max Calculator",
        "enter_weight": "Enter weight (kg):",
        "enter_reps": "Enter number of reps:",
        "orm_result_prefix": "One Rep Max: ",
        "menu_file": "File",
        "menu_new": "New",
        "menu_exit": "Exit",
        "menu_save": "Save",
        "menu_save_result": "Save result",
        "menu_other": "Other",
        "menu_orm_calc": "One Rep Max calculator",
        "menu_help": "Help",
        "menu_about": "About",
        "menu_language": "Language",
        "error_title": "Error",
        "err_weight_too_low": "Weight must be greater than or equal to 20 kg.",
        "err_weight_too_high": "Weight provided is too heavy.",
        "err_invalid_number": "Enter a valid number.",
        "err_invalid_values": "Enter valid values.",
        "msg_no_weight": "No weight to load",
        "msg_cannot_load_exact": "Cannot load this exact weight.",
        "msg_plates_per_side": "Plates per side:\n"
    }
}

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
            messagebox.showerror(translations[current_language]["error_title"], translations[current_language]["err_weight_too_low"])
            return
        elif wanted > 700:
            messagebox.showerror(translations[current_language]["error_title"], translations[current_language]["err_weight_too_high"])
            return
        if wanted == BAR_WEIGHT:
            result_label_widget.configure(text=translations[current_language]["msg_no_weight"])
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
            result_label_widget.configure(text=translations[current_language]["msg_cannot_load_exact"])
            state["loaded"] = []
        else:
            result_label_widget.configure(text=translations[current_language]["msg_plates_per_side"] + " | ".join(map(str, loaded)))
            state["loaded"] = loaded

    except ValueError:
        messagebox.showerror(translations[current_language]["error_title"], translations[current_language]["err_invalid_number"])
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

    file_btn = menu_bar.add_cascade(translations[current_language]["menu_file"])
    file_dd = new_dropdown(file_btn)
    file_dd.add_option(option=translations[current_language]["menu_new"], command=open_second_window)
    file_dd.add_separator()
    file_dd.add_option(option=translations[current_language]["menu_exit"], command=new_win.destroy)

    save_btn = menu_bar.add_cascade(translations[current_language]["menu_save"])
    save_dd = new_dropdown(save_btn)
    save_dd.add_option(option=translations[current_language]["menu_save_result"], command=lambda: save_result_orm(state["orm"], entry_weight, entry))

    other_btn = menu_bar.add_cascade(translations[current_language]["menu_other"])
    other_dd = new_dropdown(other_btn)
    other_dd.add_option(option=translations[current_language]["menu_orm_calc"], command=open_onerep_max)
    
    lang_btn = menu_bar.add_cascade(translations[current_language]["menu_language"])
    lang_dd = new_dropdown(lang_btn)
    lang_dd.add_option(option="Polski", command=lambda: set_language("pl"))
    lang_dd.add_option(option="English", command=lambda: set_language("en"))

    help_btn = menu_bar.add_cascade(translations[current_language]["menu_help"])
    help_dd = new_dropdown(help_btn)
    help_dd.add_option(option=translations[current_language]["menu_about"], command=url)

    new_win.title(translations[current_language]["title_orm"])
    new_win.geometry("600x400")
    title = ctk.CTkLabel(new_win, text=translations[current_language]["title_orm"], font=("JetBrains Mono", 16))
    title.pack(pady=10)
    weight_label = ctk.CTkLabel(new_win, text=translations[current_language]["enter_weight"], font=("JetBrains Mono", 16))
    weight_label.pack()
    entry = ctk.CTkEntry(new_win, font=("JetBrains Mono", 16))
    entry.pack(pady=5)
    reps_label = ctk.CTkLabel(new_win, text=translations[current_language]["enter_reps"], font=("JetBrains Mono", 16))
    reps_label.pack()
    entry_weight = ctk.CTkEntry(new_win, font=("JetBrains Mono", 16))
    entry_weight.pack(pady=5)
    result_label = ctk.CTkLabel(new_win, text="", font=("JetBrains Mono", 16), wraplength=350)

    def orm_result():
        try:
            orm = strength_calculator(float(entry.get()), int(entry_weight.get()))
            state["orm"] = orm
            result_label.configure(text=f"{translations[current_language]['orm_result_prefix']} {orm} kg")
        except ValueError:
            state["orm"] = None
            messagebox.showerror(translations[current_language]["error_title"], translations[current_language]["err_invalid_values"])

    calc_button = ctk.CTkButton(
        new_win,
        text=translations[current_language]["btn_calc"],
        command=lambda: orm_result(),
        font=("JetBrains Mono", 16),
        hover_color="green"
    )
    calc_button.pack(pady=10)
    result_label.pack(pady=10)
    
    switch_var = ctk.StringVar(value="on")
    switch = ctk.CTkSwitch(new_win, text=translations[current_language]["dark_mode"], command=lambda: apperance_mode(switch_var.get()), variable=switch_var, onvalue="on", offvalue="off")
    switch.pack(pady=10)
    
    save_button = ctk.CTkButton(new_win, text=translations[current_language]["btn_save"], command=lambda: save_result_orm(state["orm"], entry_weight, entry), font=("JetBrains Mono", 16))
    save_button.pack(pady=10, side="top")

def open_second_window():
    new_win = ctk.CTkToplevel(root)
    state = {"loaded": []}

    menu_bar = new_menu_bar(new_win)

    file_btn = menu_bar.add_cascade(translations[current_language]["menu_file"])
    file_dd = new_dropdown(file_btn)
    file_dd.add_option(option=translations[current_language]["menu_new"], command=open_second_window)
    file_dd.add_separator()
    file_dd.add_option(option=translations[current_language]["menu_exit"], command=new_win.destroy)

    save_btn = menu_bar.add_cascade(translations[current_language]["menu_save"])
    save_dd = new_dropdown(save_btn)
    save_dd.add_option(option=translations[current_language]["menu_save_result"], command=lambda: saveresult(entry, state))

    other_btn = menu_bar.add_cascade(translations[current_language]["menu_other"])
    other_dd = new_dropdown(other_btn)
    other_dd.add_option(option=translations[current_language]["menu_orm_calc"], command=open_onerep_max)
    
    lang_btn = menu_bar.add_cascade(translations[current_language]["menu_language"])
    lang_dd = new_dropdown(lang_btn)
    lang_dd.add_option(option="Polski", command=lambda: set_language("pl"))
    lang_dd.add_option(option="English", command=lambda: set_language("en"))

    help_btn = menu_bar.add_cascade(translations[current_language]["menu_help"])
    help_dd = new_dropdown(help_btn)
    help_dd.add_option(option=translations[current_language]["menu_about"], command=url)

    new_win.title(translations[current_language]["app_title_plates"])
    new_win.geometry("600x400")
    title_label = ctk.CTkLabel(new_win, text=translations[current_language]["title_plates"], font=("JetBrains Mono", 16))
    title_label.pack(pady=10)

    entry_label = ctk.CTkLabel(new_win, text=translations[current_language]["enter_total_weight"], font=("JetBrains Mono", 16))
    entry_label.pack()
    entry = ctk.CTkEntry(new_win, font=("JetBrains Mono", 16))
    entry.pack(pady=5)
    result_label = ctk.CTkLabel(new_win, text="", font=("JetBrains Mono", 16), wraplength=350)
    
    calc_button = ctk.CTkButton(
        new_win, text=translations[current_language]["btn_calc"],
        command=lambda: calculate(entry, result_label, state),
        font=("JetBrains Mono", 16),
        hover_color="green"
    )
    calc_button.pack(pady=10)
    result_label.pack(pady=10)
    
    switch_var = ctk.StringVar(value="on")
    switch = ctk.CTkSwitch(new_win, text=translations[current_language]["dark_mode"], command=lambda: apperance_mode(switch_var.get()), variable=switch_var, onvalue="on", offvalue="off")
    switch.pack(pady=10)
    
    save_button = ctk.CTkButton(new_win, text=translations[current_language]["btn_save"], command=lambda: saveresult(entry, root_state), font=("JetBrains Mono", 16))
    save_button.pack(pady=10, side="top")


def apperance_mode(switch_value):
    if switch_value == "on":
        ctk.set_appearance_mode("dark")
    elif switch_value == "off":
        ctk.set_appearance_mode("light")
    else:
        ctk.set_appearance_mode("System")

def set_language(lang_code):
    global current_language
    current_language = lang_code
    update_main_window_lang()

def update_main_window_lang():
    root.title(translations[current_language]["app_title_plates"])
    title_label.configure(text=translations[current_language]["title_plates"])
    entry_label.configure(text=translations[current_language]["enter_total_weight"])
    calc_button.configure(text=translations[current_language]["btn_calc"])
    save_button.configure(text=translations[current_language]["btn_save"])
    switch.configure(text=translations[current_language]["dark_mode"])
    result_label.configure(text="")

ctk.set_default_color_theme("blue")
root = ctk.CTk()
root_state = {"loaded": []}

root_menu_bar = new_menu_bar(root)

root_file_btn = root_menu_bar.add_cascade(translations[current_language]["menu_file"])
root_file_dd = new_dropdown(root_file_btn)
root_file_dd.add_option(option=translations[current_language]["menu_new"], command=open_second_window)
root_file_dd.add_separator()
root_file_dd.add_option(option=translations[current_language]["menu_exit"], command=root.quit)

root_save_btn = root_menu_bar.add_cascade(translations[current_language]["menu_save"])
root_save_dd = new_dropdown(root_save_btn)
root_save_dd.add_option(option=translations[current_language]["menu_save_result"], command=lambda: saveresult(entry, root_state))

root_other_btn = root_menu_bar.add_cascade(translations[current_language]["menu_other"])
root_other_dd = new_dropdown(root_other_btn)
root_other_dd.add_option(option=translations[current_language]["menu_orm_calc"], command=open_onerep_max)

root_lang_btn = root_menu_bar.add_cascade(translations[current_language]["menu_language"])
root_lang_dd = new_dropdown(root_lang_btn)
root_lang_dd.add_option(option="Polski", command=lambda: set_language("pl"))
root_lang_dd.add_option(option="English", command=lambda: set_language("en"))

root_help_btn = root_menu_bar.add_cascade(translations[current_language]["menu_help"])
root_help_dd = new_dropdown(root_help_btn)
root_help_dd.add_option(option=translations[current_language]["menu_about"], command=url)

root.title(translations[current_language]["app_title_plates"])
root.geometry("600x400")
root.resizable(True, True)
title_label = ctk.CTkLabel(root, text=translations[current_language]["title_plates"], font=("JetBrains Mono", 16))
title_label.pack(pady=10)
entry_label = ctk.CTkLabel(root, text=translations[current_language]["enter_total_weight"], font=("JetBrains Mono", 16))
entry_label.pack()
entry = ctk.CTkEntry(root, font=("JetBrains Mono", 16))
entry.pack(pady=5)
result_label = ctk.CTkLabel(root, text="", font=("JetBrains Mono", 16), wraplength=350)
calc_button = ctk.CTkButton(
    root, text=translations[current_language]["btn_calc"], command=lambda: calculate(entry, result_label, root_state), hover=True, hover_color="green", font=("JetBrains Mono", 16)
)
calc_button.pack(pady=10)
result_label.pack(pady=10)
switch_var = ctk.StringVar(value="on")
switch = ctk.CTkSwitch(root, text=translations[current_language]["dark_mode"], command=lambda: apperance_mode(switch_var.get()), variable=switch_var, onvalue="on", offvalue="off")
switch.pack(pady=10)
apperance_mode("on")
save_button = ctk.CTkButton(root, text=translations[current_language]["btn_save"], command=lambda: saveresult(entry, root_state), font=("JetBrains Mono", 16))
save_button.pack(pady=10, side="top")

root.mainloop()