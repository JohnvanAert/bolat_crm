import tkinter as tk
from tkinter import messagebox, ttk  # Добавьте ttk для таблицы
from database import insert_sales_data, connect  # Подключаем функции

# Функция для получения данных из таблицы sales и отображения их в интерфейсе
def display_sales_data():
    try:
        conn = connect()  # Подключение к базе данных
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sales ORDER BY date DESC")
        sales_data = cursor.fetchall()  # Получаем все строки

        # Очищаем таблицу перед вставкой новых данных
        for item in tree.get_children():
            tree.delete(item)

        # Вставляем данные в таблицу
        for row in sales_data:
            tree.insert("", tk.END, values=row)

        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

# Функция для добавления данных и обновления таблицы
def submit_data():
    try:
        cabins_count = int(entry_cabins.get())
        total_sales = float(entry_sales.get())
        customer_count = int(entry_customers.get())

        insert_sales_data(cabins_count, total_sales, customer_count)
        messagebox.showinfo("Успех", "Данные успешно добавлены!")
        display_sales_data()  # Обновляем отображение новых данных
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

# GUI setup
root = tk.Tk()
root.title("CRM Sales Entry")

# Labels and entry fields
tk.Label(root, text="Cabins Count").grid(row=0, column=0)
entry_cabins = tk.Entry(root)
entry_cabins.grid(row=0, column=1)

tk.Label(root, text="Total Sales").grid(row=1, column=0)
entry_sales = tk.Entry(root)
entry_sales.grid(row=1, column=1)

tk.Label(root, text="Customer Count").grid(row=2, column=0)
entry_customers = tk.Entry(root)
entry_customers.grid(row=2, column=1)

# Submit button
submit_button = tk.Button(root, text="Submit", command=submit_data)
submit_button.grid(row=3, columnspan=2)

# Treeview для отображения данных из sales
tree = ttk.Treeview(root, columns=("id", "cabins_count", "total_sales", "customer_count", "date"), show="headings")
tree.heading("id", text="ID")
tree.heading("cabins_count", text="Количество кабин")
tree.heading("total_sales", text="Общая продажа")
tree.heading("customer_count", text="Количество клиентов")
tree.heading("date", text="Дата")
tree.grid(row=4, column=0, columnspan=2)

# Первоначальный вызов для отображения данных при запуске
display_sales_data()

root.mainloop()
