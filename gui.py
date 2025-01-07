import tkinter as tk
from tkcalendar import DateEntry
from tkinter import messagebox, ttk
from database import insert_sales_data, fetch_sales_data, update_sales_data, fetch_products, update_product_stock, insert_order_product, get_products_for_sale, delete_product_from_sale, update_product_quantity, delete_sales, get_cabin_info_from_sale, recalculate_cabin_price, get_products_data_for_sale, update_total_sales, update_sale_total_price, add_product_to_sale, get_all_products, is_cabin_busy, get_cabin_price, add_rental_extension, get_extensions_for_sale
from cabin_data import add_observer, get_cabins_data
import datetime
from decimal import Decimal, InvalidOperation
from tkcalendar import Calendar
from datetime import timedelta

def create_gui_page(root):
    frame = tk.Frame(root)

    selected_cabin_id = tk.StringVar()
    tk.Label(frame, text="Выберите кабинку").grid(row=0, column=0)
    cabins_combo = ttk.Combobox(frame, textvariable=selected_cabin_id, state="readonly")
    cabins_combo.grid(row=0, column=1)
    # Поля для поиска
    tk.Label(frame, text="Поиск по имени").grid(row=1, column=0)
    search_name_entry = tk.Entry(frame)
    search_name_entry.grid(row=1, column=1)

    tk.Label(frame, text="Поиск по номеру").grid(row=2, column=0)
    search_number_entry = tk.Entry(frame)
    search_number_entry.grid(row=2, column=1)

        # Поля для выбора диапазона дат (модальное окно вместо DateEntry)
    selected_start_date = tk.StringVar(value="Нажмите для выбора")
    selected_end_date = tk.StringVar(value="Нажмите для выбора")

    def open_calendar(entry_variable):
        def set_date():
            selected_date = calendar.get_date()
            entry_variable.set(selected_date)
            calendar_window.destroy()

        # Создаем модальное окно для выбора даты
        calendar_window = tk.Toplevel(root)
        calendar_window.title("Выбор даты")
        calendar_window.geometry("300x300")
        calendar_window.grab_set()  # Делаем окно модальным

        calendar = Calendar(calendar_window, selectmode="day", date_pattern="yyyy-mm-dd")
        calendar.pack(pady=20)

        tk.Button(calendar_window, text="Выбрать", command=set_date).pack(pady=10)

    tk.Label(frame, text="Дата с").grid(row=3, column=0)
    tk.Button(frame, textvariable=selected_start_date, command=lambda: open_calendar(selected_start_date)).grid(row=3, column=1)

    tk.Label(frame, text="Дата по").grid(row=4, column=0)
    tk.Button(frame, textvariable=selected_end_date, command=lambda: open_calendar(selected_end_date)).grid(row=4, column=1)


    tree = ttk.Treeview(frame, columns=("id", "name", "number", "cabins_count", "total_sales", "date"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("cabins_count", text="Выбранная кабинка")
    tree.heading("total_sales", text="Общая продажа")
    tree.heading("name", text="Имя")
    tree.heading("number", text="Номер")
    tree.heading("date", text="Дата и Время")
    tree.grid(row=7, column=0, columnspan=2)
    

    # Переменные для пагинации
    current_page = tk.IntVar(value=1)
    records_per_page = tk.IntVar(value=10)

    tk.Label(frame, text="Записей на странице:").grid(row=5, column=0)
    records_per_page_combobox = ttk.Combobox(frame, textvariable=records_per_page, state="readonly", values=[10, 25, 50, 100])
    records_per_page_combobox.grid(row=5, column=1)

    pagination_frame = tk.Frame(frame)
    pagination_frame.grid(row=11, column=0, columnspan=2)

    def update_cabins_combo():
        cabins_data = get_cabins_data()
        cabins_combo_values = [f"{cabin['name']} - {cabin['price']} $" for cabin in cabins_data]
        cabins_combo['values'] = cabins_combo_values

    update_cabins_combo()
    add_observer(update_cabins_combo)

    def display_sales_data():
        for item in tree.get_children():
            tree.delete(item)
        
        all_data = fetch_sales_data()

        # Получение выбранного имени кабинки для фильтрации
        selected_cabin = selected_cabin_id.get().split(" - ")[0] if selected_cabin_id.get() else None
        
        if selected_cabin:
            cabins_data = get_cabins_data()
            selected_cabin_id_value = next((cabin['id'] for cabin in cabins_data if cabin['name'] == selected_cabin), None)
            
            if selected_cabin_id_value is not None:
                # Фильтрация данных по ID кабинки
                all_data = [row for row in all_data if row[3] == selected_cabin_id_value]  # row[3] должен содержать ID кабинки
        
         # Фильтрация по диапазону дат
        # Фильтрация по диапазону дат
        try:
            start_date = datetime.datetime.strptime(selected_start_date.get(), "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(selected_end_date.get(), "%Y-%m-%d").date()

            if start_date and end_date:
                all_data = [row for row in all_data if start_date <= row[5].date() <= end_date]
        except ValueError:
            pass  # Если дата не выбрана или формат неверный, фильтрация не применяется



            # Фильтрация данных по имени и номеру
        search_name = search_name_entry.get().lower()
        search_number = search_number_entry.get()


        if search_name:
            all_data = [row for row in all_data if row[1] and search_name in row[1].lower()]

        if search_number:
            all_data = [row for row in all_data if row[2] and search_number in row[2]]

        
        total_pages = (len(all_data) - 1) // records_per_page.get() + 1

        if current_page.get() > total_pages:
            current_page.set(total_pages)
        elif current_page.get() < 1:
            current_page.set(1)

        start_index = (current_page.get() - 1) * records_per_page.get()
        end_index = start_index + records_per_page.get()
        paginated_data = all_data[start_index:end_index]

        for row in paginated_data:
            tree.insert("", tk.END, values=row)


        update_pagination_buttons(total_pages)
    # Кнопка для поиска
        tk.Button(frame, text="Поиск", command=display_sales_data).grid(row=5, column=0, columnspan=2)

        # Кнопка для очистки полей поиска и фильтров
        def clear_filters():
            search_name_entry.delete(0, tk.END)
            search_number_entry.delete(0, tk.END)
            selected_cabin_id.set("не выбрано")
            selected_start_date.set("Нажмите для выбора")
            selected_end_date.set("Нажмите для выбора")
            display_sales_data()

        tk.Button(frame, text="Очистить фильтр", command=clear_filters).grid(row=6, column=0, columnspan=2)

    

    def update_pagination_buttons(total_pages):
        for widget in pagination_frame.winfo_children():
            widget.destroy()
        
        max_buttons_to_display = 5
        current = current_page.get()
        
        start_page = max(1, current - max_buttons_to_display // 2)
        end_page = min(total_pages, start_page + max_buttons_to_display - 1)
        
        if start_page > 1:
            tk.Button(pagination_frame, text="<<", command=lambda: go_to_page(1)).grid(row=0, column=0)
            tk.Button(pagination_frame, text="<", command=lambda: go_to_page(current - 1)).grid(row=0, column=1)
        
        col = 2
        for page in range(start_page, end_page + 1):
            button = tk.Button(pagination_frame, text=str(page), command=lambda page=page: go_to_page(page))
            button.grid(row=0, column=col)
            if page == current:
                button.config(state="disabled")
            col += 1

        if end_page < total_pages:
            tk.Button(pagination_frame, text=">", command=lambda: go_to_page(current + 1)).grid(row=0, column=col)
            tk.Button(pagination_frame, text=">>", command=lambda: go_to_page(total_pages)).grid(row=0, column=col + 1)

    def go_to_page(page_number):
        current_page.set(page_number)
        display_sales_data()

    records_per_page_combobox.bind("<<ComboboxSelected>>", lambda event: display_sales_data())
    selected_cabin_id.trace("w", lambda *args: display_sales_data())  # Обработчик для обновления данных при выборе кабинки

    display_sales_data()

    def on_item_double_click(event):
        item = tree.selection()[0]
        selected_data = tree.item(item, "values")

        edit_window = tk.Toplevel(root)
        edit_window.geometry("1000x800")  # Увеличьте размер окна
        edit_window.title("Редактирование заказа")
        edit_window.grid_rowconfigure(4, weight=1)  # Для масштабирования таблицы
        edit_window.grid_columnconfigure(1, weight=1)

        tk.Label(edit_window, text="Имя").grid(row=0, column=0, padx=10, pady=10)
        edit_name_entry = tk.Entry(edit_window)
        edit_name_entry.grid(row=0, column=1, padx=10, pady=10)
        edit_name_entry.insert(0, selected_data[1])

        tk.Label(edit_window, text="Номер").grid(row=1, column=0, padx=10, pady=10)
        edit_number_entry = tk.Entry(edit_window)
        edit_number_entry.grid(row=1, column=1, padx=10, pady=10)
        edit_number_entry.insert(0, selected_data[2])

        tk.Label(edit_window, text="Выберите кабинку").grid(row=2, column=0, padx=10, pady=10)
        edit_cabins_combo = ttk.Combobox(edit_window, state="readonly")
        edit_cabins_combo.grid(row=2, column=1, padx=10, pady=10)
        edit_cabins_combo['values'] = cabins_combo['values']

        # Добавляем выпадающий список времени
        tk.Label(edit_window, text="Продолжительность аренды").grid(row=5, column=0, padx=10, pady=10)
        time_combo = ttk.Combobox(edit_window, state="readonly")
        time_combo.grid(row=5, column=1, padx=10, pady=10)
        time_combo['values'] = ["30 минут", "1 час", "1 час 30 минут", "2 часа"]
        def calculate_new_end_date(start_date, duration):
            if duration == "30 минут":
                return start_date + timedelta(minutes=30)
            elif duration == "1 час":
                return start_date + timedelta(hours=1)
            elif duration == "1 час 30 минут":
                return start_date + timedelta(minutes=90)
            elif duration == "2 часа":
                return start_date + timedelta(hours=2)
            return start_date
        
        # Установка текущей кабинки
        selected_cabin = selected_data[3]
        edit_cabins_combo.set(selected_cabin)

            # Раздел для отображения товаров
        tk.Label(edit_window, text="Список заказов").grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        products_frame = tk.Frame(edit_window)
        products_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Загрузка товаров из базы данных
        sale_id = selected_data[0]
        products_data = get_products_for_sale(sale_id)  # Получение товаров для текущей продажи

        products_tree = ttk.Treeview(products_frame, columns=("ID", "Название", "Количество", "Цена"), show="headings")
        products_tree.pack(fill="both", expand=True)


        # Настройка столбцов
        products_tree.heading("ID", text="ID")
        products_tree.heading("Название", text="Название")
        products_tree.heading("Количество", text="Количество")
        products_tree.heading("Цена", text="Цена")

        products_tree.column("ID", width=50)
        products_tree.column("Название", width=200)
        products_tree.column("Количество", width=100)
        products_tree.column("Цена", width=100)

        # Заполнение данными
        for product in products_data:
            products_tree.insert("", "end", values=(product['id'], product['name'], product['quantity'], product['price']))

            # Новый раздел для продлений времени
        tk.Label(edit_window, text="Продления времени").grid(row=6, column=0, columnspan=2, padx=10, pady=10)
        extensions_frame = tk.Frame(edit_window)
        extensions_frame.grid(row=7, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        extensions_tree = ttk.Treeview(extensions_frame, columns=("ID", "Минуты", "Время"), show="headings")
        extensions_tree.pack(fill="both", expand=True)

            # Настройка столбцов для продлений
        extensions_tree.heading("ID", text="ID")
        extensions_tree.heading("Минуты", text="Добавленные минуты")
        extensions_tree.heading("Время", text="Время продления")

        extensions_tree.column("ID", width=50)
        extensions_tree.column("Минуты", width=150)
        extensions_tree.column("Время", width=200)

        # Получение данных о продлениях из базы
        extensions_data = get_extensions_for_sale(sale_id)
        for extension in extensions_data:
            extensions_tree.insert("", "end", values=extension)

          # Функция для добавления продуктов
        def open_add_product_window():
            add_product_window(sale_id, products_tree)

        def add_product_window(sale_id, products_tree):
            """
            Модальное окно для добавления продуктов к продаже.
            """
            product_window = tk.Toplevel(root)
            product_window.title("Добавить продукты")

            tk.Label(product_window, text="Список доступных товаров").grid(row=0, column=0, columnspan=2)

            product_list = ttk.Treeview(product_window, columns=("ID", "Название", "Цена", "Количество"), show="headings")
            product_list.grid(row=1, column=0, columnspan=2)

            product_list.heading("ID", text="ID")
            product_list.heading("Название", text="Название")
            product_list.heading("Цена", text="Цена")
            product_list.heading("Количество", text="Количество")

            product_list.column("ID", width=50)
            product_list.column("Название", width=150)
            product_list.column("Цена", width=100)
            product_list.column("Количество", width=100)

            # Получаем все доступные продукты
            all_products = get_all_products()
            current_products = {p['id']: p['quantity'] for p in get_products_for_sale(sale_id)}

            for product in all_products:
                product_id, product_name, product_price, product_quantity = (
                    product['id'], product['name'], product['price'], product['quantity']
                )

                # Проверяем, есть ли продукт в текущей продаже
                if product_id in current_products:
                    # Если количество 0, делаем строку недоступной
                    if product_quantity == 0:
                        product_list.insert(
                            "",
                            "end",
                            values=(product_id, product_name, product_price, product_quantity),
                            tags=("disabled",)
                        )
                    else:
                        product_list.insert(
                            "",
                            "end",
                            values=(product_id, product_name, product_price, product_quantity),
                            tags=("existing",)
                        )
                else:
                    # Если количество 0, делаем строку недоступной
                    if product_quantity == 0:
                        product_list.insert(
                            "",
                            "end",
                            values=(product_id, product_name, product_price, product_quantity),
                            tags=("disabled",)
                        )
                    else:
                        product_list.insert(
                            "",
                            "end",
                            values=(product_id, product_name, product_price, product_quantity)
                        )

            # Настройка тегов для таблицы
            product_list.tag_configure("existing", background="green")
            product_list.tag_configure("disabled", background="lightgray", foreground="gray")

            def add_or_update_product():
                selected_item = product_list.selection()
                if not selected_item:
                    messagebox.showerror("Ошибка", "Выберите продукт!")
                    return

                selected_product = product_list.item(selected_item[0], "values")
                product_id = int(selected_product[0])
                product_price = float(selected_product[2])
                available_quantity = int(selected_product[3])

                if available_quantity <= 0:
                    messagebox.showerror("Ошибка", "Продукт недоступен для добавления!")
                    return

                if product_id in current_products:
                    new_quantity = current_products[product_id] + 1
                    if new_quantity > available_quantity:
                        messagebox.showerror("Ошибка", "Недостаточно доступного количества!")
                        return

                    update_product_quantity(sale_id, product_id, new_quantity)
                else:
                    add_product_to_sale(sale_id, product_id, 1, product_price)
                    current_products[product_id] = 1

                update_sale_total_price(sale_id, product_price)
                refresh_products_tree(products_tree, sale_id)
                refresh_product_list(product_list, sale_id)

            tk.Button(product_window, text="Добавить", command=add_or_update_product).grid(row=2, column=0, pady=10)
            tk.Button(product_window, text="Закрыть", command=product_window.destroy).grid(row=2, column=1, pady=10)



        def delete_product():
            """Удаляет выбранный товар из заказа."""
            selected_item = products_tree.selection()
            if not selected_item:
                messagebox.showerror("Ошибка", "Выберите товар для удаления!")
                return

            product_data = products_tree.item(selected_item[0], "values")
            product_id = product_data[0]  # ID товара
            cabin_id, cabin_price = get_cabin_info_from_sale(sale_id)  # Получаем ID кабинки и её стоимость

            if cabin_id is None:
                messagebox.showerror("Ошибка", "Не удалось получить данные о кабинке!")
                return

            response = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить товар?")
            if response:
                delete_product_from_sale(sale_id, product_id)  # Удаление товара из базы данных
                refresh_products_tree(products_tree, sale_id)  # Обновление списка товаров
                recalculate_total_price(sale_id, cabin_price)  # Пересчет общей цены заказа
                recalculate_cabin_price(cabin_id)  # Пересчет стоимости кабинки

        def decrease_quantity():
            """Уменьшает количество выбранного товара."""
            selected_item = products_tree.selection()
            if not selected_item:
                messagebox.showerror("Ошибка", "Выберите товар для уменьшения количества!")
                return

            product_data = products_tree.item(selected_item[0], "values")
            product_id, current_quantity = product_data[0], int(product_data[2])
            cabin_id, cabin_price = get_cabin_info_from_sale(sale_id)  # Получаем ID кабинки и её стоимость

            if cabin_id is None:
                messagebox.showerror("Ошибка", "Не удалось получить данные о кабинке!")
                return

            if current_quantity <= 1:
                delete_product()  # Удалить товар, если количество становится 0
            else:
                update_product_quantity(sale_id, product_id, current_quantity - 1)  # Уменьшение количества
                refresh_products_tree(products_tree, sale_id)  # Обновление списка товаров
                recalculate_total_price(sale_id, cabin_price)  # Пересчет общей цены заказа
                recalculate_cabin_price(cabin_id)  # Пересчет стоимости кабинки


        def refresh_products_tree(products_tree, sale_id=None):
            # Очистка текущих данных из таблицы
            for item in products_tree.get_children():
                products_tree.delete(item)

            # Получение актуальных данных из базы данных
            if sale_id:
                products_data = get_products_for_sale(sale_id)  # Используется из database.py
            else:
                products_data = fetch_products()  # Используется из database.py

            # Заполнение TreeView новыми данными
            for product in products_data:
                products_tree.insert(
                    "",
                    "end",
                    values=(product['id'], product['name'], product['quantity'], product['price'])
                )

        def refresh_product_list(product_list, sale_id):
            """
            Обновить список доступных продуктов в интерфейсе на основе текущих данных из БД.
            """
            # Получаем все продукты и текущие продукты для продажи
            all_products = get_all_products()
            current_products = {p['id']: p['quantity'] for p in get_products_for_sale(sale_id)}

            # Очищаем интерфейсный список
            for item in product_list.get_children():
                product_list.delete(item)

            # Перезаполняем список доступными продуктами
            for product in all_products:
                product_id, product_name, product_price, product_quantity = (
                    product['id'], product['name'], product['price'], product['quantity']
                )

                # Проверяем, есть ли продукт в текущей продаже
                if product_id in current_products:
                    if product_quantity == 0:
                        product_list.insert(
                            "",
                            "end",
                            values=(product_id, product_name, product_price, product_quantity),
                            tags=("disabled",)
                        )
                    else:
                        product_list.insert(
                            "",
                            "end",
                            values=(product_id, product_name, product_price, product_quantity),
                            tags=("existing",)
                        )
                else:
                    if product_quantity == 0:
                        product_list.insert(
                            "",
                            "end",
                            values=(product_id, product_name, product_price, product_quantity),
                            tags=("disabled",)
                        )
                    else:
                        product_list.insert(
                            "",
                            "end",
                            values=(product_id, product_name, product_price, product_quantity)
                        )

 
        def save_changes():
            new_name = edit_name_entry.get().strip()
            new_number = edit_number_entry.get().strip()

            # Проверяем, выбрано ли новое значение из комбобокса
            if edit_cabins_combo.get():
                # Извлекаем только название кабинки (до дефиса)
                new_cabin = edit_cabins_combo.get().split(' - ')[0].strip().lower()
            else:
                new_cabin = selected_cabin.strip().lower()  # Используем старое значение, если новое не выбрано

            print(f"Выбранная кабинка (после извлечения названия): {new_cabin}")  # Лог выбранной кабинки

            # Получаем данные о кабинках
            cabins_data = get_cabins_data()
            print(f"Данные о кабинках: {cabins_data}")  # Лог данных кабинок

            # Определяем новую кабинку и её цену
            selected_cabin_id = next((cabin['id'] for cabin in cabins_data if cabin['name'].strip().lower() == new_cabin), None)
            new_cabin_price = next((Decimal(cabin['price']) for cabin in cabins_data if cabin['name'].strip().lower() == new_cabin), None)

            selected_cabin_id = int(selected_data[3])  # ID текущей кабинки
            cabin_hourly_price = next((Decimal(cabin['price']) for cabin in cabins_data if cabin['id'] == selected_cabin_id), None)
            if not cabin_hourly_price:
                messagebox.showerror("Ошибка", "Не удалось получить цену кабинки!")
                return
            # Рассчитываем новую дату завершения
            duration = time_combo.get()
            # Рассчитываем продолжительность в часах
            duration_hours = {
                "30 минут": 0.5,
                "1 час": 1,
                "1 час 30 минут": 1.5,
                "2 часа": 2
            }.get(duration, 0)

            # Добавляем стоимость за дополнительное время к уже существующей цене
            cabin_total_price = Decimal(selected_data[6]) + (cabin_hourly_price * Decimal(duration_hours))

            # Логирование значений
            print(f"Продолжительность: {duration}, Часы: {duration_hours}, Сумма аренды: {cabin_total_price}")

            print(f"Новая кабинка ID: {selected_cabin_id}, Новая цена: {new_cabin_price}")  # Лог ID и цены новой кабинки

            # Если кабинка не найдена, используем прежние данные
            if selected_cabin_id is None or new_cabin_price is None:
                selected_cabin_id = selected_data[3]  # Прежний ID кабинки
                cabin_price = Decimal(selected_data[4])  # Прежняя цена кабинки
                print(f"Кабинка не найдена, используем прежние данные: ID={selected_cabin_id}, Цена={cabin_price}")
            else:
                cabin_price = new_cabin_price  # Новая цена кабинки

            try:
                 # Считаем старую дату завершения
                old_end_date = datetime.datetime.strptime(selected_data[5], '%Y-%m-%d %H:%M:%S')

                
                new_end_date = calculate_new_end_date(old_end_date, duration)

                # Вычисляем разницу во времени в минутах
                extension_minutes = int((new_end_date - old_end_date).total_seconds() / 60)
                add_rental_extension(
                    order_id=selected_data[0],  # ID заказа
                    extended_minutes=extension_minutes,  # Количество дополнительных минут
                )
            
            except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка при расчете новой даты: {e}")
                    return
            
                        # Логирование значений
            print(f"Старая дата завершения: {old_end_date}, Новая дата завершения: {new_end_date}, Дополнительное время: {extension_minutes} минут")

            # Проверка имени и номера на корректность
            if not new_name:
                messagebox.showerror("Ошибка", "Имя не может быть пустым!")
                return

            # Получаем данные о продуктах
            products_data = get_products_for_sale(selected_data[0])
            print(f"Данные о продуктах: {products_data}")  # Лог продуктов

            # Проверяем сумму продуктов
            total_products_price = sum(
                Decimal(product['price']) * Decimal(product['quantity']) for product in products_data
            ) if products_data else Decimal(0)

            print(f"Сумма продуктов: {total_products_price}")  # Лог суммы продуктов

            # Общая сумма = сумма продуктов + цена кабинки
            if new_cabin == selected_cabin.strip().lower():
                cabin_price = Decimal(selected_data[6])  # Используем старую цену кабинки
                print("Кабинка не изменилась, используем старую цену:", cabin_price)

            total_price = total_products_price + cabin_total_price
            print(f"Общая сумма: {total_price}")  # Лог общей суммы

            # Проверяем корректность значения общей суммы в selected_data
            try:
                previous_total_price = Decimal(selected_data[4])
                print(f"Старая общая сумма: {previous_total_price}")  # Лог старой суммы
            except (ValueError, TypeError, InvalidOperation):
                messagebox.showerror("Ошибка", "Некорректное значение общей суммы в данных! Попробуйте еще раз.")
                return

            # Сравниваем старую и новую суммы
            if total_price != previous_total_price:
                print(f"Сумма изменилась: {previous_total_price} → {total_price}")

            # Проверка имени и номера на корректность
            if not new_name:
                messagebox.showerror("Ошибка", "Имя не может быть пустым!")
                return

            if not new_number.isdigit():
                messagebox.showerror("Ошибка", "Номер должен быть числом!")
                return

            # Обновляем данные в базе
            print(f"Обновление данных: ID={selected_data[0]}, Имя={new_name}, Номер={new_number}, Кабинка ID={selected_cabin_id}, "
                f"Общая сумма={total_price}, Цена кабинки={cabin_price}")
            update_sales_data(selected_data[0], new_name, new_number, selected_cabin_id, total_price, cabin_total_price, extension_minutes)

            # Уведомление об успешном обновлении
            messagebox.showinfo("Успех", "Данные успешно обновлены!")

            # Обновить интерфейс
            display_sales_data()

            # Закрыть окно редактирования
            edit_window.destroy()


        def recalculate_total_price(sale_id, cabin_price):
            """
            Пересчитывает общую сумму продажи.
            Использует данные о товарах и стоимости кабинки.
            """
            try:
                # Получаем данные о продуктах через database.py
                products_data = get_products_data_for_sale(sale_id)
                
                # Считаем общую стоимость товаров
                total_products_price = sum(
                    Decimal(product['price']) * Decimal(product['quantity']) for product in products_data
                )
                
                # Если товаров нет, общая цена заказа должна быть 0
                total_price = total_products_price + cabin_price
                
                # Обновляем общую стоимость продажи через database.py
                update_total_sales(sale_id, total_price)
                
                print(f"Recalculated: Products total: {total_products_price}, Cabin price: {cabin_price}, Total: {total_price}")
                return total_products_price, total_price
            except Exception as e:
                print(f"Ошибка при пересчете общей стоимости: {e}")
                return None, None
  

        def delete_sale():
            response = messagebox.askyesno("Подтверждение удаления", "Вы уверены, что хотите удалить эту запись?")
            if response:
                delete_sales(selected_data[0])  # Call to delete the record from database
                messagebox.showinfo("Успех", "Запись успешно удалена!")
                display_sales_data()  # Refresh the data displayed in the table
                edit_window.destroy()
        
        # Создаем фрейм для кнопок
        button_frame = tk.Frame(edit_window)
        button_frame.grid(row=8, column=0, columnspan=2, pady=10)  # Используем grid для размещения фрейма
        
        # Добавляем кнопки в фрейм
        tk.Button(button_frame, text="Добавить продукты", command=open_add_product_window).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Удалить товар", command=delete_product, fg="red").grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Уменьшить количество", command=decrease_quantity).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Сохранить", command=save_changes, bg="green").grid(row=0, column=3, padx=5)
        tk.Button(button_frame, text="Удалить", command=delete_sale, fg="red").grid(row=0, column=4, padx=5)


            
            
    tree.bind("<Double-1>", on_item_double_click)


    display_sales_data()

    def open_add_modal():
        add_window = tk.Toplevel(root)
        add_window.title("Добавить запись")

        tk.Label(add_window, text="Имя").grid(row=0, column=0)
        entry_name = tk.Entry(add_window)
        entry_name.grid(row=0, column=1)

        tk.Label(add_window, text="Номер").grid(row=1, column=0)
        entry_number = tk.Entry(add_window)
        entry_number.grid(row=1, column=1)
        
        tk.Label(add_window, text="Выберите кабинку").grid(row=2, column=0)
        cabins_combo_modal = ttk.Combobox(add_window, state="readonly")
        cabins_combo_modal.grid(row=2, column=1)
        cabins_combo_modal['values'] = cabins_combo['values']

        tk.Label(add_window, text="Общая продажа").grid(row=3, column=0)
        entry_sales = tk.Entry(add_window, state='readonly')
        entry_sales.grid(row=3, column=1)

        # Поле для ввода времени аренды (в часах)
        tk.Label(add_window, text="На сколько часов?").grid(row=4, column=0)
        entry_hours = tk.Entry(add_window)
        entry_hours.grid(row=4, column=1)
        

         # Обновление цены аренды на основе введенного времени
        def update_rental_price(event=None):
            try:
                hours = float(entry_hours.get())
                selected_cabin = cabins_combo_modal.get().split(" - ")[0]
                cabins_data = get_cabins_data()
                cabin_price = Decimal(0)
                for cabin in cabins_data:
                    if cabin['name'] == selected_cabin:
                        cabin_price = Decimal(cabin['price'])
                        break

                # Минимальная стоимость за первый час и половина стоимости за каждые последующие 30 минут
                total_rental_price = cabin_price * int(hours)  # Полные часы
                if hours % 1 > 0:
                    total_rental_price += (cabin_price / 2)  # Половина стоимости за дополнительные 30 минут

                # Обновляем поле Общая продажа
                total_price = total_rental_price + Decimal(total_product_price)
                entry_sales.config(state='normal')
                entry_sales.delete(0, tk.END)
                entry_sales.insert(0, round(total_price, 2))
                entry_sales.config(state='readonly')

                global total_cabin_rental  # Use a global variable or other method to pass this value
                total_cabin_rental = float(total_rental_price)
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное количество часов.")

        # Привязка обновления стоимости к изменению часов
        entry_hours.bind("<KeyRelease>", update_rental_price)

        selected_products = {}
        total_product_price = 0

        selected_products_tree = ttk.Treeview(add_window, columns=("product_name", "price", "quantity"), show="headings")
        selected_products_tree.heading("product_name", text="Название")
        selected_products_tree.heading("price", text="Цена")
        selected_products_tree.heading("quantity", text="Количество")
        selected_products_tree.grid(row=6, column=0, columnspan=2)

        def open_product_list():
            nonlocal total_product_price

            product_window = tk.Toplevel(add_window)
            product_window.title("Выбор продуктов")

            product_tree = ttk.Treeview(product_window, columns=("product_id", "product_name", "price", "quantity"), show="headings")
            product_tree.heading("product_id", text="ID")
            product_tree.heading("product_name", text="Название")
            product_tree.heading("price", text="Цена")
            product_tree.heading("quantity", text="Количество")
            product_tree.pack(fill="both", expand=True)

            # Получение списка продуктов и отображение их в таблице
            products = fetch_products()
            for product in products:
             product_tree.insert("", tk.END, values=(product['id'], product['name'], product['price'], product['quantity']))

            def add_product_to_order():
                selected_item = product_tree.selection()
                if selected_item:
                    item_data = product_tree.item(selected_item)["values"]
                    if len(item_data) == 4:  # Проверка на наличие всех полей
                        product_id, product_name, price, stock = item_data
                        if product_id in selected_products:
                            if selected_products[product_id]['quantity'] < stock:
                                selected_products[product_id]['quantity'] += 1
                            else:
                                messagebox.showerror("Ошибка", "Достигнуто максимальное количество для этого товара.")
                                return
                        else:
                            if stock > 0:
                                selected_products[product_id] = {'name': product_name, 'price': price, 'quantity': 1, 'stock': stock}
                            else:
                                messagebox.showerror("Ошибка", "Недостаточно товара на складе.")
                                return
                        
                        # Обновление отображения выбранных продуктов
                        selected_products_tree.delete(*selected_products_tree.get_children())  # Очистка таблицы
                        for prod_id, prod_info in selected_products.items():
                            selected_products_tree.insert("", tk.END, values=(prod_info['name'], prod_info['price'], prod_info['quantity']))
                        
                        update_total_price()
                    else:
                        messagebox.showerror("Ошибка", "Некорректные данные продукта!")

            def remove_product_from_order():
                selected_item = product_tree.selection()
                if selected_item:
                    item_data = product_tree.item(selected_item)["values"]
                    product_id = item_data[0]
                    if product_id in selected_products and selected_products[product_id]['quantity'] > 0:
                        selected_products[product_id]['quantity'] -= 1
                        if selected_products[product_id]['quantity'] == 0:
                            del selected_products[product_id]
                        update_total_price()

                        # Обновление отображения выбранных продуктов
                        selected_products_tree.delete(*selected_products_tree.get_children())  # Очистка таблицы
                        for prod_id, prod_info in selected_products.items():
                            selected_products_tree.insert("", tk.END, values=(prod_info['name'], prod_info['price'], prod_info['quantity']))


            def update_total_price():
                nonlocal total_product_price

                # Пересчитываем сумму продуктов заново, чтобы избежать дублирования
                total_product_price = sum(float(product['price']) * product['quantity'] for product in selected_products.values())

                # Получаем текущую цену кабинки (введенную при выборе) и используем ее только один раз
                if cabins_combo_modal.get():
                    selected_cabin_price_str = cabins_combo_modal.get().split(" - ")[1].replace(" $", "")
                    selected_cabin_price = float(selected_cabin_price_str)
                else:
                    selected_cabin_price = 0

                # Итоговая сумма включает одну цену кабинки и общую стоимость продуктов
                total_price = selected_cabin_price + total_product_price

                # Обновляем поле ввода с общей продажей
                entry_sales.config(state='normal')
                entry_sales.delete(0, tk.END)
                entry_sales.insert(0, round(total_price, 2))  # Округляем для точности
                entry_sales.config(state='readonly')

            tk.Button(product_window, text="+ Добавить", command=add_product_to_order).pack(side="left")
            tk.Button(product_window, text="- Удалить", command=remove_product_from_order).pack(side="left")
            tk.Button(product_window, text="Закрыть", command=product_window.destroy).pack(side="right")

        tk.Button(add_window, text="Выбрать продукты", command=open_product_list).grid(row=9, columnspan=2)


        def update_sales_price(event):
            selected = cabins_combo_modal.get().split(" - ")[0]
            cabins_data = get_cabins_data()
            cabin_price = Decimal(0)
            for cabin in cabins_data:
                if cabin['name'] == selected:
                    cabin_price = Decimal(cabin['price'])
                    entry_sales.config(state='normal')
                    entry_sales.delete(0, tk.END)

                    # Устанавливаем только цену кабинки при выборе
                    entry_sales.insert(0, cabin_price)
                    entry_sales.config(state='readonly')
                    break

        cabins_combo_modal.bind("<<ComboboxSelected>>", update_sales_price)

        def submit_data():
            name = entry_name.get().strip()
            if not name:
                messagebox.showerror("Ошибка", "Поле 'Имя' обязательно к заполнению.")
                return
            try:
                name = entry_name.get()
                number = entry_number.get()
                selected_cabin = cabins_combo_modal.get().split(" - ")[0]
                cabins_data = get_cabins_data()
                selected_cabin_id = next((cabin['id'] for cabin in cabins_data if cabin['name'] == selected_cabin), None)

                hours = float(entry_hours.get())
                current_time = datetime.datetime.now()
                end_date = current_time + timedelta(hours=hours)

                # Проверяем занятость кабины
                if is_cabin_busy(selected_cabin_id, current_time):
                    messagebox.showerror("Ошибка", "Эта кабина уже занята в данный момент.")
                    return

                cabin_price = next((Decimal(cabin['price']) for cabin in cabins_data if cabin['name'] == selected_cabin), None)

                # Преобразуем total_product_price в Decimal
                total_product_price_decimal = Decimal(total_product_price)

                 # Получаем количество часов аренды
                hours = float(entry_hours.get())
                total_rental_price = cabin_price * int(hours)
                if hours % 1 > 0:
                    total_rental_price += (cabin_price / 2)

                # Общая сумма заказа
                total_price = total_rental_price + total_product_price_decimal

                # Вычисляем конечное время аренды
                start_date = datetime.datetime.now().replace(microsecond=0)
                end_date = start_date + timedelta(hours=hours)
                print(f"Products total: {total_product_price_decimal}, Cabin price: {cabin_price}, Total: {total_price}")
                # Сохраняем продажу и получаем ID
                sale_id = insert_sales_data(name, number, selected_cabin_id, total_price, start_date,  total_rental_price, end_date)
                
                # Сохраняем продукты, добавленные к заказу, в таблицу sales_products
                for product_id, product_info in selected_products.items():
                    insert_order_product(sale_id, product_id, product_info['quantity'], product_info['price'])

                # Обновление количества на складе
                for product_id, product_info in selected_products.items():
                    update_product_stock(product_id, product_info['quantity'])

                messagebox.showinfo("Успех", "Данные успешно добавлены!")
                display_sales_data()
                add_window.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

        tk.Button(add_window, text="Добавить", command=submit_data).grid(row=8, columnspan=2)

    tk.Button(frame, text="Добавить запись", command=open_add_modal).grid(row=8, columnspan=2)


    return frame
