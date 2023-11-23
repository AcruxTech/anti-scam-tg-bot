from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from src.config import TECH_SUPPORT_ID
from src.keyboards.menu import get_contact_answer
from src.keyboards.basic import get_contact_cancel_keyboard, get_main_menu_keyboard
from src.utils.callbacks import ContactMessage
from src.entities.contact.service import contact_message_service


class ContactState(StatesGroup):
    get_contact_text = State()
    get_text_for_contact = State()


router = Router()


F: Message


@router.message(F.text == "Связаться с нами  📞")
async def start_contact(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Напишите сообщение и мы ответим на него! 👇👇👇", reply_markup=get_contact_cancel_keyboard())
    await state.set_state(ContactState.get_contact_text)


@router.message(ContactState.get_contact_text, F.text == "Назад")
async def back(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Возвращаю в главное меню...", reply_markup=get_main_menu_keyboard())
    await state.clear()


@router.message(ContactState.get_contact_text, F.text)
async def get_text_contact(message: Message, bot: Bot, state: FSMContext):
    await bot.send_message(TECH_SUPPORT_ID, text=f"Пришло сообщение от <b>{message.from_user.username}</b>:")
    contact_message = await contact_message_service.create_contact_message(message.from_user.id, message.text)
    await bot.send_message(
        TECH_SUPPORT_ID, text=f"<b>{message.from_user.username}</b>: {message.text}",
        reply_markup=get_contact_answer(contact_message_id=contact_message.id)
    )
    await message.answer(
        "Спасибо за вопрос! Мы ответим на него как можно скорее!",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()


F: CallbackQuery


@router.callback_query(ContactMessage.filter())
async def answer_to_contact(callback: CallbackQuery, callback_data: ContactMessage, state: FSMContext):
    await callback.message.answer("Напишите сообщению пользователю:")
    await state.update_data(contact_message_id=callback_data.id)
    await state.set_state(ContactState.get_text_for_contact)


F: Message


@router.message(ContactState.get_text_for_contact, F.text)
async def send_message_to_contact(message: Message, bot: Bot, state: FSMContext):
    contact_data = await state.get_data()
    contact_message_id = contact_data["contact_message_id"]
    contact_message = await contact_message_service.answer_contact_message(
        contact_message_id, message.text, message.from_user.id
    )
    await message.answer("Ответ был отправлен пользователю  ✅")
    await bot.send_message(
        contact_message.contact_id, text=f"Мы ответили на твой вопрос: <b>{contact_message.message}</b>"
    )
    await bot.send_message(
        contact_message.contact_id, text=f"Ответ от модератора: <b>{message.text}</b>",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()
