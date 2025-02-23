import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import io
import os
from fpdf import FPDF
from num2words import num2words
import math
import datetime
import locale

# Этот вызов должен быть первым
st.set_page_config(layout="wide")
st.title("Сервис расчета логистики и маржинальности")

# Устанавливаем локаль для вывода даты на русском языке
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, '')

def format_date_russian(date_obj):
    # Пример словаря для замены
    months = {
        "January": "Января", "February": "Февраля", "March": "Марта",
        "April": "Апреля", "May": "Мая", "June": "Июня",
        "July": "Июля", "August": "Августа", "September": "Сентября",
        "October": "Октября", "November": "Ноября", "December": "Декабря"
    }
    # Форматируем дату как "день Month год г."
    formatted = date_obj.strftime("%d %B %Y г.")
    for eng, rus in months.items():
        formatted = formatted.replace(eng, rus)
    return formatted

# CSS для унификации стилей (подберите нужные значения по вкусу)
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
    </style>
    """,
    unsafe_allow_html=True
)

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

def get_next_invoice_number(prefix="INV", format_str="{:05d}"):
    """
    Возвращает следующий уникальный номер счета с префиксом и годом.
    Номер хранится в файле 'last_invoice.txt'.
    Формат номера: префикс + год + номер с ведущими нулями (например, INV202300001)
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

