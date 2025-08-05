import tkinter as tk

# Funktion, die auf Tastendruck reagiert
def on_key(event):
    key = event.keysym  # Name der gedrückten Taste
    if key == "a":
        label.config(text="Taste A gedrückt → Hallo ESP32!")
    elif key == "b":
        label.config(text="Taste B gedrückt → Starte Motor...")
    elif key == "Escape":
        root.destroy()  # mit ESC Programm beenden
    else:
        label.config(text=f"Taste {key} gedrückt")

# Hauptfenster erstellen
root = tk.Tk()
root.title("Tasteneingaben GUI")
root.geometry("500x200")

# Textlabel
label = tk.Label(root, text="Drücke eine Taste ...", font=("Arial", 16))
label.pack(pady=50)

# Event-Handler binden
root.bind("<Key>", on_key)

# GUI starten
root.mainloop()
