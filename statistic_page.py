import tkinter as tk
from tkinter import ttk
from database import get_cabin_statistics, get_total_income, get_total_expenses
from decimal import Decimal

def create_statistics_page(root):
    """Создает фрейм для отображения статистики."""
    frame = tk.Frame(root)

    # Заголовок
    tk.Label(frame, text="Статистика по кабинкам и финансовая статистика", font=("Arial", 16)).pack(pady=10)

    # Таблица статистики по кабинкам
    columns = ("cabin_name", "rental_count", "total_income", "avg_check")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
    tree.heading("cabin_name", text="Название кабинки")
    tree.heading("rental_count", text="Кол-во аренд")
    tree.heading("total_income", text="Общий доход")
    tree.heading("avg_check", text="Средний чек")
    tree.pack(padx=10, pady=10)

    # Финансовая статистика
    finance_frame = tk.Frame(frame)
    finance_frame.pack(pady=10)

    tk.Label(finance_frame, text="Финансовая статистика", font=("Arial", 14)).pack()

    finance_tree = ttk.Treeview(finance_frame, columns=("description", "value"), show="headings", height=5)
    finance_tree.heading("description", text="Описание")
    finance_tree.heading("value", text="Сумма (₽)")
    finance_tree.pack(padx=10, pady=10)

    # Кнопки для выбора периода
    button_frame = tk.Frame(frame)
    button_frame.pack(pady=10)

    def update_cabin_statistics(period):
        """Обновляет данные по кабинкам."""
        data = get_cabin_statistics(period)
        # Очистка текущих данных
        for item in tree.get_children():
            tree.delete(item)

        total_rentals = 0
        total_income = 0.0
        total_avg_check = 0.0
        total_cabins = len(data)

        # Заполнение таблицы данными
        for row in data:
            tree.insert("", "end", values=(row[1], row[2], f"{float(row[3]):.2f}", f"{float(row[4]):.2f}"))
            total_rentals += row[2]
            total_income += float(row[3])
            total_avg_check += float(row[4])

        # Рассчитать общий средний чек
        overall_avg_check = total_income / total_rentals if total_rentals > 0 else 0

        # Добавить пустую строку для отступа
        tree.insert("", "end", values=("", "", "", ""), tags=("spacer",))

        # Добавить строку с итогами
        tree.insert("", "end", values=("Итого", total_rentals, f"{total_income:.2f}", f"{overall_avg_check:.2f}"), tags=("summary",))

        # Стилизация итоговой строки и отступа
        tree.tag_configure("summary", font=("Helvetica", 10, "bold"))
        tree.tag_configure("spacer")

    def update_financial_statistics(period):
        """Обновляет данные финансовой статистики."""
        # Очистка текущих данных
        for item in finance_tree.get_children():
            finance_tree.delete(item)

        # Получаем данные
        total_income = get_total_income(period)
        total_expenses = get_total_expenses(period)
        net_profit = Decimal(total_income) - Decimal(total_expenses)

        # Добавляем строки с данными
        finance_tree.insert("", "end", values=("Общий доход", f"{total_income:.2f}"))
        finance_tree.insert("", "end", values=("Общие расходы", f"{total_expenses:.2f}"))
        finance_tree.insert("", "end", values=("Чистая прибыль", f"{net_profit:.2f}"))

        # Стилизация итоговой строки
        finance_tree.tag_configure("summary", font=("Helvetica", 10, "bold"))

    def update_statistics(period):
        """Обновляет статистику по кабинкам и финансам."""
        update_cabin_statistics(period)
        update_financial_statistics(period)

    # Кнопки переключения периода
    tk.Button(button_frame, text="День", command=lambda: update_statistics('day')).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Неделя", command=lambda: update_statistics('week')).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Месяц", command=lambda: update_statistics('month')).pack(side=tk.LEFT, padx=5)

    # Загружаем статистику за день по умолчанию
    update_statistics('day')

    return frame
