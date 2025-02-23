import streamlit as st
import math
import datetime
import locale

def run_logistics_app():
    try:
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, '')

    st.markdown(
        """
        <style>
        .logistics-container {
            max-width: 400px !important;
            margin: 20px auto !important;
            background-color: #fff !important;
            padding: 20px !important;
            border-radius: 10px !important;
            box-shadow: 0 0 10px rgba(0,0,0,0.1) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("<div class='logistics-container'>", unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; margin-top: 30px;'>Калькулятор логистики</h1>", unsafe_allow_html=True)
    
    # Данные для городских перевозок
    city_data = [
        {"Вид транспорта": "Легковая машина", "Вес груза": 40, "Длинна груза": 2, "Стоимость доставки": "4000-8000"},
        {"Вид транспорта": "Газель", "Вес груза": 300, "Длинна груза": 3, "Стоимость доставки": "4000-12000"},
        {"Вид транспорта": "Длинномер/бортовой", "Вес груза": 1000, "Длинна груза": 12, "Стоимость доставки": "30000-35000"},
        {"Вид транспорта": "Газель Бортовая", "Вес груза": 2000, "Длинна груза": 4, "Стоимость доставки": "10000-20000"},
        {"Вид транспорта": "Бортовой грузовик", "Вес груза": 6000, "Длинна груза": 7, "Стоимость доставки": "20000-30000"},
        {"Вид транспорта": "Фура", "Вес груза": 23000, "Длинна груза": 12, "Стоимость доставки": "50000-60000"}
    ]
    
    intercity_data = {
        "Алматы-Астана": 500000,
        "Алматы-Шымкент": 300000,
        "Алматы-Актау": 1200000,
        "Алматы-Атырау": 800000,
        "Алматы-города1": 1,
        "Алматы-города2": 1,
        "Алматы-города3": 1
    }
    
    delivery_type = st.selectbox("Тип доставки", ["По городу", "Межгород"])
    
    if delivery_type == "По городу":
        weight = st.number_input("Вес (кг)", min_value=0.0, step=0.1, value=0.0)
        length = st.number_input("Длина (м) (опционально)", min_value=0.0, step=0.1, value=0.0)
    
        if st.button("Рассчитать"):
            if weight <= 0:
                st.error("Пожалуйста, введите вес груза!")
            else:
                length_val = None if length <= 0 else length
                suitable_options = [
                    entry for entry in city_data
                    if weight <= entry["Вес груза"] and (length_val is None or length_val <= entry["Длинна груза"])
                ]
                if not suitable_options:
                    st.warning("Нет подходящих вариантов для заданных параметров.")
                else:
                    suitable_options.sort(key=lambda x: int(x["Стоимость доставки"].split('-')[0]))
                    best_option = suitable_options[0]
                    alternative_option = suitable_options[1] if len(suitable_options) > 1 else None
                    
                    st.markdown(
                        f"**Лучший вариант:**<br><b>{best_option['Вид транспорта']}</b> {best_option['Стоимость доставки']} тг",
                        unsafe_allow_html=True
                    )
                    if alternative_option:
                        st.markdown(
                            f"**Альтернативный вариант:**<br><b>{alternative_option['Вид транспорта']}</b> {alternative_option['Стоимость доставки']} тг",
                            unsafe_allow_html=True
                        )
    
    elif delivery_type == "Межгород":
        direction = st.selectbox("Выберите направление", list(intercity_data.keys()))
        weight_tonn = st.number_input("Вес (тонн)", min_value=0.0, step=0.1, value=0.0)
    
        if st.button("Рассчитать"):
            if weight_tonn <= 0:
                st.error("Пожалуйста, введите вес груза!")
            else:
                tariff = intercity_data[direction]
                capacity = 20
                coef = 2
                cost = (tariff / capacity) * weight_tonn * coef
                st.success(f"Стоимость перевозки: **{round(cost)} тг**")
    
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == '__main__':
    run_logistics_app()
