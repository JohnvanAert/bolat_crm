import tkinter as tk

def create_navigation(root, show_main_page, show_products_page, show_gui_page):
    nav_frame = tk.Frame(root)
    nav_frame.pack(side="top", fill="x")

    btn_main = tk.Button(nav_frame, text="Главная", command=show_main_page)
    btn_main.pack(side="left")

    btn_products = tk.Button(nav_frame, text="Склад продуктов", command=show_products_page)
    btn_products.pack(side="left")

    btn_gui = tk.Button(nav_frame, text="GUI Страница", command=show_gui_page)
    btn_gui.pack(side="left")

    return nav_frame
