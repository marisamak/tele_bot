import logging
import requests
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def get_meme():
    try:
        response = requests.get("https://api.imgflip.com/get_memes")
        logger.info(f"Код статуса ответа: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Полученные данные из API: {data}")
            if "data" in data and "memes" in data["data"]:
                memes = data["data"]["memes"]
                valid_memes = [meme['url'] for meme in memes if 'url' in meme]
                if valid_memes:
                    selected_meme = random.choice(valid_memes)  # Выбираем случайный мем
                    logger.info(f"Выбранный мем: {selected_meme}")
                    return selected_meme
                else:
                    logger.error("Ошибка: нет доступных мемов")
                    return None
            else:
                logger.error("Ошибка: ключ 'data' или 'memes' отсутствует в ответе")
                return None
        else:
            logger.error(f"Не удалось получить мемы, код состояния: {response.status_code}, ответ: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Ошибка при запросе мемов: {e}")
        return None

async def send_meme(query, meme_url):
    await query.edit_message_text(text="Вот мем:")
    try:
        logger.info(f"Отправка мема по URL: {meme_url}")
        await query.message.reply_photo(meme_url)
        logger.info(f"Мем отправлен: {meme_url}")
    except Exception as e:
        await query.edit_message_text(text="Не удалось отправить мем.")
        logger.error(f"Ошибка при отправке мема: {e}")

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Нажми кнопку, чтобы получить смешной мем!', reply_markup=main_menu())

def main_menu():
    keyboard = [[InlineKeyboardButton("Получить мем", callback_data='get_meme')]]
    return InlineKeyboardMarkup(keyboard)

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    logger.info(f"Получены данные кнопки: {query.data}")
    if query.data == 'get_meme':
        meme_url = get_meme()
        logger.info(f"Полученный URL мема: {meme_url}")
        if meme_url:
            await send_meme(query, meme_url)
        else:
            await query.edit_message_text(text="Не удалось получить мем.")

async def error(update: Update, context: CallbackContext) -> None:
    logger.warning('Обновление "%s" вызвало ошибку "%s"', update, context.error)
    if context.error:
        logger.error(f"Ошибка: {context.error}")

def main() -> None:
    application = ApplicationBuilder().token("7699217478:AAFUr0XgcKt7geSXYOBePx858OzjsFJl82s").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_error_handler(error)
    application.run_polling()

if __name__ == '__main__':
    main()

# ПОЯСНЕНИЕ РАБОТЫ БОТА:

# 1. Импорт модулей:
# logging: для ведения логов, которые помогут отследить работу и ошибки бота.
# requests: для отправки HTTP-запросов к API, чтобы получать данные о мемах.
# random: для выбора случайного мема из полученных данных.
# telegram и telegram.ext: основные модули библиотеки python-telegram-bot, которые нужны для создания
#                          и обработки команд и взаимодействий бота.

# 2. Настройка логирования:
# Устанавливает формат и уровень логирования. Здесь логгер будет выводить сообщения уровня INFO и выше.
# logger используется для записи логов в течение работы кода.

# 3. Функция get_meme():
# Отправляет запрос к API imgflip для получения списка мемов.
# Проверка статуса ответа: Если код ответа 200 (успех), бот обрабатывает данные; если нет, записывается ошибка.
# Извлечение мемов: Если в данных API есть ключи 'data' и 'memes', сохраняет URL всех мемов.
# Выбор случайного мема: С помощью random.choice выбирается один случайный мем из списка.
# Если данные или URL мемов отсутствуют, логируется соответствующая ошибка.

# 4. Функция send_meme():
# query.edit_message_text: Обновляет сообщение с текстом "Вот мем:".
# Пытается отправить фото по полученному meme_url.
# Если отправка фото успешна, логирует URL отправленного мема. Если возникает ошибка,
# бот выводит сообщение об ошибке и логирует её.

# 5. Функция start():
# Отправляет сообщение с текстом и кнопкой, вызывая main_menu(), чтобы показать клавиатуру.


# 6. Функция main_menu():
# Создаёт клавиатуру с одной кнопкой "Получить мем". Нажатие на эту кнопку отправляет данные callback_data='get_meme'.

# 7. Функция button():
# Принимает данные из нажатой кнопки.
# await query.answer(): подтверждает нажатие кнопки для Telegram.
# Если кнопка get_meme, бот вызывает get_meme() для получения URL случайного мема.
# Если URL мема получен, бот вызывает send_meme для отправки картинки.
# Если URL отсутствует, выводится сообщение об ошибке.

# 8. Функция error():
# Логирует ошибки, возникшие во время обработки обновлений от Telegram.

# 9. Функция main():
# СОЗДАНИЕ ПРИЛОЖЕНИЯ: использует токен для создания экземпляра бота.
# РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ:
# CommandHandler для команды /start.
# CallbackQueryHandler для обработки нажатий кнопок.
# add_error_handler для обработки ошибок.
# ЗАПУСК БОТА: run_polling() запускает постоянный опрос Telegram на предмет новых сообщений.

# 10. Запуск бота:
# Убедившись, что файл выполняется как главный, запускает бота.
