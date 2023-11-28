from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery

from src.config import OWNER_IDS
from src.utils.excel import create_list_scammer
from src.keyboards.admin import get_admin_inline_keyboard


router = Router()


F: Message


@router.message(F.text == "Зайти в админку  📊")
async def open_admin(message: Message, bot: Bot):
    await message.answer("Вы зашли в админку \n\n"
                         "Выберите действие:", reply_markup=get_admin_inline_keyboard())


F: CallbackQuery


@router.callback_query(F.data == "get_scammer_list")
async def get_list_scammer(call: CallbackQuery, bot: Bot):
    await call.message.answer("Отправляю весь список скамеров...")
    await create_list_scammer()


@router.callback_query(F.data == "add_scammer")
async def start_add_scammer(call: CallbackQuery, bot: Bot):
    pass


@router.callback_query(F.data == "delete_scammer")
async def start_delete_scammer(call: CallbackQuery, bot: Bot):
    pass

