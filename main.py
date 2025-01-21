import tkinter as tk
from tkinter import ttk
from product_page import create_product_page
from gui import create_gui_page
from cabin_page import create_cabin_page  # Импорт новой страницы для кабин
from expenses_page import create_expenses_page
from statistic_page import create_statistics_page
from booking_page import create_booking_page
from database import get_occupied_cabins, get_sold_products
from datetime import datetime

def style_all_widgets(widget, frame_bg="#c01aa3", font_color="#004d99", button_bg="#0073e6", button_fg="#004d99"):
    """Применение стилей ко всем фреймам и кнопкам рекурсивно."""
    if isinstance(widget, tk.Frame):  # Если это фрейм
        widget.configure(bg=frame_bg)
    elif isinstance(widget, tk.Button):  # Если это кнопка
        widget.configure(bg=button_bg, fg=button_fg, font=("Helvetica", 12), relief=tk.FLAT)
    elif isinstance(widget, tk.Label):  # Стили для меток
            widget.configure(bg=frame_bg, fg=font_color, font=("Helvetica", 14))

    # Применяем стили рекурсивно ко всем дочерним виджетам
    for child in widget.winfo_children():
        style_all_widgets(child, frame_bg, font_color, button_bg, button_fg)

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

current_page = 1
page_size = 15  

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
    style.configure("TLabel", font=("Helvetica", 12), background="#000000", foreground="#333")
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
        main_page.pack()
        frame_booking.pack_forget()
        root.update_idletasks()

    def show_products_page():
        main_page.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        frame_expenses.pack_forget()
        frame_statistics.pack_forget()
        frame_products.pack()
        frame_booking.pack_forget()
        root.update_idletasks()

    def show_gui_page():
        main_page.pack_forget()
        frame_products.pack_forget()
        frame_cabin.pack_forget()
        frame_expenses.pack_forget()
        frame_statistics.pack_forget()
        frame_booking.pack_forget()
        frame_gui.pack()
        root.update_idletasks()

    def show_cabin_page():
        main_page.pack_forget()
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_expenses.pack_forget()
        frame_statistics.pack_forget()
        frame_booking.pack_forget()
        frame_cabin.pack()
        root.update_idletasks()

    def show_expenses_page():
        main_page.pack_forget()
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        frame_statistics.pack_forget()
        frame_booking.pack_forget()
        frame_expenses.pack()
        root.update_idletasks()

    def show_statistics_page():
        main_page.pack_forget()
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        frame_expenses.pack_forget()
        frame_booking.pack_forget()
        frame_statistics.pack()
        root.update_idletasks()

    def show_booking_page():
        main_page.pack_forget()
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        frame_expenses.pack_forget()
        frame_booking.pack()
        frame_statistics.pack_forget()
        root.update_idletasks()
    
    def update_occupied_cabins():
        cabins_listbox.delete(0, tk.END)  # Очистка текущего списка
        occupied_cabins = get_occupied_cabins()  # Получение данных о занятых кабинах

        if occupied_cabins:
            for cabin in occupied_cabins:
                cabin_name = cabin["cabin_name"]
                end_time = cabin["end_time"]

                # Рассчитываем оставшееся время
                now = datetime.now()
                remaining_time = end_time - now

                if remaining_time.total_seconds() > 0:
                    hours, remainder = divmod(remaining_time.total_seconds(), 3600)
                    minutes = remainder // 60
                    time_left = f"{int(hours)} ч {int(minutes)} мин"
                    cabins_listbox.insert(tk.END, f"{cabin_name} - осталось: {time_left}")
                else:
                    cabins_listbox.insert(tk.END, f"{cabin_name} - аренда завершена")
        else:
            cabins_listbox.insert(tk.END, "Нет занятых кабин")

        # Запускаем функцию снова через 1 минуту (60 000 миллисекунд)
        cabins_listbox.after(60000, update_occupied_cabins)




    def update_sold_products():
        global current_page
        sold_listbox.delete(0, tk.END)  # Очистка текущего списка
        sold_products = get_sold_products(page=current_page, page_size=page_size)  # Получение данных о проданных товарах

        if sold_products:
            for product in sold_products:
                product_name = product["product_name"]
                cabin_name = product["cabin_name"]
                order_time = product["order_time"].strftime("%Y-%m-%d %H:%M:%S")
                quantity = product["quantity"]
                price = product["price"]

                sold_listbox.insert(
                    tk.END,
                    f"{order_time} | Кабина: {cabin_name} | Продукт: {product_name} | Кол-во: {quantity} | Цена: {price} руб."
                )
        else:
            sold_listbox.insert(tk.END, "Нет проданных товаров")

        check_buttons_state()

    def auto_update_sold_products():
        update_sold_products()
        sold_listbox.after(60000, auto_update_sold_products)  # Обновление каждые 60 секунд

    # Функция для переключения на следующую страницу
    def next_page():
        global current_page
        current_page += 1
        update_sold_products()

    # Функция для переключения на предыдущую страницу
    def previous_page():
        global current_page
        if current_page > 1:
            current_page -= 1
            update_sold_products()

    # Проверка состояния кнопок
    def check_buttons_state():
        global current_page

        # Проверяем, есть ли данные на следующей странице
        next_page_data = get_sold_products(page=current_page + 1, page_size=page_size)
        if next_page_data:
            next_button.config(state=tk.NORMAL)
        else:
            next_button.config(state=tk.DISABLED)

        # Отключаем кнопку "Предыдущая страница", если текущая страница первая
        if current_page == 1:
            prev_button.config(state=tk.DISABLED)
        else:
            prev_button.config(state=tk.NORMAL)

    # Главная страница
    create_navigation(root, show_main_page, show_booking_page, show_products_page, show_gui_page, show_cabin_page, show_expenses_page, show_statistics_page)
    main_page = tk.Frame(root)
    main_page.pack()
    welcome_label = tk.Label(main_page, text="Добро пожаловать на главную страницу!", font=("Helvetica", 18), bg="#000")
    welcome_label.pack()

    tk.Label(main_page, text="Занятые кабины:", font=("Helvetica", 16), bg="#000").pack(pady=5)
    cabins_listbox = tk.Listbox(main_page, font=("Helvetica", 14), height=10, width=50)
    cabins_listbox.pack()
    # Интерфейс
    tk.Label(main_page, text="Заказы:", font=("Helvetica", 16)).pack(pady=5)
    sold_listbox = tk.Listbox(main_page, font=("Helvetica", 14), height=15, width=80)
    sold_listbox.pack()

    # Кнопки навигации
    pagination_frame = tk.Frame(main_page)
    pagination_frame.pack(pady=10)

    prev_button = tk.Button(pagination_frame, text="Предыдущая страница", command=previous_page)
    prev_button.pack(side=tk.LEFT, padx=1)

    next_button = tk.Button(pagination_frame, text="Следующая страница", command=next_page)
    next_button.pack(side=tk.LEFT, padx=1)



    frame_products = create_product_page(root)
    frame_gui = create_gui_page(root)
    frame_cabin = create_cabin_page(root)  # Создаем новую страницу кабин
    frame_expenses = create_expenses_page(root)
    frame_statistics = create_statistics_page(root)
    frame_booking = create_booking_page(root)
     # Применяем стили к страницам

     
    # Применяем стили ко всем страницам и их содержимому
    style_all_widgets(main_page, frame_bg="#e6f7ff", font_color="#004d99", button_bg="#0073e6", button_fg="#004d99")
    style_all_widgets(frame_booking, frame_bg="#e6f7ff", font_color="#004d99", button_bg="#0073e6", button_fg="#004d99")
    style_all_widgets(frame_products, frame_bg="#e6f7ff", font_color="#004d99", button_bg="#0073e6", button_fg="#004d99")
    style_all_widgets(frame_gui, frame_bg="#e6f7ff", font_color="#004d99", button_bg="#0073e6", button_fg="#004d99")
    style_all_widgets(frame_cabin, frame_bg="#e6f7ff", font_color="#004d99", button_bg="#0073e6", button_fg="#004d99")
    style_all_widgets(frame_statistics, frame_bg="#e6f7ff", font_color="#004d99", button_bg="#0073e6", button_fg="#004d99")
    style_all_widgets(frame_expenses, frame_bg="#e6f7ff", font_color="#004d99", button_bg="#0073e6", button_fg="#004d99")

    
    
    frame_products.pack_forget()
    frame_gui.pack_forget()
    frame_cabin.pack_forget()
    frame_expenses.pack_forget()
    frame_statistics.pack_forget()
    frame_booking.pack_forget()
    auto_update_sold_products()
    update_occupied_cabins()
    root.mainloop()

if __name__ == "__main__":
    main()
