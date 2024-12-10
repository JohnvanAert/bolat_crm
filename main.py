import tkinter as tk
from tkinter import ttk
from product_page import create_product_page
from gui import create_gui_page
from cabin_page import create_cabin_page  # Импорт новой страницы для кабин
from expenses_page import create_expenses_page
from tkcalendar import Calendar
from database import fetch_all_bookings, confirm_booking_to_sale, update_booking_status, add_booking, get_cabin_price, check_booking_conflict  # Функции из базы данных
from tkinter import messagebox
from datetime import datetime
from tktimepicker import AnalogPicker, AnalogThemes, SpinTimePickerModern, constants
from decimal import Decimal

def create_navigation(root, show_main_page, show_products_page, show_gui_page, show_cabin_page, show_expenses_page):
    nav_frame = tk.Frame(root)
    nav_frame.pack(side=tk.TOP, fill=tk.X)
    
    tk.Button(nav_frame, text="Главная", command=show_main_page).pack(side=tk.LEFT)
    tk.Button(nav_frame, text="Склад продуктов", command=show_products_page).pack(side=tk.LEFT)
    tk.Button(nav_frame, text="Страница заказов", command=show_gui_page).pack(side=tk.LEFT)
    tk.Button(nav_frame, text="Кабинки", command=show_cabin_page).pack(side=tk.LEFT)  # Кнопка для кабин
    tk.Button(nav_frame, text="Расходы", command=show_expenses_page).pack(side=tk.LEFT)  # Кнопка для кабин

def create_main_page(root):
    frame_main = tk.Frame(root)

    # Заголовок
    tk.Label(frame_main, text="Управление бронированиями", font=("Arial", 16)).pack(pady=10)

    # Таблица бронирований
    columns = ("ID", "Имя клиента", "Телефон", "Кабинка", "Дата записи", "Начало брони", "Статус")
    bookings_table = ttk.Treeview(frame_main, columns=columns, show="headings", height=10)
    bookings_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    for col in columns:
        bookings_table.heading(col, text=col)
        bookings_table.column(col, width=150)

    def load_bookings():
        """Загрузка данных бронирований в таблицу."""
        bookings_table.delete(*bookings_table.get_children())
        bookings = fetch_all_bookings()
        # Добавление данных в таблицу
        for booking in bookings:
            # Убедимся, что данные передаются в правильном порядке
            row = (
                booking[0],  # ID
                booking[1],  # Имя клиента
                booking[2],  # Телефон
                booking[4],  # Кабинка (название)
                booking[5],  # Дата бронирования
                booking[6],  # Начало брони
                booking[9]   # Статус
            )
            bookings_table.insert("", tk.END, values=row)
    load_bookings()

    # Кнопки управления
    # Модальное окно для добавления бронирования
    def add_booking_modal():
        modal = tk.Toplevel(root)
        modal.title("Добавить бронирование")
        modal.geometry("600x400")

        tk.Label(modal, text="Имя клиента:").pack(pady=5)
        name_entry = tk.Entry(modal)
        name_entry.pack(pady=5)

        tk.Label(modal, text="Телефон клиента:").pack(pady=5)
        phone_entry = tk.Entry(modal)
        phone_entry.pack(pady=5)

        tk.Label(modal, text="ID кабинки:").pack(pady=5)
        cabin_entry = tk.Entry(modal)
        cabin_entry.pack(pady=5)

        # Выбор даты и времени начала бронирования
        tk.Label(modal, text="Дата и время начала бронирования:").pack(pady=5)
        start_datetime_var = tk.StringVar(value="")
        tk.Button(modal, text="Выбрать дату и время", command=lambda: open_calendar_with_time(start_datetime_var, "Выбор даты и времени начала")).pack(pady=5)
        tk.Label(modal, textvariable=start_datetime_var).pack(pady=5)

        # Выбор даты и времени окончания бронирования
        tk.Label(modal, text="Дата и время окончания бронирования:").pack(pady=5)
        end_datetime_var = tk.StringVar(value="")
        tk.Button(modal, text="Выбрать дату и время", command=lambda: open_calendar_with_time(end_datetime_var, "Выбор даты и времени окончания")).pack(pady=5)
        tk.Label(modal, textvariable=end_datetime_var).pack(pady=5)

        def save_booking():
            """Сохранение нового бронирования."""
            name = name_entry.get()
            phone = phone_entry.get()
            cabin_id = cabin_entry.get()
            start_datetime = start_datetime_var.get()
            end_datetime = end_datetime_var.get()

            if not name or not phone or not cabin_id or not start_datetime or not end_datetime:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return

            try:
                # Получение цены кабины
                cabin_price = get_cabin_price(cabin_id)
                if cabin_price is None:
                    messagebox.showerror("Ошибка", "Кабина с указанным ID не найдена!")
                    return

                # Рассчитать общее время бронирования (в часах)
                from datetime import datetime
                start = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M")
                end = datetime.strptime(end_datetime, "%Y-%m-%d %H:%M")
                duration_hours = (end - start).total_seconds() / 3600

                # Рассчитать общую стоимость
                total_price = cabin_price * Decimal(duration_hours)

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

        tk.Button(modal, text="Сохранить", command=save_booking).pack(pady=10)

    # Открытие календаря с выбором времени
    def open_calendar_with_time(datetime_var, title):
        calendar_window = tk.Toplevel(root)
        calendar_window.title(title)
        calendar_window.geometry("500x200")

        # Календарь для выбора даты
        calendar_frame = tk.Frame(calendar_window)
        calendar_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        calendar = Calendar(calendar_frame, selectmode="day", date_pattern="yyyy-MM-dd")
        calendar.pack(pady=10)

        # Виджеты для выбора времени
        time_frame = tk.Frame(calendar_window)
        time_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        tk.Label(time_frame, text="Выбор времени").pack(pady=5)
        time_picker = SpinTimePickerModern(time_frame)
        time_picker.addAll(constants.HOURS24)  # adds hours clock, minutes and period
        time_picker.configureAll(bg="#404040", height=2, fg="#ffffff", font=("Times", 16), hoverbg="#404040",
                                hovercolor="#d73333", clickedbg="#2e2d2d", clickedcolor="#d73333")
        time_picker.configure_separator(bg="#404040", fg="#ffffff")
        time_picker.addHours24()
        time_picker.pack(fill="both", expand=True)
        button_frame = tk.Frame(calendar_window)
        button_frame.pack(side=tk.BOTTOM, fill="x", pady=10)

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


        tk.Button(button_frame, text="Выбрать", command=set_datetime).pack()


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
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Добавить бронирование", command=add_booking_modal).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Подтвердить бронирование", command=confirm_booking).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Отменить бронирование", command=cancel_booking).pack(side=tk.LEFT, padx=5)

    return frame_main


