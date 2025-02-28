# google_sheets_db.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# Настройка доступа к Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "service_account.json"  # Замените на путь к вашему JSON-файлу или используйте переменную окружения GOOGLE_CREDENTIALS

def get_credentials():
    """Получает учетные данные для доступа к Google Sheets."""
    try:
        return ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
    except FileNotFoundError:
        # Попробуем использовать переменную окружения GOOGLE_CREDENTIALS
        import os
        creds_json = os.getenv("GOOGLE_CREDENTIALS")
        if creds_json:
            import json
            return ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json), SCOPE)
        raise FileNotFoundError("Не найден файл credentials или переменная окружения GOOGLE_CREDENTIALS")

def get_or_create_spreadsheet(spreadsheet_id):
    """Получает или создаёт Google Sheet по ID."""
    try:
        credentials = get_credentials()
        client = gspread.authorize(credentials)
        return client.open_by_key(spreadsheet_id)
    except gspread.exceptions.SpreadsheetNotFound:
        raise gspread.exceptions.SpreadsheetNotFound(f"Spreadsheet with ID {spreadsheet_id} not found.")

def connect_to_sheets():
    """Устанавливает соединение с Google Sheets."""
    credentials = get_credentials()
    return gspread.authorize(credentials)

def save_calculation(spreadsheet_id, client_data, deal_data, products, save_to_history=True):
    """Сохраняет расчёт в Google Sheets."""
    sheet = get_or_create_spreadsheet(spreadsheet_id)

    # Создаём или получаем лист "Calculations"
    try:
        calculations_worksheet = sheet.worksheet("Calculations")
    except gspread.exceptions.WorksheetNotFound:
        calculations_worksheet = sheet.add_worksheet(title="Calculations", rows="1000", cols="20")

    # Создаём или получаем лист "History" (если save_to_history=True)
    if save_to_history:
        try:
            history_worksheet = sheet.worksheet("History")
        except gspread.exceptions.WorksheetNotFound:
            history_worksheet = sheet.add_worksheet(title="History", rows="1000", cols="20")
            # Добавляем заголовки в History, если лист новый
            history_worksheet.append_row(["DealID", "CalculationDate", "ClientName", "ClientCompany", "ClientBin", "ClientPhone", "ClientAddress", "ContractNumber", "TotalLogistics", "Kickback"])

    # Генерируем уникальный DealID (можно использовать timestamp или автоинкремент)
    current_time = datetime.datetime.now()
    deal_id = int(current_time.timestamp())  # Уникальный ID на основе времени

    # Сохраняем данные клиента
    client_values = [
        client_data.get('name', ''),
        client_data.get('company', ''),
        client_data.get('bin', ''),
        client_data.get('phone', ''),
        client_data.get('address', ''),
        client_data.get('contract', '')
    ]
    calculations_worksheet.append_row(["DealID"] + client_values + [deal_data.get('total_logistics', 0), deal_data.get('kickback', 0)])

    # Сохраняем продукты
    products_worksheet = sheet.worksheet("Products") if "Products" in [w.title for w in sheet.worksheets()] else sheet.add_worksheet(title="Products", rows="1000", cols="20")
    products_worksheet.clear()
    products_worksheet.append_row(["DealID", "Product", "Unit", "Quantity", "Weight", "PriceSupplier1", "CommentSupplier1", "PriceSupplier2", "CommentSupplier2", "PriceSupplier3", "CommentSupplier3", "PriceSupplier4", "CommentSupplier4", "Markup"])
    for product in products:
        products_worksheet.append_row([
            deal_id,
            product.get('Товар', ''),
            product.get('Ед_измерения', ''),
            product.get('Количество', 0),
            product.get('Вес (кг)', 0),
            product.get('Цена поставщика 1', 0),
            product.get('Комментарий поставщика 1', ''),
            product.get('Цена поставщика 2', 0),
            product.get('Комментарий поставщика 2', ''),
            product.get('Цена поставщика 3', 0),
            product.get('Комментарий поставщика 3', ''),
            product.get('Цена поставщика 4', 0),
            product.get('Комментарий поставщика 4', ''),
            product.get('Наценка (%)', 0)
        ])

    # Сохраняем в историю, если указано
    if save_to_history:
        history_worksheet.append_row([
            deal_id,
            current_time.strftime("%Y-%m-%d %H:%M:%S"),
            client_data.get('name', ''),
            client_data.get('company', ''),
            client_data.get('bin', ''),
            client_data.get('phone', ''),
            client_data.get('address', ''),
            client_data.get('contract', ''),
            deal_data.get('total_logistics', 0),
            deal_data.get('kickback', 0)
        ])

    return deal_id

