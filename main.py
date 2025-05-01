from telegram import Update, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os
import logging
from ai_api import ask_openrouter 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message and update.message.text:
            user_id = update.effective_user.id
            user_name = update.effective_user.username
            logger.info(f"Пользователь {user_id} ({user_name}) вызвал команду /start")
            keyboard = [
            [InlineKeyboardButton("Помощь", callback_data="help")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Привет! Я твой бот. Напиши что-нибудь или выбери действие:", reply_markup=reply_markup) 
        else:
            logger.warning(f"Получено сообщение без текста от пользователя {user_id} ({user_name})")
    except Exception as e:
        logger.error(f"Ошибка в обработчике команды /start: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        user_name = update.effective_user.username
        logger.info(f"Команда /help вызвана пользователем {user_id} ({user_name})")
        await update.message.reply_text(
                "Вот список доступных команд:\n"
                "/start — начать работу с ботом\n"
                "/help — получить список команд"
            )
    except Exception as e:
        logger.error(f"Ошибка в обработчике команды /help: {e}")
        await update.message.reply_text("Извините, произошла ошибка. Попробуйте позже.")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message and update.message.text:
            user_message = update.message.text
            if update.effective_user:
                user_id = update.effective_user.id
                logger.info(f"Получено сообщение от пользователя {user_id}: {user_message}")
            else:
                user_id = "Неизвестный"
                logger.info(f"Получено сообщение от неизвестного пользователя: {user_message}")

            try:
                response = await ask_openrouter(user_message)
                await update.message.reply_text(response)
            except Exception as e:
                logger.error(f"Ошибка при обращении к API: {e}")
                await update.message.reply_text("Произошла ошибка при обращении к API.")
        else:
            if update.effective_user:
                logger.warning(f"Получено сообщение без текста от пользователя {update.effective_user.id}")
            else:
                logger.warning("Получено сообщение без текста от неизвестного пользователя")
            await update.message.reply_text("Извините, я могу обрабатывать только текстовые сообщения.")
    except Exception as e:
        if update.effective_user:
            logger.error(f"Ошибка в обработчике текстового сообщения для пользователя {update.effective_user.id}: {e}")
        else:
            logger.error(f"Ошибка в обработчике текстового сообщения: {e}")

if __name__=="__main__":
    try:
        load_dotenv()
        logger.info("Загрузка переменных окружения из .env")


        TOKEN = os.getenv("BOT_TOKEN")


        if not TOKEN:
            raise ValueError("Токен бота не найден. Проверьте файл .env и переменную BOT_TOKEN.")

        app = ApplicationBuilder().token(TOKEN).build()
        commands = [
            BotCommand("start", "Начать работу с ботом"),
            BotCommand("help", "Получить список команд")
        ]
        app.bot.set_my_commands(commands)

        app.add_handler(CommandHandler("start",start))
        app.add_handler(CommandHandler("help",help_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

        logger.info("Запуск бота...")
        app.run_polling()
    except Exception as e:
         logger.critical(f"Критическая ошибка при запуске бота: {e}", exc_info=True)