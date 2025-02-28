# google_sheets_db.py

import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import streamlit as st  # Импортируем streamlit для доступа к секретам

# Настройка доступа к Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def connect_to_sheets():
    """Устанавливает соединение с Google Sheets, используя секреты Streamlit Cloud или локальный файл."""
    try:
        # Проверяем, доступны ли секреты Streamlit Cloud
        credentials_json = st.secrets.get("GOOGLE_CREDENTIALS")
        if credentials_json:
            # Парсим JSON из секрета
            creds_dict = json.loads(credentials_json)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        else:
            # Если секреты недоступны, пытаемся использовать локальный файл
            CREDS_PATH = "credentials.json"
            try:
                creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, SCOPE)
            except FileNotFoundError:
                st.error("Файл credentials.json не найден и секреты Streamlit Cloud не настроены. Убедитесь, что секрет GOOGLE_CREDENTIALS настроен в Streamlit Cloud или файл credentials.json доступен локально.")
                raise
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Ошибка подключения к Google Sheets: {e}")
        raise

def save_calculation(spreadsheet_id, client_data, deal_data, products, is_active=True):
    """Сохраняет расчёт в Google Sheets."""
    conn = connect_to_sheets()
    sheet = conn.open_by_key(spreadsheet_id)
    worksheet = sheet.worksheet("History")

    # Генерируем уникальный deal_id
    all_values = worksheet.get_all_values()
    deal_id = str(len(all_values) + 1) if not all_values else str(int(all_values[-1][0]) + 1)

    # Форматируем данные
    calculation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [
        deal_id,
        calculation_date,
        client_data['name'],
        client_data['company'],
        client_data['bin'],
        client_data['phone'],
        client_data['address'],
        client_data['contract'],
        deal_data['total_logistics'],
        deal_data['kickback'],
        str(is_active)
    ]

    # Добавляем строку в History
    worksheet.append_row(row)

    # Сохраняем продукты в отдельной таблице (например, "Products")
    if products:
        product_worksheet = sheet.worksheet("Products")
        for product in products:
            product_row = [
                deal_id,
                product['Товар'],
                product['Ед_измерения'],
                product['Количество'],
                product['Вес (кг)'],
                product['Цена поставщика 1'],
                product['Комментарий поставщика 1'],
                product['Цена поставщика 2'],
                product['Комментарий поставщика 2'],
                product['Цена поставщика 3'],
                product['Комментарий поставщика 3'],
                product['Цена поставщика 4'],
                product['Комментарий поставщика 4'],
                product['Наценка (%)']
            ]
            product_worksheet.append_row(product_row)

    return deal_id

def load_calculation(spreadsheet_id, deal_id):
    """Загружает расчёт из Google Sheets по deal_id."""
    conn = connect_to_sheets()
    sheet = conn.open_by_key(spreadsheet_id)
    history_worksheet = sheet.worksheet("History")
    product_worksheet = sheet.worksheet("Products")

    # Ищем запись в History
    all_history = history_worksheet.get_all_values()
    for row in all_history:
        if row[0] == str(deal_id):
            client_data = {
                'name': row[2],
                'company': row[3],
                'bin': row[4],
                'phone': row[5],
                'address': row[6],
                'contract': row[7]
            }
            deal_data = {
                'total_logistics': float(row[8]) if row[8] else 0,
                'kickback': float(row[9]) if row[9] else 0
            }
            # Загружаем продукты
            products = []
            all_products = product_worksheet.get_all_values()
            for product_row in all_products:
                if product_row[0] == str(deal_id):
                    products.append({
                        'Товар': product_row[1],
                        'Ед_измерения': product_row[2],
                        'Количество': float(product_row[3]),
                        'Вес (кг)': float(product_row[4]) if product_row[4] else 0,
                        'Цена поставщика 1': float(product_row[5]) if product_row[5] else 0,
                        'Комментарий поставщика 1': product_row[6],
                        'Цена поставщика 2': float(product_row[7]) if product_row[7] else 0,
                        'Комментарий поставщика 2': product_row[8],
                        'Цена поставщика 3': float(product_row[9]) if product_row[9] else 0,
                        'Комментарий поставщика 3': product_row[10],
                        'Цена поставщика 4': float(product_row[11]) if product_row[11] else 0,
                        'Комментарий поставщика 4': product_row[12],
                        'Наценка (%)': float(product_row[13]) if product_row[13] else 0
                    })
            return client_data, deal_data, products
    return None, None, None

def save_auth_state(spreadsheet_id, username, auth_state):
    """Сохраняет состояние авторизации в Google Sheets."""
    conn = connect_to_sheets()
    sheet = conn.open_by_key(spreadsheet_id)
    auth_worksheet = sheet.worksheet("AuthState")  # Создаём или используем лист для состояния авторизации

    # Проверяем, есть ли запись для этого пользователя
    all_auth = auth_worksheet.get_all_values()
    user_found = False
    for i, row in enumerate(all_auth, 1):
        if row[0] == username:
            # Обновляем существующую запись
            auth_worksheet.update_cell(i, 1, username)
            auth_worksheet.update_cell(i, 2, str(auth_state["authenticated"]))
            auth_worksheet.update_cell(i, 3, auth_state["user"] or "")
            user_found = True
            break

    if not user_found:
        # Добавляем новую запись
        auth_worksheet.append_row([username, str(auth_state["authenticated"]), auth_state["user"] or ""])

def load_auth_state(spreadsheet_id, username):
    """Загружает состояние авторизации из Google Sheets."""
    conn = connect_to_sheets()
    sheet = conn.open_by_key(spreadsheet_id)
    auth_worksheet = sheet.worksheet("AuthState")

    all_auth = auth_worksheet.get_all_values()
    for row in all_auth:
        if row[0] == username:
            return {
                "authenticated": row[1].lower() == "true",
                "user": row[2] or ""
            }
    return {"authenticated": False, "user": ""}
