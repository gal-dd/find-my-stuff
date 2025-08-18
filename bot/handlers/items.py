from telegram import Update
from telegram.ext import ContextTypes
from ..states import ITEM_LOCATION
from .. import db
from ..telemetry import log_event
from .common import show_menu, get_user_id

async def handle_item_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    item_name = (update.message.text or "").strip()
    if not item_name:
        await update.message.reply_text("שם הפריט לא יכול להיות ריק. נסה שוב.")
        return None

    context.user_data["item_name"] = item_name
    action = context.user_data.get("action")
    user = get_user_id(update)

    if action == "create":
        log_event(user, "create_item_received", item=item_name)
        await update.message.reply_text(f"איפה תרצה לשמור את '{item_name}'?")
        return ITEM_LOCATION

    elif action == "read":
        loc = db.get_item(user, item_name)
        item_exists = loc is not None
        log_event(user, "read_item_received", item=item_name,
                  exists=item_exists, location=loc if item_exists else "item does not exist")
        if item_exists:
            await update.message.reply_text(f"החפץ '{item_name}' נמצא ב: {loc}")
        else:
            await update.message.reply_text(f"לא מצאתי את '{item_name}'")
        return await show_menu(update, context)

    elif action == "update":
        loc = db.get_item(user, item_name)
        item_exists = loc is not None
        log_event(user, "update_item_received", item=item_name,
                  exists=item_exists, location=loc if item_exists else "item does not exist")
        if loc is not None:
            await update.message.reply_text(f"איפה המיקום החדש של '{item_name}'?")
            return ITEM_LOCATION
        else:
            await update.message.reply_text(f"'{item_name}' לא נמצא במאגר.")
            return await show_menu(update, context)

    elif action == "delete":
        ok = db.delete_item(user, item_name)
        log_event(user, "delete_item_received", item=item_name, success=ok)
        if ok:
            await update.message.reply_text(f"'{item_name}' נמחק בהצלחה.")
        else:
            await update.message.reply_text(f"'{item_name}' לא נמצא במאגר.")
        return await show_menu(update, context)

    else:
        log_event(user, "unknown_action")
        await update.message.reply_text("פקודה לא קיימת")
        return None


async def handle_item_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = (update.message.text or "").strip()
    if not location:
        await update.message.reply_text("המיקום החדש לא יכול להיות ריק. נסה שוב.")
        return None

    item_name = context.user_data.get("item_name")
    action = context.user_data.get("action")
    user = get_user_id(update)

    if action == "create":
        db.upsert_item(user, item_name, location)
        log_event(user, "create_location", item=item_name, location=location)
        await update.message.reply_text(f"שמרתי את '{item_name}' ב-'{location}'")

    elif action == "update":
        db.upsert_item(user, item_name, location)
        log_event(user, "update_location", item=item_name, location=location)
        await update.message.reply_text(f"עדכנתי את '{item_name}' למיקום חדש: '{location}'")

    return await show_menu(update, context)
