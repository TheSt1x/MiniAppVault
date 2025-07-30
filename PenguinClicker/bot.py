from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio
import json
import logging
import os
STATS_FILE = "stats.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_TOKEN = "BOT_TOKEN"
if not API_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

MINI_APP_URL = "https://kk59k8cw-3000.euw.devtunnels.ms/"

def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(
        text="🎮 Открыть игру", 
        web_app=types.WebAppInfo(url=MINI_APP_URL)
    )
    builder.button(text="ℹ️ Помощь")
    builder.button(text="📊 Статистика")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

async def on_startup():
    logger.info("Бот запущен")
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Запустить бота"),
        types.BotCommand(command="help", description="Помощь"),
        types.BotCommand(command="stats", description="Статистика")
    ])

async def on_shutdown():
    logger.info("Бот остановлен")

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    welcome_text = (
        f"Привет, {user.first_name}!\n\n"
        "🐧 Добро пожаловать в Пингвин Кликер!\n"
        "Нажми кнопку ниже, чтобы открыть игру и начать собирать рыбу!"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu()
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "ℹ️ <b>Помощь по игре Пингвин Кликер</b>\n\n"
        "🎮 <b>Как играть:</b>\n"
        "- Нажимай на пингвина, чтобы собирать рыбу\n"
        "- Улучшай удочку для большего дохода\n"
        "- Покупай улучшения в магазине\n\n"
        "🛒 <b>Магазин улучшений:</b>\n"
        "- Пассивные: генерируют рыбу автоматически\n"
        "- Активные: увеличивают доход за клик\n\n"
        "📊 Для просмотра статистики используй /stats"
    )
    await message.answer(help_text, parse_mode="HTML")

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    stats_text = (
        "📊 <b>Ваша статистика:</b>\n\n"
        "🐟 Всего собрано рыбы: <b>0</b>\n"
        "🔼 Максимальный уровень: <b>1</b>\n"
        "⏱ Пассивный доход: <b>0/сек</b>"
    )
    await message.answer(stats_text, parse_mode="HTML")
Я 
@dp.message(lambda message: message.text == "ℹ️ Помощь")
async def btn_help(message: types.Message):
    await cmd_help(message)

@dp.message(lambda message: message.text == "📊 Статистика")
async def btn_stats(message: types.Message):
    await cmd_stats(message)

@dp.message(lambda message: message.web_app_data is not None)
async def process_web_app_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        user_id = message.from_user.id
        
        logger.info(f"Получены данные от пользователя {user_id}: {data}")
        
        if data.get("action") == "save_game":
            score = data.get("score", 0)
            level = data.get("level", 1)
            await message.answer(
                f"🎮 Игра сохранена!\n"
                f"🐟 Рыбы: {score}\n"
                f"🔼 Уровень: {level}",
                reply_markup=get_main_menu()
            )
        elif data.get("action") == "purchase":
            item = data.get("item")
            await message.answer(f"✅ Успешно куплено: {item}")
            
    except json.JSONDecodeError:
        await message.answer("❌ Ошибка обработки данных")
    except Exception as e:
        logger.error(f"Ошибка обработки web_app_data: {e}")
        await message.answer("❌ Произошла ошибка")

@dp.message()
async def other_messages(message: types.Message):
    await message.answer(
        "Я не понимаю эту команду. Используйте меню или /help",
        reply_markup=get_main_menu()
    )

async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())