def main():
    root = tk.Tk()
    root.title("CRM Navigation Panel")
    root.geometry("1024x768")  # Устанавливаем начальный размер окна
    root.minsize(800, 600)     # Устанавливаем минимальный размер окна
    root.maxsize(1920, 1080)   # Устанавливаем максимальный размер окна

    # Главная страница
    
    frame_main = create_main_page(root)
    
    def resize_handler(event):
        # Обработка изменения размера, если необходимо
        #print(f"New size: {event.width}x{event.height}")

        root.bind("<Configure>", resize_handler)


    def show_main_page():
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        frame_expenses.pack_forget()
        welcome_label.pack()
        frame_main.pack()
        root.update_idletasks()
    def show_products_page():
        welcome_label.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        frame_expenses.pack_forget()
        frame_products.pack()
        frame_main.pack_forget()
        root.update_idletasks()
    def show_gui_page():
        welcome_label.pack_forget()
        frame_products.pack_forget()
        frame_cabin.pack_forget()
        frame_expenses.pack_forget()
        frame_main.pack_forget()
        frame_gui.pack()
        root.update_idletasks()
    def show_cabin_page():
        welcome_label.pack_forget()
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_expenses.pack_forget()
        frame_main.pack_forget()
        frame_cabin.pack()
        root.update_idletasks()
    def show_expenses_page():
        welcome_label.pack_forget()
        frame_products.pack_forget()
        frame_gui.pack_forget()
        frame_cabin.pack_forget()
        frame_main.pack_forget()
        frame_expenses.pack()
        root.update_idletasks()

    welcome_label = tk.Label(root, text="Добро пожаловать на главную страницу!")
    welcome_label.pack()

    frame_products = create_product_page(root)
    frame_gui = create_gui_page(root)
    frame_cabin = create_cabin_page(root)  # Создаем новую страницу кабин
    frame_expenses = create_expenses_page(root)
    
    frame_products.pack_forget()
    frame_gui.pack_forget()
    frame_cabin.pack_forget()
    frame_expenses.pack_forget()

    create_navigation(root, show_main_page, show_products_page, show_gui_page, show_cabin_page, show_expenses_page)

    root.mainloop()

if __name__ == "__main__":
    main()
