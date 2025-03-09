# supplier_search.py

from google_sheets_db import connect_to_sheets
import streamlit as st
import time

# Кэширование данных из Google Sheets
@st.cache_data
def load_suppliers():
    start_time = time.time()
    conn = connect_to_sheets()
    sheet = conn.open_by_key("1Z4-Moti7RVqyBQY5v4tcCwFQS3noOD84w9Q2liv9rI4")
    suppliers_sheet = sheet.worksheet("Suppliers")
    all_suppliers = suppliers_sheet.get_all_values()[1:]
    load_time = time.time() - start_time
    print(f"Загрузка данных заняла {load_time:.2f} секунд")
    return all_suppliers

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

    # Загрузка данных
    try:
        start_time = time.time()
        all_suppliers = load_suppliers()
        load_duration = time.time() - start_time
        st.write(f"Получено {len(all_suppliers)} записей из листа 'Suppliers' за {load_duration:.2f} секунд")
    except Exception as e:
        st.error(f"Ошибка подключения к Google Sheets: {e}")
        st.stop()

    # Ввод поискового запроса
    search_query = st.text_input(
        label="Поиск товара",  # Явный label для устранения предупреждений
        placeholder="например: труба",
        key="search_input"  # Уникальный ключ для избежания конфликтов
    )

    if search_query:
        # Фильтрация поставщиков
        start_time = time.time()
        filtered_suppliers = [
            row for row in all_suppliers
            if row and len(row) >= 6 and search_query.lower().strip() in (row[5].strip().lower() if row[5] else "")
        ]
        filter_duration = time.time() - start_time
        print(f"Фильтрация заняла {filter_duration:.2f} секунд")

        if filtered_suppliers:
            st.write(f"Найдено {len(filtered_suppliers)} подходящих поставщиков:")
            start_time = time.time()
            # Рендеринг карточек
            cards_html = ""
            for supplier in filtered_suppliers:
                company = supplier[0].strip() if supplier[0] and supplier[0].strip() else "Не указано"
                city = supplier[1].strip() if supplier[1] and supplier[1].strip() else "Не указан"
                website = supplier[2].strip() if supplier[2] and supplier[2].strip() else None
                phone = supplier[3].strip() if supplier[3] and supplier[3].strip() else "Не указан"
                comment = supplier[4].strip() if supplier[4] and supplier[4].strip() else "Не указан"
                has_price_list = supplier[6].strip() if len(supplier) > 6 and supplier[6] and supplier[6].strip() else "Не указано"

                cards_html += f"""
                    <div class="supplier-card">
                        <p><strong>Компания:</strong> {company}</p>
                        <p><strong>Город:</strong> {city}</p>
                        <p><strong>Сайт:</strong> {'Не указан' if not website else f'<a href="{website}" target="_blank">Посетить сайт</a>'}</p>
                        <p><strong>Есть прайс на сайте:</strong> {has_price_list}</p>
                        <p><strong>Телефон:</strong> {phone}</p>
                        <p><strong>Комментарий:</strong> {comment}</p>
                    </div>
                """
            st.markdown(cards_html, unsafe_allow_html=True)
            render_duration = time.time() - start_time
            print(f"Рендеринг занял {render_duration:.2f} секунд")
        else:
            st.warning("По вашему запросу поставщики не найдены.")
    else:
        st.info("Введите название товара для поиска.")

if __name__ == "__main__":
    run_supplier_search()
