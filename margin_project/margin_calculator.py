def run_margin_service():
    st.markdown(
        """
        <style>
        .margin-container {
            max-width: 750px !important;  /* Или ваше текущее значение, например, 1200px */
            margin: 0 auto !important;
            padding: 20px !important;
        }
        /* Стили для колонок внутри контейнера */
        .margin-container .stColumns > div {
            flex: 1 !important;
            min-width: 0 !important;
            max-width: 50% !important;  /* Равномерное распределение ширины колонок */
            display: flex !important;    /* Добавляем flex для вертикального выравнивания */
            flex-direction: column !important;  /* Стек элементов вертикально */
            justify-content: center !important; /* Центрируем содержимое по вертикали */
            align-items: stretch !important;    /* Растягиваем элементы по высоте */
        }
        /* Стили для внутренних элементов колонок (поля ввода, кнопки и т.д.) */
        .margin-container .stNumberInput, 
        .margin-container .stTextInput, 
        .margin-container .stSelectbox {
            width: 100% !important;
            margin: 0 !important;
            height: 40px !important;  /* Фиксированная высота для полей */
        }
        .margin-container div[data-testid="stNumberInput"] input,
        .margin-container div[data-testid="stTextInput"] input,
        .margin-container div[data-testid="stSelectbox"] select {
            width: 100% !important;
            min-height: 40px !important;  /* Фиксированная минимальная высота */
            padding: 4px 6px !important;
            font-size: 14px !important;
            box-sizing: border-box !important;  /* Учитываем padding в общей ширине */
            line-height: 1.5 !important;  /* Унифицируем высоту текста */
        }
        /* Стили для меток (markdown) внутри колонок */
        .margin-container p {
            margin: 0 !important;
            font-size: 14px !important;
            line-height: 1.2 !important;
            height: 20px !important;  /* Фиксированная высота для меток */
            display: flex !important;
            align-items: center !important;  /* Центрируем текст вертикально */
        }
        /* Стили для кнопки формы */
        .margin-container div.stButton > button {
            width: 100% !important;
            margin-top: 10px !important;
            padding: 10px !important;
            height: 40px !important;  /* Фиксированная высота для кнопки */
        }
        /* Убираем лишние отступы у внутренних элементов */
        .margin-container .stForm {
            padding: 0 !important;
        }
        </style>
        <div class="margin-container">
        """,
        unsafe_allow_html=True
    )

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
            st.markdown("⠀")  # Пустая метка для выравнивания

        with col_right:
            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                st.markdown('<p style="font-size:14px; margin-bottom:0px;">Цена поставщика 1 (₸)</p>', unsafe_allow_html=True)
                price1 = st.number_input("", min_value=0, value=0, format="%d", key="price_1", label_visibility="collapsed")
            with row1_col2:
                st.markdown("⠀")
                comment1 = st.text_input("", placeholder="Комментарий", key="comm_1", label_visibility="collapsed")

            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                st.markdown('<p style="font-size:14px; margin-bottom:0px;">Цена поставщика 2 (₸)</p>', unsafe_allow_html=True)
                price2 = st.number_input("", min_value=0, value=0, format="%d", key="price_2", label_visibility="collapsed")
            with row2_col2:
                st.markdown("⠀")
                comment2 = st.text_input("", placeholder="Комментарий", key="comm_2", label_visibility="collapsed")

            row3_col1, row3_col2 = st.columns(2)
            with row3_col1:
                st.markdown('<p style="font-size:14px; margin-bottom:0px;">Цена поставщика 3 (₸)</p>', unsafe_allow_html=True)
                price3 = st.number_input("", min_value=0, value=0, format="%d", key="price_3", label_visibility="collapsed")
            with row3_col2:
                st.markdown("⠀")
                comment3 = st.text_input("", placeholder="Комментарий", key="comm_3", label_visibility="collapsed")

            row4_col1, row4_col2 = st.columns(2)
            with row4_col1:
                st.markdown('<p style="font-size:14px; margin-bottom:0px;">Цена поставщика 4 (₸)</p>', unsafe_allow_html=True)
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
            st.warning("Введите название товара ⚠️ ")

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
                    if st.button("❌ Удалить товар", key=f"del_{index}"):
                        st.session_state.products.pop(index)
                        st.rerun()

    if st.button("📊 Рассчитать маржинальность"):
        if not st.session_state.products:
            st.warning("⚠️ Список товаров пуст. Добавьте хотя бы один товар.")
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
                marz_percent = net_margin / total_revenue * 100 if total_revenue > 0 else 0
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
                    "Поле": ["ФИО клиента", "Название компании", "БИН клиента", 
                             "Телефон клиента", "Адрес доставки", "Договор (№)"],
                    "Значение": [client_name, client_company, client_bin, 
                                 client_phone, client_address, client_contract],
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
                        tax_nds,
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

    st.markdown("</div>", unsafe_allow_html=True)
