import tkinter as tk
from tkinter import messagebox, filedialog, Toplevel
from PIL import Image, ImageTk
from database import insert_product, fetch_products, update_product  # Add an update_product function in your database module

def create_product_page(root):
    frame = tk.Frame(root)
    
    # Fields for adding a new product
    tk.Label(frame, text="Название продукта").grid(row=0, column=0)
    entry_name = tk.Entry(frame)
    entry_name.grid(row=0, column=1)
    
    tk.Label(frame, text="Цена").grid(row=1, column=0)
    entry_price = tk.Entry(frame)
    entry_price.grid(row=1, column=1)
    
    tk.Label(frame, text="Количество").grid(row=2, column=0)
    entry_quantity = tk.Entry(frame)
    entry_quantity.grid(row=2, column=1)
    
    tk.Label(frame, text="Изображение").grid(row=3, column=0)
    img_path_var = tk.StringVar()
    img_preview_label = tk.Label(frame, text="No Image", width=20, height=10)
    img_preview_label.grid(row=3, column=1)

    def select_image():
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            img_path_var.set(file_path)
            load_image_preview(file_path)

    def load_image_preview(file_path):
        img = Image.open(file_path)
        img = img.resize((100, 100), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        img_preview_label.configure(image=img_tk, text="")
        img_preview_label.image = img_tk

    select_img_button = tk.Button(frame, text="Выбрать изображение", command=select_image)
    select_img_button.grid(row=4, column=0, columnspan=2)

    # Function to add a new product
    def add_product():
        name = entry_name.get()
        price = entry_price.get()
        quantity = entry_quantity.get()
        image_path = img_path_var.get()
        
        if not (name and price.isdigit() and quantity.isdigit() and image_path):
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля правильно.")
            return

        insert_product(name, float(price), int(quantity), image_path)  # Adjust to save image path in the database
        messagebox.showinfo("Успех", "Продукт добавлен!")
        entry_name.delete(0, tk.END)
        entry_price.delete(0, tk.END)
        entry_quantity.delete(0, tk.END)
        img_preview_label.config(image="", text="No Image")
        img_path_var.set("")
        display_products()

    tk.Button(frame, text="Добавить продукт", command=add_product).grid(row=5, columnspan=2, pady=10)

    # Container for product cards
    product_container = tk.Frame(frame)
    product_container.grid(row=6, column=0, columnspan=2, pady=10)

    def display_products():
        for widget in product_container.winfo_children():
            widget.destroy()
        products = fetch_products()
        for product in products:
            create_product_card(product)

    def create_product_card(product):
        card = tk.Frame(product_container, borderwidth=2, relief="groove", padx=10, pady=10)
        
        # Load and display image
        try:
            img = Image.open(product["image_path"])
            img = img.resize((80, 80), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            img_label = tk.Label(card, image=img_tk)
            img_label.image = img_tk
            img_label.pack()
        except:
            img_label = tk.Label(card, text="No Image", width=10, height=5)
            img_label.pack()

        # Display product details
        tk.Label(card, text=f"Название: {product['name']}").pack()
        tk.Label(card, text=f"Цена: {product['price']}").pack()
        tk.Label(card, text=f"Количество: {product['quantity']}").pack()

        # Bind click event to open modal for editing
        card.bind("<Button-1>", lambda e, p=product: open_edit_modal(p))
        card.pack(side="left", padx=10, pady=10)

    def open_edit_modal(product):
        modal = Toplevel(root)
        modal.title("Редактирование продукта")
        modal.geometry("300x300")

        tk.Label(modal, text="Название продукта").grid(row=0, column=0)
        name_var = tk.StringVar(value=product['name'])
        entry_name = tk.Entry(modal, textvariable=name_var)
        entry_name.grid(row=0, column=1)

        tk.Label(modal, text="Цена").grid(row=1, column=0)
        price_var = tk.StringVar(value=str(product['price']))
        entry_price = tk.Entry(modal, textvariable=price_var)
        entry_price.grid(row=1, column=1)

        tk.Label(modal, text="Количество").grid(row=2, column=0)
        quantity_var = tk.StringVar(value=str(product['quantity']))
        entry_quantity = tk.Entry(modal, textvariable=quantity_var)
        entry_quantity.grid(row=2, column=1)

        tk.Label(modal, text="Изображение").grid(row=3, column=0)
        image_path_var = tk.StringVar(value=product["image_path"])
        img_preview_label = tk.Label(modal, text="No Image", width=20, height=10)
        img_preview_label.grid(row=3, column=1)

        def select_image():
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
            if file_path:
                image_path_var.set(file_path)
                load_image_preview(file_path)

        def load_image_preview(file_path):
            img = Image.open(file_path)
            img = img.resize((100, 100), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            img_preview_label.configure(image=img_tk, text="")
            img_preview_label.image = img_tk

        select_img_button = tk.Button(modal, text="Выбрать изображение", command=select_image)
        select_img_button.grid(row=4, column=0, columnspan=2)

        # Load initial preview
        load_image_preview(product["image_path"])

        # Save changes function
        def save_changes():
            new_name = name_var.get()
            new_price = price_var.get()
            new_quantity = quantity_var.get()
            new_image_path = image_path_var.get()

            if not (new_name and new_price.isdigit() and new_quantity.isdigit() and new_image_path):
                messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля правильно.")
                return

            update_product(product['id'], new_name, float(new_price), int(new_quantity), new_image_path)
            messagebox.showinfo("Успех", "Продукт обновлен!")
            modal.destroy()
            display_products()

        tk.Button(modal, text="Сохранить изменения", command=save_changes).grid(row=5, columnspan=2, pady=10)

    display_products()
    return frame
