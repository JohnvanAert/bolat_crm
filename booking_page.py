import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from database import get_cabins, confirm_booking_to_sale, update_booking_status, add_booking, get_cabin_price, check_booking_conflict, fetch_filtered_bookings, update_booking, delete_booking  # Функции из базы данных
from tkinter import messagebox
from tktimepicker import SpinTimePickerModern, constants
from decimal import Decimal
from cabin_data import add_observer, get_cabins_data
import datetime

def create_booking_page(root):
    frame_main = tk.Frame(root)
    # Заголовок
    tk.Label(frame_main, text="Управление бронированиями", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)


    # Панель фильтров
    filter_frame = tk.Frame(frame_main)
    filter_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

    tk.Label(filter_frame, text="Имя:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    name_filter = ttk.Entry(filter_frame)
    name_filter.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    # Фильтр по дате
    tk.Label(filter_frame, text="Дата:").grid(row=1, column=2, sticky="w")
    selected_date = tk.StringVar()  # Переменная для хранения выбранной даты
    date_button = ttk.Button(filter_frame, text="Выбрать дату", command=lambda: open_calendar(selected_date, date_button))
    date_button.grid(row=1, column=3, padx=5, pady=5, sticky="w")


    def open_calendar(date_var, date_button):
        """Открывает модальное окно с календарем для выбора даты."""
        def select_date():
            selected_date = calendar.get_date()
            date_var.set(selected_date)  # Устанавливаем выбранную дату в переменную
            date_button.config(text=f"Дата: {selected_date}")  # Обновляем текст кнопки
            calendar_window.destroy()

        calendar_window = tk.Toplevel()
        calendar_window.title("Выбрать дату")
        calendar = Calendar(calendar_window, selectmode="day", date_pattern="yyyy-mm-dd")
        calendar.pack(pady=10)

        tk.Button(calendar_window, text="Выбрать", command=select_date).pack(pady=5)

    tk.Label(filter_frame, text="Статус:").grid(row=1, column=4, padx=5, pady=5, sticky="w")
    status_filter = ttk.Combobox(filter_frame, values=["Все", "Подтверждено", "Отменено", "Ожидание"])
    status_filter.set("Все")
    status_filter.grid(row=1, column=5, padx=5, pady=5, sticky="w")

        # Создаем отображение ID -> имя кабинки
    cabins = get_cabins()  # Предполагается, что функция возвращает список кабинок из базы данных
    cabin_map = {cabin["name"]: cabin["id"] for cabin in cabins}  # Пример: {"Кабинка 1": 1, "Кабинка 2": 2}
    cabin_names = ["Все"] + list(cabin_map.keys())  # Список для выпадающего меню
    # Второй ряд фильтров

    tk.Label(filter_frame, text="Кабинка:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    cabin_filter = ttk.Combobox(filter_frame, values=cabin_names)
    cabin_filter.set("Все")
    cabin_filter.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    ttk.Button(filter_frame, text="Применить фильтры", command=lambda: load_bookings(1)).grid(row=2, column=2, padx=10, pady=5, sticky="w")
    ttk.Button(filter_frame, text="Очистить фильтры", command=lambda: clear_filters()).grid(row=2, column=3, padx=10, pady=5, sticky="w")

    def clear_filters():
        """Сбрасывает все фильтры в исходное состояние."""
        name_filter.delete(0, tk.END)  # Очищает поле имени
        selected_date.set("")  # Сбрасывает выбранную дату
        date_button.config(text="Выбрать дату")
        status_filter.set("Все")  # Сбрасывает статус на "Все"
        cabin_filter.set("Все")  # Сбрасывает кабинку на "Все"
        load_bookings(1)  # Перезагружает бронирования без фильтров

    # Таблица бронирований
    columns = ("ID", "Имя клиента", "Телефон", "Кабинка", "Добавлено", "Начало брони", "Конец брони", "Статус")
    bookings_table = ttk.Treeview(frame_main, columns=columns, show="headings", height=10)
    bookings_table.grid(row=7, column=0, columnspan=2, padx=10, pady=10)
    
    # Заголовки столбцов
    bookings_table.heading("ID", text="ID")
    bookings_table.heading("Имя клиента", text="Имя клиента")
    bookings_table.heading("Телефон", text="Телефон")
    bookings_table.heading("Кабинка", text="Кабина")
    bookings_table.heading("Добавлено", text="Добавлено")
    bookings_table.heading("Начало брони", text="Начало брони")
    bookings_table.heading("Конец брони", text="Конец брони")
    bookings_table.heading("Статус", text="Статус")
    # Обработчик двойного клика

    # Настройка ширины столбцов
    bookings_table.column("ID", width=40)
    bookings_table.column("Имя клиента", width=100)
    bookings_table.column("Телефон", width=120)
    bookings_table.column("Кабинка", width=60)
    bookings_table.column("Добавлено", width=150)
    bookings_table.column("Начало брони", width=150)
    bookings_table.column("Конец брони", width=150)
    bookings_table.column("Статус", width=120)

     # Параметры пагинации
    records_per_page = 10
    current_page = 1
    total_pages = 1

    def update_pagination_controls():
        """Обновление кнопок пагинации."""
        pagination_label.config(text=f"Страница {current_page} из {total_pages}")
        prev_button.config(state=tk.NORMAL if current_page > 1 else tk.DISABLED)
        next_button.config(state=tk.NORMAL if current_page < total_pages else tk.DISABLED)


    def load_bookings(page=1):
        """Загрузка данных бронирований с учетом фильтров и пагинации."""
        nonlocal current_page, total_pages
        current_page = page

        # Получение данных фильтров
        name = name_filter.get().strip()
        date = selected_date.get()
        status = status_filter.get().strip()
        cabin_name = cabin_filter.get().strip()
        # Получаем ID кабинки или None, если выбрано "Все"
        cabin_id = None if cabin_name == "Все" else cabin_map.get(cabin_name)

        # Запрос данных из базы
        bookings, total_count = fetch_filtered_bookings(name, date, status, cabin_id, records_per_page, current_page)
        bookings_table.delete(*bookings_table.get_children())
        # Добавление данных в таблицу
        for booking in bookings:
            # Убедимся, что данные передаются в правильном порядке
            row = (
                booking[0],  # ID
                booking[1],  # Имя клиента
                booking[2],  # Телефон
                booking[3],  # Кабинка (название)
                booking[4],  # Дата записи бронирования
                booking[5],  # Начало брони
                booking[6],  # Конец брони
                booking[8]   # Статус
            )
            bookings_table.insert("", tk.END, values=row)
            # Обновление параметров пагинации
        total_pages = (total_count + records_per_page - 1) // records_per_page
        update_pagination_controls()
    
         # Панель пагинации
    pagination_frame = tk.Frame(frame_main)
    pagination_frame.grid(row=8, column=0, columnspan=3, pady=10)

    prev_button = ttk.Button(pagination_frame, text="<<", command=lambda: load_bookings(current_page - 1))
    prev_button.grid(row=0, column=0, padx=5)

    pagination_label = tk.Label(pagination_frame, text="Страница 1 из 1")
    pagination_label.grid(row=0, column=1, padx=5)

    next_button = ttk.Button(pagination_frame, text=">>", command=lambda: load_bookings(current_page + 1))
    next_button.grid(row=0, column=2, padx=5)

    
    load_bookings()
    def on_booking_double_click(event):
        """Открытие модального окна для редактирования брони."""
        selected_item = bookings_table.selection()
        if not selected_item:
            return

        item = bookings_table.item(selected_item)
        booking_data = item["values"]

        # Создание модального окна
        edit_window = tk.Toplevel(root)
        edit_window.title("Редактировать бронь")
        edit_window.geometry("400x600")
        edit_window.transient(root)
        edit_window.grab_set()

        # Поля для редактирования
        # Поля для редактирования
        fields_map = {
            "Имя клиента": 1,   # booking_data[1]
            "Телефон": 2,       # booking_data[2]
            "Кабинка": 3,       # booking_data[3]
            "Начало брони": 5,  # booking_data[5]
            "Конец брони": 6,   # booking_data[6]
            "Статус": 7         # booking_data[7]
        }

        entries = {}

        for label, index in fields_map.items():
            tk.Label(edit_window, text=label).pack(pady=(10, 0))
            entry = ttk.Entry(edit_window, width=40)
            entry.pack(pady=5)
            entry.insert(0, booking_data[index])  
            entries[label] = entry

        def save_changes():
            """Сохранение изменений в базе данных."""
            updated_data = {
                "customer_name": entries["Имя клиента"].get().strip(),
                "customer_phone": entries["Телефон"].get().strip(),
                "cabin_name": entries["Кабинка"].get().strip(),
                "start_date": entries["Начало брони"].get().strip(),
                "end_date": entries["Конец брони"].get().strip(),
                "status": entries["Статус"].get().strip()
            }
            if not updated_data["cabin_name"]:
                raise ValueError("Название кабинки не может быть пустым.")

            # Вызов функции обновления в базе
            
            update_booking(booking_data[0], updated_data)
            load_bookings()  # Перезагрузка таблицы
            edit_window.destroy()

        def delete_booking_confirm():
            """Подтверждение удаления и удаление брони."""
            answer = messagebox.askyesno("Удалить бронь", "Вы уверены, что хотите удалить эту бронь?")
            if answer:
                delete_booking(booking_data[0])
                load_bookings()  # Перезагрузка таблицы
                edit_window.destroy()

        # Кнопки управления
        ttk.Button(edit_window, text="Сохранить", command=save_changes).pack(pady=10)
        ttk.Button(edit_window, text="Удалить", command=delete_booking_confirm).pack(pady=5)
        ttk.Button(edit_window, text="Отмена", command=edit_window.destroy).pack(pady=5)

        
    bookings_table.bind("<Double-1>", on_booking_double_click)
    
    # Кнопки управления
    # Модальное окно для добавления бронирования
    def add_booking_modal(selected_cabin=None):
        modal = tk.Toplevel(root)
        modal.title("Добавить бронирование")
        modal.geometry("600x300")
        modal.configure(bg="#e6f7ff")
        modal.resizable(False, False)
        def validate_only_letters(event):
            """Разрешает вводить только буквы и пробелы."""
            entry = event.widget
            value = entry.get()
            # Фильтруем строку: оставляем только буквы и пробелы
            filtered_value = ''.join(char for char in value if char.isalpha() or char.isspace())
            
            if value != filtered_value:
                entry.delete(0, tk.END)
                entry.insert(0, filtered_value)
                
        def validate_only_numbers(event):
            """Разрешает вводить только цифры."""
            entry = event.widget
            value = entry.get()
            if not value.isdigit():
                entry.delete(0, tk.END)
                entry.insert(0, ''.join(filter(str.isdigit, value)))

        style = ttk.Style()
        style.configure("Custom.TLabel", font=("Arial", 12), background="#e6f7ff", foreground="#333333")
        ttk.Label(modal, style="Custom.TLabel", text="Имя клиента:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        name_entry = ttk.Entry(modal)
        name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        name_entry.bind("<KeyRelease>", validate_only_letters)

        ttk.Label(modal, style="Custom.TLabel", text="Телефон клиента:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        phone_entry = ttk.Entry(modal)
        phone_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        phone_entry.bind("<KeyRelease>", validate_only_numbers)

        ttk.Label(modal, style="Custom.TLabel", text="Кабинка:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        cabins = get_cabins()  # Функция для получения списка кабинок из базы данных
        cabin_choices = [f"{cabin['id']} - {cabin['name']}" for cabin in cabins]
        cabin_combobox = ttk.Combobox(modal, values=cabin_choices)
        cabin_combobox.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        if selected_cabin:
            # Устанавливаем выбранную кабинку по ID и блокируем список
            for cabin in cabins:
                if cabin["id"] == selected_cabin:
                    cabin_combobox.set(f"{cabin['id']} - {cabin['name']}")
                    cabin_combobox.config(state="disabled")
                    break
        else:
            # Разблокируем список, если кабинка не выбрана
            cabin_combobox.config(state="readonly")

        def update_capacity(*args):
            """Обновляет поле 'Количество людей' в зависимости от выбранной кабинки."""
            selected_cabin = cabin_combobox.get().split(" - ")[0]  # Получаем ID выбранной кабины
            cabins_data = get_cabins_data()  

            # Находим вместимость кабинки
            capacity = next((cabin['capacity'] for cabin in cabins_data if str(cabin['id']) == selected_cabin), 1)
            
            # Обновляем поле
            num_people_entry.delete(0, tk.END)
            num_people_entry.insert(0, str(capacity))
        ttk.Label(modal, style="Custom.TLabel", text="Количество людей:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        num_people_entry = ttk.Entry(modal)
        num_people_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")
        cabin_combobox.bind("<<ComboboxSelected>>", update_capacity)
        update_capacity()

        # Выбор даты и времени начала бронирования
        ttk.Label(modal, style="Custom.TLabel", text="Дата и время начала бронирования:").grid(row=3, column=0, sticky="w", pady=5, padx=10)
        start_datetime_var = tk.StringVar(value="")
        tk.Button(modal, text="Выбрать дату и время", command=lambda: open_calendar_with_time(start_datetime_var, "Выбор даты и времени начала")).grid(row=3, column=1, pady=5, padx=5)
        ttk.Label(modal, style="Custom.TLabel", textvariable=start_datetime_var).grid(row=3, column=2, pady=5, padx=10)

        # Выбор даты и времени окончания бронирования
        ttk.Label(modal, style="Custom.TLabel", text="Дата и время окончания бронирования:").grid(row=4, column=0, sticky="w", pady=5, padx=5)
        end_datetime_var = tk.StringVar(value="")
        tk.Button(modal, text="Выбрать дату и время", command=lambda: open_calendar_with_time(end_datetime_var, "Выбор даты и времени окончания")).grid(row=4, column=1, pady=5, padx=10)
        ttk.Label(modal, style="Custom.TLabel", textvariable=end_datetime_var).grid(row=4, column=2, pady=5, padx=10)

        def save_booking():
            """Сохранение нового бронирования."""
            name = name_entry.get()
            phone = phone_entry.get()
            selected_cabin = cabin_combobox.get()
            start_datetime = start_datetime_var.get()
            end_datetime = end_datetime_var.get()
            num_people = num_people_entry.get()
            cabins_data = get_cabins_data()
            num_people = int(num_people)

            if not name or not phone or not selected_cabin or not start_datetime or not end_datetime or not num_people:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return

            try:
                # Преобразование строк в datetime
                cabin_id = selected_cabin.split(" - ")[0]

                from datetime import datetime
                start = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M")
                end = datetime.strptime(end_datetime, "%Y-%m-%d %H:%M")

                # Проверка на порядок времени
                if start >= end:
                    messagebox.showerror("Ошибка", "Время начала должно быть раньше времени окончания!")
                    return

                # Получение цены кабины
                cabin_price = get_cabin_price(cabin_id)
                cabin_capacity = next((Decimal(cabin['capacity']) for cabin in cabins_data if str(cabin['id']) == cabin_id), None)
                if cabin_price is None:
                    messagebox.showerror("Ошибка", "Кабина с указанным ID не найдена!")
                    return
                
                        # Расчет общего времени бронирования
                total_seconds = (end - start).total_seconds()
                full_hours = total_seconds // 3600  # Полные часы
                remaining_minutes = (total_seconds % 3600) // 60  # Оставшиеся минуты

                # Расчет стоимости
                total_price = cabin_price * Decimal(full_hours)  # Стоимость за полные часы
                if remaining_minutes > 0:  # Добавление стоимости за минуты
                    total_price += cabin_price * Decimal(remaining_minutes / 60)

                extra_people = max(0, num_people - cabin_capacity)
                extra_charge = extra_people * 1000  # 1000 за каждого дополнительного человека
                total_price += extra_charge

                # Проверка конфликта
                if check_booking_conflict(cabin_id, start_datetime, end_datetime):
                    tk.messagebox.showerror("Ошибка", "Выбранное время уже занято. Пожалуйста, выберите другое время.")
                    return

                # Вызов функции добавления бронирования
                booking_id = add_booking(name, phone, cabin_id, start, end, total_price, num_people, extra_charge)
                if booking_id:
                    print(f"Добавлено бронирование: {name}, {phone}, {cabin_id}, {start_datetime}, {end_datetime}, {total_price}")
                    messagebox.showinfo("Успех", "Бронирование добавлено!")
                    modal.destroy()
                    load_bookings()
                else:
                    messagebox.showerror("Ошибка", "Не удалось добавить бронирование!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить бронирование: {e}")

        ttk.Button(modal, text="Сохранить", command=save_booking).grid(row=6, column=0, pady=10, padx=5)


    # Открытие календаря с выбором времени
    def open_calendar_with_time(datetime_var, title):
        calendar_window = tk.Toplevel(root)
        calendar_window.title(title)
        calendar_window.geometry("500x400")
        calendar_window.configure(bg="#e6f7ff")

        # Календарь для выбора даты
        calendar_frame = ttk.Frame(calendar_window, style="Custom.TFrame")
        calendar_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")
        today = datetime.date.today()
        calendar = Calendar(calendar_frame, selectmode="day", date_pattern="yyyy-MM-dd", mindate=today)
        calendar.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # Виджеты для выбора времени
        time_frame = ttk.Frame(calendar_window, style="Custom.TFrame")
        time_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        ttk.Label(time_frame, style="Custom.TLabel", text="Выбор времени").grid(row=0, column=0, pady=5, sticky="n")
        time_picker = SpinTimePickerModern(time_frame)
        time_picker.addAll(constants.HOURS24)  # adds hours clock, minutes and period
        time_picker.configureAll(bg="#404040", height=2, fg="#ffffff", font=("Times", 16), hoverbg="#404040",
                                hovercolor="#d73333", clickedbg="#2e2d2d", clickedcolor="#d73333")
        time_picker.configure_separator(bg="#404040", fg="#ffffff")
        time_picker.addHours24()
        time_picker.grid(row=1, column=0, padx=5, pady=10, sticky="n")
        
        style = ttk.Style()
        style.configure("Custom.TFrame", background="#e6f7ff")
        button_frame = ttk.Frame(calendar_window, style="Custom.TFrame")
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
    
        def set_datetime():
            date = calendar.get_date()
            hours, minutes = time_picker.time()[:2]  # Берем только часы и минуты
            time_24h = f"{hours:02}:{minutes:02}"  # Форматируем в HH:mm

            print("Выбранное время (24-часовой формат):", time_24h)  # Отладка
            
            datetime_var.set(f"{date} {time_24h}")
            calendar_window.destroy()


        ttk.Button(button_frame, text="Выбрать", command=set_datetime).grid(row=5, pady=5)


    def confirm_booking():
        """Подтверждение бронирования."""
        selected_item = bookings_table.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите бронирование!")
            return

        booking_id = bookings_table.item(selected_item, "values")[0]
        try:
            sale_id = confirm_booking_to_sale(booking_id)
            messagebox.showinfo("Успех", f"Бронирование подтверждено! Продажа ID: {sale_id}")
            load_bookings()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подтвердить бронирование: {e}")

    def cancel_booking():
        """Отмена бронирования."""
        selected_item = bookings_table.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите бронирование!")
            return

        booking_id = bookings_table.item(selected_item, "values")[0]
        try:
            update_booking_status(booking_id, "Отменено")
            messagebox.showinfo("Успех", "Бронирование отменено.")
            load_bookings()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отменить бронирование: {e}")

    # Панель кнопок
    button_frame = tk.Frame(frame_main)
    button_frame.grid(row=10, column=0, pady=10, columnspan=2)

    ttk.Button(button_frame, text="Добавить бронирование", command=lambda:add_booking_modal()).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Подтвердить бронирование", command=confirm_booking).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Отменить бронирование", command=cancel_booking).grid(row=0, column=2, padx=5)

    cabins_frame = tk.Frame(frame_main)
    cabins_frame.grid(row=11, column=0, pady=10, columnspan=2)
    BUTTON_BG = "#76c7c0"  # Основной цвет фона кнопки
    BUTTON_FG = "white"    # Цвет текста
    BUTTON_ACTIVE_BG = "#5aa9a4"  # Цвет кнопки при нажатии

    def create_cabin_buttons():
        """Создает квадратные кнопки для кабинок."""
        for widget in cabins_frame.winfo_children():
            widget.destroy()

        cabins = get_cabins_data()  # Получаем данные кабинок

        for idx, cabin in enumerate(cabins):
            cabin_name = cabin.get("name", f"Кабинка {idx + 1}")

            # Создаем кнопку
            cabin_button = tk.Button(
                cabins_frame,
                text=cabin_name,
                width=10,
                height=5,
                relief=tk.GROOVE,
                bd=0.5,
                highlightbackground=BUTTON_BG,  # Обводка цвета
                highlightthickness=2,  # Толщина обводки
                command=lambda c=cabin: handle_cabin_click(c)  # Передаем кабинку в обработчик
            )

            # Расположение кнопок в сетке
            row, col = divmod(idx, 5)  # 5 кнопок в строке
            cabin_button.grid(row=row, column=col, padx=5, pady=5)
    
    def handle_cabin_click(cabin):
        """Обработчик нажатия на кнопку кабинки."""
        cabin_id = cabin.get("id")  # Получаем ID кабинки
        if cabin_id is not None:
            add_booking_modal(selected_cabin=cabin_id)
        else:
            tk.messagebox.showerror("Ошибка", "Некорректные данные кабинки!")

        # Обновление интерфейса при изменении данных в базе
    def on_cabin_data_update():
        """Функция вызывается при изменении данных кабинок в базе."""
        create_cabin_buttons()

    # Подписываемся на обновления данных кабинок
    add_observer(on_cabin_data_update)

    create_cabin_buttons()
    def refresh_booking_page():
        get_cabins()
        fetch_filtered_bookings()
        load_bookings()
        frame_main.after(200000, refresh_booking_page)

    return frame_main
