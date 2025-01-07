import tkinter as tk
from tkinter import ttk
from database import get_cabin_statistics

def create_statistics_page(root):
    """Создает фрейм для отображения статистики."""
    frame = tk.Frame(root)

    # Заголовок
    tk.Label(frame, text="Статистика по кабинкам", font=("Arial", 16)).pack(pady=10)

    # Таблица
    columns = ("cabin_name", "rental_count", "total_income", "avg_check")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
    tree.heading("cabin_name", text="Название кабинки")
    tree.heading("rental_count", text="Кол-во аренд")
    tree.heading("total_income", text="Общий доход")
    tree.heading("avg_check", text="Средний чек")
    tree.pack(padx=10, pady=10)

    # Кнопки для выбора периода
    button_frame = tk.Frame(frame)
    button_frame.pack(pady=10)

    def update_statistics(period):
        data = get_cabin_statistics(period)  # Получение данных из базы
        # Очистка текущих данных
        for item in tree.get_children():
            tree.delete(item)

        total_rentals = 0
        total_income = 0.0
        total_avg_check = 0.0
        total_cabins = len(data)  # Количество кабин

        # Заполнение таблицы данными
        for row in data:
            tree.insert("", "end", values=(row[1], row[2], f"{float(row[3]):.2f}", f"{float(row[4]):.2f}"))
            total_rentals += row[2]
            total_income += float(row[3])
            total_avg_check += float(row[4])

        # Рассчитать общий средний чек (если общее количество аренды > 0)
        overall_avg_check = total_income / total_rentals if total_rentals > 0 else 0

        # Добавить пустую строку для отступа
        tree.insert("", "end", values=("", "", "", ""), tags=("spacer",))

        # Добавить строку с итогами
        tree.insert("", "end", values=("Итого", total_rentals, f"{total_income:.2f}", f"{overall_avg_check:.2f}"), tags=("summary",))

        # Стилизация итоговой строки и отступа
        tree.tag_configure("summary", font=("Helvetica", 10, "bold"))
        tree.tag_configure("spacer")  # Белый фон для пустой строки


    # Кнопки переключения
    tk.Button(button_frame, text="День", command=lambda: update_statistics('day')).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Неделя", command=lambda: update_statistics('week')).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Месяц", command=lambda: update_statistics('month')).pack(side=tk.LEFT, padx=5)

    # Загружаем статистику за день по умолчанию
    update_statistics('day')

    return frame