########################################
# Функция генерации PDF-счёта (ГОС. ОБРАЗЦА)
########################################
def generate_invoice_gos(
    invoice_number,
    invoice_date,  # параметр, который перезаписывается ниже
    supplier_name,
    supplier_bin,
    supplier_address,
    supplier_bank_name,
    supplier_iik,
    supplier_bik,
    client_name,
    client_company,
    client_bin,      # БИН покупателя
    client_phone,
    client_address,
    contract_number,  # номер договора
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

    import os
    font_path = os.path.join(os.path.dirname(__file__), "assets", "DejaVuSans.ttf")
    bold_font_path = os.path.join(os.path.dirname(__file__), "assets", "DejaVuSans-Bold.ttf")
    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.add_font("DejaVu", "B", bold_font_path, uni=True)

    pdf.set_font("DejaVu", "", 9)
    attention_text = (
        "Внимание! Оплата данного счета означает согласие с условиями поставки товара. "
        "Уведомление об оплате обязательно, в противном случае не гарантируется наличие товара на складе. "
        "Товар отпускается по факту прихода денег на р/с Поставщика, самовывозом/доставкой, "
        "при наличии доверенности и документов, удостоверяющих личность."
    )
    pdf.multi_cell(0, 5, attention_text)
    pdf.ln(3)
    # ... продолжение вашего кода ...
    pdf.set_font("DejaVu", "B", 9)
    pdf.cell(0, 5, "Образец платежного поручения", ln=True, align="L")
    pdf.ln(2)
    pdf.set_font("DejaVu", "", 9)
    # Первая строка: три столбца (Бенефициар, ИИК, Кбе)
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
    # Вторая строка: банк, БИК, Код назначения платежа
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
    # Таблица товаров (оставляем без изменений)
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
    import os
    
    # Построение абсолютных путей для печати и подписи
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

###############################################
# Объединение сервисов через вкладки
###############################################
# Оборачиваем весь код сервиса маржинальности в функцию, чтобы он выполнялся только во вкладке "Калькулятор маржинальности"
def run_margin_service():
    # --- Блок "Данные клиента" (компактный вариант)
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
    
    # --- Блок "Данные по сделке" (компактный вариант)
    with st.expander("📌 Данные по сделке"):
        col1, col2 = st.columns(2)
        with col1:
            total_logistics = st.number_input("Общая стоимость логистики (₸)", min_value=0, value=0, format="%d")
        with col2:
            kickback = st.number_input("Откат клиенту (₸)", min_value=0, value=0, format="%d")
    
    # Хранение товаров
    if "products" not in st.session_state:
        st.session_state.products = []
    
    # --- Форма для добавления товаров (одна форма)
    st.subheader("🛒 Добавление товаров")
    with st.form("add_product_form"):
        # Две основные колонки: левая (общие поля), правая (поставщики)
        col_left, col_right = st.columns(2)
    
        with col_left:
            st.markdown("Наименование товара")
            name = st.text_input("", key="name", label_visibility="collapsed")
            st.markdown("Ед. измерения")
            unit = st.selectbox("", ["шт", "м", "кг", "км", "бухта", "рулон", "м²", "тонна"], key="unit", label_visibility="collapsed")
            st.markdown("Количество")
            quantity = st.number_input("", min_value=1, value=1, key="quantity", label_visibility="collapsed")
            st.markdown("Вес (кг)")
            weight = st.number_input("", min_value=0, value=0, format="%d", key="weight", label_visibility="collapsed")
    
        with col_right:
            # Ряд 1: Цена поставщика 1, Комментарий 1
            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                st.markdown('<p style="font-size:16px; margin-bottom:0px;">Цена поставщика 1 (₸)</p>', unsafe_allow_html=True)
                price1 = st.number_input("", min_value=0, value=0, format="%d", key="price_1", label_visibility="collapsed")
            with row1_col2:
                st.markdown("⠀")
                comment1 = st.text_input("", placeholder="Введите комментарий", key="comm_1", label_visibility="collapsed")
    
            # Ряд 2: Цена поставщика 2, Комментарий 2
            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                st.markdown('<p style="font-size:16px; margin-bottom:0px;">Цена поставщика 2 (₸)</p>', unsafe_allow_html=True)
                price2 = st.number_input("", min_value=0, value=0, format="%d", key="price_2", label_visibility="collapsed")
            with row2_col2:
                st.markdown("⠀")
                comment2 = st.text_input("", placeholder="Введите комментарий", key="comm_2", label_visibility="collapsed")
    
            # Ряд 3: Цена поставщика 3, Комментарий 3
            row3_col1, row3_col2 = st.columns(2)
            with row3_col1:
                st.markdown('<p style="font-size:16px; margin-bottom:0px;">Цена поставщика 3 (₸)</p>', unsafe_allow_html=True)
                price3 = st.number_input("", min_value=0, value=0, format="%d", key="price_3", label_visibility="collapsed")
            with row3_col2:
                st.markdown("⠀")
                comment3 = st.text_input("", placeholder="Введите комментарий", key="comm_3", label_visibility="collapsed")
    
            # Ряд 4: Цена поставщика 4, Комментарий 4
            row4_col1, row4_col2 = st.columns(2)
            with row4_col1:
                st.markdown('<p style="font-size:16px; margin-bottom:0px;">Цена поставщика 4 (₸)</p>', unsafe_allow_html=True)
                price4 = st.number_input("", min_value=0, value=0, format="%d", key="price_4", label_visibility="collapsed")
            with row4_col2:
                st.markdown("⠀")
                comment4 = st.text_input("", placeholder="Введите комментарий", key="comm_4", label_visibility="collapsed")
    
            # Ряд 5: Наценка (%)
            row5_col1, row5_col2, row5_col3 = st.columns([2,1,2])
            with row5_col1:
                st.markdown("Наценка (%)")
                markup = st.number_input("", min_value=0, value=20, format="%d", key="markup", label_visibility="collapsed")
            with row5_col2:
                st.markdown("")
            with row5_col3:
                st.markdown("")
    
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
    
    # --- Отображение товаров ---
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
                    st.write(f"**Цена для клиента:** {int(revenue):,} ₸")
                    st.write(f"**Себестоимость:** {int(cost_price):,} ₸")
                    st.write(f"**Наша маржа (наценка):** {int(margin):,} ₸")
                    st.write(f"**Наценка:** {product['Наценка (%)']}%")
                with col2:
                    st.write(f"**Цена поставщика (диапазон):** {int(min_supplier_price):,} – {int(max_supplier_price):,} ₸")
                    st.write(f"**Цена для клиента (за ед.):** {int(price_for_client):,} ₸")
                    if st.button("❌ Удалить товар", key=f"del_{index}"):
                        st.session_state.products.pop(index)
                        st.rerun()
    
    # --- Кнопка "Рассчитать" ---
    if st.button("📊 Рассчитать маржинальность"):
        if not st.session_state.products:
            st.warning("⚠️ Заполните данные для расчета!")
        else:
            df = pd.DataFrame(st.session_state.products)
            df["Мин. цена поставщика"] = df[
                [
                    "Цена поставщика 1",
                    "Цена поставщика 2",
                    "Цена поставщика 3",
                    "Цена поставщика 4",
                ]
            ].replace(0, float("inf")).min(axis=1).replace(float("inf"), 0)
            df["Цена для клиента"] = df["Мин. цена поставщика"] * (1 + df["Наценка (%)"] / 100)
            df["Выручка"] = df["Цена для клиента"] * df["Количество"]
            df["Себестоимость"] = df["Мин. цена поставщика"] * df["Количество"]
            df["Прибыль"] = df["Выручка"] - df["Себестоимость"]
            df["Маржинальность (%)"] = df["Прибыль"] / df["Выручка"] * 100
    
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
                marz_percent = 0 if math.isclose(total_revenue, 0, abs_tol=1e-9) else net_margin / total_revenue * 100
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
                    "Поле": ["ФИО клиента", "Название компании", "БИН клиента", "Телефон клиента", "Адрес доставки", "Договор (№)"],
                    "Значение": [client_name, client_company, client_bin, client_phone, client_address, client_contract],
                })
                client_data.to_excel(writer, index=False, sheet_name="Данные клиента")
    
                deal_data = pd.DataFrame({
                    "Поле": ["Общая стоимость логистики", "Откат клиенту"],
                    "Значение (₸)": [total_logistics, kickback],
                })
                deal_data.to_excel(writer, index=False, sheet_name="Данные сделки")
    
                df.to_excel(writer, index=False, sheet_name="Список товаров")
    
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
                        df["Прибыль"].sum() * 0.12,
                        net_margin,
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

###############################################
# Объединение сервисов через вкладки
###############################################
tab_margin, tab_logistics = st.tabs(["**Калькулятор маржинальности**", "**Калькулятор логистики**"])

with tab_margin:
    # Запускаем сервис маржинальности
    run_margin_service()
