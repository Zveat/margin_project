# google_sheets_db.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import base64
from datetime import datetime

# Настройка доступа к Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def connect_to_sheets():
    """Подключается к Google Sheets с использованием Base64-кодированных credentials из переменной окружения."""
    try:
        # Получаем закодированную строку Base64 из переменной окружения
        credentials_b64 = os.getenv("GOOGLE_CREDENTIALS")
        if not credentials_b64:
            raise ValueError("Переменная окружения GOOGLE_CREDENTIALS не найдена")

        # Декодируем Base64 в JSON
        credentials_json = base64.b64decode(credentials_b64).decode('utf-8')

        # Парсим JSON и создаём учётные данные
        creds_dict = json.loads(credentials_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"Ошибка подключения к Google Sheets: {e}")
        raise

def get_or_create_spreadsheet(spreadsheet_id=None, spreadsheet_name="MarginCalculations"):
    """Получает или создаёт Google Таблицу."""
    client = connect_to_sheets()
    if spreadsheet_id:
        try:
            return client.open_by_key(spreadsheet_id)
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"Таблица с ID {spreadsheet_id} не найдена. Создаём новую таблицу с именем {spreadsheet_name}.")
            return client.create(spreadsheet_name)
    else:
        return client.create(spreadsheet_name)

def save_calculation(spreadsheet_id, client_data, deal_data, products, calculation_result):
    """Сохраняет расчёт в Google Sheets с отдельными листами."""
    sheet = get_or_create_spreadsheet(spreadsheet_id)

    # Лист "Clients"
    clients_sheet = sheet.worksheet("Clients")
    clients_data = [
        [client_data['name'], client_data['company'], client_data['bin'], 
         client_data['phone'], client_data['address'], client_data['contract']]
    ]
    clients_sheet.append_row(clients_data[0])  # Добавляем нового клиента
    client_row = len(clients_sheet.get_all_values())  # Последняя строка
    client_id = client_row  # Используем номер строки как ID

    # Лист "Deals"
    deals_sheet = sheet.worksheet("Deals")
    deals_data = [
        [client_id, deal_data['total_logistics'], deal_data['kickback']]
    ]
    deals_sheet.append_row(deals_data[0])  # Добавляем сделку
    deal_row = len(deals_sheet.get_all_values())  # Последняя строка
    deal_id = deal_row  # Используем номер строки как ID

    # Лист "Products"
    products_sheet = sheet.worksheet("Products")
    for product in products:
        products_data = [
            [deal_id, product['Товар'], product['Ед_измерения'], product['Количество'], 
             product['Вес (кг)'], product['Цена поставщика 1'], product['Комментарий поставщика 1'],
             product['Цена поставщика 2'], product['Комментарий поставщика 2'],
             product['Цена поставщика 3'], product['Комментарий поставщика 3'],
             product['Цена поставщика 4'], product['Комментарий поставщика 4'],
             product['Наценка (%)']]
        ]
        products_sheet.append_row(products_data[0])

    # Лист "History"
    history_sheet = sheet.worksheet("History")
    history_data = [
        [deal_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'черновик' if not calculation_result else 'завершён']
    ]
    history_sheet.append_row(history_data[0])

    return deal_id  # Возвращаем ID сделки (номер строки)

def load_calculation(spreadsheet_id, deal_id):
    """Восстанавливает расчёт по ID сделки (номер строки в Deals)."""
    sheet = get_or_create_spreadsheet(spreadsheet_id)

    # Загружаем сделку
    deals_sheet = sheet.worksheet("Deals")
    deal_data = deals_sheet.row_values(deal_id)
    if not deal_data:
        return None
    client_id, total_logistics, kickback = deal_data

    # Загружаем клиента
    clients_sheet = sheet.worksheet("Clients")
    client_data = clients_sheet.row_values(int(client_id))
    if not client_data:
        return None
    client_name, client_company, client_bin, client_phone, client_address, client_contract = client_data

    # Загружаем товары
    products_sheet = sheet.worksheet("Products")
    all_products = products_sheet.get_all_values()
    products = []
    for row in all_products[1:]:  # Пропускаем заголовок
        if row[1] == str(deal_id):  # deal_id
            products.append({
                "Товар": row[2], "Ед_измерения": row[3], "Количество": int(row[4]) if row[4] else 0,
                "Вес (кг)": int(row[5]) if row[5] else 0, "Цена поставщика 1": int(row[6]) if row[6] else 0,
                "Комментарий поставщика 1": row[7], "Цена поставщика 2": int(row[8]) if row[8] else 0,
                "Комментарий поставщика 2": row[9], "Цена поставщика 3": int(row[10]) if row[10] else 0,
                "Комментарий поставщика 3": row[11], "Цена поставщика 4": int(row[12]) if row[12] else 0,
                "Комментарий поставщика 4": row[13], "Наценка (%)": int(row[14]) if row[14] else 0
            })

    return (client_name, client_company, client_bin, client_phone, client_address, client_contract), \
           (total_logistics, kickback), products
