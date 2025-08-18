from telegram import Update
from telegram.ext import ContextTypes
from ..keyboards import update_submenu_kb
from ..states import ACTION, ITEM_NAME
from ..formatting import format_items_list_emojis
from .. import db
from ..telemetry import log_event
from .common import show_menu, get_user_id

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    action = query.data
    context.user_data["action"] = action
    user = get_user_id(update)
    log_event(user, "menu_click", choice=action)

    if action == "create":
        log_event(user, "prompt_item_name", flow=action)
        await query.message.reply_text("מה שם החפץ שברצונך לשמור?")
        return ITEM_NAME

    elif action == "read":
        log_event(user, "prompt_item_name", flow=action)
        await query.message.reply_text("מה שם החפץ שברצונך לחפש?")
        return ITEM_NAME

    elif action == "update":
        log_event(user, "open_update_submenu")
        await query.message.reply_text("בחר אפשרות לעדכון:", reply_markup=update_submenu_kb())
        return ACTION

    elif action == "delete":
        log_event(user, "prompt_item_name", flow=action)
        await query.message.reply_text("מה שם החפץ שברצונך למחוק?")
        return ITEM_NAME

    elif action == "list":
        rows = db.list_items(user)
        log_event(user, "list_items", count=len(rows))
        msg = format_items_list_emojis(rows)
        await query.message.reply_text(msg)
        return await show_menu(query, context)

    # Update submenu
    elif action == "update_show_all":
        rows = db.list_items(user)
        log_event(user, "list_items", count=len(rows))
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
        log_event(user, "update_type_item")
        await query.message.reply_text("שלח את שם הפריט שברצונך לעדכן:")
        context.user_data["action"] = "update"
        return ITEM_NAME

    else:
        await query.message.reply_text("פקודה לא קיימת")
        return None
