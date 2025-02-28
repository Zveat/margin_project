# google_sheets_db.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import base64
from datetime import datetime  # Импортируем datetime напрямую

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

def save_calculation(spreadsheet_id, client_data, deal_data, products, include_products=False):
    """Сохраняет расчёт в Google Sheets с отдельными листами: Clients, Deals, Products, History."""
    sheet = get_or_create_spreadsheet(spreadsheet_id)

    # Лист "Clients"
    clients_sheet = sheet.worksheet("Clients")
    # Проверяем, существует ли клиент с таким client_id или добавляем нового
    client_id = f"client_{len(clients_sheet.get_all_values()) + 1}"  # Уникальный client_id на основе количества строк
    client_exists = any(row[0] == client_id for row in clients_sheet.get_all_values()[1:])
    if not client_exists:
        clients_sheet.append_row([
            client_id,
            client_data['name'],
            client_data['company'],
            client_data['bin'],
            client_data['phone'],
            client_data['address'],
            client_data['contract'],
        ])

    # Лист "Deals"
    deals_sheet = sheet.worksheet("Deals")
    # Генерируем следующий deal_id (увеличиваем максимальный существующий)
    existing_deals = [int(row[0]) for row in deals_sheet.get_all_values()[1:] if row and row[0].isdigit()]
    deal_id = max(existing_deals) + 1 if existing_deals else 1

    # Сохраняем данные сделки в Deals
    deals_sheet.append_row([
        str(deal_id),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Используем datetime.now() вместо datetime.datetime.now()
        client_data['name'],  # client_name
        client_data['company'],  # client_company
        client_data['bin'],  # client_bin
        client_data['phone'],  # client_phone
        client_data['address'],  # client_address
        str(deal_data['total_logistics']),  # total_logistics
        str(deal_data['kickback']),  # kickback
    ])

    # Лист "Products"
    if include_products:
        products_sheet = sheet.worksheet("Products")
        for product in products:
            products_sheet.append_row([
                f"prod_{deal_id}_{len(products_sheet.get_all_values()) + 1}",  # product_id
                str(deal_id),  # deal_id
                product['Товар'],  # ProductName
                product['Ед_измерения'],  # Unit
                str(product['Количество']),  # Quantity
                str(product['Вес (кг)']),  # Weight
                str(product['Цена поставщика 1']),  # PriceSupplier1
                product['Комментарий поставщика 1'],  # CommentSupplier1
                str(product['Цена поставщика 2']),  # PriceSupplier2
                product['Комментарий поставщика 2'],  # CommentSupplier2
                str(product['Цена поставщика 3']),  # PriceSupplier3
                product['Комментарий поставщика 3'],  # CommentSupplier3
                str(product['Цена поставщика 4']),  # PriceSupplier4
                product['Комментарий поставщика 4'],  # CommentSupplier4
                str(product['Наценка (%)']),  # Markup
            ])

    # Лист "History"
    history_sheet = sheet.worksheet("History")
    history_sheet.append_row([
        str(deal_id),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Используем datetime.now() вместо datetime.datetime.now()
        client_data['name'],  # client_name
        client_data['company'],  # client_company
        client_data['bin'],  # client_bin
        client_data['phone'],  # client_phone
        client_data['address'],  # client_address
        client_data['contract'],  # client_contract
        str(deal_data['total_logistics']),  # total_logistics
        str(deal_data['kickback']),  # kickback
    ])

    return deal_id  # Возвращаем ID сделки

