import tkinter as tk
from tkinter import messagebox


weights = [25, 20, 15, 10, 5, 2.5, 1.25, 0.5]
BAR_WEIGHT = 20
def calculate():
    try:   
        wanted = float(entry.get())
        if wanted < BAR_WEIGHT:
            messagebox.showerror("Błąd", "Ciężar musi być większy lub równy 20 kg.")
            return
        if wanted == BAR_WEIGHT:
            result_label.config(text="Brak ciężaru do załadowania")
            return
        weight_per_side = (wanted - BAR_WEIGHT) / 2
        loaded = []
        for weight in weights:
            while weight_per_side - weight >= 0:
                loaded.append(weight)
                weight_per_side -= weight
        if weight_per_side > 0:
            result_label.config(text="Nie można dokładnie załadować takiego ciężaru.")
        else:
            result_label.config(
                text="Talerze na jedną stronę:\n" + " | ".join(map(str, loaded))
            )
    except ValueError:
        messagebox.showerror("Błąd", "Podaj poprawną liczbę.")

root = tk.Tk()
root.title("Kalkulator talerzy na sztangę")
root.geometry("400x300")
root.resizable(True, True)
title_label = tk.Label(root, text="Kalkulator talerzy", font=("Arial", 16))
title_label.pack(pady=10)
entry_label = tk.Label(root, text="Podaj ciężar całkowity (kg):")
entry_label.pack()
entry = tk.Entry(root, font=("Arial", 12))
entry.pack(pady=5)
calc_button = tk.Button(root, text="Count", command=calculate)
calc_button.pack(pady=10)
result_label = tk.Label(root, text="", font=("Arial", 12), wraplength=350)
result_label.pack(pady=10)
root.mainloop()