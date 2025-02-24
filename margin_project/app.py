import streamlit as st
from margin_calculator import run_margin_service
from logistics_calculator import run_logistics_service

# Устанавливаем конфигурацию приложения
st.set_page_config(page_title="Объединённый сервис", layout="wide")

# Восстанавливаем заголовок и вкладки с нормальными отступами
st.markdown("<h1 style='margin-top: 20px; margin-bottom: 20px;'>Объединённый сервис</h1>", unsafe_allow_html=True)

# Создаём вкладки
tab_margin, tab_logistics = st.tabs(["**Калькулятор маржинальности**", "**Калькулятор логистики**"])

with tab_margin:
    # Широкий дизайн для маржинальности
    with st.container():
        st.markdown(
            """
            <style>
            #root > div:nth-child(1) > div > div > div > section > div.block-container {
                max-width: 1200px !important;
                width: 100% !important;
                margin: 0 auto !important;
                padding: 20px !important;
            }
            .stTabs [data-baseweb="tab"] {
                background-color: #f0f0f0 !important;
            }
            .stTabs [data-baseweb="tab"]:hover {
                background-color: #e0e0f0 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        run_margin_service()

with tab_logistics:
    # Компактный дизайн для логистики
    with st.container():
        st.markdown(
            """
            <style>
            #root > div:nth-child(1) > div > div > div > section > div.block-container {
                max-width: 400px !important;
                margin: 0 auto !important;
                padding: 20px !important;
                background-color: #fff !important;
                border-radius: 10px !important;
                box-shadow: 0 0 10px rgba(0,0,0,0.1) !important;
            }
            body {
                background-color: #f8f9fa !important;
            }
            div[data-testid="stNumberInput"] input,
            div[data-testid="stTextInput"] input,
            div[data-testid="stSelectbox"] select {
                border: 1px solid #ccc !important;
                border-radius: 5px !important;
                padding: 8px !important;
                font-size: 14px !important;
                max-width: 100% !important;
            }
            div.stButton > button {
                background-color: #007bff !important;
                color: #fff !important;
                border: none !important;
                border-radius: 5px !important;
                padding: 10px 20px !important;
                font-size: 16px !important;
                cursor: pointer !important;
                transition: background-color 0.3s ease !important;
                max-width: 100% !important;
            }
            div.stButton > button:hover {
                background-color: #0056b3 !important;
            }
            .stTabs {
                margin-top: 20px !important;
            }
            .stTab {
                text-align: center !important;
                padding: 10px !important;
                font-size: 16px !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        run_logistics_service()
