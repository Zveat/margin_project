# supplier_search.py

from google_sheets_db import connect_to_sheets
import streamlit as st

def run_supplier_search():
    """
    Функция для поиска поставщиков, которая возвращает интерфейс Streamlit для отображения.
    """
    st.subheader("🔍 Поиск поставщиков")

    # CSS для стилизации (аналогичный вашему текущему стилю)
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
    except Exception as e:
        st.error(f"Ошибка подключения к Google Sheets: {e}")
        st.stop()

    # Ввод поискового запроса
    search_query = st.text_input("Введите название товара (например, 'труба')", "")

    if search_query:
        # Фильтрация поставщиков по поисковому запросу (ищем в столбце F — "Перечень товаров, которые продаёт поставщик")
        filtered_suppliers = [
            row for row in all_suppliers
            if any(search_query.lower() in str(cell).lower() for cell in row[5:])  # Столбец F (индекс 5)
        ]

        if filtered_suppliers:
            st.write(f"Найдено {len(filtered_suppliers)} подходящих поставщиков:")
            for supplier in filtered_suppliers:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Компания:** {supplier[0]}")  # Название компании (столбец A)
                    st.write(f"**Город:** {supplier[1]}")  # Город (столбец B)
                with col2:
                    if supplier[2]:  # Ссылка на сайт (столбец C)
                        st.link_button("Сайт", url=supplier[2])
                    else:
                        st.write("Сайт: Не указан")
                    st.write(f"**Телефон:** {supplier[3]}")  # Телефон (столбец D)
                with col3:
                    st.write(f"**Комментарий:** {supplier[4]}")  # Комментарий (столбец E)
                st.write("---")
        else:
            st.warning("По вашему запросу поставщики не найдены.")
    else:
        st.info("Введите название товара для поиска.")
