import asyncio
from telegram import Update, BotCommand, MenuButtonCommands
from telegram.error import BadRequest
from telegram.ext import ContextTypes
from ..states import ACTION
from ..keyboards import main_menu_kb
from ..config import MENU_DELAY_SEC, MULTI_USER

HELP_TEXT = """
🤖 *Find My Stuff* – עוזר אישי למציאת חפצים בבית

הבוט שומר ומנהל רשימה של חפצים ומיקומם, כדי שלא תשכח איפה שמת כל דבר.

📋 *מה אפשר לעשות?*
- 📥 *שמירת חפץ חדש* – שמירת פריט חדש ומיקומו
- 🔍 *חיפוש חפץ* – מציאת המיקום של פריט שכבר שמור
- ♻️ *עדכון מיקום של חפץ* – שינוי מיקום של פריט קיים
- 🗑️ *מחיקת מיקום של חפץ* – מחיקת פריט מהרשימה
- 📋 *צפייה בכל החפצים* – הצגת כל הפריטים והיכן הם נמצאים

🛠 *איך משתמשים?*
1. שלח את הפקודה /start ובחר פעולה מתפריט הכפתורים
2. עקוב אחרי ההוראות שהבוט ישאל אותך
3. תמיד תוכל לשלוח /cancel כדי לבטל פעולה

💡 טיפ: ניתן לבחור פקודות גם מהתפריט בשורת הקלט.
"""

def get_user_id(update: Update) -> str:
    if MULTI_USER and update.effective_user:
        return str(update.effective_user.id)
    return "local"

async def show_menu(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu after a short delay (always send a NEW message)."""
    await asyncio.sleep(MENU_DELAY_SEC)
    kb = main_menu_kb()
    if isinstance(update_or_query, Update) and update_or_query.message:
        await update_or_query.message.reply_text("בחר פעולה:", reply_markup=kb)
    else:
        await update_or_query.message.reply_text("בחר פעולה:", reply_markup=kb)
    return ACTION

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await show_menu(update, context)

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("בוטל.")
    return await show_menu(update, context)

async def post_init(app):
    await app.bot.set_my_commands([
        BotCommand("start",  "הצגת התפריט"),
        BotCommand("help",   "עזרה"),
        BotCommand("cancel", "ביטול פעולה"),
    ])
    await app.bot.set_chat_menu_button(menu_button=MenuButtonCommands())

async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    err = context.error
    if isinstance(err, BadRequest) and "Message is not modified" in str(err):
        return
    print(f"[ERROR] {err!r}")
