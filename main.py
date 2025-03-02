import tkinter as tk
from tkinter import ttk, Label, Toplevel
from product_page import create_product_page
from gui import create_gui_page
from cabin_page import create_cabin_page  # Импорт новой страницы для кабин
from expenses_page import create_expenses_page
from statistic_page import create_statistics_page
from booking_page import create_booking_page
from database import get_occupied_cabins, get_sold_products, fetch_low_stock_products, get_renter_details, fetch_product_details
from datetime import datetime
from PIL import Image, ImageTk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import Meter
from ttkbootstrap.dialogs import Messagebox
import json
import os

CONFIG_FILE = "config.json"

def load_theme():
    """Загрузка темы из файла конфигурации."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
            return config.get("theme", "flatly")  # По умолчанию "flatly"
    return "flatly"

def save_theme(theme_name):
    """Сохранение выбранной темы в файл конфигурации."""
    with open(CONFIG_FILE, "w") as file:
        json.dump({"theme": theme_name}, file)

def open_settings(root):
    """Открывает окно настроек для выбора темы."""
    settings_window = tb.Toplevel(root)
    settings_window.title("Настройки")
    settings_window.geometry("300x200")
    settings_window.transient(root)
    settings_window.grab_set()

    tb.Label(settings_window, text="Выберите тему:", font=("Arial", 12)).pack(pady=10)
    
    theme_var = tb.StringVar(value=root.style.theme_use())  # Текущая тема
    themes = ["flatly", "superhero", "minty", "darkly", "cosmo"]
    
    theme_menu = tb.Combobox(settings_window, values=themes, textvariable=theme_var)
    theme_menu.pack(pady=5)
    
    def apply_theme():
        selected_theme = theme_var.get()
        root.style.theme_use(selected_theme)
        save_theme(selected_theme)
        settings_window.destroy()
    
    tb.Button(settings_window, text="Применить", command=apply_theme).pack(pady=10)

def create_navigation(root, show_main_page,show_booking_page, show_products_page, show_gui_page, show_cabin_page, show_expenses_page, show_statistics_page):
    nav_frame = tb.Frame(root)
    nav_frame.pack(side=tk.TOP, fill=tk.X)
    
    tb.Button(nav_frame, text="Главная", command=show_main_page).pack(side=tk.LEFT, padx=5)
    tb.Button(nav_frame, text="Бронирование", command=show_booking_page).pack(side=tk.LEFT,padx=5)
    tb.Button(nav_frame, text="Склад продуктов", command=show_products_page).pack(side=tk.LEFT, padx=5)
    tb.Button(nav_frame, text="Страница заказов", command=show_gui_page).pack(side=tk.LEFT, padx=5)
    tb.Button(nav_frame, text="Кабинки", command=show_cabin_page).pack(side=tk.LEFT, padx=5)  # Кнопка для кабин
    tb.Button(nav_frame, text="Расходы", command=show_expenses_page).pack(side=tk.LEFT, padx=5)  # Кнопка для кабин
    tb.Button(nav_frame, text="Статистика", command=show_statistics_page).pack(side=tk.LEFT, padx=5)  # Кнопка для кабин

current_page = 1
restock_page = 1
occupied_cabins_page = 1
page_size = 15  

def main():
    selected_theme = load_theme()
    root = tb.Window(themename=selected_theme)
    root.title("3B CRM")
    root.geometry("1450x800")  # Устанавливаем начальный размер окна
    root.minsize(800, 600)     # Устанавливаем минимальный размер окна
    root.maxsize(1920, 1080)   # Устанавливаем максимальный размер окна
    root.iconbitmap("icon.ico")
    # Создаем стиль
    def resize_handler(event):
        # Обработка изменения размера, если необходимо
        #print(f"New size: {event.width}x{event.height}")

        root.bind("<Configure>", resize_handler)
    
    
    

    def show_main_page():
        # left_panel.pack(side='left', fill='y')
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        frame_expenses.pack_forget()
        frame_statistics.pack_forget()
        main_page.pack()
        frame_booking.pack_forget()
        root.update_idletasks()

    def show_products_page():
        # left_panel.pack_forget()
        main_page.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        frame_expenses.pack_forget()
        frame_statistics.pack_forget()
        frame_products.pack()
        frame_booking.pack_forget()
        root.update_idletasks()

    def show_gui_page():
        # left_panel.pack_forget()
        main_page.pack_forget()
        frame_products.pack_forget()
        frame_cabin.pack_forget()
        frame_expenses.pack_forget()
        frame_statistics.pack_forget()
        frame_booking.pack_forget()
        frame_gui.pack()
        root.update_idletasks()

    def show_cabin_page():
        # left_panel.pack_forget()
        main_page.pack_forget()
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_expenses.pack_forget()
        frame_statistics.pack_forget()
        frame_booking.pack_forget()
        frame_cabin.pack()
        root.update_idletasks()

    def show_expenses_page():
        # left_panel.pack_forget()
        main_page.pack_forget()
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        frame_statistics.pack_forget()
        frame_booking.pack_forget()
        frame_expenses.pack()
        root.update_idletasks()

    def show_statistics_page():
        # left_panel.pack_forget()
        main_page.pack_forget()
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        frame_expenses.pack_forget()
        frame_booking.pack_forget()
        frame_statistics.pack()
        root.update_idletasks()

    def show_booking_page():
        # left_panel.pack_forget()
        main_page.pack_forget()
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        frame_expenses.pack_forget()
        frame_booking.pack()
        frame_statistics.pack_forget()
        root.update_idletasks()

    # Функция для создания стильно оформленного Listbox
    def create_styled_listbox(parent, title, row=None, column=None, pack=False, width=50):
        # Заголовок
        title_label = tk.Label(parent, text=title, font=("Helvetica", 16, "bold"), bg="#E8F6F3", fg="#2E4053")
        
        # Контейнер для Listbox с рамкой
        frame = tk.Frame(parent, bg="#D1E7E0", bd=2, relief="groove")
        
        # Стилизованный Listbox
        listbox = tk.Listbox(frame, font=("Helvetica", 14), bg="#F8F9F9", fg="#2C3E50",
                            selectbackground="#76D7C4", selectforeground="white",
                            height=10, width=width, relief="flat", highlightthickness=0, activestyle="none")
        
        listbox.pack(padx=5, pady=5, fill="both", expand=True)

        # Расположение элементов
        if pack:
            title_label.pack(padx=10, pady=(10, 5), anchor="w")
            frame.pack(padx=10, pady=5, fill="x")
        else:
            title_label.grid(row=row, column=column, padx=10, pady=(10, 5), sticky="nw")
            frame.grid(row=row+1, column=column, padx=10, pady=5, sticky="nw")

        return listbox
    
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
                people_count = cabin["people"]
                now = datetime.now()

                if now < start_time:
                    # До начала аренды
                    time_until_start = start_time - now
                    hours, remainder = divmod(time_until_start.total_seconds(), 3600)
                    minutes = remainder // 60
                    time_left = f"{int(hours)} ч {int(minutes)} мин"
                    cabins_listbox.insert(tk.END, f"{cabin_name} - до начала аренды: {time_left}, людей: {people_count}")
                    cabins_listbox.bind('<Double-Button-1>', show_cabin_details)
                elif start_time <= now <= end_time:
                    # Во время аренды
                    remaining_time = end_time - now
                    hours, remainder = divmod(remaining_time.total_seconds(), 3600)
                    minutes = remainder // 60
                    time_left = f"{int(hours)} ч {int(minutes)} мин"
                    cabins_listbox.insert(tk.END, f"{cabin_name} - осталось: {time_left}, людей: {people_count}")
                    cabins_listbox.bind('<Double-Button-1>', show_cabin_details)
                else:
                    # Аренда завершена
                    cabins_listbox.insert(tk.END, f"{cabin_name} - аренда завершена")
        else:
            cabins_listbox.insert(tk.END, "Нет занятых кабин")

        # Запускаем функцию снова через 1 минуту (60 000 миллисекунд)
        cabins_listbox.after(20000, update_occupied_cabins)
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
    
    def show_cabin_details(event):
        selection = cabins_listbox.curselection()
        if not selection:
            return

        selected_index = selection[0]
        cabin_info = cabins_listbox.get(selected_index)

        # Извлекаем имя кабины из строки
        cabin_name = cabin_info.split(" - ")[0]

        # Получаем данные арендатора из базы данных
        renter_details = get_renter_details(cabin_name)

        if renter_details:
            # Создание модального окна с использованием ttkbootstrap
            details_window = tb.Toplevel()
            details_window.title(f"Арендаторы {cabin_name}")
            details_window.geometry("400x350")
            details_window.configure(background=tb.Style().colors.bg)
            details_window.grab_set()  # Блокируем основное окно

            # Заголовок модального окна
            tb.Label(details_window, text=f"Кабина: {cabin_name}",
                    bootstyle="primary", font=("Helvetica", 16, "bold")).pack(pady=15)

            # Информация о клиенте
            tb.Label(details_window, text=f"Имя клиента: {renter_details['name']}",
                    bootstyle="info", font=("Helvetica", 12)).pack(pady=5)

            tb.Label(details_window, text=f"Номер: {renter_details['number']}",
                    bootstyle="info", font=("Helvetica", 12)).pack(pady=5)

            tb.Label(details_window, text=f"Сумма заказа: {renter_details['total_sales']} ₸",
                    bootstyle="success", font=("Helvetica", 12, "bold")).pack(pady=5)

            tb.Label(details_window, text=f"Время начала: {renter_details['date']}",
                    bootstyle="warning", font=("Helvetica", 12)).pack(pady=5)

            tb.Label(details_window, text=f"Время окончания: {renter_details['end_date']}",
                    bootstyle="warning", font=("Helvetica", 12)).pack(pady=5)

            # Кнопка закрытия
            tb.Button(details_window, text="Закрыть", bootstyle="danger", command=details_window.destroy).pack(pady=20)

        else:
            # Используем ttkbootstrap Messagebox
            Messagebox.show_info("Информация", "Информация о клиента не найдена.")

    def show_product_details(event):
        """
        Отображает модальное окно с информацией о выбранном продукте.
        """
        selected_item = restock_listbox.get(restock_listbox.curselection())  # Получаем выделенный товар
        product_name = selected_item.split(",")[0]  # Извлекаем имя товара

        product = fetch_product_details(product_name)  # Загружаем информацию о товаре

        if not product:
            return

        modal = Toplevel()
        modal.title("Информация о товаре")
        modal.configure(bg="#E6F7FF")
        modal.geometry("400x400")

        Label(modal, text=f"Наименование: {product['name']}", font=("Arial", 12), bg="#E6F7FF", fg="black").pack(pady=5)
        Label(modal, text=f"Количество: {product['quantity']} шт.", font=("Arial", 12), bg="#E6F7FF", fg="black").pack(pady=5)
        Label(modal, text=f"Цена: {product['price']} тг", font=("Arial", 12), bg="#E6F7FF", fg="black").pack(pady=5)

        if product["image_path"]:
            try:
                image = Image.open(product["image_path"])  # Открываем изображение
                image = image.resize((200, 200))  # Изменяем размер
                img = ImageTk.PhotoImage(image)  # Преобразуем в формат Tkinter
                
                img_label = Label(modal, image=img, bg="#E6F7FF")
                img_label.image = img
                img_label.pack(pady=10)
            except Exception as e:
                Label(modal, text="Ошибка загрузки изображения", font=("Arial", 10), bg="#E6F7FF", fg="red").pack()
                print(f"Ошибка загрузки изображения: {e}")

        ttk.Button(modal, text="Закрыть", command=modal.destroy).pack(pady=20)
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
                    f"{order_time} | Кабина: {cabin_name} | Продукт: {product_name} | Кол-во: {quantity} шт. | Цена: {price} тнг."
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


    # Кнопка "Настройки" в левом нижнем углу
    settings_button = tb.Button(root, text="Настройки", command=lambda: open_settings(root), bootstyle="primary")
    settings_button.place(x=10, y=700)
    
    # Левая панель с навигационными кнопками
    # left_panel = tk.Frame(root, bg="#cfe2f3", width=200)
    # left_panel.pack(side='left', fill='y')
    # left_panel.pack_propagate(0)  # Фиксируем ширину
    main_page.pack()
    # Кнопки навигации
    # nav_buttons = [
    #     ("Кабинки", show_main_page),
    #     ("Мужской зал", show_main_page),
    #     ("Женский зал", show_main_page),
    # ]

    # for text, command in nav_buttons:
    #     btn = ttk.Button(left_panel, text=text, command=command, style='TButton')
    #     btn.pack(pady=5, padx=10, fill='x')
    

    # Создаем рамку для содержимого
    content_frame = tk.Frame(main_page, bg="#7FC3BD")
    content_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    # Занятые кабины (левая колонка)
    cabins_listbox = create_styled_listbox(content_frame, "Занятые кабины:", row=0, column=0, width=50)

    # Продукты для закупа (правая колонка)
    restock_listbox = create_styled_listbox(content_frame, "Продукты для закупа:", row=0, column=1, width=50)

    # Интерфейс для отображения заказов
    orders_frame = tk.Frame(main_page, bg="#7FC3BD")
    orders_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    sold_listbox = create_styled_listbox(orders_frame, "Заказы:", pack=True, width=80)
    

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
                    tk.END, f"{product['name']}, Количество: {product['quantity']} шт."
                )
            restock_listbox.bind("<Double-Button-1>", show_product_details)
        except Exception as e:
            restock_listbox.insert(tk.END, f"Ошибка загрузки: {e}")
        
        check_restock_buttons_state()
    
    def auto_update_restock_list():
        update_restock_list()
        sold_listbox.after(60000, auto_update_restock_list)  # Обновление каждые 60 секунд

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
    
    # Кнопки навигации
    pagination_frame = tk.Frame(main_page)
    pagination_frame.pack(pady=10)

    prev_button = ttk.Button(pagination_frame, text="<<", style="TButton", command=previous_page)
    prev_button.pack(side=tk.LEFT, padx=1)

    next_button = ttk.Button(pagination_frame, text=">>", command=next_page)
    next_button.pack(side=tk.LEFT, padx=1)

    

    frame_products = create_product_page(root)
    frame_gui = create_gui_page(root)
    frame_cabin = create_cabin_page(root)  # Создаем новую страницу кабин
    frame_expenses = create_expenses_page(root)
    frame_statistics = create_statistics_page(root)
    frame_booking = create_booking_page(root)
     # Применяем стили к страницам

     
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
