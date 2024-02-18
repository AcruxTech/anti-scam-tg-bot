import logging
import random

from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from src.config import MODERATOR_ID, OWNER_IDS

from src.keyboards.basic import (
    get_send_user_keyboard,
    get_main_menu_keyboard,
    get_send_media_scammer_keyboard,
    get_contact_cancel_keyboard,
    get_report_keyboard,
    get_send_channel_keyboard
)
from src.keyboards.menu import get_report_message
from src.messages import get_about_scammer_message

from src.entities.scammers.schemas import ScammerScheme, ScammerAnsweredScheme, ProofScheme
from src.entities.scammers.service import scammers_service
from src.entities.scammers.models import media_repository, proof_repository

from src.utils.callbacks import ProofMessage
from src.utils.scammers import get_scammer_data_from_message

scammer_router = Router()

F: Message


class AddScammerForm(StatesGroup):
    get_who_report = State()
    get_profile = State()
    add_profile = State()
    detect_hide_profile = State()
    get_username = State()
    get_proofs = State()
    get_media = State()
    add_scam_to_database = State()
    get_explanation = State()


@scammer_router.message(F.text == "Кинуть репорт  ✍")
async def send_scam_user(message: Message, bot: Bot, state: FSMContext):
    await message.answer(
        "На кого вы кидаете репорт?\n\n", reply_markup=get_report_keyboard()
    )
    await state.set_state(AddScammerForm.get_who_report)


@scammer_router.message(AddScammerForm.get_who_report, F.text == "На пользователя  👤")
async def send_scam_user(message: Message, bot: Bot, state: FSMContext):
    await message.answer(
        f"Перешли сообщение мошенника или отправь мне его контакт\n\n"
        f"Если нет такой возможности, то отправь мне его username", reply_markup=get_send_user_keyboard()
    )
    await state.set_state(AddScammerForm.get_profile)


@scammer_router.message(AddScammerForm.get_who_report, F.text == "На канал  📢")
async def send_scam_user(message: Message, bot: Bot, state: FSMContext):
    await message.answer(
        f"Перешли сообщение канала или отправь мне его через кнопку\n\n"
        f"Если нет такой возможности, то отправь мне его username", reply_markup=get_send_channel_keyboard()
    )
    await state.set_state(AddScammerForm.get_profile)


