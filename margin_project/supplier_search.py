# supplier_search.py

from google_sheets_db import connect_to_sheets
import streamlit as st
import time

def run_supplier_search():
    """
    Функция для поиска поставщиков с использованием столбца G (наличие прайс-листа).
    """
    st.subheader("🔍 Введите название товара")

    # CSS для стилизации
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 750px !important;
            margin-left: 20px !important;
            background-color: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        body {
            background-color: #f1c40f;
        }
        div[data-testid="stTextInput"] input {
            border: 1px solid #ccc !important;
            border-radius: 5px !important;
            padding: 8px !important;
            font-size: 14px !important;
        }
        .supplier-card {
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .supplier-card p {
            margin: 0 0 5px 0;
            font-size: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Подключение к Google Sheets
    start_time = time.time()
    conn = connect_to_sheets()
    print(f"Подключение к Google Sheets заняло {time.time() - start_time:.2f} секунд")
    try:
        start_time = time.time()
        sheet = conn.open_by_key("1Z4-Moti7RVqyBQY5v4tcCwFQS3noOD84w9Q2liv9rI4")
        print(f"Открытие таблицы заняло {time.time() - start_time:.2f} секунд")
        
        start_time = time.time()
        suppliers_sheet = sheet.worksheet("Suppliers")
        print(f"Доступ к листу 'Suppliers' занял {time.time() - start_time:.2f} секунд")
        
        start_time = time.time()
        all_suppliers = suppliers_sheet.get_all_values()[1:]  # Пропускаем заголовок
        load_time = time.time() - start_time
        print(f"Загрузка данных заняла {load_time:.2f} секунд")
        print(f"Всего записей из листа 'Suppliers': {len(all_suppliers)}")
    except Exception as e:
        st.error(f"Ошибка подключения к Google Sheets: {e}")
        print(f"Ошибка подключения: {e}")
        st.stop()

    # Ввод поискового запроса
    search_query = st.text_input(label="Поиск товара", placeholder="например: труба", key="search_input")

    if search_query:
        # Фильтрация поставщиков по поисковому запросу
        start_time = time.time()
        filtered_suppliers = []
        for row in all_suppliers:
            if not row or len(row) < 7:  # Проверяем наличие минимум 7 столбцов (G включен)
                print(f"Пропущена строка с недостаточным количеством столбцов: {row}")
                continue
            products = row[5].strip() if row[5] else ""
            if search_query.lower().strip() in products.lower().strip():
                filtered_suppliers.append(row)
        filter_time = time.time() - start_time
        print(f"Фильтрация заняла {filter_time:.2f} секунд")
        print(f"Найдено {len(filtered_suppliers)} поставщиков по запросу: {search_query}")
        print(f"Пример первой строки после фильтрации: {filtered_suppliers[0] if filtered_suppliers else 'Нет данных'}")

        if filtered_suppliers:
            st.write(f"Найдено {len(filtered_suppliers)} подходящих поставщиков:")
            start_time = time.time()
            cards_html = ""
            for supplier in filtered_suppliers:
                company = supplier[0].strip() if supplier[0] else "Не указано"
                city = supplier[1].strip() if supplier[1] else "Не указан"
                website = supplier[2].strip() if supplier[2] else None
                phone = supplier[3].strip() if supplier[3] else "Не указан"
                comment = supplier[4].strip() if supplier[4] else "Не указан"
                # Обработка столбца G (наличие прайс-листа)
                has_price_list = supplier[6].strip() if len(supplier) > 6 and supplier[6] else "Не указано"
                if "✅" in has_price_list:
                    has_price_list = "Да"
                elif "❌" in has_price_list:
                    has_price_list = "Нет"

                print(f"Обработка поставщика: {company}, {city}, {website}, {phone}, {comment}, Прайс: {has_price_list}")
                cards_html += f"""
                    <div class="supplier-card">
                        <p><strong>Компания:</strong> {company}</p>
                        <p><strong>Город:</strong> {city}</p>
                        <p><strong>Сайт:</strong> {'Не указан' if not website else f'<a href="{website}" target="_blank">Посетить сайт</a>'}</p>
                        <p><strong>Телефон:</strong> {phone}</p>
                        <p><strong>Комментарий:</strong> {comment}</p>
                        <p><strong>Прайс на сайте:</strong> {has_price_list}</p>
                    </div>
                """
            st.markdown(cards_html, unsafe_allow_html=True)
            render_time = time.time() - start_time
            print(f"Рендеринг занял {render_time:.2f} секунд")
        else:
            st.warning("По вашему запросу поставщики не найдены.")
    else:
        st.info("Введите название товара для поиска.")

if __name__ == "__main__":
    run_supplier_search()
