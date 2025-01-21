import tkinter as tk
from tkinter import ttk
from product_page import create_product_page
from gui import create_gui_page
from cabin_page import create_cabin_page  # Импорт новой страницы для кабин
from expenses_page import create_expenses_page
from statistic_page import create_statistics_page
from booking_page import create_booking_page

# Функция стилизации
def style_frame(frame, bg_color="#f0f0f0", font_color="#333", button_color="#4CAF50"):
    frame.configure(bg=bg_color)  # Устанавливаем фон фрейма
    for widget in frame.winfo_children():
        if isinstance(widget, tk.Label):  # Стили для меток
            widget.configure(bg=bg_color, fg=font_color, font=("Helvetica", 14))
        elif isinstance(widget, tk.Button):  # Стили для кнопок
            widget.configure(bg=button_color, fg="#fff", font=("Helvetica", 12), relief=tk.FLAT)


def create_navigation(root, show_main_page,show_booking_page, show_products_page, show_gui_page, show_cabin_page, show_expenses_page, show_statistics_page):
    nav_frame = tk.Frame(root)
    nav_frame.pack(side=tk.TOP, fill=tk.X)
    
    tk.Button(nav_frame, text="Главная", command=show_main_page).pack(side=tk.LEFT)
    tk.Button(nav_frame, text="Бронирование", command=show_booking_page).pack(side=tk.LEFT)
    tk.Button(nav_frame, text="Склад продуктов", command=show_products_page).pack(side=tk.LEFT)
    tk.Button(nav_frame, text="Страница заказов", command=show_gui_page).pack(side=tk.LEFT)
    tk.Button(nav_frame, text="Кабинки", command=show_cabin_page).pack(side=tk.LEFT)  # Кнопка для кабин
    tk.Button(nav_frame, text="Расходы", command=show_expenses_page).pack(side=tk.LEFT)  # Кнопка для кабин
    tk.Button(nav_frame, text="Статистика", command=show_statistics_page).pack(side=tk.LEFT)  # Кнопка для кабин


def main():
    root = tk.Tk()
    root.title("CRM Navigation Panel")
    root.geometry("1200x800")  # Устанавливаем начальный размер окна
    root.minsize(800, 600)     # Устанавливаем минимальный размер окна
    root.maxsize(1920, 1080)   # Устанавливаем максимальный размер окна
    root.configure(bg="#f9f9f9")
     # Создаем стиль
    style = ttk.Style()
    style.theme_use("clam")  # Используем нейтральную тему
    style.configure("TButton", font=("Helvetica", 12), padding=6, background="#4CAF50", foreground="#fff")
    style.configure("TLabel", font=("Helvetica", 12), background="#f9f9f9", foreground="#333")
    style.configure("TEntry", font=("Helvetica", 12), padding=4)
    style.map("TButton", background=[("active", "#45A049")])

    def resize_handler(event):
        # Обработка изменения размера, если необходимо
        #print(f"New size: {event.width}x{event.height}")

        root.bind("<Configure>", resize_handler)


    def show_main_page():
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        frame_expenses.pack_forget()
        frame_statistics.pack_forget()
        welcome_label.pack()
        frame_booking.pack_forget()
        root.update_idletasks()

    def show_products_page():
        welcome_label.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        frame_expenses.pack_forget()
        frame_statistics.pack_forget()
        frame_products.pack()
        frame_booking.pack_forget()
        root.update_idletasks()

    def show_gui_page():
        welcome_label.pack_forget()
        frame_products.pack_forget()
        frame_cabin.pack_forget()
        frame_expenses.pack_forget()
        frame_statistics.pack_forget()
        frame_booking.pack_forget()
        frame_gui.pack()
        root.update_idletasks()

    def show_cabin_page():
        welcome_label.pack_forget()
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_expenses.pack_forget()
        frame_statistics.pack_forget()
        frame_booking.pack_forget()
        frame_cabin.pack()
        root.update_idletasks()

    def show_expenses_page():
        welcome_label.pack_forget()
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        frame_statistics.pack_forget()
        frame_booking.pack_forget()
        frame_expenses.pack()
        root.update_idletasks()

    def show_statistics_page():
        welcome_label.pack_forget()
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        frame_expenses.pack_forget()
        frame_booking.pack_forget()
        frame_statistics.pack()
        root.update_idletasks()

    def show_booking_page():
        welcome_label.pack_forget()
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        frame_expenses.pack_forget()
        frame_booking.pack()
        frame_statistics.pack_forget()
        root.update_idletasks()

    welcome_label = tk.Label(root, text="Добро пожаловать на главную страницу!")
    welcome_label.pack()

    frame_products = create_product_page(root)
    frame_gui = create_gui_page(root)
    frame_cabin = create_cabin_page(root)  # Создаем новую страницу кабин
    frame_expenses = create_expenses_page(root)
    frame_statistics = create_statistics_page(root)
    frame_booking = create_booking_page(root)
     # Применяем стили к страницам
    style_frame(frame_booking, bg_color="#e6f7ff", font_color="#004d99", button_color="#0073e6")
    style_frame(frame_products, bg_color="#e6f7ff", font_color="#004d99", button_color="#0073e6")
    style_frame(frame_gui, bg_color="#e6f7ff", font_color="#004d99", button_color="#0073e6")

    
    frame_products.pack_forget()
    frame_gui.pack_forget()
    frame_cabin.pack_forget()
    frame_expenses.pack_forget()
    frame_statistics.pack_forget()
    frame_booking.pack_forget()

    create_navigation(root, show_main_page, show_booking_page, show_products_page, show_gui_page, show_cabin_page, show_expenses_page, show_statistics_page)

    root.mainloop()

if __name__ == "__main__":
    main()
