import asyncio
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, MenuButtonCommands
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, ConversationHandler, filters
)
from telegram.error import BadRequest


import db  # our SQLite layer

# Conversation states
ACTION, ITEM_NAME, ITEM_LOCATION = range(3)

# Use single-user for now; we'll flip to per-user in step 2
USER = "local"

# --- Helpers ---

async def show_menu(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu after a short delay."""
    await asyncio.sleep(1)

    keyboard = [
        [InlineKeyboardButton("📥 שמירת חפץ חדש", callback_data="create")],
        [InlineKeyboardButton("🔍 חיפוש חפץ", callback_data="read")],
        [InlineKeyboardButton("♻️ עדכון מיקום של חפץ", callback_data="update")],
        [InlineKeyboardButton("🗑️ מחיקת מיקום של חפץ", callback_data="delete")],
        [InlineKeyboardButton("📋 צפייה בכל החפצים", callback_data="list")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Always send a NEW message (don't edit), keeps history & avoids "not modified".
    if isinstance(update_or_query, Update) and update_or_query.message:
        await update_or_query.message.reply_text("בחר פעולה:", reply_markup=reply_markup)
    else:
        await update_or_query.message.reply_text("בחר פעולה:", reply_markup=reply_markup)

    return ACTION


def format_items_list_emojis(rows: list[tuple[str, str]]) -> str:
    """Emoji list, sorted + numbered. rows: [(item, location), ...]"""
    if not rows:
        return "אין חפצים שמורים כרגע."
    lines = []
    for i, (item, loc) in enumerate(sorted(rows, key=lambda x: x[0]), start=1):
        lines.append(f"#️⃣ {i}\n📦 {item}\n📍 {loc}\n")
    return "📋 כל החפצים\n\n" + "\n".join(lines)

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await show_menu(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action = query.data
    context.user_data["action"] = action

    if action == "create":
        await query.message.reply_text("מה שם החפץ שברצונך לשמור?")
        return ITEM_NAME

    elif action == "read":
        await query.message.reply_text("מה שם החפץ שברצונך לחפש?")
        return ITEM_NAME

    elif action == "update":
        # Submenu for update
        sub_keyboard = [
            [InlineKeyboardButton("📋 הצגת כל הפריטים", callback_data="update_show_all")],
            [InlineKeyboardButton("⌨️ הקלד פריט", callback_data="update_type_item")],
        ]
        await query.message.reply_text("בחר אפשרות לעדכון:", reply_markup=InlineKeyboardMarkup(sub_keyboard))
        return ACTION

    elif action == "delete":
        await query.message.reply_text("מה שם החפץ שברצונך למחוק?")
        return ITEM_NAME

    elif action == "list":
        rows = db.list_items(USER)
        msg = format_items_list_emojis(rows)
        await query.message.reply_text(msg)
        return await show_menu(query, context)

    # --- Update submenu callbacks ---
    elif action == "update_show_all":
        rows = db.list_items(USER)
        if rows:
            names = "\n".join(f"- {item}" for item, _ in rows)
            await query.message.reply_text(
                f"הנה כל הפריטים:\n{names}\n\nשלח את שם הפריט שברצונך לעדכן:"
            )
            context.user_data["action"] = "update"
            return ITEM_NAME  # stay waiting for item name
        else:
            await query.message.reply_text("אין פריטים לעדכן.")
            return await show_menu(query, context)

    elif action == "update_type_item":
        await query.message.reply_text("שלח את שם הפריט שברצונך לעדכן:")
        context.user_data["action"] = "update"
        return ITEM_NAME

async def handle_item_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    item_name = (update.message.text or "").strip()
    # Input guard
    if not item_name:
        await update.message.reply_text("שם הפריט לא יכול להיות ריק. נסה שוב.")
        return ITEM_NAME

    context.user_data["item_name"] = item_name
    action = context.user_data.get("action")

    if action == "create":
        await update.message.reply_text(f"איפה תרצה לשמור את '{item_name}'?")
        return ITEM_LOCATION

    elif action == "read":
        loc = db.get_item(USER, item_name)
        if loc:
            await update.message.reply_text(f"החפץ '{item_name}' נמצא ב: {loc}")
        else:
            await update.message.reply_text(f"לא מצאתי את '{item_name}'")
        return await show_menu(update, context)

    elif action == "update":
        loc = db.get_item(USER, item_name)
        if loc is not None:
            await update.message.reply_text(f"איפה המיקום החדש של '{item_name}'?")
            return ITEM_LOCATION
        else:
            await update.message.reply_text(f"'{item_name}' לא נמצא במאגר.")
            return await show_menu(update, context)

    elif action == "delete":
        ok = db.delete_item(USER, item_name)
        if ok:
            await update.message.reply_text(f"'{item_name}' נמחק בהצלחה.")
        else:
            await update.message.reply_text(f"'{item_name}' לא נמצא במאגר.")
        return await show_menu(update, context)

async def handle_item_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = (update.message.text or "").strip()
    # Input guard
    if not location:
        await update.message.reply_text("המיקום החדש לא יכול להיות ריק. נסה שוב.")
        return ITEM_LOCATION

    item_name = context.user_data.get("item_name")
    action = context.user_data.get("action")

    if action == "create":
        db.upsert_item(USER, item_name, location)
        await update.message.reply_text(f"שמרתי את '{item_name}' ב-'{location}'")

    elif action == "update":
        db.upsert_item(USER, item_name, location)
        await update.message.reply_text(f"עדכנתי את '{item_name}' למיקום חדש: '{location}'")

    return await show_menu(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("בוטל.")
    return await show_menu(update, context)

async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    err = context.error
    # Ignore harmless no-op edit error
    if isinstance(err, BadRequest) and "Message is not modified" in str(err):
        return
    # Log others
    print(f"[ERROR] {err!r}")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
3. תמיד תוכל ללחוץ על הכפתור *ביטול פעולה* או לשלוח /cancel

💡 טיפ: ניתן גם לבחור פקודות מהתפריט של השורת הקלט (ליד כפתור האימוג'ים)

"""

    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")



async def post_init(app):
    # Commands appear in the input menu; names must be latin/underscored
    await app.bot.set_my_commands([
        BotCommand("start",  "הצגת התפריט"),
        BotCommand("cancel", "ביטול פעולה"),
        BotCommand("help",   "עזרה")
    ])
    # Ensure the chat menu button shows the command list
    await app.bot.set_chat_menu_button(menu_button=MenuButtonCommands())



def main():
    # Load token from .env
    load_dotenv()
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set in environment (.env)")

    # Init DB
    db.init_db()

    app = Application.builder().token(token).post_init(post_init).build()
    app.add_error_handler(on_error)


    conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        ACTION: [CallbackQueryHandler(button_handler)],
        ITEM_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_item_name)],
        ITEM_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_item_location)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    # per_message=True,       # <-- add this to silence the warning
    allow_reentry=True,     # optional: lets users /start again mid-convo
)


    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
