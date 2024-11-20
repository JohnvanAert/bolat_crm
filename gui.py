import tkinter as tk
from tkcalendar import DateEntry
from tkinter import messagebox, ttk
from database import insert_sales_data, fetch_sales_data, get_cabins, update_sales_data, remove_sales_data, fetch_products, update_product_stock, insert_order_product, get_products_for_sale, update_products_for_sale, get_product_price, get_products_data
from cabin_data import add_observer, get_cabins_data
import datetime
from decimal import Decimal

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

    # Поля для выбора диапазона дат
    tk.Label(frame, text="Дата с").grid(row=3, column=0)
    start_date_entry = DateEntry(frame, width=12, background='white', foreground='white', borderwidth=2)
    start_date_entry.grid(row=3, column=1)
    start_date_entry.focus_set()  # Устанавливаем фокус на поле выбора даты
    
    tk.Label(frame, text="Дата по").grid(row=4, column=0)
    end_date_entry = DateEntry(frame, width=12, background='darkblue', foreground='white', borderwidth=2)
    end_date_entry.grid(row=4, column=1)


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
        start_date = start_date_entry.get_date()
        end_date = end_date_entry.get_date()
        all_data = [row for row in all_data if start_date <= row[5].date() <= end_date]


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
            start_date_entry.set_date(datetime.date.today())
            end_date_entry.set_date(datetime.date.today())
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
        edit_window.title("Редактирование заказа")

        tk.Label(edit_window, text="Имя").grid(row=0, column=0)
        edit_name_entry = tk.Entry(edit_window)
        edit_name_entry.grid(row=0, column=1)
        edit_name_entry.insert(0, selected_data[1])

        tk.Label(edit_window, text="Номер").grid(row=1, column=0)
        edit_number_entry = tk.Entry(edit_window)
        edit_number_entry.grid(row=1, column=1)
        edit_number_entry.insert(0, selected_data[2])

        tk.Label(edit_window, text="Выберите кабинку").grid(row=2, column=0)
        edit_cabins_combo = ttk.Combobox(edit_window, state="readonly")
        edit_cabins_combo.grid(row=2, column=1)
        edit_cabins_combo['values'] = cabins_combo['values']
        
        # Установка текущей кабинки
        selected_cabin = selected_data[3]
        edit_cabins_combo.set(selected_cabin)

            # Раздел для отображения товаров
        tk.Label(edit_window, text="Список товаров").grid(row=3, column=0, columnspan=2)
        products_frame = tk.Frame(edit_window)
        products_frame.grid(row=4, column=0, columnspan=2, sticky="nsew")

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
        products_tree.column("Название", width=150)
        products_tree.column("Количество", width=100)
        products_tree.column("Цена", width=100)

        # Заполнение данными
        for product in products_data:
            products_tree.insert("", "end", values=(product['id'], product['name'], product['quantity'], product['price']))

        def save_changes():
            new_name = edit_name_entry.get()
            new_number = edit_number_entry.get()
            
            # Проверяем, выбрано ли новое значение из комбобокса
            if edit_cabins_combo.get():
                new_cabin = edit_cabins_combo.get().split(" - ")[0]
            else:
                new_cabin = selected_cabin  # Используем старое значение, если новое не выбрано

            # Проверяем, существует ли кабинка с таким именем и получаем ее ID и цену
            cabins_data = get_cabins_data()
            selected_cabin_id = next((cabin['id'] for cabin in cabins_data if cabin['name'] == new_cabin), None)
            cabin_price = next((cabin['price'] for cabin in cabins_data if cabin['name'] == new_cabin), None)

            # Если выбранная кабинка не найдена (например, при сохранении без изменений)
            if selected_cabin_id is None:
                selected_cabin_id = selected_data[3]  # Используем прежнее значение ID кабинки
                cabin_price = selected_data[4]        # Используем прежнее значение цены

            # Получаем текущую стоимость товаров
            products_data = get_products_for_sale(selected_data[0])
            total_products_price = sum(product['price'] * product['quantity'] for product in products_data)

            # Пересчитываем общий чек
            total_price = cabin_price + total_products_price

            # Обновить данные в базе данных
            update_sales_data(selected_data[0], new_name, new_number, selected_cabin_id, total_price)
            
            # Обновить данные в интерфейсе
            messagebox.showinfo("Успех", "Данные успешно обновлены!")
            display_sales_data()
            
            # Закрыть окно редактирования
            edit_window.destroy()


        def delete_sale():
            response = messagebox.askyesno("Подтверждение удаления", "Вы уверены, что хотите удалить эту запись?")
            if response:
                remove_sales_data(selected_data[0])  # Call to delete the record from database
                messagebox.showinfo("Успех", "Запись успешно удалена!")
                display_sales_data()  # Refresh the data displayed in the table
                edit_window.destroy()


        tk.Button(edit_window, text="Сохранить", command=save_changes).grid(row=6, columnspan=2)
        tk.Button(edit_window, text="Удалить", command=delete_sale, fg="red").grid(row=7, columnspan=2)

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

        tk.Button(add_window, text="Выбрать продукты", command=open_product_list).grid(row=4, columnspan=2)


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
                cabin_price = next((Decimal(cabin['price']) for cabin in cabins_data if cabin['name'] == selected_cabin), None)

                # Преобразуем total_product_price в Decimal
                total_product_price_decimal = Decimal(total_product_price)

                # Общая сумма заказа
                total_price = cabin_price + total_product_price_decimal

                # Сохраняем продажу и получаем ID
                sale_id = insert_sales_data(name, number, selected_cabin_id, total_price)
                
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
