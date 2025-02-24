import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import os
import math
import datetime
import locale

from fpdf import FPDF
from num2words import num2words

# 1) Настраиваем страницу (width - на ваш вкус)
st.set_page_config(layout="wide")

# 2) ВНОСИМ ЕДИНЫЙ СТИЛЬ ДЛЯ ВСЕГО ПРИЛОЖЕНИЯ
common_style = """
<style>
/* Фон страницы */
body {
    background-color: #f8f9fa;
}

/* Общий контейнер Streamlit */
.block-container {
    max-width: 700px !important; /* Можно поставить 600, 800 или 400, как в логистике */
    margin-left: 20px !important; /* Отступ слева */
    background-color: #fff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}

/* Пример: чуток поправить параграфы */
.block-container p {
    margin: 0.3rem 0 0.2rem 0 !important;
    font-size: 16px !important;
    line-height: 1.2 !important;
}

/* Поля ввода */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] select {
    border: 1px solid #ccc !important;
    border-radius: 5px !important;
    padding: 8px !important;
    font-size: 14px !important;
}

/* Кнопки */
div.stButton > button {
    background-color: #007bff;
    color: #fff;
    border: none;
    border-radius: 5px;
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}
div.stButton > button:hover {
    background-color: #0056b3;
}
</style>
"""

st.markdown(common_style, unsafe_allow_html=True)

# Заголовок приложения (по желанию)
st.title("Сервис расчета логистики и маржинальности")

# Устанавливаем локаль для вывода даты на русском языке
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, '')


