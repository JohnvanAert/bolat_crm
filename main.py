import tkinter as tk
from tkinter import ttk
from product_page import create_product_page
from gui import create_gui_page
from cabin_page import create_cabin_page  # Импорт новой страницы для кабин
from expenses_page import create_expenses_page
from statistic_page import create_statistics_page
from booking_page import create_booking_page
from database import get_occupied_cabins, get_sold_products, fetch_low_stock_products
from datetime import datetime

def style_all_widgets(widget, frame_bg="#c01aa3", font_color="#004d99", button_bg="#6fa8dc", button_fg="#004d99"):
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
restock_page = 1
occupied_cabins_page = 1
page_size = 15  

def main():
    root = tk.Tk()
    root.title("Bublik")
    root.geometry("1200x800")  # Устанавливаем начальный размер окна
    root.minsize(800, 600)     # Устанавливаем минимальный размер окна
    root.maxsize(1920, 1080)   # Устанавливаем максимальный размер окна
    root.configure(bg="#e6f7ff")
     # Создаем стиль
    style = ttk.Style()
    style.theme_use("clam")  # Используем нейтральную тему
    style.configure("TButton", font=("Helvetica", 12), padding=6, background="#4CAF50", foreground="#fff")
    style.configure("TLabel", font=("Helvetica", 12), background="#d7d7d7", foreground="#004d99")
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
        global occupied_cabins_page
        cabins_listbox.delete(0, tk.END)  # Очистка текущего списка
        occupied_cabins = get_occupied_cabins()  # Получение данных о занятых кабинах

        if occupied_cabins:
            start_idx = (occupied_cabins_page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_cabins = occupied_cabins[start_idx:end_idx]  # Пагинация данных

            for cabin in paginated_cabins:
                cabin_name = cabin["cabin_name"]
                start_time = cabin["start_time"]
                end_time = cabin["end_time"]

                now = datetime.now()

                if now < start_time:
                    # До начала аренды
                    time_until_start = start_time - now
                    hours, remainder = divmod(time_until_start.total_seconds(), 3600)
                    minutes = remainder // 60
                    time_left = f"{int(hours)} ч {int(minutes)} мин"
                    cabins_listbox.insert(tk.END, f"{cabin_name} - до начала аренды: {time_left}")
                elif start_time <= now <= end_time:
                    # Во время аренды
                    remaining_time = end_time - now
                    hours, remainder = divmod(remaining_time.total_seconds(), 3600)
                    minutes = remainder // 60
                    time_left = f"{int(hours)} ч {int(minutes)} мин"
                    cabins_listbox.insert(tk.END, f"{cabin_name} - осталось: {time_left}")
                else:
                    # Аренда завершена
                    cabins_listbox.insert(tk.END, f"{cabin_name} - аренда завершена")
        else:
            cabins_listbox.insert(tk.END, "Нет занятых кабин")

        # Запускаем функцию снова через 1 минуту (60 000 миллисекунд)
        cabins_listbox.after(60000, update_occupied_cabins)
        check_cabins_buttons_state()


    # Функции для управления пагинацией "Занятых кабин"
    def next_cabins_page():
        global occupied_cabins_page
        occupied_cabins_page += 1
        update_occupied_cabins()

    def previous_cabins_page():
        global occupied_cabins_page
        if occupied_cabins_page > 1:
            occupied_cabins_page -= 1
            update_occupied_cabins()

    def check_cabins_buttons_state():
        global occupied_cabins_page
        total_cabins = len(get_occupied_cabins())
        if (occupied_cabins_page * page_size) >= total_cabins:
            next_cabins_button.config(state=tk.DISABLED)
        else:
            next_cabins_button.config(state=tk.NORMAL)

        if occupied_cabins_page == 1:
            prev_cabins_button.config(state=tk.DISABLED)
        else:
            prev_cabins_button.config(state=tk.NORMAL)
    


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
            sold_listbox.insert(tk.END, "Нет заказанных товаров")

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

    # Создаем рамку для содержимого
    content_frame = tk.Frame(main_page, bg="#7FC3BD")
    content_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    # Занятые кабины (левая колонка)
    tk.Label(content_frame, text="Занятые кабины:", font=("Helvetica", 16), bg="#7FC3BD", fg="#93c47d").grid(row=0, column=0, padx=10, pady=5, sticky="nw")
    cabins_listbox = tk.Listbox(content_frame, font=("Helvetica", 14), bg="#F0F3F4", fg="#566573", selectbackground="#7FB3D5", selectforeground="white", height=10, width=50)
    cabins_listbox.grid(row=1, column=0, padx=10, pady=5, sticky="nw")

    # Продукты для закупа (правая колонка)
    tk.Label(content_frame, text="Продукты для закупа:", font=("Helvetica", 16), bg="#7FC3BD", fg="#fff").grid(row=0, column=1, padx=10, pady=5, sticky="nw")
    restock_listbox = tk.Listbox(content_frame, font=("Helvetica", 14), bg="#F0F3F4", fg="#566573", selectbackground="#7FB3D5", selectforeground="white", height=10, width=50)
    restock_listbox.grid(row=1, column=1, padx=10, pady=5, sticky="nw")
    # Интерфейс
    tk.Label(main_page, text="Заказы:", font=("Helvetica", 16)).pack(pady=5)
    sold_listbox = tk.Listbox(main_page, font=("Helvetica", 14), bg="#F0F3F4", fg="#566573", selectbackground="#7FB3D5", selectforeground="white", height=15, width=80)
    sold_listbox.pack()
    

    def update_restock_list():
        global restock_page
        """
        Функция для обновления списка продуктов для пополнения.
        """
        restock_listbox.delete(0, tk.END)  # Очищаем текущий список
        
        try:
            low_stock_products = fetch_low_stock_products()  # Получаем продукты для закупа
            start_index = (restock_page - 1) * page_size
            end_index = start_index + page_size
            paginated_products = low_stock_products[start_index:end_index]
            for product in paginated_products:
                restock_listbox.insert(
                    tk.END, f"{product['name']}, Количество: {product['quantity']}"
                )
        except Exception as e:
            restock_listbox.insert(tk.END, f"Ошибка загрузки: {e}")
        
        check_restock_buttons_state()

    # Функции для управления пагинацией "Продуктов для закупки"
    def next_restock_page():
        global restock_page
        restock_page += 1
        update_restock_list()

    def previous_restock_page():
        global restock_page
        if restock_page > 1:
            restock_page -= 1
            update_restock_list()

    def check_restock_buttons_state():
        global restock_page
        total_products = len(fetch_low_stock_products())
        if (restock_page * page_size) >= total_products:
            next_restock_button.config(state=tk.DISABLED)
        else:
            next_restock_button.config(state=tk.NORMAL)

        if restock_page == 1:
            prev_restock_button.config(state=tk.DISABLED)
        else:
            prev_restock_button.config(state=tk.NORMAL)


       # Пагинация для "Продуктов для закупки"
    prev_restock_button = ttk.Button(content_frame, text="<<", command=previous_restock_page)
    prev_restock_button.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    next_restock_button = ttk.Button(content_frame, text=">>", command=next_restock_page)
    next_restock_button.grid(row=2, column=1, padx=5, pady=5, sticky="e")

    update_restock_list()
    tk.Label(content_frame, text="").grid(row=2, column=1)

        # Пагинация для "Занятых кабин"
    prev_cabins_button = ttk.Button(content_frame, text="<<", command=previous_cabins_page)
    prev_cabins_button.grid(row=2, column=0, padx=5, pady=5, sticky="w")
    next_cabins_button = ttk.Button(content_frame, text=">>", command=next_cabins_page)
    next_cabins_button.grid(row=2, column=0, padx=5, pady=5, sticky="e")

    update_occupied_cabins()
    # Обновляем список продуктов для пополнения при загрузке страницы
    
    style = ttk.Style()
    style.configure("TButton", background="#7fc3bd", foreground="#ffffff", font=("Arial", 12))

    # Кнопки навигации
    pagination_frame = tk.Frame(main_page)
    pagination_frame.pack(pady=10)

    prev_button = ttk.Button(pagination_frame, text="Предыдущая страница", style="TButton", command=previous_page)
    prev_button.pack(side=tk.LEFT, padx=1)

    next_button = ttk.Button(pagination_frame, text="Следующая страница", command=next_page)
    next_button.pack(side=tk.LEFT, padx=1)

    

    frame_products = create_product_page(root)
    frame_gui = create_gui_page(root)
    frame_cabin = create_cabin_page(root)  # Создаем новую страницу кабин
    frame_expenses = create_expenses_page(root)
    frame_statistics = create_statistics_page(root)
    frame_booking = create_booking_page(root)
     # Применяем стили к страницам

     
    # Применяем стили ко всем страницам и их содержимому
    style_all_widgets(main_page, frame_bg="#e6f7ff", font_color="#004d99", button_bg="#bcbcbc", button_fg="#004d99")
    style_all_widgets(frame_booking, frame_bg="#e6f7ff", font_color="#004d99", button_bg="#bcbcbc", button_fg="#004d99")
    style_all_widgets(frame_products, frame_bg="#e6f7ff", font_color="#004d99", button_bg="#bcbcbc", button_fg="#004d99")
    style_all_widgets(frame_gui, frame_bg="#e6f7ff", font_color="#004d99", button_bg="#bcbcbc", button_fg="#004d99")
    style_all_widgets(frame_cabin, frame_bg="#e6f7ff", font_color="#004d99", button_bg="#bcbcbc", button_fg="#004d99")
    style_all_widgets(frame_statistics, frame_bg="#e6f7ff", font_color="#004d99", button_bg="#bcbcbc", button_fg="#004d99")
    style_all_widgets(frame_expenses, frame_bg="#e6f7ff", font_color="#004d99", button_bg="#bcbcbc", button_fg="#004d99")

    
    
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
