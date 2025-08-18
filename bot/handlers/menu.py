from telegram import Update
from telegram.ext import ContextTypes
from ..keyboards import update_submenu_kb
from ..states import ACTION, ITEM_NAME
from ..formatting import format_items_list_emojis
from .. import db
from .common import show_menu, get_user_id

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.effective_user.id)

    query = update.callback_query
    await query.answer()

    action = query.data
    context.user_data["action"] = action
    user = get_user_id(update)

    if action == "create":
        await query.message.reply_text("מה שם החפץ שברצונך לשמור?")
        return ITEM_NAME

    elif action == "read":
        await query.message.reply_text("מה שם החפץ שברצונך לחפש?")
        return ITEM_NAME

    elif action == "update":
        await query.message.reply_text("בחר אפשרות לעדכון:", reply_markup=update_submenu_kb())
        return ACTION

    elif action == "delete":
        await query.message.reply_text("מה שם החפץ שברצונך למחוק?")
        return ITEM_NAME

    elif action == "list":
        rows = db.list_items(user)
        msg = format_items_list_emojis(rows)
        await query.message.reply_text(msg)
        return await show_menu(query, context)

    # Update submenu
    elif action == "update_show_all":
        rows = db.list_items(user)
        if rows:
            names = "\n".join(f"{i}. {item}" for i, (item, _) in enumerate(rows, 1))
            await query.message.reply_text(
                f"הנה כל הפריטים:\n{names}\n\nשלח את שם הפריט שברצונך לעדכן:"
            )
            context.user_data["action"] = "update"
            return ITEM_NAME
        else:
            await query.message.reply_text("אין פריטים לעדכן.")
            return await show_menu(query, context)

    elif action == "update_type_item":
        await query.message.reply_text("שלח את שם הפריט שברצונך לעדכן:")
        context.user_data["action"] = "update"
        return ITEM_NAME

    else:
        await query.message.reply_text("פקודה לא קיימת")
        return None