###############################################################################
#                         БЛОК 1: КОД ЛОГИСТИЧЕСКОГО КАЛЬКУЛЯТОРА
###############################################################################
def run_logistics_service():
    st.markdown("<h2 style='margin-top: 30px;'>Калькулятор логистики</h2>", unsafe_allow_html=True)

    # Все стили мы уже внесли в общий блок выше — здесь ничего не вставляем повторно

    # Данные для городских перевозок
    city_data = [
        {"Вид транспорта": "Легковая машина",    "Вес груза": 40,   "Длинна груза": 2,  "Стоимость доставки": "4000-8000"},
        {"Вид транспорта": "Газель",             "Вес груза": 300,  "Длинна груза": 3,  "Стоимость доставки": "4000-12000"},
        {"Вид транспорта": "Длинномер/бортовой", "Вес груза": 1000, "Длинна груза": 12, "Стоимость доставки": "30000-35000"},
        {"Вид транспорта": "Газель Бортовая",    "Вес груза": 2000, "Длинна груза": 4,  "Стоимость доставки": "10000-20000"},
        {"Вид транспорта": "Бортовой грузовик",  "Вес груза": 6000, "Длинна груза": 7,  "Стоимость доставки": "20000-30000"},
        {"Вид транспорта": "Фура",               "Вес груза": 23000,"Длинна груза": 12, "Стоимость доставки": "50000-60000"}
    ]

    # Данные для междугородних перевозок
    intercity_data = {
        "Алматы-Астана": 500000,
        "Алматы-Шымкент": 300000,
        "Алматы-Актау": 1200000,
        "Алматы-Атырау": 800000,
        "Алматы-города1": 1,
        "Алматы-города2": 1,
        "Алматы-города3": 1
    }

    # Выбор типа доставки
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
                        f"**Лучший вариант:**<br>**{best_option['Вид транспорта']}** "
                        f"{best_option['Стоимость доставки']} тг",
                        unsafe_allow_html=True
                    )
                    if alternative_option:
                        st.markdown(
                            f"**Альтернативный вариант:**<br>**{alternative_option['Вид транспорта']}** "
                            f"{alternative_option['Стоимость доставки']} тг",
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


###############################################################################
#                 БЛОК 2: КОД КАЛЬКУЛЯТОРА МАРЖИНАЛЬНОСТИ (Основной сервис)
###############################################################################
def get_line_count(pdf, width, text):
    lines = text.split("\n")
    count = 0
    for line in lines:
        if not line:
            count += 1
        else:
            count += math.ceil(pdf.get_string_width(line) / width)
    return count

def format_date_russian(date_obj):
    months = {
        "January": "Января", "February": "Февраля", "March": "Марта",
        "April": "Апреля",  "May": "Мая",      "June": "Июня",
        "July": "Июля",     "August": "Августа","September": "Сентября",
        "October": "Октября","November": "Ноября","December": "Декабря"
    }
    formatted = date_obj.strftime("%d %B %Y г.")
    for eng, rus in months.items():
        formatted = formatted.replace(eng, rus)
    return formatted

def get_next_invoice_number(prefix="INV", format_str="{:05d}"):
    storage_file = "last_invoice.txt"
    current_year = datetime.datetime.now().year

    try:
        with open(storage_file, "r") as f:
            data = f.read().splitlines()
            saved_year = int(data[0])
            saved_number = int(data[1])
    except Exception:
        saved_year = current_year
        saved_number = 0

    if current_year != saved_year:
        saved_number = 0

    saved_number += 1

    with open(storage_file, "w") as f:
        f.write(f"{current_year}\n{saved_number}\n")

    return f"{prefix}{current_year}{format_str.format(saved_number)}"

def generate_invoice_gos(
    invoice_number,
    invoice_date,
    supplier_name,
    supplier_bin,
    supplier_address,
    supplier_bank_name,
    supplier_iik,
    supplier_bik,
    client_name,
    client_company,
    client_bin,
    client_phone,
    client_address,
    contract_number,
    df,
    total_logistics,
    kickback,
    tax_delivery,
    tax_kickback,
    tax_nds,
    net_margin,
):
    # Текущая дата в формате "XX Месяц YYYY г."
    invoice_date = format_date_russian(datetime.datetime.now())

    pdf = FPDF()
    pdf.add_page()

    # Пример подключения шрифта (если нужно DejaVu)
    try:
        font_path = os.path.join(os.path.dirname(__file__), "assets", "DejaVuSans.ttf")
        bold_font_path = os.path.join(os.path.dirname(__file__), "assets", "DejaVuSans-Bold.ttf")
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.add_font("DejaVu", "B", bold_font_path, uni=True)
        pdf.set_font("DejaVu", "", 9)
    except:
        pdf.set_font("Arial", "", 9)

    attention_text = (
        "Внимание! Оплата данного счета означает согласие с условиями поставки товара. "
        "Уведомление об оплате обязательно, в противном случае не гарантируется наличие товара на складе. "
        "Товар отпускается по факту прихода денег на р/с Поставщика, самовывозом/доставкой, "
        "при наличии доверенности и документов, удостоверяющих личность."
    )
    pdf.multi_cell(0, 5, attention_text)
    pdf.ln(3)

    # Образец платежного поручения
    pdf.set_font("DejaVu", "B", 9)
    pdf.cell(0, 5, "Образец платежного поручения", ln=True, align="L")
    pdf.ln(2)
    pdf.set_font("DejaVu", "", 9)

    # Первая строка таблицы
    start_x = pdf.get_x()
    start_y = pdf.get_y()
    w1, w2, w3 = 70, 65, 50
    line_height = 5
    txt1 = "Бенефициар:\nТОО «OOK-STORE»\nБИН: 170740032780"
    pdf.multi_cell(w1, line_height, txt1, border=1, align="L")
    col1_end = pdf.get_y()
    pdf.set_xy(start_x + w1, start_y)
    txt2 = "ИИК\nKZ11722S000024087169\n\n"
    pdf.multi_cell(w2, line_height, txt2, border=1, align="C")
    col2_end = pdf.get_y()
    pdf.set_xy(start_x + w1 + w2, start_y)
    txt3 = "Кбе\n17\n\n"
    pdf.multi_cell(w3, line_height, txt3, border=1, align="C")
    col3_end = pdf.get_y()
    row1_end = max(col1_end, col2_end, col3_end)
    pdf.set_xy(start_x, row1_end)

    # Вторая строка
    start_x2 = pdf.get_x()
    start_y2 = pdf.get_y()
    txt4 = "Банк бенефициара:\nАО «Kaspi Bank»"
    pdf.multi_cell(w1, line_height, txt4, border=1, align="L")
    col1_end2 = pdf.get_y()
    pdf.set_xy(start_x2 + w1, start_y2)
    txt5 = "БИК\nCASPKZKA"
    pdf.multi_cell(w2, line_height, txt5, border=1, align="C")
    col2_end2 = pdf.get_y()
    pdf.set_xy(start_x2 + w1 + w2, start_y2)
    txt6 = "Код назначения платежа\n710"
    pdf.multi_cell(w3, line_height, txt6, border=1, align="C")
    col3_end2 = pdf.get_y()
    row2_end = max(col1_end2, col2_end2, col3_end2)
    pdf.set_xy(start_x2, row2_end)

    pdf.ln(2)
    pdf.set_font("DejaVu", "B", 11)
    pdf.cell(0, 6, f"Счет на оплату № {invoice_number} от {invoice_date}", ln=True, align="C")
    pdf.ln(2)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.8)
    current_y = pdf.get_y()
    pdf.line(10, current_y, 200, current_y)
    pdf.ln(4)

    pdf.set_font("DejaVu", "", 9)
    pdf.cell(0, 5, f"Поставщик: {supplier_name}, БИН {supplier_bin}, {supplier_address}", ln=True)
    pdf.ln(2)
    pdf.cell(0, 5, f"Покупатель: {client_company}, БИН: {client_bin}, Тел: {client_phone}", ln=True)
    pdf.ln(2)
    if contract_number:
        contract_text = f"Договор: {contract_number}"
    else:
        contract_text = "Договор: Без договора"
    pdf.cell(0, 5, contract_text, ln=True)
    pdf.ln(2)

    # Таблица товаров
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.2)
    pdf.set_font("DejaVu", "B", 9)
    pdf.cell(10, 8, "№", 1, align="C")
    pdf.cell(25, 8, "Код", 1, align="C")
    pdf.cell(60, 8, "Наименование", 1)
    pdf.cell(25, 8, "Кол-во", 1, align="C")
    pdf.cell(15, 8, "Ед.", 1, align="C")
    pdf.cell(25, 8, "Цена", 1, align="C")
    pdf.cell(25, 8, "Сумма", 1, align="C")
    pdf.ln()
    pdf.set_font("DejaVu", "", 9)

    total_sum = 0
    row_line_height = 8
    for idx, row in df.iterrows():
        product_text = str(row["Товар"])
        num_lines = get_line_count(pdf, 60, product_text)
        cell_height = num_lines * row_line_height
        start_x = pdf.get_x()
        start_y = pdf.get_y()

        pdf.cell(10, cell_height, str(idx + 1), border=1, align="C")
        pdf.cell(25, cell_height, "", border=1, align="C")
        
        x_product = pdf.get_x()
        y_product = pdf.get_y()
        pdf.multi_cell(60, row_line_height, product_text, border=1)
        pdf.set_xy(x_product + 60, start_y)

        pdf.cell(25, cell_height, str(row["Количество"]), border=1, align="C")
        pdf.cell(15, cell_height, str(row["Ед_измерения"]), border=1, align="C")
        pdf.cell(25, cell_height, f"{int(row['Цена для клиента']):,}₸", border=1, align="R")
        pdf.cell(25, cell_height, f"{int(row['Выручка']):,}₸", border=1, align="R")
        pdf.ln(cell_height)
        total_sum += row["Выручка"]

    pdf.cell(185, 8, f"Итого: {int(total_sum):,}₸", 0, ln=True, align="R")
    pdf.ln(2)

    total_revenue_pdf = df["Выручка"].sum()
    nds_calculated = total_revenue_pdf * 12 / 112
    pdf.cell(185, 8, f"В том числе НДС: {int(nds_calculated):,}₸", 0, ln=True, align="R")
    pdf.ln(2)

    total_items = len(df)
    pdf.cell(0, 5, f"Всего наименований {total_items}, на сумму {int(total_sum):,} тенге", ln=True)
    pdf.ln(2)
    sum_words = num2words(int(total_sum), lang="ru").capitalize() + " тенге 00 тиын"
    pdf.cell(0, 5, f"Итого к оплате: {sum_words}", ln=True)
    pdf.ln(2)

    current_y = pdf.get_y()
    pdf.line(10, current_y, 200, current_y)
    pdf.ln(4)
    pdf.ln(2)

    pdf.set_font("DejaVu", "", 8)
    pdf.multi_cell(
        0,
        4,
        (
            "СЧЕТ ДЕЙСТВИТЕЛЕН В ТЕЧЕНИИ 3-Х БАНКОВСКИХ ДНЕЙ.\n"
            "ПО ИСТЕЧЕНИИ УКАЗАННОГО СРОКА Поставщик не гарантирует наличие товара.\n"
            "ПРИ ПОКУПКЕ Б/У ТРУБ, ТОВАР ВОЗВРАТУ НЕ ПОДЛЕЖИТ."
        ),
    )
    pdf.ln(5)
    pdf.set_font("DejaVu", "", 9)
    pdf.cell(30, 5, "Исполнитель", ln=False)
    pdf.cell(60, 5, "_______", ln=True)
    y_sign = pdf.get_y()
    pdf.ln(5)

    stamp_path = os.path.join(os.path.dirname(__file__), "assets", "stamp.PNG")
    signature_path = os.path.join(os.path.dirname(__file__), "assets", "signature.png")

    try:
        pdf.image(stamp_path, x=100, y=y_sign - 10, w=50)
    except Exception as e:
        print("Ошибка загрузки печати:", e)
    try:
        pdf.image(signature_path, x=40, y=y_sign - 10, w=20)
    except Exception as e:
        print("Ошибка загрузки подписи:", e)

    os.makedirs("output", exist_ok=True)
    pdf_path = os.path.join("output", "invoice_gos_full.pdf")
    pdf.output(pdf_path, "F")
    return pdf_path


