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
        print(f"Получено {len(all_suppliers)} записей из листа 'Suppliers'")  # Отладка
    except Exception as e:
        st.error(f"Ошибка подключения к Google Sheets: {e}")
        print(f"Ошибка подключения: {e}")
        st.stop()

    # Ввод поискового запроса
    search_query = st.text_input("Введите название товара (например, 'труба')", "")

    if search_query:
        # Фильтрация поставщиков по поисковому запросу (ищем в столбце F — "Перечень товаров, которые продаёт поставщик")
        filtered_suppliers = [
            row for row in all_suppliers
            if row and len(row) > 5 and any(search_query.lower().strip() in str(cell).lower().strip() for cell in [row[5]] if cell)  # Столбец F (индекс 5), проверяем, что строка не пустая
        ]

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
                # Форматируем телефон для единообразия (убираем лишние символы, такие как скобки и дефисы)
                if phone and phone != "Не указан":
                    phone = ''.join(filter(str.isdigit, phone))  # Оставляем только цифры
                    if phone.startswith('8'):
                        phone = f"8 {phone[1:4]} {phone[4:7]} {phone[7:9]} {phone[9:11]}"  # Формат: 8 XXX XXX XX XX
                comment = supplier[4].strip() if supplier[4] and supplier[4].strip() else "Не указан"

                print(f"Обработка поставщика: Компания={company}, Город={city}, Сайт={website}, Телефон={phone}, Комментарий={comment}")  # Отладка

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Компания:** {company}")
                    st.write(f"**Город:** {city}")
                with col2:
                    if website and website.startswith(('http://', 'https://')):
                        st.link_button("Сайт", url=website)
                    else:
                        st.write("Сайт: Не указан")
                    st.write(f"**Телефон:** {phone}")
                with col3:
                    st.write(f"**Комментарий:** {comment}")
                st.write("---")
        else:
            st.warning("По вашему запросу поставщики не найдены.")
    else:
        st.info("Введите название товара для поиска.")
