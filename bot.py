import asyncio
import EasyGraph
import logging
import sys
from os import getenv
import re
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery , FSInputFile
from datetime import datetime
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, InputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keys = {}
with open('keys.conf', 'r') as f:
    exec(f.read(), keys)
bot = Bot(keys['TOKEN'])
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

def is_format(sting):
    return bool(re.fullmatch(r"[A-Za-z]+\s[A-Za-z]+\s\d+\n", sting))

def sorting(string):
    cleaned = string.replace(" ", "").replace("\n", "")
    result = [(cleaned[i], cleaned[i + 1], int(cleaned[i + 2])) for i in range(0, len(cleaned), 3)]
    sorted_result = []
    for a, b, weight in result:
        if a > b:
            sorted_result.append((b, a, weight))
        else:
            sorted_result.append((a, b, weight))
    return list(set(sorted_result))

class InputLinesAB(StatesGroup):
    pointA = State()
    pointB = State()
    graph = State()

class InputLinesABC(StatesGroup):
    pointA = State()
    pointB = State()
    pointC = State()
    graph = State()

# Команда /graph — меню с кнопками
@dp.message(Command("graph"))
async def send_menu(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Из точки А в Б", callback_data="btn1")],
            [InlineKeyboardButton(text="Из точки А в Б через В", callback_data="btn2")],
        ]
    )
    await message.answer("Выберите действие:", reply_markup=keyboard)

@dp.callback_query(F.data == "btn1")
async def handle_btn1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введите точку отправления:")
    await state.set_state(InputLinesAB.pointA)

@dp.message(InputLinesAB.pointA)
async def input_pointA_btn1(message: Message, state: FSMContext):
    await state.update_data(PointA=message.text)
    await message.answer("Введите точку прибытия:")
    await state.set_state(InputLinesAB.pointB)

@dp.message(InputLinesAB.pointB)
async def input_pointB_btn1(message: Message, state: FSMContext):
    await state.update_data(PointB=message.text)
    await message.answer("Введите граф в формате *Точка А* *Точка Б* *Расстояние*:")
    await state.set_state(InputLinesAB.graph)

@dp.message(InputLinesAB.graph)
async def input_graph_btn1(message: Message, state: FSMContext):
    await state.update_data(Graph=message.text)
    data = await state.get_data()

    graph = EasyGraph.EasyGraph(edges=sorting(data['Graph']))
    user_id = message.from_user.id
    temp = graph.task(pointA=data['PointA'], pointB=data['PointB'])
    text = graph.textmaker(route_length=temp[0], route=temp[1])
    graph.make(route=temp[1], filename=str(user_id))

    file_path = f"pics/{user_id}.png"
    graph_photo = FSInputFile(file_path)

    await message.answer_photo(graph_photo, caption=f"{text[0]}, {text[1]}")
    await state.clear()

@dp.callback_query(F.data == "btn2")
async def handle_btn2(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введите точку отправления:")
    await state.set_state(InputLinesABC.pointA)

@dp.message(InputLinesABC.pointA)
async def input_pointA_btn2(message: Message, state: FSMContext):
    await state.update_data(PointA=message.text)
    await message.answer("Введите точку прибытия:")
    await state.set_state(InputLinesABC.pointB)

@dp.message(InputLinesABC.pointB)
async def input_pointB_btn2(message: Message, state: FSMContext):
    await state.update_data(PointB=message.text)
    await message.answer("Введите точку, через которую лежит путь:")
    await state.set_state(InputLinesABC.pointC)

@dp.message(InputLinesABC.pointC)
async def input_pointC_btn2(message: Message, state: FSMContext):
    await state.update_data(PointC=message.text)
    await message.answer("Введите граф в формате *Точка А* *Точка Б* *Расстояние*:")
    await state.set_state(InputLinesABC.graph)

@dp.message(InputLinesABC.graph)
async def input_graph_btn2(message: Message, state: FSMContext):
    await state.update_data(Graph=message.text)
    data = await state.get_data()

    graph = EasyGraph.EasyGraph(edges=sorting(data['Graph']))
    user_id = message.from_user.id
    temp = graph.task(pointA=data['PointA'], pointB=data['PointB'], pointC=data['PointC'])
    text = graph.textmaker(route_length=temp[0], route=temp[1])
    graph.make(route=temp[1], filename=str(user_id))

    file_path = f"pics/{user_id}.png"
    graph_photo = FSInputFile(file_path)

    await message.answer_photo(graph_photo, caption=f"{text[0]}, {text[1]}")
    await state.clear()

@dp.message(Command("start"))
async def send_menu(message: Message):
    await message.answer("Привет, это бот для решения 4 номера из огэ по информатике и построения графа. Загляни в /help. Если ты знаешь как работать с ботом, то тебе в /graph")

@dp.message(Command("help"))
async def send_menu(message: Message):
    file_path = FSInputFile("pics/sample.png")
    await message.answer_photo(
        file_path,
        caption=(
            "На фото таблица путей с КИМ, но бот принимает таблицу графа только в таком формате:\n"
            "<pre>"
            "a b 5\n"
            "a c 3\n"
            "b a 5\n"
            "b c 1\n"
            "b d 4\n"
            "c a 3\n"
            "c b 1\n"
            "c d 6\n"
            "d b 4\n"
            "d c 6\n"
            "d e 1\n"
            "e d 1\n"
            "</pre>"
            "если все понятно, то за решением в /graph"
        ),
        parse_mode="HTML"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
