import tkinter as tk
from tkinter import messagebox, ttk
from database import insert_product, fetch_products

def create_product_page(root):
    frame = tk.Frame(root)
    
    tk.Label(frame, text="Название продукта").grid(row=0, column=0)
    entry_name = tk.Entry(frame)
    entry_name.grid(row=0, column=1)
    
    tk.Label(frame, text="Цена").grid(row=1, column=0)
    entry_price = tk.Entry(frame)
    entry_price.grid(row=1, column=1)
    
    tk.Label(frame, text="Количество").grid(row=2, column=0)
    entry_quantity = tk.Entry(frame)
    entry_quantity.grid(row=2, column=1)

    def add_product():
        name = entry_name.get()
        price = entry_price.get()
        quantity = entry_quantity.get()
        
        if not (name and price.isdigit() and quantity.isdigit()):
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля правильно.")
            return
        
        insert_product(name, float(price), int(quantity))
        messagebox.showinfo("Успех", "Продукт добавлен!")
        display_products()

    tk.Button(frame, text="Добавить продукт", command=add_product).grid(row=3, columnspan=2)
    
    tree = ttk.Treeview(frame, columns=("id", "name", "price", "quantity"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("name", text="Название")
    tree.heading("price", text="Цена")
    tree.heading("quantity", text="Количество")
    tree.grid(row=4, column=0, columnspan=2)

    def display_products():
        for item in tree.get_children():
            tree.delete(item)
        for row in fetch_products():
            tree.insert("", tk.END, values=row)

    display_products()
    return frame
