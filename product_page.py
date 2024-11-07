import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk  # Ensure Pillow library is installed
from database import insert_product, fetch_products

def create_product_page(root):
    frame = tk.Frame(root)
    
    # Fields for product details
    tk.Label(frame, text="Название продукта").grid(row=0, column=0)
    entry_name = tk.Entry(frame)
    entry_name.grid(row=0, column=1)
    
    tk.Label(frame, text="Цена").grid(row=1, column=0)
    entry_price = tk.Entry(frame)
    entry_price.grid(row=1, column=1)
    
    tk.Label(frame, text="Количество").grid(row=2, column=0)
    entry_quantity = tk.Entry(frame)
    entry_quantity.grid(row=2, column=1)

    # Image upload
    image_path = None
    img_label = tk.Label(frame, text="Нет изображения", width=20, height=10)
    img_label.grid(row=3, column=0, columnspan=2, pady=10)

    def select_image():
        nonlocal image_path
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")]
        )
        if file_path:
            image_path = file_path
            load_image_preview(image_path)

    def load_image_preview(file_path):
        img = Image.open(file_path)
        img = img.resize((100, 100), Image.ANTIALIAS)  # Resize image for preview
        img_tk = ImageTk.PhotoImage(img)
        img_label.configure(image=img_tk, text="")
        img_label.image = img_tk

    # Button to select image
    tk.Button(frame, text="Выбрать изображение", command=select_image).grid(row=4, column=0, columnspan=2)

    # Add product function
    def add_product():
        name = entry_name.get()
        price = entry_price.get()
        quantity = entry_quantity.get()
        
        if not (name and price.isdigit() and quantity.isdigit()):
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля правильно.")
            return
        if not image_path:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите изображение для продукта.")
            return
        
        # Save product with image path (or process to save image as binary if needed)
        insert_product(name, float(price), int(quantity), image_path)
        messagebox.showinfo("Успех", "Продукт добавлен!")
        entry_name.delete(0, tk.END)
        entry_price.delete(0, tk.END)
        entry_quantity.delete(0, tk.END)
        img_label.configure(image=None, text="Нет изображения")
        display_products()

    # Button to add product
    tk.Button(frame, text="Добавить продукт", command=add_product).grid(row=5, columnspan=2)
    
    # Table to display products
    tree = ttk.Treeview(frame, columns=("id", "name", "price", "quantity"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("name", text="Название")
    tree.heading("price", text="Цена")
    tree.heading("quantity", text="Количество")
    tree.grid(row=6, column=0, columnspan=2)

    # Display products in table
    def display_products():
        for item in tree.get_children():
            tree.delete(item)
        for row in fetch_products():
            tree.insert("", tk.END, values=row)

    display_products()
    return frame