def load_calculation(spreadsheet_id, deal_id):
    """Загружает расчёт из Google Sheets по DealID."""
    sheet = get_or_create_spreadsheet(spreadsheet_id)

    # Получаем данные клиента из листа "Calculations"
    try:
        calculations_worksheet = sheet.worksheet("Calculations")
        all_calculations = calculations_worksheet.get_all_values()
        header = all_calculations[0]
        for row in all_calculations[1:]:
            if row[0] == str(deal_id):
                client_data = {
                    'name': row[header.index("DealID") + 1] if len(row) > header.index("DealID") + 1 else '',
                    'company': row[header.index("DealID") + 2] if len(row) > header.index("DealID") + 2 else '',
                    'bin': row[header.index("DealID") + 3] if len(row) > header.index("DealID") + 3 else '',
                    'phone': row[header.index("DealID") + 4] if len(row) > header.index("DealID") + 4 else '',
                    'address': row[header.index("DealID") + 5] if len(row) > header.index("DealID") + 5 else '',
                    'contract': row[header.index("DealID") + 6] if len(row) > header.index("DealID") + 6 else ''
                }
                deal_data = {
                    'total_logistics': float(row[header.index("DealID") + 7]) if len(row) > header.index("DealID") + 7 else 0,
                    'kickback': float(row[header.index("DealID") + 8]) if len(row) > header.index("DealID") + 8 else 0
                }
                break
        else:
            return None, None, None  # Расчёт не найден

        # Получаем продукты из листа "Products"
        try:
            products_worksheet = sheet.worksheet("Products")
            all_products = products_worksheet.get_all_values()
            products_header = all_products[0]
            products = []
            for row in all_products[1:]:
                if row[products_header.index("DealID")] == str(deal_id):
                    products.append({
                        "Товар": row[products_header.index("Product")],
                        "Ед_измерения": row[products_header.index("Unit")],
                        "Количество": float(row[products_header.index("Quantity")]),
                        "Вес (кг)": float(row[products_header.index("Weight")]),
                        "Цена поставщика 1": float(row[products_header.index("PriceSupplier1")]),
                        "Комментарий поставщика 1": row[products_header.index("CommentSupplier1")],
                        "Цена поставщика 2": float(row[products_header.index("PriceSupplier2")]),
                        "Комментарий поставщика 2": row[products_header.index("CommentSupplier2")],
                        "Цена поставщика 3": float(row[products_header.index("PriceSupplier3")]),
                        "Комментарий поставщика 3": row[products_header.index("CommentSupplier3")],
                        "Цена поставщика 4": float(row[products_header.index("PriceSupplier4")]),
                        "Комментарий поставщика 4": row[products_header.index("CommentSupplier4")],
                        "Наценка (%)": float(row[products_header.index("Markup")])
                    })
        except gspread.exceptions.WorksheetNotFound:
            products = []

        return (client_data['name'], client_data['company'], client_data['bin'], client_data['phone'], 
                client_data['address'], client_data['contract']), (deal_data['total_logistics'], deal_data['kickback']), products

    except gspread.exceptions.WorksheetNotFound:
        return None, None, None

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
