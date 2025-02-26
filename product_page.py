import tkinter as tk
from tkinter import messagebox, filedialog, Toplevel, ttk
from PIL import Image, ImageTk
from database import insert_product, fetch_products, update_product, delete_product, insert_expense, is_product_in_sales
from datetime import datetime
import os
import shutil

def create_product_page(root):
    frame = tk.Frame(root)
    tk.Label(frame, text="Склад продуктов", font=("Arial", 16)).grid(row=0, column=0, columnspan=3, pady=10)
    items_per_page_var = tk.IntVar(value=10)
    current_page_var = tk.IntVar(value=1)

    pagination_frame = tk.Frame(frame)
    pagination_frame.grid(row=3, column=0, columnspan=3)
    
    def open_add_product_modal():
        modal = Toplevel(root)
        modal.title("Добавление продукта")
        modal.geometry("500x600")
        modal.grid_columnconfigure(1, weight=1)
        modal.grab_set()
        IMAGE_DIR = 'images'
        if not os.path.exists(IMAGE_DIR):
            os.makedirs(IMAGE_DIR)
        style = ttk.Style()
        style.configure("Custom.TLabel", font=("Arial", 12), background="#e6f7ff", foreground="#333333")
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


        ttk.Label(modal, text="Название продукта").grid(row=0, column=0)
        entry_name = ttk.Entry(modal)
        entry_name.grid(row=0, column=1, pady="5")
        entry_name.bind("<KeyRelease>", validate_only_letters)

        ttk.Label(modal, text="Цена").grid(row=1, column=0)
        entry_price = ttk.Entry(modal)
        entry_price.grid(row=1, column=1, pady="5")
        entry_price.bind("<KeyRelease>", validate_only_numbers)

        ttk.Label(modal, text="Количество").grid(row=2, column=0)
        entry_quantity = ttk.Entry(modal)
        entry_quantity.grid(row=2, column=1, pady="5")
        entry_quantity.bind("<KeyRelease>", validate_only_numbers)


        ttk.Label(modal, text="Изображение").grid(row=3, column=0)
        img_path_var = tk.StringVar()
        # Frame to hold the image preview and the close button
        img_frame = tk.Frame(modal, bg="#e6f7ff")
        img_frame.grid(row=3, column=1, sticky="w")

        img_preview_label = tk.Label(img_frame, text="Нет изображения")
        img_preview_label.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")
        

            # Checkbox for expense
        is_expense = tk.BooleanVar()
        expense_checkbox = tk.Checkbutton(modal, text="Добавить как расход", variable=is_expense, command=lambda: toggle_expense_field())
        expense_checkbox.grid(row=7, column=0, columnspan=2, pady="5")

        # Expense amount entry (initially disabled)
        ttk.Label(modal, text="Сумма расхода").grid(row=5, column=0)
        entry_expense_amount = ttk.Entry(modal, state="disabled")
        entry_expense_amount.grid(row=5, column=1, pady="5")
        entry_expense_amount.bind("<KeyRelease>", validate_only_numbers)

        def remove_image():
            img_preview_label.config(image="", text="Нет изображения")
            img_preview_label.image = None
            img_path_var.set("")
            close_button.place_forget()

        # Кнопка удаления тоже внутри img_frame
        close_button = ttk.Button(img_frame, text="✖", command=lambda: remove_image(), width=2)
        close_button.place(relx=0, rely=0, anchor="nw")  # Размещаем в правом верхнем углу
        close_button.place_forget()

        def compress_image(input_path, output_path, quality=85, size_limit_kb=500, min_resolution=(800, 800)):
            """Сжимает изображение, если размер превышает лимит или разрешение больше минимального."""
            file_size_kb = os.path.getsize(input_path) / 1024  # Размер файла в КБ

            with Image.open(input_path) as img:
                width, height = img.size

                # Проверка: нужно ли сжимать?
                needs_compression = file_size_kb > size_limit_kb or width > min_resolution[0] or height > min_resolution[1]

                if needs_compression:
                    img = img.convert("RGB")
                    img.save(output_path, "JPEG", optimize=True, quality=quality)
                else:
                    # Если изображение уже оптимизировано, просто копируем
                    shutil.copy(input_path, output_path)

        def select_image():
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
            if file_path:
                file_name = os.path.basename(file_path)
                new_file_path = os.path.join(IMAGE_DIR, file_name)

                if not os.path.exists(new_file_path):
                    compress_image(file_path, new_file_path, quality=85, size_limit_kb=500, min_resolution=(800, 800))

                img_path_var.set(new_file_path)
                load_image_preview(new_file_path)

        def load_image_preview(file_path):
            try:
                img = Image.open(file_path)
                width, height = img.size
                max_size = (300, 200)
                ratio = min(max_size[0]/width, max_size[1]/height)
                new_size = (int(width * ratio), int(height * ratio))
                img = img.resize(new_size, Image.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                img_preview_label.configure(image=img_tk, text="")
                img_preview_label.image = img_tk
                close_button.place(relx=0, rely=0, anchor="nw")
            except (FileNotFoundError, IOError):
                messagebox.showerror("Ошибка", "Не удалось загрузить изображение.")

        select_img_button = ttk.Button(modal, text="Выбрать изображение", command=select_image)
        select_img_button.grid(row=4, column=0, columnspan=2)

            # Toggle expense field based on checkbox
        def toggle_expense_field():
            if is_expense.get():
                entry_expense_amount.config(state="normal")
            else:
                entry_expense_amount.delete(0, tk.END)
                entry_expense_amount.config(state="disabled")

        def add_product():
            name = entry_name.get()
            try:
                price = float(entry_price.get())
                quantity = int(entry_quantity.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Цена и количество должны быть числами.")
                return

            image_path = img_path_var.get()

            if not (name and price >= 0 and quantity >= 0 and image_path):
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля правильно.")
                return

            insert_product(name, price, quantity, image_path)

             # If expense checkbox is checked, add to expenses table
            if is_expense.get():
                try:
                    expense_amount = float(entry_expense_amount.get())
                except ValueError:
                    messagebox.showerror("Ошибка", "Сумма расхода должна быть числом.")
                    return
                expense_name = f"Закуп {name}"
                expense_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                insert_expense(expense_name, expense_amount, expense_date)

            messagebox.showinfo("Успех", "Продукт добавлен!")
            modal.destroy()
            display_products()

        ttk.Button(modal, text="Добавить продукт", command=add_product).grid(row=9, columnspan=2, pady=10)
        


    add_product_button = ttk.Button(frame, text="Добавить продукт", command=open_add_product_modal)
    add_product_button.grid(row=1, column=0, pady=10)

    tk.Label(frame, text="Записей на странице:").grid(row=1, column=1)
    items_per_page_dropdown = ttk.Combobox(
        frame,
        textvariable=items_per_page_var,
        values=[10, 25, 50, 100],
        state="readonly"
    )
    items_per_page_dropdown.grid(row=1, column=2)
    items_per_page_dropdown.bind("<<ComboboxSelected>>", lambda e: [current_page_var.set(1), display_products()])

    product_container = tk.Frame(frame)
    product_container.grid(row=2, column=0, columnspan=3, pady=10)

    def display_products():
        # Очистка контейнера продуктов
        for widget in product_container.winfo_children():
            widget.destroy()

        # Получение и отображение продуктов
        products = fetch_products()
        items_per_page = items_per_page_var.get()
        current_page = current_page_var.get()
        start_index = (current_page - 1) * items_per_page
        end_index = start_index + items_per_page

        total_products = len(products)
        total_pages = (total_products + items_per_page - 1) // items_per_page

        current_row = 0
        current_col = 0
        max_cols = 5

        for product in products[start_index:end_index]:
            create_product_card(product, current_row, current_col)
            current_col += 1
            if current_col >= max_cols:
                current_col = 0
                current_row += 1

        # Очистка старых кнопок пагинации
        for widget in pagination_frame.winfo_children():
            widget.destroy()

        # Количество отображаемых кнопок страниц
        max_buttons_to_display = 5
        start_page = max(1, current_page - max_buttons_to_display // 2)
        end_page = min(total_pages, start_page + max_buttons_to_display - 1)

        # Кнопка для перехода на первую страницу
        if start_page > 1:
            first_button = ttk.Button(pagination_frame, text="<<", command=lambda: [current_page_var.set(1), display_products()])
            first_button.pack(side="left")
            prev_button = ttk.Button(pagination_frame, text="<", command=lambda: [current_page_var.set(current_page - 1), display_products()])
            prev_button.pack(side="left")

        # Кнопки для страниц в пределах видимого диапазона
        for page_num in range(start_page, end_page + 1):
            state = "disabled" if page_num == current_page else "normal"
            page_button = ttk.Button(pagination_frame, text=str(page_num), state=state, command=lambda p=page_num: [current_page_var.set(p), display_products()])
            page_button.pack(side="left")

        # Кнопки для перехода на следующую и последнюю страницы
        if end_page < total_pages:
            next_button = ttk.Button(pagination_frame, text=">", command=lambda: [current_page_var.set(current_page + 1), display_products()])
            next_button.pack(side="left")
            last_button = ttk.Button(pagination_frame, text=">>", command=lambda: [current_page_var.set(total_pages), display_products()])
            last_button.pack(side="left")

    def create_product_card(product, row, col):
        card = ttk.Frame(product_container, borderwidth=2, relief="groove")
        
        def handle_click(event):
            open_edit_modal(product)

        try:
            img = Image.open(product["image_path"])
            img = img.resize((150, 100), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            img_label = ttk.Label(card, image=img_tk)
            img_label.image = img_tk
            img_label.pack()
            img_label.bind("<Button-1>", handle_click)  # Привязка события к изображению
        except (FileNotFoundError, IOError):
            img_label = ttk.Label(card, text="No Image", width=10, height=5)
            img_label.pack()
            img_label.bind("<Button-1>", handle_click)  # Привязка события к метке с текстом

        name_label = ttk.Label(card, text=f"Название: {product['name']}")
        name_label.pack()
        name_label.bind("<Button-1>", handle_click)  # Привязка события к метке с названием

        price_label = ttk.Label(card, text=f"Цена: {product['price']}")
        price_label.pack()
        price_label.bind("<Button-1>", handle_click)  # Привязка события к метке с ценой

        quantity_label = ttk.Label(card, text=f"Количество: {product['quantity']}")
        quantity_label.pack()
        quantity_label.bind("<Button-1>", handle_click)  # Привязка события к метке с количеством

        card.bind("<Button-1>", handle_click)  # Привязка события к карточке
        card.grid(row=row, column=col, padx=10, pady=10)

    def open_edit_modal(product):
        modal = Toplevel(root)
        modal.title("Редактирование продукта")
        modal.geometry("400x550")
        modal.configure(bg="#e0f7fa")
        modal.grab_set()
        style = ttk.Style()
        style.configure("Custom.TLabel", font=("Arial", 12), background="#e6f7ff", foreground="#333333")
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

        # Добавляем переменные для расхода
        expense_amount_var = tk.StringVar()
        is_expense = tk.BooleanVar()

        def toggle_expense_field():
            """Активирует/деактивирует поле ввода расхода"""
            if is_expense.get():
                entry_expense_amount.config(state="normal")
            else:
                entry_expense_amount.config(state="disabled")
                expense_amount_var.set("")  # Очищаем поле при отключении

        expense_checkbox = tk.Checkbutton(
            modal, 
            bg="#e0f7fa", 
            fg="black", 
            text="Добавить как расход",
            variable=is_expense,
            command=toggle_expense_field
        )
        expense_checkbox.grid(row=5, column=0, columnspan=2, pady=5)


        # Поле для суммы расхода
    
        ttk.Label(modal, style="Custom.TLabel", text="Название продукта").grid(row=0, column=0)
        name_var = tk.StringVar(value=product['name'])
        entry_name = ttk.Entry(modal, textvariable=name_var)
        entry_name.grid(row=0, column=1, pady=5)
        
        ttk.Label(modal, style="Custom.TLabel", text="Цена").grid(row=1, column=0)
        price_var = tk.StringVar(value=str(product['price']))
        entry_price = ttk.Entry(modal, textvariable=price_var)
        entry_price.grid(row=1, column=1, pady=5)
        entry_price.bind("<KeyRelease>", validate_only_numbers)

        ttk.Label(modal, style="Custom.TLabel", text="Количество").grid(row=2, column=0)
        quantity_var = tk.StringVar(value=str(product['quantity']))
        entry_quantity = ttk.Entry(modal, textvariable=quantity_var)
        entry_quantity.grid(row=2, column=1, pady=5)
        entry_quantity.bind("<KeyRelease>", validate_only_numbers)
        
        ttk.Label(modal, style="Custom.TLabel", text="Изображение").grid(row=3, column=0)
        image_path_var = tk.StringVar(value=product["image_path"])
        img_preview_label = tk.Label(modal, bg="#e6f7ff", text="No Image", width=200, height=200)
        img_preview_label.grid(row=3, column=1)

        ttk.Label(modal, style="Custom.TLabel", text="Сумма расхода").grid(row=6, column=0, pady=5)
        entry_expense_amount = ttk.Entry(
            modal, 
            textvariable=expense_amount_var, 
            state="disabled"
        )
        entry_expense_amount.grid(row=6, column=1, pady=5)
        entry_expense_amount.bind("<KeyRelease>", validate_only_numbers)

        def compress_image(input_path, output_path, quality=85, size_limit_kb=500, min_resolution=(800, 800)):
            """Сжимает изображение, если размер превышает лимит или разрешение больше минимального."""
            file_size_kb = os.path.getsize(input_path) / 1024  # Размер файла в КБ

            with Image.open(input_path) as img:
                width, height = img.size

                # Проверка: нужно ли сжимать?
                needs_compression = file_size_kb > size_limit_kb or width > min_resolution[0] or height > min_resolution[1]

                if needs_compression:
                    img = img.convert("RGB")
                    img.save(output_path, "JPEG", optimize=True, quality=quality)
                else:
                    # Если изображение уже оптимизировано, просто копируем
                    shutil.copy(input_path, output_path)

        def select_image():
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
            if file_path:
                try:
                    # Создаем папку для изображений если ее нет
                    IMAGE_DIR = "images"
                    os.makedirs(IMAGE_DIR, exist_ok=True)

                    # Генерируем уникальное имя файла
                    file_name = os.path.basename(file_path)
                    new_file_path = os.path.join(IMAGE_DIR, file_name)

                    # Обрабатываем дубликаты
                    counter = 1
                    while os.path.exists(new_file_path):
                        name, ext = os.path.splitext(file_name)
                        new_file_path = os.path.join(IMAGE_DIR, f"{name}_{counter}{ext}")
                        counter += 1

                    # Сжимаем и сохраняем изображение
                    compress_image(file_path, new_file_path)

                    # Обновляем интерфейс
                    image_path_var.set(new_file_path)
                    load_image_preview(new_file_path)

                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось обработать изображение: {str(e)}")

        def load_image_preview(file_path):
            try:
                img = Image.open(file_path)
                img = img.resize((300, 200), Image.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                img_preview_label.configure(image=img_tk, text="")
                img_preview_label.image = img_tk
            except (FileNotFoundError, IOError):
                messagebox.showerror("Ошибка", "Не удалось загрузить изображение.")

        select_img_button = ttk.Button(modal, text="Выбрать изображение", command=select_image)
        select_img_button.grid(row=4, column=0, columnspan=2)

        load_image_preview(product["image_path"])

        def save_changes():
            new_name = name_var.get()
            try:
                new_price = float(price_var.get())
                new_quantity = int(quantity_var.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Цена и количество должны быть числами.")
                return

            new_image_path = image_path_var.get()

            if not (new_name and new_price >= 0 and new_quantity >= 0 and new_image_path):
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля правильно.")
                return

            update_product(product['id'], new_name, new_price, new_quantity, new_image_path)

            # Добавляем расход если нужно
            if is_expense.get():
                expense_amount = expense_amount_var.get()
                if not expense_amount:
                    messagebox.showerror("Ошибка", "Введите сумму расхода.")
                    return
                try:
                    expense_amount = float(expense_amount)
                except ValueError:
                    messagebox.showerror("Ошибка", "Сумма расхода должна быть числом.")
                    return
                
                expense_name = f"Закуп {new_name}"
                expense_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                insert_expense(expense_name, expense_amount, expense_date)

            messagebox.showinfo("Успех", "Продукт обновлен!")
            modal.destroy()
            display_products()

        def delete_products():
            if is_product_in_sales(product['id']):
                messagebox.showwarning("Ошибка", "Нельзя удалить продукт, так как он используется в продажах!")
                return
            response = messagebox.askyesno("Подтверждение удаления", "Вы уверены, что хотите удалить этот продукт?")
            if response:
                delete_product(product['id'])
                messagebox.showinfo("Успех", "Продукт успешно удален!")
                modal.destroy()
                display_products()

        ttk.Button(modal, text="Сохранить изменения", command=save_changes).grid(row=7, columnspan=2, pady=10)
        ttk.Button(modal, text="Удалить продукт", command=delete_products).grid(row=8, columnspan=2, pady=10)

    def refresh_product_page():
        display_products()
        frame.after(300000, refresh_product_page)

    display_products()
    return frame
