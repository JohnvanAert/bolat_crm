import tkinter as tk
from tkinter import messagebox, filedialog, Toplevel, ttk
from PIL import Image, ImageTk
from database import insert_product, fetch_products, update_product, delete_product, insert_expense
from datetime import datetime

def create_product_page(root):
    frame = tk.Frame(root)
    items_per_page_var = tk.IntVar(value=10)
    current_page_var = tk.IntVar(value=1)

    pagination_frame = tk.Frame(frame)
    pagination_frame.grid(row=2, column=0, columnspan=3)

    def open_add_product_modal():
        modal = Toplevel(root)
        modal.title("Добавление продукта")
        modal.geometry("400x400")

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


        tk.Label(modal, text="Название продукта").grid(row=0, column=0)
        entry_name = tk.Entry(modal)
        entry_name.grid(row=0, column=1)
        entry_name.bind("<KeyRelease>", validate_only_letters)

        tk.Label(modal, text="Цена").grid(row=1, column=0)
        entry_price = tk.Entry(modal)
        entry_price.grid(row=1, column=1)
        entry_price.bind("<KeyRelease>", validate_only_numbers)

        tk.Label(modal, text="Количество").grid(row=2, column=0)
        entry_quantity = tk.Entry(modal)
        entry_quantity.grid(row=2, column=1)
        entry_quantity.bind("<KeyRelease>", validate_only_numbers)


        tk.Label(modal, text="Изображение").grid(row=3, column=0)
        img_path_var = tk.StringVar()
        # Frame to hold the image preview and the close button
        img_frame = tk.Frame(modal)
        img_frame.grid(row=3, column=1, sticky="w")
        img_preview_label = tk.Label(modal, text="No Image", width=20, height=10)
        img_preview_label.grid(row=3, column=1)

            # Checkbox for expense
        is_expense = tk.BooleanVar()
        expense_checkbox = tk.Checkbutton(modal, text="Добавить как расход", variable=is_expense, command=lambda: toggle_expense_field())
        expense_checkbox.grid(row=7, column=0, columnspan=2)

        # Expense amount entry (initially disabled)
        tk.Label(modal, text="Сумма расхода").grid(row=5, column=0)
        entry_expense_amount = tk.Entry(modal, state="disabled")
        entry_expense_amount.grid(row=5, column=1)
        entry_expense_amount.bind("<KeyRelease>", validate_only_numbers)

        def remove_image():
            img_preview_label.config(image="", text="No Image")
            img_preview_label.image = None
            img_path_var.set("")

        close_button = tk.Button(img_frame, text="X", command=remove_image, width=2, height=1)
        close_button.grid(row=0, column=1, sticky="ne", padx=2, pady=2)


        def select_image():
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
            if file_path:
                img_path_var.set(file_path)
                load_image_preview(file_path)

        def load_image_preview(file_path):
            try:
                img = Image.open(file_path)
                img = img.resize((150, 100), Image.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                img_preview_label.configure(image=img_tk, text="")
                img_preview_label.image = img_tk
            except (FileNotFoundError, IOError):
                messagebox.showerror("Ошибка", "Не удалось загрузить изображение.")

        select_img_button = tk.Button(modal, text="Выбрать изображение", command=select_image)
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

        tk.Button(modal, text="Добавить продукт", command=add_product).grid(row=9, columnspan=2, pady=10)
        


    add_product_button = tk.Button(frame, text="Добавить продукт", command=open_add_product_modal)
    add_product_button.grid(row=0, column=0, pady=10)

    tk.Label(frame, text="Записей на странице:").grid(row=0, column=1)
    items_per_page_dropdown = ttk.Combobox(
        frame,
        textvariable=items_per_page_var,
        values=[10, 25, 50, 100],
        state="readonly"
    )
    items_per_page_dropdown.grid(row=0, column=2)
    items_per_page_dropdown.bind("<<ComboboxSelected>>", lambda e: [current_page_var.set(1), display_products()])

    product_container = tk.Frame(frame)
    product_container.grid(row=1, column=0, columnspan=3, pady=10)

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
            first_button = tk.Button(pagination_frame, text="<<", command=lambda: [current_page_var.set(1), display_products()])
            first_button.pack(side="left")
            prev_button = tk.Button(pagination_frame, text="<", command=lambda: [current_page_var.set(current_page - 1), display_products()])
            prev_button.pack(side="left")

        # Кнопки для страниц в пределах видимого диапазона
        for page_num in range(start_page, end_page + 1):
            state = "disabled" if page_num == current_page else "normal"
            page_button = tk.Button(pagination_frame, text=str(page_num), state=state, command=lambda p=page_num: [current_page_var.set(p), display_products()])
            page_button.pack(side="left")

        # Кнопки для перехода на следующую и последнюю страницы
        if end_page < total_pages:
            next_button = tk.Button(pagination_frame, text=">", command=lambda: [current_page_var.set(current_page + 1), display_products()])
            next_button.pack(side="left")
            last_button = tk.Button(pagination_frame, text=">>", command=lambda: [current_page_var.set(total_pages), display_products()])
            last_button.pack(side="left")

    def create_product_card(product, row, col):
        card = tk.Frame(product_container, borderwidth=2, relief="groove", padx=10, pady=10)
        
        def handle_click(event):
            open_edit_modal(product)

        try:
            img = Image.open(product["image_path"])
            img = img.resize((150, 100), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            img_label = tk.Label(card, image=img_tk)
            img_label.image = img_tk
            img_label.pack()
            img_label.bind("<Button-1>", handle_click)  # Привязка события к изображению
        except (FileNotFoundError, IOError):
            img_label = tk.Label(card, text="No Image", width=10, height=5)
            img_label.pack()
            img_label.bind("<Button-1>", handle_click)  # Привязка события к метке с текстом

        name_label = tk.Label(card, text=f"Название: {product['name']}")
        name_label.pack()
        name_label.bind("<Button-1>", handle_click)  # Привязка события к метке с названием

        price_label = tk.Label(card, text=f"Цена: {product['price']}")
        price_label.pack()
        price_label.bind("<Button-1>", handle_click)  # Привязка события к метке с ценой

        quantity_label = tk.Label(card, text=f"Количество: {product['quantity']}")
        quantity_label.pack()
        quantity_label.bind("<Button-1>", handle_click)  # Привязка события к метке с количеством

        card.bind("<Button-1>", handle_click)  # Привязка события к карточке
        card.grid(row=row, column=col, padx=10, pady=10)

    def open_edit_modal(product):
        modal = Toplevel(root)
        modal.title("Редактирование продукта")
        modal.geometry("600x400")

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


        tk.Label(modal, text="Название продукта").grid(row=0, column=0)
        name_var = tk.StringVar(value=product['name'])
        entry_name = tk.Entry(modal, textvariable=name_var)
        entry_name.grid(row=0, column=1)
        entry_name.bind("<KeyRelease>", validate_only_letters)
        
        tk.Label(modal, text="Цена").grid(row=1, column=0)
        price_var = tk.StringVar(value=str(product['price']))
        entry_price = tk.Entry(modal, textvariable=price_var)
        entry_price.grid(row=1, column=1)
        entry_price.bind("<KeyRelease>", validate_only_numbers)

        tk.Label(modal, text="Количество").grid(row=2, column=0)
        quantity_var = tk.StringVar(value=str(product['quantity']))
        entry_quantity = tk.Entry(modal, textvariable=quantity_var)
        entry_quantity.grid(row=2, column=1)
        entry_quantity.bind("<KeyRelease>", validate_only_numbers)
        
        tk.Label(modal, text="Изображение").grid(row=3, column=0)
        image_path_var = tk.StringVar(value=product["image_path"])
        img_preview_label = tk.Label(modal, text="No Image", width=150, height=200)
        img_preview_label.grid(row=3, column=1)


        def select_image():
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
            if file_path:
                image_path_var.set(file_path)
                load_image_preview(file_path)

        def load_image_preview(file_path):
            try:
                img = Image.open(file_path)
                img = img.resize((300, 200), Image.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                img_preview_label.configure(image=img_tk, text="")
                img_preview_label.image = img_tk
            except (FileNotFoundError, IOError):
                messagebox.showerror("Ошибка", "Не удалось загрузить изображение.")

        select_img_button = tk.Button(modal, text="Выбрать изображение", command=select_image)
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
            messagebox.showinfo("Успех", "Продукт обновлен!")
            modal.destroy()
            display_products()

        def delete_products():
            response = messagebox.askyesno("Подтверждение удаления", "Вы уверены, что хотите удалить этот продукт?")
            if response:
                delete_product(product['id'])
                messagebox.showinfo("Успех", "Продукт успешно удален!")
                modal.destroy()
                display_products()

        tk.Button(modal, text="Сохранить изменения", command=save_changes).grid(row=5, columnspan=2, pady=10)
        tk.Button(modal, text="Удалить продукт", command=delete_products, fg="red").grid(row=6, columnspan=2, pady=10)

    display_products()
    return frame
