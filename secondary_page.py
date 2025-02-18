import tkinter as tk
from tkinter import Button, Frame, Label

def create_secondary_page(root):
    frame = tk.Frame(root)
    frame.pack(fill='both', expand=True)  # Добавляем эту строку
    
    main_area = Frame(frame, bg='#e0e0e0', width=824, height=768)
    main_area.pack(side='left', fill='both', expand=True)

    Label(main_area, text="Персонал", bg='#e0e0e0', font=('Arial', 14)).pack(pady=10)

    open_orders_frame = Frame(main_area, bg='#ffffff', width=600, height=500)
    open_orders_frame.pack(pady=20, padx=20, fill='both', expand=True)


    return frame  # Добавляем return без mainloop
