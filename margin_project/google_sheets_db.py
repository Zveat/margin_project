# google_sheets_db.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

def connect_to_sheets():
    """Устанавливает соединение с Google Sheets с помощью сервисного аккаунта."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(credentials)
    return client

def save_calculation(spreadsheet_id, client_data, deal_data, products, include_products=False):
    """Сохраняет данные расчёта в Google Sheets: клиента, сделку и (опционально) товары."""
    conn = connect_to_sheets()
    sheet = conn.open_by_key(spreadsheet_id)

    # Сохраняем в лист "History"
    history_sheet = sheet.worksheet("History")
    # Генерируем следующий deal_id (увеличиваем максимальный существующий)
    existing_deals = [int(row[0]) for row in history_sheet.get_all_values()[1:] if row and row[0].isdigit()]
    deal_id = max(existing_deals) + 1 if existing_deals else 1

    # Сохраняем данные клиента и сделки в History
    history_sheet.append_row([
        str(deal_id),
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # CalculationDate
        client_data['name'],  # client_name
        client_data['company'],  # client_company
        client_data['bin'],  # client_bin
        client_data['phone'],  # client_phone
        client_data['address'],  # client_address
        client_data['contract'],  # client_contract
        str(deal_data['total_logistics']),  # total_logistics
        str(deal_data['kickback']),  # kickback
    ])

    if include_products:
        # Сохраняем товары в лист "Products"
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

    # Опционально: сохраняем данные клиента в лист "Clients" (если нужно)
    clients_sheet = sheet.worksheet("Clients")
    # Проверяем, существует ли клиент с таким client_id или добавляем нового
    client_id = f"client_{deal_id}"  # Уникальный client_id на основе deal_id
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

    # Опционально: сохраняем данные сделки в лист "Deals" (если нужно)
    deals_sheet = sheet.worksheet("Deals")
    deals_sheet.append_row([
        str(deal_id),
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # CalculationDate
        client_data['name'],  # client_name
        client_data['company'],  # client_company
        client_data['bin'],  # client_bin
        client_data['phone'],  # client_phone
        client_data['address'],  # client_address
        str(deal_data['total_logistics']),  # total_logistics
        str(deal_data['kickback']),  # kickback
    ])

    return deal_id

def load_calculation(spreadsheet_id, deal_id):
    """Загружает данные расчёта из Google Sheets по deal_id."""
    conn = connect_to_sheets()
    sheet = conn.open_by_key(spreadsheet_id)
    history_sheet = sheet.worksheet("History")
    products_sheet = sheet.worksheet("Products")

    # Ищем данные в History по deal_id (столбец A)
    history_data = history_sheet.get_all_values()
    for row in history_data[1:]:  # Пропускаем заголовок
        if row[0] == str(deal_id):
            client_name = row[2]  # client_name (столбец C)
            client_company = row[3]  # client_company (столбец D)
            client_bin = row[4]  # client_bin (столбец E)
            client_phone = row[5]  # client_phone (столбец F)
            client_address = row[6]  # client_address (столбец G)
            client_contract = row[7]  # client_contract (столбец H)
            total_logistics = float(row[8]) if row[8] else 0  # total_logistics (столбец I)
            kickback = float(row[9]) if row[9] else 0  # kickback (столбец J)

            # Загружаем продукты для этого deal_id
            products = []
            for product_row in products_sheet.get_all_values()[1:]:  # Пропускаем заголовок
                if product_row[1] == str(deal_id):  # deal_id в столбце B
                    products.append({
                        "Товар": product_row[2],  # ProductName (столбец C)
                        "Ед_измерения": product_row[3],  # Unit (столбец D)
                        "Количество": int(product_row[4]),  # Quantity (столбец E)
                        "Вес (кг)": int(product_row[5]),  # Weight (столбец F)
                        "Цена поставщика 1": float(product_row[6]) if product_row[6] else 0,  # PriceSupplier1 (столбец G)
                        "Комментарий поставщика 1": product_row[7],  # CommentSupplier1 (столбец H)
                        "Цена поставщика 2": float(product_row[8]) if product_row[8] else 0,  # PriceSupplier2 (столбец I)
                        "Комментарий поставщика 2": product_row[9],  # CommentSupplier2 (столбец J)
                        "Цена поставщика 3": float(product_row[10]) if product_row[10] else 0,  # PriceSupplier3 (столбец K)
                        "Комментарий поставщика 3": product_row[11],  # CommentSupplier3 (столбец L)
                        "Цена поставщика 4": float(product_row[12]) if product_row[12] else 0,  # PriceSupplier4 (столбец M)
                        "Комментарий поставщика 4": product_row[13],  # CommentSupplier4 (столбец N)
                        "Наценка (%)": float(product_row[14]) if product_row[14] else 0,  # Markup (столбец O)
                    })
            return (
                (client_name, client_company, client_bin, client_phone, client_address, client_contract),
                (total_logistics, kickback),
                products
            )
    return None, None, None
