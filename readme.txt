3B CRM - Руководство по установке и развертыванию 🚀📌💻

1. Описание проекта 🎯📋✅

3B CRM - это система управления бронированием кабинок, продажами и запасами товаров. Разработана на Python с использованием Tkinter и PostgreSQL. 🎨🐍💾

2. Требования 🛠️📌⚙️

Операционная система:

macOS / Windows / Linux

Зависимости:

Python 3.11+

PostgreSQL 14+

Git

PyInstaller (для создания исполняемых файлов)

PyUpdater (для обновлений)

Python-библиотеки:

Установи все зависимости командой: 🏗️📦🔧

pip install -r requirements.txt

3. Установка базы данных PostgreSQL 🗄️🛠️🔗

Установить PostgreSQL:

macOS: brew install postgresql

Ubuntu: sudo apt install postgresql

Windows: Скачать с официального сайта

Создать пользователя и базу данных: 🏛️🔑📝

CREATE USER crm_bolat WITH PASSWORD 'your_password';
CREATE DATABASE bolat_crm OWNER crm_bolat;

Импортировать схему: 📥📂🛠️

pg_restore -U crm_bolat -d bolat_crm -h localhost -p 5432 schema_backup.dump

Проверить подключение: ✅🔍🖥️

psql -U crm_bolat -d bolat_crm -h localhost -p 5432
\dt  -- Должны отобразиться таблицы

4. Запуск приложения 🚀🎛️🖥️

Запусти CRM через Python: 🏃‍♂️💨

python main.py

5. Создание установочного файла 📦💾⚙️

Собери исполняемый файл: 🏗️💻

pyinstaller --onefile --windowed --name BolatCRM main.py

После этого приложение будет доступно в папке dist/. 📂✅

6. Обновление приложения с PyUpdater 🔄📦🛠️

Инициализировать репозиторий обновлений: 🏗️🔍✅

pyupdater init

Создать новую версию и загрузить: 📤🔢💡

pyupdater build --app-version=0.2.0 main.py
pyupdater upload

Проверить обновления: 🔄🔍✅

pyupdater check

7. Подключение к GitHub (для обновлений) 🌍🔗📂

Добавить репозиторий: 📤📌💾

git remote add origin https://github.com/JohnvanAert/bolat_crm.git
git push -u origin main

Создавать новые релизы через GitHub Releases и загружать бинарные файлы. 📦🚀✅

8. Поддержка 📞📧🤝

Если у тебя есть вопросы или предложения, свяжись через GitHub Issues. 💬🔗✅

