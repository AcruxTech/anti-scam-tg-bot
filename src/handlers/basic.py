from aiogram import Bot, Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command

from src.messages import get_start_message
from src.keyboards.basic import get_main_menu_keyboard
from src.entities.users.schemas import UserScheme
from src.entities.users.service import user_service
from src.entities.scammers.service import scammers_service

basic_router = Router()

F: Message


@basic_router.message(Command("start"))
async def start(message: Message, bot: Bot):
    photo_path = r"./media/systems/menu.png"
    await message.answer_photo(
        FSInputFile(photo_path),
        caption=get_start_message(message),
        reply_markup=get_main_menu_keyboard(message.from_user.id)
    )
    user = UserScheme(**message.from_user.model_dump())
    await user_service.add_user(user)


@basic_router.message(F.user_shared)
async def get_contact(message: Message, bot: Bot):
    scammer = await scammers_service.get_scammer(message.user_shared.user_id)

    info_about_scammer = f"<b>Информация о пользователе:</b>\n\n" \
                         f"ID = <code>{message.user_shared.user_id}</code>"

    if scammer and scammer.is_scam:
        scammer_message = "Этот пользователь - скаммер!   ❌"
        if scammer.username:
            info_about_scammer += f"\n\nUsername = <code>{scammer.username}</code>"

        if scammer.first_name:
            info_about_scammer += f"\n\nFirst Name = <code>{scammer.first_name}</code>"
    else:
        scammer_message = "Данный пользователь не был найден в базе, но будьте осторожны"

    await message.answer(f"{scammer_message}\n\n"
                         f"{info_about_scammer}")

    