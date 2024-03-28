from aiogram import Dispatcher, Router, Bot, F
from aiogram.types import Message, CallbackQuery, BotCommand
from aiogram.filters import Command, CommandObject
import matplotlib.pyplot as plt
import os
from aiogram.types.input_file import FSInputFile
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

from .parser import top_10_tounaments, count_games, get_graph_command, rating_of_commands


_router = Router()
_commands = [
    BotCommand(command='start', description='Начать'), # d
    BotCommand(command='help', description='Помощь'), # d
    BotCommand(command='top10_i', description='Показать топ-10 турниров для игрока, давших наибольшее число очков'), # d
    BotCommand(command='top10_t', description='Показать топ-10 турниров для команды, давших наибольшее число очков'), # d
    BotCommand(command='rating_10', description='Показать топ-10 команд игрока по рейтингу'), # d
    BotCommand(command='rating', description='Показать все команды игрока по рейтингу'), # d
    BotCommand(command='teams_10', description='Показать топ-10 команд по числу участий в них игрока'), # d
    BotCommand(command='teams', description='Показать, в каких командах участвовал игрок'), # d
    BotCommand(command='graph_i', description='Показать график активности игрока'), # d
    BotCommand(command='graph_t', description='Показать график активности команды') # d
]
wait = {}

start_kb = [
    [KeyboardButton(text="1. Топ-10 турниров команды")],  # d
    [KeyboardButton(text="2. Топ-10 турниров игрока")],  # d
    [KeyboardButton(text="3. Топ-10 команд игрока по рейтингу")],  # d
    [KeyboardButton(text="4. Топ-10 команд игрока по его числу участий")],  # d
    [KeyboardButton(text="5. Все команды игрока по рейтингу")],  # d
    [KeyboardButton(text="6. Все команды игрока по его числу участий")],  # d
    [KeyboardButton(text="7. График активности игрока")],  # d
    [KeyboardButton(text="8. График активности команды")]  # d
]
start_keyboard = ReplyKeyboardMarkup(keyboard=start_kb, resize_keyboard=True)
bot = None

async def setup_bot_and_dispatcher(bot_: Bot, dispatcher: Dispatcher) -> None:
    await bot_.set_my_commands(_commands)
    dispatcher.include_router(_router)
    global bot
    bot = bot_


@_router.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    # await message.answer("Привет! Это бот для просмотра статистики по ЧГК! Выбери, что хочешь сделать:", reply_markup=keyboard)
    photo = FSInputFile("logo.yellow.png")
    await bot.send_photo(message.chat.id, photo, caption="Привет! Это бот для просмотра статистики по ЧГК! Выбери, что хочешь сделать:", reply_markup=start_keyboard)


@_router.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    await message.answer("Этот бот предоставляет различную информацию о игроках и командах ЧГК. Воспользуйся клавиатурой, или напиши команду из 'Меню', и id после нее через пробел")


@_router.message(Command("top10_i"))
async def command_top10_i_handler(message: Message, command: CommandObject) -> None:
    command_args = command.args

    if command_args and command_args.strip().isdigit():
        await top10_f(message, command_args.strip(), 0)
    else:
        await message.answer("Пожалуйста, укажите id игрока после команды /top10_i")


@_router.message(Command("top10_t"))
async def command_top10_t_handler(message: Message, command: CommandObject) -> None:
    command_args = command.args

    if command_args and command_args.strip().isdigit():
        await top10_f(message, command_args.strip(), 1)
    else:
        await message.answer("Пожалуйста, укажите id команды после команды /top10_t")


async def top10_f(message, id, t):
    wait_message = await message.answer("Ожидайте...")
    try:
        data = await top_10_tounaments(id, t)
    except:
        await wait_message.edit_text("Неверный id :(")
        return

    formatted_strings = []
    for entry in data:
        formatted_strings.append(", ".join(map(str, entry)))

    result = "\n".join([f"{i + 1}. {string}" for i, string in enumerate(formatted_strings)])

    await wait_message.edit_text("Имя турнира, дата, D:\n" + result)


@_router.message(Command("teams"))
async def teams_handler(message: Message, command: CommandObject) -> None:
    command_args = command.args

    if command_args and command_args.strip().isdigit():
        await teams_f(message, command_args.strip())
    else:
        await message.answer("Пожалуйста, укажите id игрока после команды /teams")


