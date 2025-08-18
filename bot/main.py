from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters
)
from .config import BOT_TOKEN, BASE_DIR
from .states import ACTION, ITEM_NAME, ITEM_LOCATION
from .handlers.common import start, cmd_help, cancel, post_init, on_error
from .handlers.menu import button_handler
from .handlers.items import handle_item_name, handle_item_location
from . import db
from .logging_config import setup_logging

def build_app():
    setup_logging(BASE_DIR)

    db.init_db()

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_error_handler(on_error)

    # /help is available always
    app.add_handler(CommandHandler("help", cmd_help))

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ACTION: [CallbackQueryHandler(button_handler)],
            ITEM_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_item_name)],
            ITEM_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_item_location)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    app.add_handler(conv)
    return app

def main():
    app = build_app()
    app.run_polling()

if __name__ == "__main__":
    main()
