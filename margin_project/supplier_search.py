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
    # Заголовок
    st.markdown('<h3 style="text-align: center; color: #1a535c;">🔍 Введите название товара</h3>', unsafe_allow_html=True)

    # Добавляем стили CSS для улучшенного дизайна
    st.markdown(
        """
        <style>
        /* Общий стиль контейнера */
        .supplier-search-container {
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            max-width: 800px;
            margin: 0 auto;
        }
        /* Стили для поля ввода */
        .search-input-container {
            position: relative;
            margin-bottom: 20px;
        }
        .search-input-container input {
            width: 100% !important;
            padding: 12px 40px 12px 20px !important;
            font-size: 16px !important;
            border: 2px solid #1a535c !important;
            border-radius: 25px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
            transition: border-color 0.3s ease;
        }
        .search-input-container input:focus {
            border-color: #656dff !important;
            outline: none !important;
        }
        /* Иконка лупы в поле ввода */
        .search-icon {
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 20px;
            color: #1a535c;
        }
        /* Стили для карточек поставщиков */
        .supplier-card {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 5px solid #1a535c;
            transition: transform 0.2s ease;
        }
        .supplier-card:hover {
            transform: translateY(-2px);
        }
        .company-name {
            font-size: 18px;
            font-weight: bold;
            color: #1a535c;
            margin-bottom: 5px;
        }
        .supplier-info {
            font-size: 16px;
            color: #333;
            margin: 3px 0;
        }
        .price-info {
            font-size: 14px;
            color: #2e7d32; /* Зелёный для цен */
            font-weight: bold;
            margin: 3px 0;
        }
        .comment-info {
            font-size: 14px;
            color: #666;
            font-style: italic;
            margin: 3px 0;
        }
        /* Стили для кнопки сайта (изменённые) */
        .website-btn {
            background-color: #E0FFFF; /* Бледно-синий, менее яркий */
            color: #1a535c; /* Тёмно-синий текст */
            border: 1px solid #b0c4de; /* Нейтральная граница */
            border-radius: 4px;
            padding: 3px 8px; /* Уменьшенный размер */
            font-size: 12px;
            cursor: pointer;
            text-decoration: none;
            transition: background-color 0.3s ease;
        }
        .website-btn:hover {
            background-color: #c0d0ff; /* Ещё более мягкий оттенок при наведении */
        }
        /* Адаптивность */
        @media (max-width: 600px) {
            .supplier-search-container {
                padding: 15px;
            }
            .search-input-container input {
                padding: 10px 35px 10px 15px !important;
                font-size: 14px !important;
            }
            .search-icon {
                font-size: 18px;
                right: 10px;
            }
            .company-name {
                font-size: 16px;
            }
            .supplier-info, .price-info, .comment-info {
                font-size: 12px;
            }
            .website-btn {
                padding: 2px 6px; /* Ещё меньше на мобильных */
                font-size: 10px;
            }
        }
        /* Стили для кнопки обновления */
        div.stButton > button {
            background-color: #656dff;
            color: #FFFFFF;
            border: none;
            border-radius: 4px;
            padding: 8px 15px;
            font-size: 14px;
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

    # Контейнер для поиска
    st.markdown('<div class="supplier-search-container">', unsafe_allow_html=True)

    # Поле ввода с иконкой лупы
    st.markdown('<div class="search-input-container">', unsafe_allow_html=True)
    search_query = st.text_input(
        "",
        placeholder="Например: труба",
        key="search_input",
        label_visibility="collapsed"
    )
    st.markdown('<span class="search-icon">🔍</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Загрузка данных из Google Sheets
    all_suppliers = load_suppliers()

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
            st.markdown(f'<p style="color: #1a535c; font-weight: bold;">Найдено {len(filtered_suppliers)} поставщиков:</p>', unsafe_allow_html=True)
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

                # HTML-карточка для аккуратного отображения поставщика с исправленной кнопкой
                st.markdown(
                    f"""
                    <div class="supplier-card">
                        <div class="company-name">{company}</div>
                        <div class="supplier-info"><strong>🏙 Города:</strong> {city}</div>
                        <div class="supplier-info"><strong>🌐 Сайт:</strong> {'Не указан' if not website else f'<a href="{website}" target="_blank"><button class="website-btn">Перейти на сайт</button></a>'}</div>
                        <div class="supplier-info"><strong>💰 Прайс на сайте:</strong> {price_info}</div>
                        <div class="supplier-info"><strong>📞 Телефон:</strong> {phone}</div>
                        <div class="comment-info"><strong>💬 Комментарий:</strong> {comment}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            render_time = time.time() - start_time
            print(f"Рендеринг занял {render_time:.2f} секунд")
        else:
            st.markdown('<p style="text-align: center; color: #d32f2f;">Поставщики не найдены.</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="text-align: center; color: #666;">Начните поиск, введя название товара.</p>', unsafe_allow_html=True)

    # Добавляем кнопку ручного обновления
    if st.button("🔄 Обновить данные"):
        st.cache_data.clear()  # Очищаем кэш вручную
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    run_supplier_search()
