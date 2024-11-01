import tkinter as tk
from product_page import create_product_page
from gui import create_gui_page
from cabin_page import create_cabin_page  # Импорт новой страницы для кабин

def create_navigation(root, show_main_page, show_products_page, show_gui_page, show_cabin_page):
    nav_frame = tk.Frame(root)
    nav_frame.pack(side=tk.TOP, fill=tk.X)
    
    tk.Button(nav_frame, text="Главная", command=show_main_page).pack(side=tk.LEFT)
    tk.Button(nav_frame, text="Склад продуктов", command=show_products_page).pack(side=tk.LEFT)
    tk.Button(nav_frame, text="GUI Страница", command=show_gui_page).pack(side=tk.LEFT)
    tk.Button(nav_frame, text="Кабинки", command=show_cabin_page).pack(side=tk.LEFT)  # Кнопка для кабин

def main():
    root = tk.Tk()
    root.title("CRM Navigation Panel")

    def show_main_page():
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        welcome_label.pack()

    def show_products_page():
        welcome_label.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        frame_products.pack()

    def show_gui_page():
        welcome_label.pack_forget()
        frame_products.pack_forget()
        frame_cabin.pack_forget()
        frame_gui.pack()

    def show_cabin_page():
        welcome_label.pack_forget()
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack()

    welcome_label = tk.Label(root, text="Добро пожаловать на главную страницу!")
    welcome_label.pack()

    frame_products = create_product_page(root)
    frame_gui = create_gui_page(root)
    frame_cabin = create_cabin_page(root)  # Создаем новую страницу кабин

    frame_products.pack_forget()
    frame_gui.pack_forget()
    frame_cabin.pack_forget()

    create_navigation(root, show_main_page, show_products_page, show_gui_page, show_cabin_page)

    root.mainloop()

if __name__ == "__main__":
    main()
