# margin_calculator.py

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

# НОВОЕ: Импорт для работы с Google Sheets
from google_sheets_db import save_calculation, load_calculation, connect_to_sheets

# Устанавливаем параметры страницы
st.set_page_config(page_title="Margin Calculator", page_icon="💰")

# -------------------------
# Данные пользователей
# -------------------------
users = {
    "zveat": {"name": "John Doe", "password": bcrypt.hash("2097")},
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
#                         БЛОК 1: КОД ЛОГИСТИЧЕСКОГО КАЛЬКУЛЯТОРА
###############################################################################
def run_logistics_service():

    # Дополнительные стили (CSS) логистического калькулятора
    st.markdown(
        """
        <style>
        /* Задаём для .block-container желаемую ширину и отступ слева 
           (можете подправить стили под себя) */
        .block-container {
            max-width: 750px !important; /* Желаемая ширина */
            margin-left: 20px !important; /* Отступ слева */
            background-color: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        body {
            background-color: #f8f9fa;
        }
        /* Стили для полей ввода */
        div[data-testid="stNumberInput"] input,
        div[data-testid="stTextInput"] input,
        div[data-testid="stSelectbox"] select {
             border: 1px solid #ccc !important;
             border-radius: 5px !important;
             padding: 8px !important;
             font-size: 14px !important;
        }
        /* Стили для кнопок */
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
        """,
        unsafe_allow_html=True
    )

    # Данные для городских перевозок
    city_data = [
        {"Вид транспорта": "Легковая машина",    "Вес груза": 40,   "Длинна груза": 2,  "Стоимость доставки": "4000-8000"},
        {"Вид транспорта": "Газель",             "Вес груза": 300,  "Длинна груза": 3,  "Стоимость доставки": "4000-12000"},
        {"Вид транспорта": "Длинномer/бортовой", "Вес груза": 1000, "Длинна груза": 12, "Стоимость доставки": "30000-35000"},
        {"Вид транспорта": "Газель Бортовая",    "Вес груза": 2000, "Длинна груза": 4,  "Стоимость доставки": "10000-20000"},
        {"Вид транспорта": "Бортовой грузовик",  "Вес груза": 6000, "Длинna груза": 7,  "Стоимость доставки": "20000-30000"},
        {"Вид транспорта": "Фура",               "Вес груза": 23000,"Длинna груza": 12, "Стоимость доставки": "50000-60000"}
    ]

    # Данные для междугородних перевозок
    intercity_data = {
        "Алматы-Aстана": 500000,
        "Алматы-Шымкент": 300000,
        "Алматы-Aктау": 1200000,
        "Алматы-Aтыраu": 800000,
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
    """
    Возвращает количество строк, которое потребуется для вывода текста в ячейке заданной ширины.
    """
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
    """
    Генерирует следующий уникальный номер счёта (invoice).
    Хранится в файле 'last_invoice.txt' (можно заменить на базу данных или другое хранилище).
    """
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
    # Убедитесь, что у вас есть папка assets и в ней DejaVuSans.ttf, DejaVuSans-Bold.ttf
    try:
        font_path = os.path.join(os.path.dirname(__file__), "assets", "DejaVuSans.ttf")
        bold_font_path = os.path.join(os.path.dirname(__file__), "assets", "DejaVuSans-Bold.ttf")
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.add_font("DejaVu", "B", bold_font_path, uni=True)
        pdf.set_font("DejaVu", "", 9)
    except:
        # Если не нашли шрифт, пусть хотя бы базовый работает
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

    # Первая строка таблицы (Бенефициар, ИИК, Кбе)
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
        pdf.cell(25, cell_height, "", border=1, align="C")  # Под "Код" (пусто)
        
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

    # Пример: вставка печати и подписи из папки assets
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
    # CSS для единообразия в «Калькуляторе маржинальности» с добавлением скрытия суффикса _X цветом фона кнопок
    st.markdown(
        """
        <style>
        /* Унифицируем шрифт и отступы для markdown-меток внутри контейнера */
        .block-container p {
            margin: 0.3rem 0 0.2rem 0 !important;
            font-size: 16px !important;
            line-height: 1.2 !important;
        }
        /* Унифицируем высоту и шрифт полей ввода */
        div[data-testid="stNumberInput"] input,
        div[data-testid="stTextInput"] input {
             min-height: 35px !important;
             padding: 4px 6px !important;
             font-size: 14px !important;
        }
        /* Скрываем суффикс _X в кнопках "Редактировать товар_X" и "Удалить товар_X" с помощью цвета фона кнопок (#007bff) */
        .stButton > button[data-label^="✏️ Редактировать товар_"] {
            position: relative;
        }
        .stButton > button[data-label^="✏️ Редактировать товар_"]:after {
            content: attr(data-label);
            color: #007bff; /* Цвет фона кнопок, чтобы суффикс стал незаметным */
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
        }
        .stButton > button[data-label^="✏️ Редактировать товар_"]:before {
            content: "✏️ Редактировать товар"; /* Отображаем только нужный текст */
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px; /* Убедимся, что размер текста совпадает */
            color: #fff; /* Цвет текста кнопки */
            z-index: 2;
        }
        .stButton > button[data-label^="❌ Удалить товар_"] {
            position: relative;
        }
        .stButton > button[data-label^="❌ Удалить товар_"]:after {
            content: attr(data-label);
            color: #007bff; /* Цвет фона кнопок, чтобы суффикс стал незаметным */
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
        }
        .stButton > button[data-label^="❌ Удалить товар_"]:before {
            content: "❌ Удалить товар"; /* Отображаем только нужный текст */
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px; /* Убедимся, что размер текста совпадает */
            color: #fff; /* Цвет текста кнопки */
            z-index: 2;
        }
        /* Оставляем другие кнопки (Войти, Выйти, Рассчитать) без изменений */
        .stButton > button:not([data-label^="✏️ Редактировать товар_"]):not([data-label^="❌ Удалить товар_"]) {
            /* Без изменений для других кнопок */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # НОВОЕ: Фиксированный spreadsheet_id для вашей Google Таблицы
    spreadsheet_id = "1Z4-Moti7RVqyBQY5v4tcCwFQS3noOD84w9Q2liv9rI4"

    # НОВОЕ: Блок с историей расчётов
    st.subheader("📜 История расчётов")
    conn = connect_to_sheets()  # Подключаемся к Google Sheets
    try:
        sheet = conn.open_by_key(spreadsheet_id)
    except gspread.exceptions.SpreadsheetNotFound:
        st.error("Google Таблица не найдена. Убедитесь, что spreadsheet_id корректен и сервисный аккаунт имеет доступ.")
        return

    # Загружаем историю расчётов
    history_sheet = sheet.worksheet("History")
    history = history_sheet.get_all_values()[1:]  # Пропускаем заголовок

    if history:
        deal_ids = [row[0] for row in history]  # deal_id (индекс 0 в History)
        # Исправляем format_func, чтобы использовать данные из history для отображения даты
        def format_deal(deal_id):
            for row in history:
                if row[0] == str(deal_id):
                    return f"Расчёт #{deal_id} ({row[1]})"  # deal_id и дата (столбец 1 — дата)
            return f"Расчёт #{deal_id}"
        
        selected_deal = st.selectbox("Выберите прошлый расчёт для восстановления", deal_ids, format_func=format_deal)
        if st.button("Восстановить расчёт"):
            try:
                # Отладка: выведем, что возвращает load_calculation
                print(f"Попытка восстановить расчёт с deal_id: {selected_deal}")
                client_data_restored, deal_data_restored, products_restored = load_calculation(spreadsheet_id, int(selected_deal))
                if client_data_restored:
                    client_name, client_company, client_bin, client_phone, client_address, client_contract = client_data_restored
                    total_logistics, kickback = deal_data_restored

                    # Отладка: выведем восстановленные продукты
                    print(f"Восстановленные продукты: {products_restored}")

                    st.session_state.client_name = client_name
                    st.session_state.client_company = client_company
                    st.session_state.client_bin = client_bin
                    st.session_state.client_phone = client_phone
                    st.session_state.client_address = client_address
                    st.session_state.client_contract = client_contract
                    st.session_state.total_logistics = int(total_logistics) if total_logistics else 0
                    st.session_state.kickback = int(kickback) if kickback else 0
                    st.session_state.products = products_restored if products_restored else []
                    st.success("Расчёт восстановлен!")
                    st.rerun()
                else:
                    st.error("Расчёт с указанным ID не найден.")
            except Exception as e:
                st.error(f"Ошибка при восстановлении расчёта: {e}")
                print(f"Ошибка в восстановлении: {e}")
    else:
        st.info("История расчётов пуста.")

    # --- Блок "Данные клиента"
    # Если данные восстановлены, используем их; иначе — пустые значения
    client_name = st.session_state.get('client_name', '')
    client_company = st.session_state.get('client_company', '')
    client_bin = st.session_state.get('client_bin', '')
    client_phone = st.session_state.get('client_phone', '')
    client_address = st.session_state.get('client_address', '')
    client_contract = st.session_state.get('client_contract', '')
    total_logistics = st.session_state.get('total_logistics', 0)
    kickback = st.session_state.get('kickback', 0)
    if "products" not in st.session_state:
        st.session_state.products = []

    with st.expander("📌 Данные клиента"):
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("ФИО клиента", value=client_name)
            client_company = st.text_input("Название компании", value=client_company)
            client_bin = st.text_input("БИН клиента", value=client_bin)
        with col2:
            client_phone = st.text_input("Телефон клиента", value=client_phone)
            client_address = st.text_input("Адрес доставки", value=client_address)
            client_contract = st.text_input("Договор (№)", placeholder="Без договора", value=client_contract)

    # --- Блок "Данные по сделке"
    with st.expander("📌 Данные по сделке"):
        col1, col2 = st.columns(2)
        with col1:
            total_logistics = st.number_input("Общая стоимость логистики (₸)", min_value=0, value=total_logistics, format="%d")
        with col2:
            kickback = st.number_input("Откат клиенту (₸)", min_value=0, value=kickback, format="%d")

    # Хранение товаров в сессии
    if "products" not in st.session_state:
        st.session_state.products = []

    # --- Форма для добавления товаров
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
            # Цена поставщика 1
            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                st.markdown('<p style="font-size:16px; margin-bottom:0px;">Цена поставщика 1 (₸)</p>', unsafe_allow_html=True)
                price1 = st.number_input("", min_value=0, value=0, format="%d", key="price_1", label_visibility="collapsed")
            with row1_col2:
                st.markdown("⠀")
                comment1 = st.text_input("", placeholder="Комментарий", key="comm_1", label_visibility="collapsed")

            # Цена поставщика 2
            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                st.markdown('<p style="font-size:16px; margin-bottom:0px;">Цена поставщика 2 (₸)</p>', unsafe_allow_html=True)
                price2 = st.number_input("", min_value=0, value=0, format="%d", key="price_2", label_visibility="collapsed")
            with row2_col2:
                st.markdown("⠀")
                comment2 = st.text_input("", placeholder="Комментарий", key="comm_2", label_visibility="collapsed")

            # Цена поставщика 3
            row3_col1, row3_col2 = st.columns(2)
            with row3_col1:
                st.markdown('<p style="font-size:16px; margin-bottom:0px;">Цена поставщика 3 (₸)</p>', unsafe_allow_html=True)
                price3 = st.number_input("", min_value=0, value=0, format="%d", key="price_3", label_visibility="collapsed")
            with row3_col2:
                st.markdown("⠀")
                comment3 = st.text_input("", placeholder="Комментарий", key="comm_3", label_visibility="collapsed")

            # Цена поставщика 4
            row4_col1, row4_col2 = st.columns(2)
            with row4_col1:
                st.markdown('<p style="font-size:16px; margin-bottom:0px;">Цена поставщика 4 (₸)</p>', unsafe_allow_html=True)
                price4 = st.number_input("", min_value=0, value=0, format="%d", key="price_4", label_visibility="collapsed")
            with row4_col2:
                st.markdown("⠀")
                comment4 = st.text_input("", placeholder="Комментарий", key="comm_4", label_visibility="collapsed")

            # Наценка
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
            st.warning("Введите название товара ⚠️ ")

    # --- Список товаров ---
    st.subheader("📦 Список товаров")
    if not st.session_state.products:
        st.info("Товары ещё не добавлены❗")
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
                
                # Кнопки "Редактировать" и "Удалить" в одной колонке, как в исходном коде
                col_btn, _ = st.columns([1, 1])
                with col_btn:
                    if st.button(f"✏️ Редактировать товар_{index}", key=f"edit_{index}"):
                        # Открываем форму редактирования для выбранного товара
                        st.session_state.edit_index = index
                        st.session_state.edit_product = product.copy()
                        # Убедимся, что cancel_key существует и инициализирован
                        if "cancel_key" not in st.session_state:
                            st.session_state.cancel_key = f"cancel_edit_{index}"
                        print(f"Сгенерирован и сохранён ключ для кнопки 'Отмена': {st.session_state.cancel_key}")
                        st.rerun()

                    if st.button(f"❌ Удалить товар_{index}", key=f"del_{index}"):
                        st.session_state.products.pop(index)
                        st.rerun()

    # --- Форма редактирования товара (если выбрано редактирование)
    if "edit_index" in st.session_state and "edit_product" in st.session_state:
        # Отладка: выведем текущий edit_index
        print(f"Редактируется товар с индексом: {st.session_state.edit_index}")
        
        # Проверяем, что edit_index в пределах допустимого диапазона
        if st.session_state.edit_index < 0 or st.session_state.edit_index >= len(st.session_state.get("products", [])):
            st.error("Ошибка: Индекс товара для редактирования некорректен. Пожалуйста, попробуйте снова.")
            if "edit_index" in st.session_state:
                del st.session_state.edit_index
            if "edit_product" in st.session_state:
                del st.session_state.edit_product
            if "cancel_key" in st.session_state:
                del st.session_state.cancel_key
            st.rerun()

        st.subheader("🛠 Редактирование товара")
        # Используем фиксированный ключ для формы, основанный на edit_index
        form_key = f"edit_product_form_{st.session_state.edit_index}"
        print(f"Используется ключ для формы редактирования: {form_key}")
        with st.form(form_key):
            col_left, col_right = st.columns(2)
            with col_left:
                name = st.text_input("Наименование товара", value=st.session_state.edit_product["Товар"], key=f"edit_name_{st.session_state.edit_index}")
                unit = st.selectbox("Ед. измерения", ["шт", "м", "кг", "км", "бухта", "рулон", "м²", "тонна"], 
                                    index=["шт", "м", "кг", "км", "бухта", "рулон", "м²", "тонна"].index(st.session_state.edit_product["Ед_измерения"]),
                                    key=f"edit_unit_{st.session_state.edit_index}")
                quantity = st.number_input("Количество", min_value=1, value=int(st.session_state.edit_product["Количество"]), key=f"edit_quantity_{st.session_state.edit_index}")
                weight = st.number_input("Вес (кг)", min_value=0, value=int(st.session_state.edit_product["Вес (кг)"]), format="%d", key=f"edit_weight_{st.session_state.edit_index}")

            with col_right:
                # Цена поставщика 1
                row1_col1, row1_col2 = st.columns(2)
                with row1_col1:
                    st.markdown('<p style="font-size:16px; margin-bottom:0px;">Цена поставщика 1 (₸)</p>', unsafe_allow_html=True)
                    price1 = st.number_input("", min_value=0, value=int(st.session_state.edit_product["Цена поставщика 1"]), format="%d", key=f"edit_price_1_{st.session_state.edit_index}", label_visibility="collapsed")
                with row1_col2:
                    st.markdown("⠀")
                    comment1 = st.text_input("", placeholder="Комментарий", value=st.session_state.edit_product["Комментарий поставщика 1"], key=f"edit_comm_1_{st.session_state.edit_index}", label_visibility="collapsed")

                # Цена поставщика 2
                row2_col1, row2_col2 = st.columns(2)
                with row2_col1:
                    st.markdown('<p style="font-size:16px; margin-bottom:0px;">Цена поставщика 2 (₸)</p>', unsafe_allow_html=True)
                    price2 = st.number_input("", min_value=0, value=int(st.session_state.edit_product["Цена поставщика 2"]), format="%d", key=f"edit_price_2_{st.session_state.edit_index}", label_visibility="collapsed")
                with row2_col2:
                    st.markdown("⠀")
                    comment2 = st.text_input("", placeholder="Комментарий", value=st.session_state.edit_product["Комментарий поставщика 2"], key=f"edit_comm_2_{st.session_state.edit_index}", label_visibility="collapsed")

                # Цена поставщика 3
                row3_col1, row3_col2 = st.columns(2)
                with row3_col1:
                    st.markdown('<p style="font-size:16px; margin-bottom:0px;">Цена поставщика 3 (₸)</p>', unsafe_allow_html=True)
                    price3 = st.number_input("", min_value=0, value=int(st.session_state.edit_product["Цена поставщика 3"]), format="%d", key=f"edit_price_3_{st.session_state.edit_index}", label_visibility="collapsed")
                with row3_col2:
                    st.markdown("⠀")
                    comment3 = st.text_input("", placeholder="Комментарий", value=st.session_state.edit_product["Комментарий поставщика 3"], key=f"edit_comm_3_{st.session_state.edit_index}", label_visibility="collapsed")

                # Цена поставщика 4
                row4_col1, row4_col2 = st.columns(2)
                with row4_col1:
                    st.markdown('<p style="font-size:16px; margin-bottom:0px;">Цена поставщика 4 (₸)</p>', unsafe_allow_html=True)
                    price4 = st.number_input("", min_value=0, value=int(st.session_state.edit_product["Цена поставщика 4"]), format="%d", key=f"edit_price_4_{st.session_state.edit_index}", label_visibility="collapsed")
                with row4_col2:
                    st.markdown("⠀")
                    comment4 = st.text_input("", placeholder="Комментарий", value=st.session_state.edit_product["Комментарий поставщика 4"], key=f"edit_comm_4_{st.session_state.edit_index}", label_visibility="collapsed")

                # Наценка
                row5_col1, _, _ = st.columns([2,1,2])
                with row5_col1:
                    st.markdown("Наценка (%)")
                    markup = st.number_input("", min_value=0, value=int(st.session_state.edit_product["Наценка (%)"]), format="%d", key=f"edit_markup_{st.session_state.edit_index}", label_visibility="collapsed")

            # Отладка нажатия кнопки "Сохранить изменения" с проверкой значений
            if st.form_submit_button("💾 Сохранить изменения"):
                print(f"Кнопка 'Сохранить изменения' нажата для товара с индексом: {st.session_state.edit_index}")
                print(f"Текущие значения формы: name={name}, unit={unit}, quantity={quantity}, weight={weight}, price1={price1}, price2={price2}, price3={price3}, price4={price4}, markup={markup}")
                # Проверяем, что значения не пустые
                if name.strip():
                    # Обновляем товар в st.session_state.products
                    st.session_state.products[st.session_state.edit_index] = {
                        "Товар": name,
                        "Ед_измерения": unit,
                        "Количество": quantity,
                        "Вес (кг)": weight,
                        "Цена поставщика 1": price1,
                        "Комментарий поставщика 1": comment1,
                        "Цена поставщика 2": price2,
                        "Комментарий поставщика 2": comment2,
                        "Цена поставщика 3": price3,
                        "Комментарий поставщика 3": comment3,
                        "Цена поставщика 4": price4,
                        "Комментарий поставщика 4": comment4,
                        "Наценка (%)": markup,
                    }
                    del st.session_state.edit_index
                    del st.session_state.edit_product
                    if "cancel_key" in st.session_state:
                        del st.session_state.cancel_key
                    st.success("Товар успешно отредактирован!")
                    st.rerun()
                else:
                    st.error("Название товара не может быть пустым. Пожалуйста, введите название.")

        # Кнопка "Отмена" использует сохранённый ключ из сессии
        if "cancel_key" in st.session_state:
            print(f"Используется сохранённый ключ для кнопки 'Отмена': {st.session_state.cancel_key}")
            col_cancel, _ = st.columns([1, 1])  # Размещаем кнопку в отдельной колонке
            with col_cancel:
                if st.button("✖️ Отмена", key=st.session_state.cancel_key):
                    print(f"Кнопка 'Отмена' нажата с ключом: {st.session_state.cancel_key}")
                    # Проверяем, что edit_index и edit_product существуют перед удалением
                    if "edit_index" in st.session_state:
                        del st.session_state.edit_index
                    if "edit_product" in st.session_state:
                        del st.session_state.edit_product
                    if "cancel_key" in st.session_state:
                        del st.session_state.cancel_key
                    st.rerun()
        else:
            # Если ключ отсутствует, генерируем новый и сохраняем его
            st.session_state.cancel_key = f"cancel_edit_{st.session_state.edit_index}"
            print(f"Сгенерирован новый ключ для кнопки 'Отмена', так как предыдущий не найден: {st.session_state.cancel_key}")
            col_cancel, _ = st.columns([1, 1])  # Размещаем кнопку в отдельной колонке
            with col_cancel:
                if st.button("✖️ Отмена", key=st.session_state.cancel_key):
                    print(f"Кнопка 'Отмена' нажата с ключом: {st.session_state.cancel_key}")
                    # Проверяем, что edit_index и edit_product существуют перед удалением
                    if "edit_index" in st.session_state:
                        del st.session_state.edit_index
                    if "edit_product" in st.session_state:
                        del st.session_state.edit_product
                    if "cancel_key" in st.session_state:
                        del st.session_state.cancel_key
                    st.rerun()

    # --- Кнопка «Рассчитать»
    if st.button("📊 Рассчитать маржинальность"):
        if not st.session_state.products:
            st.warning("⚠️ Список товаров пуст. Добавьте хотя бы один товар.")
        else:
            df = pd.DataFrame(st.session_state.products)
            # Рассчитываем мин. цену поставщика
            df["Мин. цена поставщика"] = df[
                [
                    "Цена поставщика 1",
                    "Цена поставщика 2",
                    "Цена поставщика 3",
                    "Цена поставщика 4",
                ]
            ].replace(0, float("inf")).min(axis=1).replace(float("inf"), 0)

            # Цена для клиента, выручка, себестоимость, прибыль (маржа)
            df["Цена для клиента"] = df["Мин. цена поставщика"] * (1 + df["Наценка (%)"] / 100)
            df["Выручка"] = df["Цена для клиента"] * df["Количество"]
            df["Себестоимость"] = df["Мин. цена поставщика"] * df["Количество"]
            df["Прибыль"] = df["Выручка"] - df["Себестоимость"]
            df["Маржинальность (%)"] = df["Прибыль"] / df["Выручка"] * 100

            # Расходы
            tax_delivery = total_logistics * 0.15
            tax_kickback = kickback * 0.32
            tax_nds = df["Прибыль"].sum() * 12 / 112  # Примерный расчет НДС
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
                if math.isclose(total_revenue, 0, abs_tol=1e-9):
                    marz_percent = 0
                else:
                    marz_percent = net_margin / total_revenue * 100
                st.metric("📈 Маржинальность (%)", f"{max(0, marz_percent):.2f} %")

            st.write("### 🛑 Расходы")
            st.text(f"🚚 Логистика: {int(total_logistics):,} ₸")
            st.text(f"💵 Откат клиенту: {int(kickback):,} ₸")
            st.text(f"📊 Налог на обнал (15%) (логистика): {int(tax_delivery):,} ₸")
            st.text(f"💸 Налог на обнал (32%) (откат): {int(tax_kickback):,} ₸")
            st.text(f"📊 Налог НДС от маржи (12%): {int(tax_nds):,} ₸")

            # Сохранение результатов в Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                # Лист 1: данные клиента
                client_data = pd.DataFrame({
                    "Поле": ["ФИО клиента", "Название компании", "БИН клиента", 
                             "Телефон клиента", "Адрес доставки", "Договор (№)"],
                    "Значение": [client_name, client_company, client_bin, 
                                 client_phone, client_address, client_contract],
                })
                client_data.to_excel(writer, index=False, sheet_name="Данные клиента")

                # Лист 2: данные сделки
                deal_data = pd.DataFrame({
                    "Поле": ["Общая стоимость логистики", "Откат клиенту"],
                    "Значение (₸)": [total_logistics, kickback],
                })
                deal_data.to_excel(writer, index=False, sheet_name="Данные сделки")

                # Лист 3: товары
                df.to_excel(writer, index=False, sheet_name="Список товаров")

                # Лист 4: расчет итогов
                final_data = pd.DataFrame({
                    "Показатель": [
                        "Выручка",
                        "Наша маржа (итог)",
                        "Чистый маржинальный доход",
                        "Бонус менеджера (20%)",
                        "Логистика",
                        "Откат клиенту",
                        "Налог на обнал (15%)",
                        "Налог на обнал (32%)",
                        "Налог НДС (12%)",
                        "Итоговая сумма (net_margin)",
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
                        net_margin,
                    ],
                })
                final_data.to_excel(writer, index=False, sheet_name="Расчет+Расходы")

            st.download_button(
                "📥 Скачать расчёт в Excel",
                data=output.getvalue(),
                file_name="margin_calculator.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            # Генерация PDF
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
                client_name=client_name,
                client_company=client_company,
                client_bin=client_bin,
                client_phone=client_phone,
                client_address=client_address,
                contract_number=client_contract,
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

            # НОВОЕ: Сохранение данных в Google Sheets
            client_data = {
                'name': client_name,
                'company': client_company,
                'bin': client_bin,
                'phone': client_phone,
                'address': client_address,
                'contract': client_contract
            }
            deal_data = {
                'total_logistics': total_logistics,
                'kickback': kickback
            }
            try:
                deal_id = save_calculation(spreadsheet_id, client_data, deal_data, st.session_state.products, True)
                st.success(f"Расчёт сохранён в Google Sheets с ID сделки: {deal_id}")
            except Exception as e:
                st.error(f"Ошибка при сохранении в Google Sheets: {e}")

# ... (оставляем остальной код — логистику, вкладки, JS — без изменений)
###############################################################################
#                     ОСНОВНОЙ БЛОК: ВКЛАДКИ (TABS)
###############################################################################
tab_margin, tab_logistics = st.tabs(["**Калькулятор маржинальности**", "**Калькулятор логистики**"])

with tab_margin:
    run_margin_service()

with tab_logistics:
    run_logistics_service()

# --- В самом конце файла вставляем JS, отключающий автозаполнение ---
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
