# supplier_search.py

from google_sheets_db import connect_to_sheets
import streamlit as st

def run_supplier_search():
    """
    Функция для поиска поставщиков, которая возвращает интерфейс Streamlit для отображения.
    """
    st.subheader("🔍 Введите название товара")

    # CSS для стилизации (обновленный современный дизайн)
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 900px !important;
            margin: 0 auto !important;
            background-color: #ffffff;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        body {
            background-color: #f4d03f; /* Мягкий желтый фон */
        }
        div[data-testid="stTextInput"] input {
            border: 2px solid #e0e0e0 !important;
            border-radius: 8px !important;
            padding: 10px !important;
            font-size: 16px !important;
            transition: border-color 0.3s ease;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: #1a73e8 !important;
            box-shadow: 0 0 5px rgba(26, 115, 232, 0.2);
        }
        .supplier-card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .supplier-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        }
        .supplier-card p {
            margin: 0 0 8px 0;
            font-size: 15px;
            color: #333333;
        }
        .supplier-card p strong {
            color: #1a73e8; /* Синий цвет для заголовков */
            font-weight: 600;
        }
        .supplier-card a {
            color: #1a73e8;
            text-decoration: none;
            font-weight: 500;
        }
        .supplier-card a:hover {
            text-decoration: underline;
            color: #155ab5;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Подключение к Google Sheets
    conn = connect_to_sheets()
    try:
        sheet = conn.open_by_key("1Z4-Moti7RVqyBQY5v4tcCwFQS3noOD84w9Q2liv9rI4")  # Замените на ID вашей таблицы
        suppliers_sheet = sheet.worksheet("Suppliers")  # Название листа с данными поставщиков
        all_suppliers = suppliers_sheet.get_all_values()[1:]  # Пропускаем заголовок
        print(f"Получено {len(all_suppliers)} записей из листа 'Suppliers'")  # Отладка
    except Exception as e:
        st.error(f"Ошибка подключения к Google Sheets: {e}")
        print(f"Ошибка подключения: {e}")
        st.stop()

    # Ввод поискового запроса
    search_query = st.text_input("например: труба")

    if search_query:
        # Фильтрация поставщиков по поисковому запросу (ищем в столбце F — "Перечень товаров, которые продаёт поставщик")
        filtered_suppliers = []
        for row in all_suppliers:
            # Пропускаем пустые строки
            if not row or len(row) < 6:  # Убедимся, что есть хотя бы 6 столбцов (до F)
                print(f"Пропущена строка с недостаточным количеством столбцов: {row}")  # Отладка
                continue
            # Проверяем, что столбец F (индекс 5) существует и содержит данные
            products = row[5].strip() if row[5] else ""
            if search_query.lower().strip() in products.lower().strip():
                filtered_suppliers.append(row)
            else:
                print(f"Строка не прошла фильтрацию: {row}")  # Отладка

        print(f"Найдено {len(filtered_suppliers)} поставщиков по запросу: {search_query}")  # Отладка
        print(f"Пример первой строки после фильтрации: {filtered_suppliers[0] if filtered_suppliers else 'Нет данных'}")  # Отладка

        if filtered_suppliers:
            st.write(f"Найдено {len(filtered_suppliers)} подходящих поставщиков:")
            for supplier in filtered_suppliers:
                # Проверка и форматирование данных для каждого поставщика
                company = supplier[0].strip() if supplier[0] and supplier[0].strip() else "Не указано"
                city = supplier[1].strip() if supplier[1] and supplier[1].strip() else "Не указан"
                website = supplier[2].strip() if supplier[2] and supplier[2].strip() else None
                phone = supplier[3].strip() if supplier[3] and supplier[3].strip() else "Не указан"
                comment = supplier[4].strip() if supplier[4] and supplier[4].strip() else "Не указан"
                # Обработка столбца G (Есть прайс на сайте)
                has_price_list = supplier[6].strip() if len(supplier) > 6 and supplier[6] and supplier[6].strip() else "Не указано"

                print(f"Обработка поставщика: Компания={company}, Город={city}, Сайт={website}, Телефон={phone}, Комментарий={comment}, Есть прайс на сайте={has_price_list}")  # Отладка

                # HTML-карточка для аккуратного отображения поставщика
                st.markdown(
                    f"""
                    <div class="supplier-card">
                        <p><strong>Компания:</strong> {company}</p>
                        <p><strong>Город:</strong> {city}</p>
                        <p><strong>Сайт:</strong> {'Не указан' if not website else f'<a href="{website}" target="_blank">Посетить сайт</a>'}</p>
                        <p><strong>Есть прайс на сайте:</strong> {has_price_list}</p>
                        <p><strong>Телефон:</strong> {phone}</p>
                        <p><strong>Комментарий:</strong> {comment}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.warning("По вашему запросу поставщики не найдены.")
    else:
        st.info("Введите название товара для поиска.")
