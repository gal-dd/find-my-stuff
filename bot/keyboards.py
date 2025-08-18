from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📥 שמירת חפץ חדש", callback_data="create")],
        [InlineKeyboardButton("🔍 חיפוש חפץ", callback_data="read")],
        [InlineKeyboardButton("♻️ עדכון מיקום של חפץ", callback_data="update")],
        [InlineKeyboardButton("🗑️ מחיקת מיקום של חפץ", callback_data="delete")],
        [InlineKeyboardButton("📋 צפייה בכל החפצים", callback_data="list")],
    ]
    return InlineKeyboardMarkup(keyboard)

def update_submenu_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📋 הצגת כל הפריטים", callback_data="update_show_all")],
        [InlineKeyboardButton("⌨️ הקלד פריט", callback_data="update_type_item")],
    ]
    return InlineKeyboardMarkup(keyboard)
