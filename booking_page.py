import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from database import get_cabins, confirm_booking_to_sale, update_booking_status, add_booking, get_cabin_price, check_booking_conflict, fetch_filtered_bookings  # Функции из базы данных
from tkinter import messagebox
from datetime import datetime
from tktimepicker import AnalogPicker, AnalogThemes, SpinTimePickerModern, constants
from decimal import Decimal

def create_booking_page(root):
    frame_main = tk.Frame(root)
    # Заголовок
    tk.Label(frame_main, text="Управление бронированиями", font=("Arial", 16)).grid(row=0, column=0, columnspan=3, pady=10)


    # Панель фильтров
    filter_frame = tk.Frame(frame_main)
    filter_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

    tk.Label(filter_frame, text="Имя:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    name_filter = ttk.Entry(filter_frame)
    name_filter.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    # Фильтр по дате
    tk.Label(filter_frame, text="Дата:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
    selected_date = tk.StringVar()  # Переменная для хранения выбранной даты
    date_button = ttk.Button(filter_frame, text="Выбрать дату", command=lambda: open_calendar(selected_date, date_button))
    date_button.grid(row=0, column=3, padx=5, pady=5, sticky="w")


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

    tk.Label(filter_frame, text="Статус:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
    status_filter = ttk.Combobox(filter_frame, values=["Все", "Подтверждено", "Отменено", "Ожидание"])
    status_filter.set("Все")
    status_filter.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        # Создаем отображение ID -> имя кабинки
    cabins = get_cabins()  # Предполагается, что функция возвращает список кабинок из базы данных
    cabin_map = {cabin["name"]: cabin["id"] for cabin in cabins}  # Пример: {"Кабинка 1": 1, "Кабинка 2": 2}
    cabin_names = ["Все"] + list(cabin_map.keys())  # Список для выпадающего меню

    tk.Label(filter_frame, text="Кабинка:").grid(row=0, column=6, padx=5, pady=5, sticky="w")
    cabin_filter = ttk.Combobox(filter_frame, values=cabin_names)
    cabin_filter.set("Все")
    cabin_filter.grid(row=0, column=7, padx=5, pady=5, sticky="w")
    ttk.Button(filter_frame, text="Применить фильтры", command=lambda: load_bookings(1)).grid(row=0, column=8, padx=10, pady=5, sticky="w")
    ttk.Button(filter_frame, text="Очистить фильтры", command=lambda: clear_filters()).grid(row=0, column=9, padx=10, pady=5, sticky="w")

    def clear_filters():
        """Сбрасывает все фильтры в исходное состояние."""
        name_filter.delete(0, tk.END)  # Очищает поле имени
        selected_date.set("")  # Сбрасывает выбранную дату
        status_filter.set("Все")  # Сбрасывает статус на "Все"
        cabin_filter.set("Все")  # Сбрасывает кабинку на "Все"
        load_bookings(1)  # Перезагружает бронирования без фильтров

    # Таблица бронирований
    columns = ("ID", "Имя клиента", "Телефон", "Кабинка", "Добавлено", "Начало брони", "Конец брони", "Статус")
    bookings_table = ttk.Treeview(frame_main, columns=columns, show="headings", height=10)
    bookings_table.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

    for col in columns:
        bookings_table.heading(col, text=col)
        bookings_table.column(col, width=150)

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
    pagination_frame.grid(row=7, column=0, columnspan=3, pady=10)

    prev_button = ttk.Button(pagination_frame, text="<<", command=lambda: load_bookings(current_page - 1))
    prev_button.grid(row=0, column=0, padx=5)

    pagination_label = tk.Label(pagination_frame, text="Страница 1 из 1")
    pagination_label.grid(row=0, column=1, padx=5)

    next_button = ttk.Button(pagination_frame, text=">>", command=lambda: load_bookings(current_page + 1))
    next_button.grid(row=0, column=2, padx=5)

    
    load_bookings()
    
    
    # Кнопки управления
    # Модальное окно для добавления бронирования
    def add_booking_modal(selected_cabin=None):
        modal = tk.Toplevel(root)
        modal.title("Добавить бронирование")
        modal.geometry("600x400")
        modal.resizable(False, False)
        def validate_only_letters(event):
            """Разрешает вводить только буквы."""
            entry = event.widget
            value = entry.get()
            if not value.isalpha():
                entry.delete(0, tk.END)
                entry.insert(0, ''.join(filter(str.isalpha, value)))

        def validate_only_numbers(event):
            """Разрешает вводить только цифры."""
            entry = event.widget
            value = entry.get()
            if not value.isdigit():
                entry.delete(0, tk.END)
                entry.insert(0, ''.join(filter(str.isdigit, value)))


        tk.Label(modal, text="Имя клиента:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        name_entry = ttk.Entry(modal)
        name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        name_entry.bind("<KeyRelease>", validate_only_letters)

        tk.Label(modal, text="Телефон клиента:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        phone_entry = ttk.Entry(modal)
        phone_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        phone_entry.bind("<KeyRelease>", validate_only_numbers)

        tk.Label(modal, text="Кабинка:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
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

        # Выбор даты и времени начала бронирования
        tk.Label(modal, text="Дата и время начала бронирования:").grid(row=3, column=0, sticky="w", pady=5, padx=10)
        start_datetime_var = tk.StringVar(value="")
        tk.Button(modal, text="Выбрать дату и время", command=lambda: open_calendar_with_time(start_datetime_var, "Выбор даты и времени начала")).grid(row=3, column=1, pady=5, padx=5)
        tk.Label(modal, textvariable=start_datetime_var).grid(row=3, column=2, pady=5, padx=10)

        # Выбор даты и времени окончания бронирования
        tk.Label(modal, text="Дата и время окончания бронирования:").grid(row=4, column=0, sticky="w", pady=5, padx=5)
        end_datetime_var = tk.StringVar(value="")
        tk.Button(modal, text="Выбрать дату и время", command=lambda: open_calendar_with_time(end_datetime_var, "Выбор даты и времени окончания")).grid(row=4, column=1, pady=5, padx=10)
        tk.Label(modal, textvariable=end_datetime_var).grid(row=4, column=2, pady=5, padx=10)

        def save_booking():
            """Сохранение нового бронирования."""
            name = name_entry.get()
            phone = phone_entry.get()
            selected_cabin = cabin_combobox.get()
            start_datetime = start_datetime_var.get()
            end_datetime = end_datetime_var.get()

            if not name or not phone or not selected_cabin or not start_datetime or not end_datetime:
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

                # Проверка конфликта
                if check_booking_conflict(cabin_id, start_datetime, end_datetime):
                    tk.messagebox.showerror("Ошибка", "Выбранное время уже занято. Пожалуйста, выберите другое время.")
                    return

                # Вызов функции добавления бронирования
                booking_id = add_booking(name, phone, cabin_id, start, end, total_price)
                if booking_id:
                    print(f"Добавлено бронирование: {name}, {phone}, {cabin_id}, {start_datetime}, {end_datetime}, {total_price}")
                    messagebox.showinfo("Успех", "Бронирование добавлено!")
                    modal.destroy()
                    load_bookings()
                else:
                    messagebox.showerror("Ошибка", "Не удалось добавить бронирование!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить бронирование: {e}")

        tk.Button(modal, text="Сохранить", command=save_booking).grid(row=5, column=0, pady=10, padx=5)


    # Открытие календаря с выбором времени
    def open_calendar_with_time(datetime_var, title):
        calendar_window = tk.Toplevel(root)
        calendar_window.title(title)
        calendar_window.geometry("500x200")

        # Календарь для выбора даты
        calendar_frame = tk.Frame(calendar_window)
        calendar_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        calendar = Calendar(calendar_frame, selectmode="day", date_pattern="yyyy-MM-dd")
        calendar.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # Виджеты для выбора времени
        time_frame = tk.Frame(calendar_window)
        time_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        tk.Label(time_frame, text="Выбор времени").grid(row=0, column=0, pady=5, sticky="n")
        time_picker = SpinTimePickerModern(time_frame)
        time_picker.addAll(constants.HOURS24)  # adds hours clock, minutes and period
        time_picker.configureAll(bg="#404040", height=2, fg="#ffffff", font=("Times", 16), hoverbg="#404040",
                                hovercolor="#d73333", clickedbg="#2e2d2d", clickedcolor="#d73333")
        time_picker.configure_separator(bg="#404040", fg="#ffffff")
        time_picker.addHours24()
        time_picker.grid(row=1, column=0, padx=5, pady=10, sticky="n")

        button_frame = tk.Frame(calendar_window)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        def convert_am_pm_to_24h(time):
            """
            Конвертирует время из формата AM/PM в HH:mm (24-часовой формат).
            """
            try:
                # Разделяем строку времени
                if " " in time:
                    time, period = time.split(" ")
                else:
                    raise ValueError("Некорректный формат времени.")

                hours, minutes = map(int, time.split(":"))

                # Преобразуем в 24-часовой формат
                if period == "PM" and hours != 12:
                    hours += 12
                elif period == "AM" and hours == 12:
                    hours = 0

                return f"{hours:02}:{minutes:02}"
            except Exception as e:
                raise ValueError(f"Ошибка при обработке времени: {e}")

        def set_datetime():
            date = calendar.get_date()
            time_am_pm = time_picker.time()  # Получаем выбранное время из time_picker

            # Преобразуем кортеж в строку, если это необходимо
            if isinstance(time_am_pm, tuple):
                time_am_pm = f"{time_am_pm[0]}:{time_am_pm[1]} {time_am_pm[2]}"
            
            time_24h = convert_am_pm_to_24h(time_am_pm)  # Конвертируем в 24-часовой формат
            datetime_var.set(f"{date} {time_24h}")
            calendar_window.destroy()


        tk.Button(button_frame, text="Выбрать", command=set_datetime).grid(row=5, pady=5)


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
    button_frame.grid(row=9, column=0, pady=10, columnspan=2)
    ttk.Button(button_frame, text="Добавить бронирование", command=lambda:add_booking_modal()).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="Подтвердить бронирование", command=confirm_booking).grid(row=0, column=1, padx=5)
    ttk.Button(button_frame, text="Отменить бронирование", command=cancel_booking).grid(row=0, column=2, padx=5)

    cabins_frame = tk.Frame(frame_main)
    cabins_frame.grid(row=10, column=0, columnspan=2, pady=10)

    def create_cabin_buttons():
        """Создает квадратные кнопки для кабинок."""
        for widget in cabins_frame.winfo_children():
            widget.destroy()

        cabins = get_cabins()  # Получаем данные кабинок

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

    
    create_cabin_buttons()
    def refresh_booking_page():
        get_cabins()
        fetch_filtered_bookings()
        load_bookings()
        frame_main.after(200000, refresh_booking_page)

    return frame_main