def load_calculation(spreadsheet_id, deal_id):
    """Восстанавливает расчёт по ID сделки (deal_id из Deals)."""
    sheet = get_or_create_spreadsheet(spreadsheet_id)

    # Загружаем сделку из листа "Deals"
    deals_sheet = sheet.worksheet("Deals")
    deal_data = None
    for row in deals_sheet.get_all_values()[1:]:  # Пропускаем заголовок
        if row[0] == str(deal_id):
            deal_data = row
            break
    if not deal_data:
        return None, None, None

    # Извлекаем данные сделки
    _, calculation_date, client_name, client_company, client_bin, client_phone, client_address, total_logistics, kickback = deal_data

    # Загружаем клиента (опционально, для проверки, если нужно)
    clients_sheet = sheet.worksheet("Clients")
    client_data_verified = None
    for row in clients_sheet.get_all_values()[1:]:  # Пропускаем заголовок
        if row[1] == client_name and row[2] == client_company:  # Сравниваем Name и Company
            client_data_verified = row
            break
    if not client_data_verified:
        print(f"Клиент с именем {client_name} и компанией {client_company} не найден в Clients.")

    # Загружаем товары из листа "Products"
    products_sheet = sheet.worksheet("Products")
    products = []
    for row in products_sheet.get_all_values()[1:]:  # Пропускаем заголовок
        if row[1] == str(deal_id):  # deal_id в столбце B
            products.append({
                "Товар": row[2],  # ProductName (столбец C)
                "Ед_измерения": row[3],  # Unit (столбец D)
                "Количество": int(float(row[4])) if row[4] else 0,  # Quantity (столбец E)
                "Вес (кг)": int(float(row[5])) if row[5] else 0,  # Weight (столбец F)
                "Цена поставщика 1": int(float(row[6])) if row[6] else 0,  # PriceSupplier1 (столбец G)
                "Комментарий поставщика 1": row[7],  # CommentSupplier1 (столбец H)
                "Цена поставщика 2": int(float(row[8])) if row[8] else 0,  # PriceSupplier2 (столбец I)
                "Комментарий поставщика 2": row[9],  # CommentSupplier2 (столбец J)
                "Цена поставщика 3": int(float(row[10])) if row[10] else 0,  # PriceSupplier3 (столбец K)
                "Комментарий поставщика 3": row[11],  # CommentSupplier3 (столбец L)
                "Цена поставщика 4": int(float(row[12])) if row[12] else 0,  # PriceSupplier4 (столбец M)
                "Комментарий поставщика 4": row[13],  # CommentSupplier4 (столбец N)
                "Наценка (%)": int(float(row[14])) if row[14] else 0,  # Markup (столбец O)
            })
    print(f"Восстановленные продукты для deal_id {deal_id}: {products}")  # Отладка

    return (
        (client_name, client_company, client_bin, client_phone, client_address, ""),
        (total_logistics, kickback),
        products
    )

def save_auth_state(spreadsheet_id, session_id, auth_state):
    """Сохраняет состояние авторизации в Google Sheets с привязкой к session_id."""
    sheet = get_or_create_spreadsheet(spreadsheet_id)
    auth_worksheet = sheet.worksheet("AuthState")  # Создаём или используем лист для состояния авторизации

    # Проверяем, есть ли запись для этой сессии
    all_auth = auth_worksheet.get_all_values()
    session_found = False
    for i, row in enumerate(all_auth, 1):
        if row[0] == session_id:
            # Обновляем существующую запись
            auth_worksheet.update_cell(i, 1, session_id)
            auth_worksheet.update_cell(i, 2, str(auth_state["authenticated"]).upper())  # Сохраняем как "TRUE" или "FALSE"
            auth_worksheet.update_cell(i, 3, auth_state["user"] or "")
            session_found = True
            break

    if not session_found:
        # Добавляем новую запись
        auth_worksheet.append_row([session_id, str(auth_state["authenticated"]).upper(), auth_state["user"] or ""])

def load_auth_state(spreadsheet_id, session_id):
    """Загружает состояние авторизации из Google Sheets по session_id."""
    sheet = get_or_create_spreadsheet(spreadsheet_id)
    auth_worksheet = sheet.worksheet("AuthState")

    all_auth = auth_worksheet.get_all_values()
    for row in all_auth:
        if row[0] == session_id:
            # Улучшенная обработка значения Authenticated (учитываем "TRUE", "True", "true")
            authenticated = row[1].strip().upper() in ["TRUE", "True", "true"]
            user = row[2].strip() if row[2] else ""
            print(f"Найдена запись для сессии {session_id}: authenticated={authenticated}, user={user}")
            return {
                "authenticated": authenticated,
                "user": user
            }
    print(f"Запись для сессии {session_id} не найдена, возвращаем состояние по умолчанию")
    return {"authenticated": False, "user": ""}
