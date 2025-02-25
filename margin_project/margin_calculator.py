import streamlit as st
import os
import base64
import locale
from passlib.hash import bcrypt
import pandas as pd
import io
import math
import datetime
from fpdf import FPDF
from num2words import num2words

# Устанавливаем параметры страницы
st.set_page_config()

# -------------------------
# Данные пользователей
# -------------------------
users = {
    "john": {"name": "John Doe", "password": bcrypt.hash("123")},
    "jane": {"name": "Jane Doe", "password": bcrypt.hash("456")}
}

def check_credentials(username, password):
    """Функция проверки логина и пароля с отладочными выводами"""
    print(f"Проверка логина: {username}, пароль: {password}")  # Отладка
    if username in users:
        print(f"Найден пользователь, проверка пароля: {password}")
        result = bcrypt.verify(password, users[username]["password"])
        print(f"Результат проверки пароля: {result}")
        return result
    print("Пользователь не найден")
    return False

# -------------------------
# Состояние сессии
# -------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = ""

# -------------------------
# Форма входа
# -------------------------
if not st.session_state["authenticated"]:
    st.title("Вход в сервис")
    username_input = st.text_input("Логин").strip().lower()
    password_input = st.text_input("Пароль", type="password").strip()
    
    if st.button("Войти"):
        if check_credentials(username_input, password_input):
            st.session_state["authenticated"] = True
            st.session_state["user"] = username_input
            st.rerun()
        else:
            st.error("Неверный логин или пароль")
    st.stop()

# -------------------------
# Основной сервис
# -------------------------
st.success(f"Добро пожаловать, {users[st.session_state['user']]['name']}!")

# Загрузка логотипа
logo_path = os.path.join(os.path.dirname(__file__), "assets", "Logo.png")
with open(logo_path, "rb") as f:
    data = f.read()
encoded_logo = base64.b64encode(data).decode()
logo_src = f"data:image/png;base64,{encoded_logo}"

# HTML-блок с логотипом и заголовком
html_block = f"""
<style>
  .responsive-header {{
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 20px;
  }}
  .responsive-header img {{
    max-width: 200px;
    width: 100%;
    height: auto;
    margin-right: 20px;
  }}
  .responsive-header h2 {{
    margin: 0;
    font-size: 25px;
  }}
  @media (max-width: 480px) {{
    .responsive-header img {{
      max-width: 150px;
      margin-right: 10px;
    }}
    .responsive-header h2 {{
      font-size: 20px;
      text-align: center;
    }}
  }}
</style>
<div class="responsive-header">
  <img src="{logo_src}" alt="Logo" />
  <h2>
    <span style="color:#007bff;">СЕРВСИС РАСЧЕТА ЛОГИСТИКИ И МАРЖИНАЛЬНОСТИ</span>
  </h2>
</div>
"""
st.markdown(html_block, unsafe_allow_html=True)

# Настройка локали
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, '')

# Кнопка выхода
if st.button("Выйти"):
    st.session_state["authenticated"] = False
    st.session_state["user"] = ""
    st.rerun()

###############################################################################
# БЛОК 1: КОД ЛОГИСТИЧЕСКОГО КАЛЬКУЛЯТОРА
###############################################################################
def run_logistics_service():
    st.markdown(
        """
        <style>
        .logistics-container {
            max-width: 750px;
            margin: 0 auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        div[data-testid="stNumberInput"] input,
        div[data-testid="stTextInput"] input,
        div[data-testid="stSelectbox"] select {
             border: 1px solid #ccc;
             border-radius: 5px;
             padding: 8px;
             font-size: 14px;
        }
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
        <div class="logistics-container">
        """,
        unsafe_allow_html=True
    )

    # Данные для городских перевозок
    city_data = [
        {"Вид транспорта": "Легковая машина",    "Вес груза": 40,   "Длинна груза": 2,  "Стоимость доставки": "4000-8000"},
        {"Вид транспорта": "Газель",             "Вес груза": 300,  "Длинна груza": 3,  "Стоимость доставки": "4000-12000"},
        {"Вид транспорта": "Длинномер/бортовой", "Вес груза": 1000, "Длинна груza": 12, "Стоимость доставки": "30000-35000"},
        {"Вид транспорта": "Газель Бортовая",    "Вес груza": 2000, "Длинна груza": 4,  "Стоимость доставки": "10000-20000"},
        {"Вид транспорта": "Бортовой грузовик",  "Вес груza": 6000, "Длинна груza": 7,  "Стоимость доставки": "20000-30000"},
        {"Вид транспорта": "Фура",               "Вес груza": 23000,"Длинна груza": 12, "Стоимость доставки": "50000-60000"}
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
                capacity = 20
                coef = 2
                cost = (tariff / capacity) * weight_tonn * coef
                st.success(f"Стоимость перевозки: **{round(cost)} тг**")

    st.markdown("</div>", unsafe_allow_html=True)

###############################################################################
# БЛОК 2: КОД КАЛЬКУЛЯТОРА МАРЖИНАЛЬНОСТИ
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
    invoice_date = format_date_russian(datetime.datetime.now())
    pdf = FPDF()
    pdf.add_page()

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

    pdf.set_font("DejaVu", "B", 9)
    pdf.cell(0, 5, "Образец платежного поручения", ln=True, align="L")
    pdf.ln(2)
    pdf.set_font("DejaVu", "", 9)

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
    contract_text = f"Договор: {contract_number}" if contract_number else "Договор: Без договора"
    pdf.cell(0, 5, contract_text, ln=True)
    pdf.ln(2)

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

###############################################################################
# ОСНОВНОЙ БЛОК: ВКЛАДКИ (TABS)
###############################################################################
tab_margin, tab_logistics = st.tabs(["**Калькулятор маржинальности**", "**Калькулятор логистики**"])

with tab_margin:
    run_margin_service()

with tab_logistics:
    run_logistics_service()

st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('input').forEach(function(el) {
    el.setAttribute('autocomplete', 'off');
    el.setAttribute('autocorrect', 'off');
    el.setAttribute('autocapitalize', 'off');
  });
});
</script>
""", unsafe_allow_html=True)
