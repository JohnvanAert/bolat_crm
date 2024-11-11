# expenses_data.py
expense_observers = []
expenses_data = []

def add_observer(observer_func):
    expense_observers.append(observer_func)

def notify_observers():
    for observer in expense_observers:
        observer()

def update_expenses_data(new_data):
    global expenses_data
    expenses_data = new_data
    notify_observers()

def get_expenses_data():
    return expenses_data
