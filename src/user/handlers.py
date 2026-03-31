import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes

from src.handlers import main_keyboard
from src.templates.renderer import render
from src.user.service import is_valid_email, set_user_email

logger = logging.getLogger(__name__)


async def setemail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /setemail user@example.com"""
    args = context.args
    if not args:
        await update.message.reply_text(
            "Использование: /setemail your@email.com",
            reply_markup=main_keyboard,
        )
        return

    email = args[0].strip()
    if not is_valid_email(email):
        await update.message.reply_text(
            render("email_set_invalid.md"),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_keyboard,
        )
        return

    success = await set_user_email(update.effective_user.id, email)
    if success:
        await update.message.reply_text(
            render("email_set_success.md", email=email),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_keyboard,
        )
    else:
        await update.message.reply_text(
            "Ошибка при сохранении email. Попробуйте снова. ❌",
            reply_markup=main_keyboard,
        )


def register_user_handlers(application):
    application.add_handler(CommandHandler("setemail", setemail))
