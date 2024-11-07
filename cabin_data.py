# cabin_data.py
cabin_observers = []
cabins_data = []

def add_observer(observer_func):
    cabin_observers.append(observer_func)

def notify_observers():
    for observer in cabin_observers:
        observer()

def update_cabins_data(new_data):
    global cabins_data
    cabins_data = new_data
    notify_observers()

def get_cabins_data():
    return cabins_data
