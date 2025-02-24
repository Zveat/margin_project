import streamlit as st
import math

def run_logistics_service():
    # Данные для городских перевозок
    city_data = [
        {"Вид транспорта": "Легковая машина", "Вес груза": 40, "Длинна груза": 2, "Стоимость доставки": "4000-8000"},
        {"Вид транспорта": "Газель", "Вес груза": 300, "Длинна груза": 3, "Стоимость доставки": "4000-12000"},
        {"Вид транспорта": "Длинномер/бортовой", "Вес груза": 1000, "Длинна груза": 12, "Стоимость доставки": "30000-35000"},
        {"Вид транспорта": "Газель Бортовая", "Вес груза": 2000, "Длинна груза": 4, "Стоимость доставки": "10000-20000"},
        {"Вид транспорта": "Бортовой грузовик", "Вес груза": 6000, "Длинна груза": 7, "Стоимость доставки": "20000-30000"},
        {"Вид транспорта": "Фура", "Вес груза": 23000, "Длинна груза": 12, "Стоимость доставки": "50000-60000"}
    ]

    # Данные для междугородних перевозок
    intercity_data = {
        "Алматы-Астана": 500000,
        "Алматы-Шымкент": 300000,
        "Алматы-Aктау": 1200000,
        "Алматы-Атыраu": 800000,
        "Алматы-города1": 1,
        "Алматы-города2": 1,
        "Алматы-города3": 1
    }

    st.title("Калькулятор логистики")
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
                        f"**Лучший вариант:**<br>**{best_option['Вид транспорта']}** {best_option['Стоимость доставки']} тг",
                        unsafe_allow_html=True
                    )
                    if alternative_option:
                        st.markdown(
                            f"**Альтернативный вариант:**<br>**{alternative_option['Вид транспорта']}** {alternative_option['Стоимость доставки']} тг",
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
                capacity = 20  # Допустим, фура может перевозить до 20 тонн
                coef = 2       # Коэффициент догруза
                cost = (tariff / capacity) * weight_tonn * coef
                st.success(f"Стоимость перевозки: **{round(cost)} тг**")
