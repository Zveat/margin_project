# google_sheets_db.py (фрагмент)

def save_auth_state(spreadsheet_id, session_id, auth_state):
    """Сохраняет состояние авторизации в Google Sheets с привязкой к session_id."""
    sheet = get_or_create_spreadsheet(spreadsheet_id)
    auth_worksheet = sheet.worksheet("AuthState")  # Создаём или используем лист для состояния авторизации

    # Проверяем, есть ли запись для этой сессии
    all_auth = auth_worksheet.get_all_values()
    session_found = False
    for i, row in enumerate(all_auth, 1):
        if row[0] == session_id:
            # Обновляем существующую запись
            auth_worksheet.update_cell(i, 1, session_id)
            auth_worksheet.update_cell(i, 2, str(auth_state["authenticated"]).upper())  # Сохраняем как "TRUE" или "FALSE"
            auth_worksheet.update_cell(i, 3, auth_state["user"] or "")
            session_found = True
            break

    if not session_found:
        # Добавляем новую запись
        auth_worksheet.append_row([session_id, str(auth_state["authenticated"]).upper(), auth_state["user"] or ""])

def load_auth_state(spreadsheet_id, session_id):
    """Загружает состояние авторизации из Google Sheets по session_id."""
    sheet = get_or_create_spreadsheet(spreadsheet_id)
    auth_worksheet = sheet.worksheet("AuthState")

    all_auth = auth_worksheet.get_all_values()
    for row in all_auth:
        if row[0] == session_id:
            # Улучшенная обработка значения Authenticated (учитываем "TRUE", "True", "true")
            authenticated = row[1].strip().upper() in ["TRUE", "True", "true"]
            user = row[2].strip() if row[2] else ""
            print(f"Найдена запись для сессии {session_id}: authenticated={authenticated}, user={user}")
            return {
                "authenticated": authenticated,
                "user": user
            }
    print(f"Запись для сессии {session_id} не найдена, возвращаем состояние по умолчанию")
    return {"authenticated": False, "user": ""}
