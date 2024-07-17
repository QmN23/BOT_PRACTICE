import asyncio  # Импорт библиотеки для работы с асинхронностью
import aiosqlite  # Импорт библиотеки для работы с SQLite в асинхронном режиме
from aiogram import Bot, Dispatcher  # Импорт основных классов из aiogram
from app.handlers import router


# Функция инициализации базы данных
async def init_db():
    async with aiosqlite.connect('db/tasks.db') as db:  # Подключаемся к базе данных
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                user_id BIGINTEGER NOT NULL,  
                task TEXT NOT NULL,  
                completed BOOLEAN NOT NULL DEFAULT 0  
            )
        ''')
        await db.commit()  # Сохраняем изменения


# Основная функция
async def main():
    # Подключение API Telegram
    API_TOKEN = '7368625175:AAF9NI4jmv3Sn3B3JL1SWBlPbc-l93rEP1o'

    # Инициализация бота и диспетчера
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    dp.include_router(router)
    await init_db()  # Инициализация базы данных
    await dp.start_polling(bot)  # Запуск polling


# Запуск бота
if __name__ == '__main__':
    try:
        asyncio.run(main())  # Запуск основной функции
    except KeyboardInterrupt:  # Обработка прерывания
        print('Bot disabled')  # Вывод сообщения о завершении работы бота
