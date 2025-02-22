import tkinter as tk
from tkinter import Button, Frame, Label

def create_secondary_page(root):
    frame = tk.Frame(root)
    frame.pack(fill='both', expand=True)  # Добавляем эту строку
    
    main_area = Frame(frame)
    main_area.pack(fill='both', expand=True)

    Label(main_area, text="Персонал", bg='#e0e0e0', font=('Arial', 14)).pack(pady=10)

    return frame  # Добавляем return без mainloop
