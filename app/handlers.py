from aiogram import Router
from aiogram.types import Message  # Импорт класса Message
from aiogram.filters import CommandStart, Command  # Импорт фильтров команд
import aiosqlite  # Импорт библиотеки для работы с SQLite в асинхронном режиме

router = Router()


# Обработчик команды /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет! Я бот для управления задачами. Используй команды /add, /list, /done и /delete.')


# Обработчик команды /add

async def cmd_add(message: Message):
    user_id = message.from_user.id  # Получаем ID пользователя
    text = message.text[len("/add "):].strip()  # Получение аргументов после команды /add
    if text:
        async with aiosqlite.connect('db/tasks.db') as db:  # Подключаемся к базе данных
            await db.execute('INSERT INTO tasks (user_id, task) VALUES (?, ?)', (user_id, text))  # Добавляем задачу
            await db.commit()  # Сохраняем изменения
        await message.reply(f'Задача "{text}" добавлена.')
        await list_tasks(message)  # Вывод списка задач после добавления
    else:
        await message.reply('Использование: /add <текст задачи>')


# Обработчик команды /list

async def cmd_list(message: Message):
    user_id = message.from_user.id  # Получаем ID пользователя
    await list_tasks(message)  # Вызываем функцию для вывода списка задач


# Функция для вывода списка задач
async def list_tasks(message: Message):
    user_id = message.from_user.id  # Получаем ID пользователя
    async with aiosqlite.connect('db/tasks.db') as db:  # Подключаемся к базе данных
        async with db.execute('SELECT id, task, completed FROM tasks WHERE user_id = ? ORDER BY id',
                              (user_id,)) as cursor:
            tasks = await cursor.fetchall()  # Получаем все задачи пользователя

    if tasks:
        # Формируем список задач с порядковыми номерами
        task_list = '\n'.join([f'{idx + 1}. {"[X]" if task[2] else "[ ]"} {task[1]}' for idx, task in enumerate(tasks)])
        await message.reply(f'Ваши задачи:\n{task_list}')
    else:
        await message.reply('У вас нет задач.')


# Обработчик команды /done
@router.message(Command('done'))
async def cmd_done(message: Message):
    user_id = message.from_user.id  # Получаем ID пользователя
    task_number = message.text[len("/done "):].strip()  # Получение аргументов после команды /done
    if task_number.isdigit():  # Проверяем, что аргумент является числом
        task_number = int(task_number)
        async with aiosqlite.connect('db/tasks.db') as db:  # Подключаемся к базе данных
            async with db.execute('SELECT id FROM tasks WHERE user_id = ? ORDER BY id', (user_id,)) as cursor:
                tasks = await cursor.fetchall()  # Получаем все задачи пользователя
                if 0 < task_number <= len(tasks):  # Проверяем, что номер задачи корректен
                    task_id = tasks[task_number - 1][0]  # Получаем ID задачи из базы данных
                    await db.execute('UPDATE tasks SET completed = 1 WHERE id = ? AND user_id = ?', (task_id, user_id))
                    await db.commit()  # Сохраняем изменения
                    await message.reply(f'Задача {task_number} отмечена как выполненная.')
                    await list_tasks(message)  # Вывод списка задач после отметки выполненной задачи
                else:
                    await message.reply('Неверный номер задачи.')
    else:
        await message.reply('Использование: /done <номер задачи>')


# Обработчик команды /delete
@router.message(Command('delete'))
async def cmd_delete(message: Message):
    user_id = message.from_user.id  # Получаем ID пользователя
    task_number = message.text[len("/delete "):].strip()  # Получение аргументов после команды /delete
    if task_number.isdigit():  # Проверяем, что аргумент является числом
        task_number = int(task_number)
        async with aiosqlite.connect('db/tasks.db') as db:  # Подключаемся к базе данных
            async with db.execute('SELECT id FROM tasks WHERE user_id = ? ORDER BY id', (user_id,)) as cursor:
                tasks = await cursor.fetchall()  # Получаем все задачи пользователя
                if 0 < task_number <= len(tasks):  # Проверяем, что номер задачи корректен
                    task_id = tasks[task_number - 1][0]  # Получаем ID задачи из базы данных
                    await db.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
                    await db.commit()  # Сохраняем изменения

                    # Если после удаления задач больше нет, сбросим AUTOINCREMENT
                    async with db.execute('SELECT COUNT(*) FROM tasks WHERE user_id = ?', (user_id,)) as cursor:
                        count = await cursor.fetchone()  # Получаем количество задач пользователя
                        if count[0] == 0:  # Если задач нет
                            await db.execute('DELETE FROM sqlite_sequence WHERE name="tasks"')
                            await db.commit()  # Сбрасываем AUTOINCREMENT

                    await message.reply(f'Задача {task_number} удалена.')
                    await list_tasks(message)  # Вывод списка задач после удаления задачи
                else:
                    await message.reply('Неверный номер задачи.')
    else:
        await message.reply('Использование: /delete <номер задачи>')