@scammer_router.message(F.text == "Назад")
async def back(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Возвращаю в главное меню...", reply_markup=get_main_menu_keyboard(message.from_user.id))
    await state.clear()


@scammer_router.message(AddScammerForm.get_profile)
async def get_scam(message: Message, bot: Bot, state: FSMContext):
    if message.user_shared or message.forward_from:
        await message.answer("Мы получили профиль пользователя ✅", reply_markup=get_contact_cancel_keyboard())
        scammer = get_scammer_data_from_message(message)

        await state.update_data(scammer=scammer)

        #if message.from_user.id in OWNER_IDS:
        await message.answer("Пришлите username пользователя:")
        await state.set_state(AddScammerForm.get_username)
        #else:
        #    await message.answer("Распиши ситуацию, которая произошла у тебя с мошенником:")
        #    await state.set_state(AddScammerForm.get_proofs)
    elif message.text:
        username = message.text.replace("https://t.me/", "").replace("@", "")
        scammer = ScammerScheme(id=random.randrange(1, 10000), username=username)

        scammer_existing = await scammers_service.get_scammer(scammer.id)

        while scammer_existing:
            scammer = ScammerScheme(id=random.randrange(1, 10000), username=username)
            scammer_existing = await scammers_service.get_scammer(scammer.id)

        await state.update_data(scammer=scammer)
        await message.answer("Распиши ситуацию, которая произошла у тебя с мошенником:")
        await state.set_state(AddScammerForm.get_proofs)
    elif message.chat_shared:
        scammer = get_scammer_data_from_message(message)
        await state.update_data(scammer=scammer)
        await message.answer("Распиши ситуацию, которая произошла у тебя с каналом:")
        await state.set_state(AddScammerForm.get_proofs)
    else:
        await message.answer(
            "Пользователь либо скрыл данные о себе, либо вы отправили что-то не то \n\n"
            "Отправьте его контакт с помощью кнопки ниже 👇👇👇",
            reply_markup=get_send_user_keyboard()
        )


@scammer_router.message(AddScammerForm.get_username)
async def get_username(message: Message, bot: Bot, state: FSMContext):
    if message.text:
        username = message.text.replace("https://t.me/", "").replace("@", "")
        data = await state.get_data()
        data["scammer"].username = username

        await state.update_data(scammer=data["scammer"])
        await message.answer("Распиши ситуацию, которая произошла у тебя с мошенником:")
        await state.set_state(AddScammerForm.get_proofs)
    else:
        await message.answer("Пожалуйста, отправьте корректный username")


@scammer_router.message(F.text == "Отправить репорт 🚩")
async def send_report(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()

    scammer = data.get("scammer")
    proof = data.get("proof")
    media = data.get("media")

    print("-" * 100)
    print(scammer)
    print(proof)
    print(media)

    if media:
        scammer_from_db, proof_from_db = await scammers_service.save(scammer, proof, media)
        await state.clear()
        await send_post_to_moderator_chat(message, bot, scammer_from_db, proof_from_db)
        await message.answer(
            "<b>Спасибо за обращение!</b>\n\n"
            "Ваша заявка на рассмотрении у модераторов, ожидайте…",
            reply_markup=get_main_menu_keyboard(message.from_user.id)
        )
    else:
        await message.answer("Загрузите хотя бы 1 фотографию или видео")


@scammer_router.message(F.text == "Сбросить фото 📸")
async def delete_media(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(media=None)
    await message.answer("Пруфы сброшены, можете загрузить новые", reply_markup=get_send_media_scammer_keyboard())


async def send_post_to_moderator_chat(
    message: Message,
    bot: Bot,
    scammer_from_db: ScammerScheme,
    proof_from_db: ProofScheme
):
    media = await media_repository.get_list(
        media_repository.model.proof_id == proof_from_db.id
    )

    album_builder = MediaGroupBuilder(
        caption=proof_from_db.text
    )

    for media_item in media:
        if media_item.type == "photo":
            album_builder.add_photo(media=media_item.file_id)
        elif media_item.type == "video":
            album_builder.add_video(media=media_item.file_id)

    about_scammer = get_about_scammer_message(scammer_from_db)

    await bot.send_message(
        MODERATOR_ID,
        f"Репорт от <b>@{message.from_user.username}</b> \n\n"
        f"На пользователя: \n\n"
        f"{about_scammer}  🛑"
    )

    await bot.send_media_group(MODERATOR_ID, album_builder.build())

    await bot.send_message(
        MODERATOR_ID, "Выберите действие:",
        reply_markup=get_report_message(message.from_user.id, proof_from_db.id, scammer_from_db.id)
    )


@scammer_router.callback_query(ProofMessage.filter())
async def accept_decision(call: CallbackQuery, bot: Bot, state: FSMContext, callback_data: ProofMessage):
    await proof_repository.update(
        {"decision": callback_data.decision, "moderator_id": call.from_user.id},
        callback_data.id,
    )

    if callback_data.decision:
        await scammers_service.confirm(callback_data.scammer_id)
        await bot.edit_message_text(
            f"{call.from_user.username} добавил мошенника в базу  ✅",
            call.message.chat.id,
            call.message.message_id
        )
        await bot.send_message(
            callback_data.user_id,
            "Мы рассмотрели ваш репорт на пользователя и занесли его в базу! 👮‍♂\n\n"
            "Благодарим за помощь в борьбе с мошенниками!  🤝"
        )
    else:
        await bot.edit_message_text(
            f"{call.from_user.username} отклонил данный репорт  ❌",
            call.message.chat.id,
            call.message.message_id
        )
        await bot.send_message(
            callback_data.user_id,
            f"Мы отклонили ваш репорт на пользователя! \n\n"
            f"Попробуйте подать новый репорт или написать в тех поддержку!"
        )

    await call.answer()


@scammer_router.message(AddScammerForm.get_media, F.video)
async def get_video(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    scammer_id = data["scammer"].id

    video_id = message.video.file_id

    media = data.get("media")

    media_item = {
        "file_id": video_id,
        "type": "video",
        "scammer_id": scammer_id
    }

    if media:
        media.append(media_item)
    else:
        media = [media_item]

    await state.update_data(media=media)

    await message.edit_reply_markup(
        reply_markup=get_send_media_scammer_keyboard()
    )


@scammer_router.message(AddScammerForm.get_media, F.photo)
async def get_photo(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    scammer_id = data["scammer"].id

    photo_id = message.photo[0].file_id

    media = data.get("media")

    media_item = {
        "file_id": photo_id,
        "type": "photo",
        "scammer_id": scammer_id
    }

    if media:
        media.append(media_item)
    else:
        media = [media_item]

    await state.update_data(media=media)

    await message.edit_reply_markup(
        reply_markup=get_send_media_scammer_keyboard()
    )


@scammer_router.message(AddScammerForm.get_proofs, F.text)
async def ask_proofs(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    scammer = data["scammer"]
    proof = ProofScheme(text=message.text, scammer_id=scammer.id, user_id=message.from_user.id)
    await message.answer(
        "Отправь фото/видео для доказательства скама 🖼 🎥 \n\n"
        "После отправки нажмите на кнопку ниже 👇👇👇",
        reply_markup=get_send_media_scammer_keyboard()
    )
    await state.update_data(proof=proof)
    await state.set_state(AddScammerForm.get_media)