def run_margin_service():
    # Здесь мы НЕ прописываем локальные <style> — у нас уже всё в едином блоке common_style
    with st.expander("📌 Данные клиента"):
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("ФИО клиента")
            client_company = st.text_input("Название компании")
            client_bin = st.text_input("БИН клиента")
        with col2:
            client_phone = st.text_input("Телефон клиента")
            client_address = st.text_input("Адрес доставки")
            client_contract = st.text_input("Договор (№)", placeholder="Без договора")

    with st.expander("📌 Данные по сделке"):
        col1, col2 = st.columns(2)
        with col1:
            total_logistics = st.number_input("Общая стоимость логистики (₸)", min_value=0, value=0, format="%d")
        with col2:
            kickback = st.number_input("Откат клиенту (₸)", min_value=0, value=0, format="%d")

    if "products" not in st.session_state:
        st.session_state.products = []

    st.subheader("🛒 Добавление товаров")
    with st.form("add_product_form"):
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("Наименование товара")
            name = st.text_input("", key="name", label_visibility="collapsed")
            st.markdown("Ед. измерения")
            unit = st.selectbox("", ["шт", "м", "кг", "км", "бухта", "рулон", "м²", "тонна"], 
                                key="unit", label_visibility="collapsed")
            st.markdown("Количество")
            quantity = st.number_input("", min_value=1, value=1, key="quantity", label_visibility="collapsed")
            st.markdown("Вес (кг)")
            weight = st.number_input("", min_value=0, value=0, format="%d", key="weight", label_visibility="collapsed")

        with col_right:
            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                st.markdown('<p style="font-size:16px; margin-bottom:0px;">Поставщик 1 (₸)</p>', unsafe_allow_html=True)
                price1 = st.number_input("", min_value=0, value=0, format="%d", key="price_1", label_visibility="collapsed")
            with row1_col2:
                st.markdown("⠀")
                comment1 = st.text_input("", placeholder="Комментарий", key="comm_1", label_visibility="collapsed")

            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                st.markdown('<p style="font-size:16px; margin-bottom:0px;">Цена поставщика 2 (₸)</p>', unsafe_allow_html=True)
                price2 = st.number_input("", min_value=0, value=0, format="%d", key="price_2", label_visibility="collapsed")
            with row2_col2:
                st.markdown("⠀")
                comment2 = st.text_input("", placeholder="Комментарий", key="comm_2", label_visibility="collapsed")

            row3_col1, row3_col2 = st.columns(2)
            with row3_col1:
                st.markdown('<p style="font-size:16px; margin-bottom:0px;">Цена поставщика 3 (₸)</p>', unsafe_allow_html=True)
                price3 = st.number_input("", min_value=0, value=0, format="%d", key="price_3", label_visibility="collapsed")
            with row3_col2:
                st.markdown("⠀")
                comment3 = st.text_input("", placeholder="Комментарий", key="comm_3", label_visibility="collapsed")

            row4_col1, row4_col2 = st.columns(2)
            with row4_col1:
                st.markdown('<p style="font-size:16px; margin-bottom:0px;">Цена поставщика 4 (₸)</p>', unsafe_allow_html=True)
                price4 = st.number_input("", min_value=0, value=0, format="%d", key="price_4", label_visibility="collapsed")
            with row4_col2:
                st.markdown("⠀")
                comment4 = st.text_input("", placeholder="Комментарий", key="comm_4", label_visibility="collapsed")

            row5_col1, _, _ = st.columns([2,1,2])
            with row5_col1:
                st.markdown("Наценка (%)")
                markup = st.number_input("", min_value=0, value=20, format="%d", key="markup", label_visibility="collapsed")

        submit_btn = st.form_submit_button("➕ Добавить товар")

    if submit_btn:
        if st.session_state.name.strip():
            st.session_state.products.append({
                "Товар": st.session_state.name,
                "Ед_измерения": st.session_state.unit,
                "Количество": st.session_state.quantity,
                "Вес (кг)": st.session_state.weight,
                "Цена поставщика 1": st.session_state.price_1,
                "Комментарий поставщика 1": st.session_state.comm_1,
                "Цена поставщика 2": st.session_state.price_2,
                "Комментарий поставщика 2": st.session_state.comm_2,
                "Цена поставщика 3": st.session_state.price_3,
                "Комментарий поставщика 3": st.session_state.comm_3,
                "Цена поставщика 4": st.session_state.price_4,
                "Комментарий поставщика 4": st.session_state.comm_4,
                "Наценка (%)": st.session_state.markup,
            })
            st.rerun()
        else:
            st.warning("⚠️ Введите название товара!")

    st.subheader("📦 Список товаров")
    if not st.session_state.products:
        st.info("❗ Товары ещё не добавлены")
    else:
        for index, product in enumerate(st.session_state.products):
            supplier_prices = [
                p for p in [
                    product["Цена поставщика 1"],
                    product["Цена поставщика 2"],
                    product["Цена поставщика 3"],
                    product["Цена поставщика 4"],
                ] if p > 0
            ]
            min_supplier_price = min(supplier_prices, default=0)
            max_supplier_price = max(supplier_prices, default=0)
            price_for_client = min_supplier_price * (1 + product["Наценка (%)"] / 100)
            revenue = price_for_client * product["Количество"]
            cost_price = min_supplier_price * product["Количество"]
            margin = revenue - cost_price

            with st.expander(f"🛒 {product['Товар']} ({product['Количество']} {product['Ед_измерения']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Цена для клиента (итого):** {int(revenue):,} ₸")
                    st.write(f"**Себестоимость:** {int(cost_price):,} ₸")
                    st.write(f"**Наша маржа:** {int(margin):,} ₸")
                    st.write(f"**Наценка:** {product['Наценка (%)']}%")
                with col2:
                    st.write(f"**Цена поставщика (мин – макс):** {int(min_supplier_price):,} – {int(max_supplier_price):,} ₸")
                    st.write(f"**Цена для клиента (за ед.):** {int(price_for_client):,} ₸")
                    if st.button("❌ Удалить товар", key=f"del_{index}"):
                        st.session_state.products.pop(index)
                        st.rerun()

    if st.button("📊 Рассчитать маржинальность"):
        if not st.session_state.products:
            st.warning("⚠️ Список товаров пуст. Добавьте хотя бы один товар.")
        else:
            df = pd.DataFrame(st.session_state.products)
            df["Мин. цена поставщика"] = df[
                ["Цена поставщика 1","Цена поставщика 2","Цена поставщика 3","Цена поставщика 4"]
            ].replace(0, float("inf")).min(axis=1).replace(float("inf"), 0)

            df["Цена для клиента"] = df["Мин. цена поставщика"] * (1 + df["Наценка (%)"] / 100)
            df["Выручка"] = df["Цена для клиента"] * df["Количество"]
            df["Себестоимость"] = df["Мин. цена поставщика"] * df["Количество"]
            df["Прибыль"] = df["Выручка"] - df["Себестоимость"]
            df["Маржинальность (%)"] = df["Прибыль"] / df["Выручка"] * 100

            # Из expander "Данные по сделке"
            total_logistics = st.session_state["add_product_form-total_logistics"] \
                              if "add_product_form-total_logistics" in st.session_state else 0
            kickback = st.session_state["add_product_form-kickback"] \
                       if "add_product_form-kickback" in st.session_state else 0

            tax_delivery = total_logistics * 0.15
            tax_kickback = kickback * 0.32
            tax_nds = df["Прибыль"].sum() * 12 / 112
            net_margin = df["Прибыль"].sum() - total_logistics - kickback - tax_delivery - tax_kickback - tax_nds

            manager_bonus = net_margin * 0.2

            st.subheader("📊 Итоговый расчёт")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Выручка", f"{int(df['Выручка'].sum()):,} ₸")
                st.metric("📊 Наша маржа (наценка)", f"{int(df['Прибыль'].sum()):,} ₸")
            with col2:
                st.metric("💰 Чистый маржинальный доход", f"{int(net_margin):,} ₸")
                st.metric("🏆 Бонус менеджера (20%)", f"{int(manager_bonus):,} ₸")
            with col3:
                total_revenue = df["Выручка"].sum()
                marz_percent = 0
                if not math.isclose(total_revenue, 0, abs_tol=1e-9):
                    marz_percent = net_margin / total_revenue * 100
                st.metric("📈 Маржинальность (%)", f"{max(0, marz_percent):.2f} %")

            st.write("### 🛑 Расходы")
            st.text(f"🚚 Логистика: {int(total_logistics):,} ₸")
            st.text(f"💵 Откат клиенту: {int(kickback):,} ₸")
            st.text(f"📊 Налог на обнал (15%) (логистика): {int(tax_delivery):,} ₸")
            st.text(f"💸 Налог на обнал (32%) (откат): {int(tax_kickback):,} ₸")
            st.text(f"📊 Налог НДС от маржи (12%): {int(tax_nds):,} ₸")

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                client_data = pd.DataFrame({
                    "Поле": ["ФИО клиента","Название компании","БИН клиента","Телефон клиента","Адрес доставки","Договор (№)"],
                    "Значение": [
                        st.session_state["add_product_form-name"], 
                        st.session_state["add_product_form-company"] 
                        if "add_product_form-company" in st.session_state else "",
                        st.session_state["add_product_form-bin"] 
                        if "add_product_form-bin" in st.session_state else "",
                        st.session_state["add_product_form-phone"] 
                        if "add_product_form-phone" in st.session_state else "",
                        st.session_state["add_product_form-address"] 
                        if "add_product_form-address" in st.session_state else "",
                        st.session_state["add_product_form-contract"] 
                        if "add_product_form-contract" in st.session_state else ""
                    ],
                })
                client_data.to_excel(writer, index=False, sheet_name="Данные клиента")

                deal_data = pd.DataFrame({
                    "Поле": ["Общая стоимость логистики","Откат клиенту"],
                    "Значение (₸)": [total_logistics, kickback],
                })
                deal_data.to_excel(writer, index=False, sheet_name="Данные сделки")

                df.to_excel(writer, index=False, sheet_name="Список товаров")

                final_data = pd.DataFrame({
                    "Показатель": [
                        "Выручка","Наша маржа (итог)","Чистый маржинальный доход","Бонус менеджера (20%)",
                        "Логистика","Откат клиенту","Налог на обнал (15%)","Налог на обнал (32%)","Налог НДС (12%)","Итоговая сумма (net_margin)",
                    ],
                    "Значение (₸)": [
                        df["Выручка"].sum(),
                        df["Прибыль"].sum(),
                        net_margin,
                        manager_bonus,
                        total_logistics,
                        kickback,
                        tax_delivery,
                        tax_kickback,
                        tax_nds,
                        net_margin
                    ],
                })
                final_data.to_excel(writer, index=False, sheet_name="Расчет+Расходы")

            st.download_button(
                "📥 Скачать расчёт в Excel",
                data=output.getvalue(),
                file_name="margin_calculation.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            unique_invoice_number = get_next_invoice_number(prefix="INV")
            pdf_path = generate_invoice_gos(
                invoice_number=unique_invoice_number,
                invoice_date="placeholder",
                supplier_name="ТОО OOK-STORE",
                supplier_bin="170740032780",
                supplier_address="г. Алматы, ул. Березовского 19",
                supplier_bank_name="Kaspi Bank",
                supplier_iik="KZ11722S000024087169",
                supplier_bik="CASPKZKA",
                client_name=st.session_state.get("add_product_form-name", "—"),
                client_company=st.session_state.get("add_product_form-company", "—"),
                client_bin=st.session_state.get("add_product_form-bin", "—"),
                client_phone=st.session_state.get("add_product_form-phone", "—"),
                client_address=st.session_state.get("add_product_form-address", "—"),
                contract_number=st.session_state.get("add_product_form-contract", ""),
                df=df,
                total_logistics=total_logistics,
                kickback=kickback,
                tax_delivery=tax_delivery,
                tax_kickback=tax_kickback,
                tax_nds=tax_nds,
                net_margin=net_margin,
            )
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "📥 Скачать счет (гос)",
                    data=f,
                    file_name="invoice_gos_full.pdf",
                    mime="application/pdf",
                )


###############################################################################
#                     ОСНОВНОЙ БЛОК: ВКЛАДКИ (TABS)
###############################################################################
tab_margin, tab_logistics = st.tabs(["**Калькулятор маржинальности**", "**Калькулятор логистики**"])

with tab_margin:
    run_margin_service()

with tab_logistics:
    run_logistics_service()
