import tkinter as tk
from tkinter import ttk, Label, Toplevel
from ttkbootstrap.constants import *
import ttkbootstrap as tb
from database import get_occupied_cabins, get_sold_products, fetch_low_stock_products, get_renter_details, fetch_product_details
from datetime import datetime
from PIL import Image, ImageTk
from ttkbootstrap.dialogs import Messagebox

class MainPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.page_size = 15
        self.occupied_cabins_page = 1
        self.restock_page = 1
        self.current_page = 1
        # Инициализация виджетов как атрибутов
        self.cabins_listbox = None
        self.restock_listbox = None
        self.sold_listbox = None
        self.prev_restock_button = None
        self.next_restock_button = None
        self.prev_cabins_button = None
        self.next_cabins_button = None
        self.prev_button = None
        self.next_button = None

        self.create_widgets()
        self.setup_auto_updates()

    def create_widgets(self):
        # Заголовок
        tk.Label(self, text="Добро пожаловать в BolatCRM!", font=("Arial", 20)).pack(pady=20)
        
        # Основной контейнер
        content_frame = tk.Frame(self, bg="#7FC3BD")
        content_frame.pack(fill="both", expand=True)

        # Создание Listbox'ов
        self.cabins_listbox = self.create_styled_listbox(content_frame, "Занятые кабины:", 0, 0)
        self.restock_listbox = self.create_styled_listbox(content_frame, "Продукты для закупа:", 0, 1)
        
        self.sold_listbox = self.create_styled_listbox(content_frame, "Заказы:", pack=True, width=80)
        # Пагинация
        self.create_pagination_controls(content_frame)


    def create_pagination_controls(self, content_frame):
        """Создает кнопки пагинации для всех разделов"""
        # Пагинация для "Продуктов для закупки"
        self.prev_restock_button = ttk.Button(
            content_frame, 
            text="<<", 
            command=self.previous_restock_page
        )
        self.next_restock_button = ttk.Button(
            content_frame, 
            text=">>", 
            command=self.next_restock_page
        )
        self.prev_restock_button.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.next_restock_button.grid(row=2, column=1, padx=5, pady=5, sticky="e")
        tk.Label(content_frame, text="").grid(row=2, column=1)

        # Пагинация для "Занятых кабин"
        self.prev_cabins_button = ttk.Button(
            content_frame, 
            text="<<", 
            command=self.previous_cabins_page
        )
        self.next_cabins_button = ttk.Button(
            content_frame, 
            text=">>", 
            command=self.next_cabins_page
        )
        self.prev_cabins_button.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.next_cabins_button.grid(row=2, column=0, padx=5, pady=5, sticky="e")

        # Кнопки навигации для заказов
        pagination_frame = tk.Frame(self)
        pagination_frame.pack(pady=10)
        self.prev_button = ttk.Button(
            pagination_frame, 
            text="<<", 
            style="TButton", 
            command=self.previous_page
        )
        self.next_button = ttk.Button(
            pagination_frame, 
            text=">>", 
            command=self.next_page
        )
        self.prev_button.pack(side=tk.LEFT, padx=1)
        self.next_button.pack(side=tk.LEFT, padx=1)

        # Первоначальное обновление данных
        self.update_restock_list()
        self.update_occupied_cabins()

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
    
    def update_occupied_cabins(self):
        self.cabins_listbox.delete(0, tk.END) # Очистка текущего списка
        occupied_cabins = get_occupied_cabins()  # Получение данных о занятых кабинах

        if occupied_cabins:
            start_idx = (self.occupied_cabins_page - 1) * self.page_size
            end_idx = start_idx + self.page_size
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
                    self.cabins_listbox.insert(tk.END, f"{cabin_name} - до начала аренды: {time_left}, людей: {people_count}")
                    self.cabins_listbox.bind('<Double-Button-1>', self.show_cabin_details)
                elif start_time <= now <= end_time:
                    # Во время аренды
                    remaining_time = end_time - now
                    hours, remainder = divmod(remaining_time.total_seconds(), 3600)
                    minutes = remainder // 60
                    time_left = f"{int(hours)} ч {int(minutes)} мин"
                    self.cabins_listbox.insert(tk.END, f"{cabin_name} - осталось: {time_left}, людей: {people_count}")
                    self.cabins_listbox.bind('<Double-Button-1>', self.show_cabin_details)
                else:
                    # Аренда завершена
                    self.cabins_listbox.insert(tk.END, f"{cabin_name} - аренда завершена")
        else:
            self.cabins_listbox.insert(tk.END, "Нет занятых кабин")

        # Запускаем функцию снова через 1 минуту (60 000 миллисекунд)
        self.cabins_listbox.after(20000, self.update_occupied_cabins)
        self.check_cabins_buttons_state()


    # Функции для управления пагинацией "Занятых кабин"
    def next_cabins_page(self):
        occupied_cabins_page += 1
        self.update_occupied_cabins()

    def previous_cabins_page(self):
        if occupied_cabins_page > 1:
            occupied_cabins_page -= 1
            self.update_occupied_cabins()

    def check_cabins_buttons_state(self):
        total_cabins = len(get_occupied_cabins())
        if (self.occupied_cabins_page * self.page_size) >= total_cabins:
            self.next_cabins_button.config(state=tk.DISABLED)
        else:
            self.next_cabins_button.config(state=tk.NORMAL)

        if self.occupied_cabins_page == 1:
            self.prev_cabins_button.config(state=tk.DISABLED)
        else:
            self.prev_cabins_button.config(state=tk.NORMAL)
    
    def show_cabin_details(event, self):
        selection = self.cabins_listbox.curselection()
        if not selection:
            return

        selected_index = selection[0]
        cabin_info = self.cabins_listbox.get(selected_index)

        # Извлекаем имя кабины из строки
        cabin_name = cabin_info.split(" - ")[0]

        # Получаем данные арендатора из базы данных
        renter_details = get_renter_details(cabin_name)

        if renter_details:
            # Создание модального окна с использованием ttkbootstrap
            details_window = tb.Toplevel()
            details_window.title(f"Арендаторы {cabin_name}")
            details_window.geometry("400x320")
            details_window.grab_set()  # Блокируем основное окно

            # Создаем рамку-карточку
            card_frame = tb.Frame(details_window, padding=15)
            card_frame.pack(padx=20, pady=20, fill="both", expand=True)

            # Заголовок карточки
            tb.Label(card_frame, text=f"Кабина: {cabin_name}",
                     font=("Helvetica", 16, "bold")).pack(pady=5)

            # Информация о клиенте
            tb.Label(card_frame, text=f"Имя клиента: {renter_details['name']}",
                     font=("Helvetica", 12)).pack(anchor="w", pady=2)

            tb.Label(card_frame, text=f"Номер: {renter_details['number']}",
                     font=("Helvetica", 12)).pack(anchor="w", pady=2)

            # Сумма заказа (выделена)
            tb.Label(card_frame, text=f"Сумма заказа: {renter_details['total_sales']} ₸",
                     font=("Helvetica", 14, "bold")).pack(pady=8)

            # Время аренды
            tb.Label(card_frame, text=f"Время начала: {renter_details['date']}",
                     font=("Helvetica", 12)).pack(anchor="w", pady=2)

            tb.Label(card_frame, text=f"Время окончания: {renter_details['end_date']}",
                     font=("Helvetica", 12)).pack(anchor="w", pady=2)
            
            tb.Label(card_frame, text=f"Способ Оплаты: {renter_details['payment_method']}",
                     font=("Helvetica", 12)).pack(anchor="w", pady=2)

            # Кнопка закрытия
            tb.Button(card_frame, text="Закрыть", bootstyle="danger", command=details_window.destroy).pack(pady=10)

        else:
            # Используем ttkbootstrap Messagebox
            Messagebox.show_info("Информация", "Информация о клиента не найдена.")
    def show_product_details(event, self):
        """
        Отображает модальное окно с информацией о выбранном продукте.
        """
        selected_item = self.restock_listbox.get(self.restock_listbox.curselection())  # Получаем выделенный товар
        product_name = selected_item.split(",")[0]  # Извлекаем имя товара

        product = fetch_product_details(product_name)  # Загружаем информацию о товаре

        if not product:
            return

        modal = Toplevel()
        modal.title("Информация о товаре")
        modal.geometry("400x400")

        Label(modal, text=f"Наименование: {product['name']}").pack(pady=5)
        Label(modal, text=f"Количество: {product['quantity']} шт.").pack(pady=5)
        Label(modal, text=f"Цена: {product['price']} тг").pack(pady=5)

        if product["image_path"]:
            try:
                image = Image.open(product["image_path"])  # Открываем изображение
                image = image.resize((200, 200))  # Изменяем размер
                img = ImageTk.PhotoImage(image)  # Преобразуем в формат Tkinter
                
                img_label = Label(modal, image=img)
                img_label.image = img
                img_label.pack(pady=10)
            except Exception as e:
                Label(modal, text="Ошибка загрузки изображения", font=("Arial", 10)).pack()

        ttk.Button(modal, text="Закрыть", command=modal.destroy).pack(pady=20)
    def update_sold_products(self):
        self.sold_listbox.delete(0, tk.END)  # Очистка текущего списка
        sold_products = get_sold_products(page=self.current_page, page_size=self.page_size)  # Получение данных о проданных товарах

        if sold_products:
            for product in sold_products:
                product_name = product["product_name"]
                cabin_name = product["cabin_name"]
                order_time = product["order_time"].strftime("%Y-%m-%d %H:%M:%S")
                quantity = product["quantity"]
                price = product["price"]

                self.sold_listbox.insert(
                    tk.END,
                    f"{order_time} | Кабина: {cabin_name} | Продукт: {product_name} | Кол-во: {quantity} шт. | Цена: {price} ₸"
                )
        else:
            self.sold_listbox.insert(tk.END, "Нет заказанных товаров")

        self.check_buttons_state()

    def auto_update_sold_products(self):
        self.update_sold_products()
        self.sold_listbox.after(60000, self.auto_update_sold_products)  # Обновление каждые 60 секунд

    # Функция для переключения на следующую страницу
    def next_page(self):
        current_page += 1
        self.update_sold_products()

    # Функция для переключения на предыдущую страницу
    def previous_page(self):
        if current_page > 1:
            current_page -= 1
            self.update_sold_products()

    # Проверка состояния кнопок
    def check_buttons_state(self):

        # Проверяем, есть ли данные на следующей странице
        next_page_data = get_sold_products(page=self.current_page + 1, page_size=self.page_size)
        if next_page_data:
            self.next_button.config(state=tk.NORMAL)
        else:
            self.next_button.config(state=tk.DISABLED)

        # Отключаем кнопку "Предыдущая страница", если текущая страница первая
        if self.current_page == 1:
            self.prev_button.config(state=tk.DISABLED)
        else:
            self.prev_button.config(state=tk.NORMAL)
    

    def update_restock_list(self):
        """
        Функция для обновления списка продуктов для пополнения.
        """
        self.restock_listbox.delete(0, tk.END)  # Очищаем текущий список
        
        try:
            low_stock_products = fetch_low_stock_products()  # Получаем продукты для закупа
            start_index = (self.restock_page - 1) * self.page_size
            end_index = start_index + self.page_size
            paginated_products = low_stock_products[start_index:end_index]
            for product in paginated_products:
                self.restock_listbox.insert(
                    tk.END, f"{product['name']}, Количество: {product['quantity']} шт."
                )
            self.restock_listbox.bind("<Double-Button-1>", self.show_product_details)
        except Exception as e:
            self.restock_listbox.insert(tk.END, f"Ошибка загрузки: {e}")
        
        self.check_restock_buttons_state()
    
    def auto_update_restock_list(self):
        self.update_restock_list()
        self.sold_listbox.after(60000, self.auto_update_restock_list)  # Обновление каждые 60 секунд

    # Функции для управления пагинацией "Продуктов для закупки"
    def next_restock_page(self):
        restock_page += 1
        self.update_restock_list()

    def previous_restock_page(self):
        if restock_page > 1:
            restock_page -= 1
            self.update_restock_list()

    def check_restock_buttons_state(self):
        total_products = len(fetch_low_stock_products())
        if (self.restock_page * self.page_size) >= total_products:
            self.next_restock_button.config(state=tk.DISABLED)
        else:
            self.next_restock_button.config(state=tk.NORMAL)

        if self.restock_page == 1:
            self.prev_restock_button.config(state=tk.DISABLED)
        else:
            self.prev_restock_button.config(state=tk.NORMAL)


       