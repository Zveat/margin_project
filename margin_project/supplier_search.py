import streamlit as st

def run_supplier_search():
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
            font-size: 14px;
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
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Заголовок
    st.markdown('<h3 style="text-align: center; color: #1a535c;">🔍 Поиск поставщиков</h3>', unsafe_allow_html=True)

    # Контейнер для поиска
    st.markdown('<div class="supplier-search-container">', unsafe_allow_html=True)

    # Поле ввода с иконкой лупы
    st.markdown('<div class="search-input-container">', unsafe_allow_html=True)
    search_query = st.text_input(
        "",
        placeholder="Введите название товара (например, труба)",
        key="supplier_search_input",
        label_visibility="collapsed"
    )
    st.markdown('<span class="search-icon">🔍</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Данные о поставщиках (пример, замените на ваши реальные данные)
    suppliers_data = [
        {
            "company": "ТОО КазТемирКонтакт",
            "cities": "Алматы, Астана, Актобе, Актау, Атырау, Уральск",
            "website": "ДОСТУПТЬ САЙТ",
            "price": "Есть на сайте",
            "phones": ["8 707 722 7315", "8 (701) 722 73 15", "8 (777) 599 45 80"],
            "comment": "Не указано"
        },
        {
            "company": "ТОО Стальтрейд",
            "cities": "Алматы, Астана, Актау, Шымкент, Павлодар",
            "website": "ДОСТУПТЬ САЙТ",
            "price": "Есть на сайте",
            "phones": [],
            "comment": "Не указано"
        }
    ]

    # Фильтрация поставщиков на основе поискового запроса
    if search_query:
        filtered_suppliers = [
            supplier for supplier in suppliers_data
            if search_query.lower() in supplier["company"].lower() or search_query.lower() in "труба"
        ]
    else:
        filtered_suppliers = suppliers_data

    # Отображение результатов поиска
    if not search_query:
        st.markdown('<p style="text-align: center; color: #666;">Начните поиск, чтобы увидеть поставщиков.</p>', unsafe_allow_html=True)
    elif not filtered_suppliers:
        st.markdown('<p style="text-align: center; color: #d32f2f;">Поставщики не найдены.</p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<p style="color: #1a535c; font-weight: bold;">Найдено {len(filtered_suppliers)} поставщиков:</p>', unsafe_allow_html=True)
        for supplier in filtered_suppliers:
            # Формируем карточку поставщика
            phones_str = ", ".join(supplier["phones"]) if supplier["phones"] else "Не указаны"
            st.markdown(
                f"""
                <div class="supplier-card">
                    <div class="company-name">{supplier["company"]}</div>
                    <div class="supplier-info">🏙 Города: {supplier["cities"]}</div>
                    <div class="supplier-info">🌐 Сайт: <a href="{supplier["website"]}" target="_blank">{supplier["website"]}</a></div>
                    <div class="price-info">💰 Цены на сайте: {supplier["price"]}</div>
                    <div class="supplier-info">📞 Телефоны: {phones_str}</div>
                    <div class="comment-info">💬 Комментарий: {supplier["comment"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown('</div>', unsafe_allow_html=True)