@_router.message(Command("teams_10"))
async def teams_10_handler(message: Message, command: CommandObject) -> None:
    command_args = command.args

    if command_args and command_args.strip().isdigit():
        await teams_f(message, command_args.strip(), ten=True)
    else:
        await message.answer("Пожалуйста, укажите id игрока после команды /teams_10")


async def teams_f(message, id, ten=False):
    wait_message = await message.answer("Ожидайте...")
    try:
        data = await count_games(id)
    except:
        await wait_message.edit_text("Неверный id :(")
        return

    if ten:
        data = data[:10]

    formatted_strings = []
    for entry in data:
        formatted_strings.append(", ".join(map(str, entry)))

    result = "\n".join([f"{i + 1}. {string}" for i, string in enumerate(formatted_strings)])

    await wait_message.edit_text("Название команды (город), количество игр:\n" + result)


@_router.message(Command("graph_i"))
async def graph_i_handler(message: Message, command: CommandObject) -> None:
    command_args = command.args

    if command_args and command_args.strip().isdigit():
        await graph_f(message, command_args.strip(), 0, "График за последний год")
    else:
        await message.answer("Пожалуйста, укажите id игрока после команды /graph_i")


@_router.message(Command("graph_t"))
async def graph_t_handler(message: Message, command: CommandObject) -> None:
    command_args = command.args

    if command_args and command_args.strip().isdigit():
        await graph_f(message, command_args.strip(), 1, "График за последний год")
    else:
        await message.answer("Пожалуйста, укажите id команды после команды /graph_t")


@_router.callback_query(F.data.startswith('График за последние пол года'))
async def process_callback(callback_query: CallbackQuery):
    _, a, b = list(callback_query.data.split(';'))
    await graph_f(callback_query.message, int(a), int(b), 'График за последние пол года')


@_router.callback_query(F.data.startswith('График за последний год'))
async def process_callback(callback_query: CallbackQuery):
    _, a, b = list(callback_query.data.split(';'))
    await graph_f(callback_query.message, int(a), int(b), 'График за последний год')


@_router.callback_query(F.data.startswith('График за последние 2 года'))
async def process_callback(callback_query: CallbackQuery):
    _, a, b = list(callback_query.data.split(';'))
    await graph_f(callback_query.message, int(a), int(b), 'График за последние 2 года')


@_router.callback_query(F.data.startswith('График за все время'))
async def process_callback(callback_query: CallbackQuery):
    _, a, b = list(callback_query.data.split(';'))
    await graph_f(callback_query.message, int(a), int(b), 'График за все время')


async def filter_dates(start_date, end_date, d1_list, d2_list):
    filtered_dates = []
    for date, value in zip(d1_list, d2_list):
        if start_date <= date <= end_date:
            filtered_dates.append((date.strftime('%m-%Y'), value))
    return filtered_dates


async def graph_f(message, id, t, tm):
    try:
        d1, d2 = await get_graph_command(id, t)
    except:
        await message.answer("Неверный id :(")
        return

    times = ["График за последние пол года", "График за последний год", "График за последние 2 года", "График за все время"]
    times.remove(tm)

    buttons = [InlineKeyboardButton(text=i, callback_data=i+';'+str(id)+';'+str(t)) for i in times]
    graph_keyboard = InlineKeyboardMarkup(inline_keyboard=[[buttons[0]], [buttons[1]], [buttons[2]]])

    if tm == "График за все время":
        plt.figure(figsize=(30, 15))
    else:
        d1_datetime = [datetime.strptime(date, '%m-%Y') for date in d1]
        current_date = datetime.now()
        smf = []
        if tm == "График за последние пол года":
            half_year_start = current_date - timedelta(days=182)
            smf = await filter_dates(half_year_start, current_date, d1_datetime, d2)
            plt.figure(figsize=(12, 9))
        if tm == "График за последний год":
            last_year_start = current_date - timedelta(days=365)
            smf = await filter_dates(last_year_start, current_date, d1_datetime, d2)
            plt.figure(figsize=(12, 9))
        elif tm == "График за последние 2 года":
            two_years_start = current_date - timedelta(days=365 * 2)
            smf = await filter_dates(two_years_start, current_date, d1_datetime, d2)
            plt.figure(figsize=(12, 9))
        d1 = [item[0] for item in smf]
        d2 = [item[1] for item in smf]

    plt.bar(d1, d2)
    plt.title('Количество игр в каждом месяце')
    plt.xlabel('Месяц-Год')
    plt.ylabel('Количество игр')
    plt.xticks(rotation=45)
    plt.margins(x=0)
    plt.tight_layout()
    plt.savefig(str(message.chat.id) + '.png')

    photo = FSInputFile(str(message.chat.id) + '.png')
    await bot.send_document(message.chat.id, photo, caption=tm, reply_markup=graph_keyboard)

    os.remove(str(message.chat.id) + '.png')


