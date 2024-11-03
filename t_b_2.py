import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, CallbackContext

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# Получаем список мемов
def get_memes():
    try:
        response = requests.get("https://api.imgflip.com/get_memes")
        logger.info(f"Статус код ответа: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"Полученные данные из API: {data}")

            if "data" in data:
                memes = data["data"]
                return [{'url': meme['image_url']} for meme in memes if 'image_url' in meme]
            else:
                logger.error("Ошибка: ключ 'data' отсутствует в ответе")
                return []
        else:
            logger.error(f"Не удалось получить мемы, статус код: {response.status_code}, ответ: {response.text}")
            return []
    except Exception as e:
        logger.error(f"Ошибка при запросе мемов: {e}")
        return []



# Функция для отправки мемов
async def send_meme(query, meme):
    await query.edit_message_text(text="Вот мем:")
    try:
        logger.info(f"Отправка мема по URL: {meme['url']}")
        await query.message.reply_photo(meme['url'])  # Отправляем изображение
        logger.info(f"Мем отправлен: {meme['url']}")
    except Exception as e:
        await query.edit_message_text(text="Не удалось отправить мем.")
        logger.error(f"Ошибка при отправке мема: {e}")


# Обработчик команды /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Нажми кнопку, чтобы получить смешной мем!', reply_markup=main_menu())


# Генерируем меню с кнопкой
def main_menu():
    keyboard = [[InlineKeyboardButton("Получить мем", callback_data='get_meme')]]
    return InlineKeyboardMarkup(keyboard)


# Обработчик нажатия кнопки
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    logger.info(f"Получены данные кнопки: {query.data}")

    if query.data == 'get_meme':
        memes = get_memes()  # Получаем мемы
        logger.info(f"Полученные мемы: {memes}")

        if memes:
            meme = memes[0]  # Выбираем первый мем
            await send_meme(query, meme)
        else:
            await query.edit_message_text(text="Не удалось получить мемы.")


# Определяем ошибку
async def error(update: Update, context: CallbackContext) -> None:
    logger.warning('Обновление "%s" вызвало ошибку "%s"', update, context.error)
    if context.error:
        logger.error(f"Ошибка: {context.error}")


def main() -> None:
    application = ApplicationBuilder().token("7699217478:AAFUr0XgcKt7geSXYOBePx858OzjsFJl82s").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    application.add_error_handler(error)

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()
