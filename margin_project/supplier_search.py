from google_sheets_db import connect_to_sheets
import streamlit as st
import time
import datetime

@st.cache_data(ttl=6000)  # Автоматическое обновление кэша каждые 6000 секунд, 1.6 час
def load_suppliers():
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
        return all_suppliers
    except Exception as e:
        st.error(f"Ошибка подключения к Google Sheets: {e}")
        print(f"Ошибка подключения: {e}")
        return []

def run_supplier_search():
    """
    Функция для поиска поставщиков, которая возвращает интерфейс Streamlit для отображения.
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
        div.stButton > button {
             background-color: #656dff;
             color: #FFFFFF;
             border: none;
             border-radius: 4px;
             padding: 2px 8px;
             font-size: 6px;
             cursor: pointer;
             transition: background-color 0.3s ease;
        }
        div.stButton > button:hover {
             background-color: #94db00;
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
            white-space: pre-wrap; /* Сохраняет переносы строк */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Загрузка данных из Google Sheets
    all_suppliers = load_suppliers()

    # Ввод поискового запроса
    search_query = st.text_input(label="Поиск товара", placeholder="например: труба", key="search_input")

    if search_query:
        # Фильтрация поставщиков по поисковому запросу (ищем в столбце F — "Перечень товаров")
        start_time = time.time()
        filtered_suppliers = [
            row for row in all_suppliers
            if row and len(row) > 5 and any(search_query.lower().strip() in str(cell).lower().strip() for cell in [row[5]] if cell)  # Столбец F (индекс 5)
        ]
        filter_time = time.time() - start_time
        print(f"Фильтрация заняла {filter_time:.2f} секунд")
        print(f"Найдено {len(filtered_suppliers)} поставщиков по запросу: {search_query}")
        print(f"Пример первой строки после фильтрации: {filtered_suppliers[0] if filtered_suppliers else 'Нет данных'}")

        if filtered_suppliers:
            st.write(f"Найдено {len(filtered_suppliers)} подходящих поставщиков:")
            start_time = time.time()
            for supplier in filtered_suppliers:
                # Проверка и форматирование данных для каждого поставщика
                company = supplier[0].strip() if supplier[0] and supplier[0].strip() else "Не указано"
                city = supplier[1].strip() if supplier[1] and supplier[1].strip() else "Не указан"
                website = supplier[2].strip() if supplier[2] and supplier[2].strip() else None
                phone = supplier[3].strip() if supplier[3] and supplier[3].strip() else "Не указан"
                comment = supplier[4].strip() if supplier[4] and supplier[4].strip() else "Не указан"
                price_info = supplier[6].strip() if len(supplier) > 6 and supplier[6] else "Не указано"  # Столбец G (индекс 6)

                print(f"Обработка поставщика: {company}, {city}, {website}, {phone}, {comment}, Прайс: {price_info}")

                # HTML-карточка для аккуратного отображения поставщика
                st.markdown(
                    f"""
                    <div class="supplier-card">
                        <p><strong>Компания:</strong> {company}</p>
                        <p><strong>Город:</strong> {city}</p>
                        <p><strong>Сайт:</strong> {'Не указан' if not website else f'<a href="{website}" target="_blank">Посетить сайт</a>'}</p>
                        <p><strong>Прайс на сайте:</strong> {price_info}</p>
                        <p><strong>Телефон:</strong> {phone}</p>
                        <p><strong>Комментарий:</strong> {comment}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            render_time = time.time() - start_time
            print(f"Рендеринг занял {render_time:.2f} секунд")
        else:
            st.warning("По вашему запросу поставщики не найдены.")
    else:
        st.info("Введите название товара для поиска.")

    # Добавляем кнопку ручного обновления (опционально)
    if st.button("🔄 Обновить данные"):
        st.cache_data.clear()  # Очищаем кэш вручную
        st.rerun()

if __name__ == "__main__":
    run_supplier_search()