@_router.message(Command("rating_10"))
async def rating_10_handler(message: Message, command: CommandObject) -> None:
    command_args = command.args

    if command_args and command_args.strip().isdigit():
        await rating_f(message, command_args.strip(), ten=True)
    else:
        await message.answer("Пожалуйста, укажите id игрока после команды /rating_10")


@_router.message(Command("rating"))
async def rating_handler(message: Message, command: CommandObject) -> None:
    command_args = command.args

    if command_args and command_args.strip().isdigit():
        await rating_f(message, command_args.strip())
    else:
        await message.answer("Пожалуйста, укажите id игрока после команды /rating")


async def rating_f(message, id, ten=False):
    wait_message = await message.answer("Ожидайте...")

    try:
        data = await rating_of_commands(id)
    except:
        await wait_message.edit_text("Неверный id :(")
        return

    if ten:
        data = data[:10]

    formatted_strings = []
    for entry in data:
        formatted_strings.append(", ".join(map(str, entry)))

    result = "\n".join([f"{i + 1}. {string}" for i, string in enumerate(formatted_strings)])

    await wait_message.edit_text("Название команды (город), рейтинг:\n" + result)


@_router.message()
async def handle_text_message(message: Message):
    if message.text == "1. Топ-10 турниров команды":
        await message.answer("Окей, а теперь напиши id команды, о котором ты хочешь узнать")
        wait[message.chat.id] = 1
    elif message.text == "2. Топ-10 турниров игрока":
        await message.answer("Окей, а теперь напиши id игрока, о котором ты хочешь узнать")
        wait[message.chat.id] = 2
    elif message.text == "3. Топ-10 команд игрока по рейтингу":
        await message.answer("Окей, а теперь напиши id игрока, о котором ты хочешь узнать")
        wait[message.chat.id] = 3
    elif message.text == "4. Топ-10 команд игрока по его числу участий":
        await message.answer("Окей, а теперь напиши id игрока, о котором ты хочешь узнать")
        wait[message.chat.id] = 4
    elif message.text == "5. Все команды игрока по рейтингу":
        await message.answer("Окей, а теперь напиши id игрока, о котором ты хочешь узнать")
        wait[message.chat.id] = 5
    elif message.text == "6. Все команды игрока по его числу участий":
        await message.answer("Окей, а теперь напиши id игрока, о котором ты хочешь узнать")
        wait[message.chat.id] = 6
    elif message.text == "7. График активности игрока":
        await message.answer("Окей, а теперь напиши id игрока, о котором ты хочешь узнать")
        wait[message.chat.id] = 7
    elif message.text == "8. График активности команды":
        await message.answer("Окей, а теперь напиши id команды, о котором ты хочешь узнать")
        wait[message.chat.id] = 8
    else:
        if message.text.isdigit():
            if wait[message.chat.id] == 1:
                await top10_f(message, message.text, 1)
            if wait[message.chat.id] == 2:
                await top10_f(message, message.text, 0)
            if wait[message.chat.id] == 3:
                await rating_f(message, message.text, ten=True)
            if wait[message.chat.id] == 4:
                await teams_f(message, message.text, ten=True)
            if wait[message.chat.id] == 5:
                await rating_f(message, message.text)
            if wait[message.chat.id] == 6:
                await teams_f(message, message.text)
            if wait[message.chat.id] == 7:
                await graph_f(message, message.text, 0, "График за последний год")
            if wait[message.chat.id] == 8:
                await graph_f(message, message.text, 1, "График за последний год")
            wait[message.chat.id] = 0
