from aiogram.types import Message


def get_start_message(message: Message) -> str:
    start_message = f"""
<b>AntiSkamBot</b> – твой <b>незаменимый помощник</b> во время работы в телеграмме. 

<b>Проверяй</b> исполнителя услуг на честность <b>с помощью нашего бота.</b>

<b>Узнавай больше про ТГ:</b> @keroytg / Rakhimov ВЕЩАЕТ (https://t.me/+PXCfc4FyhMVjMzQ6)

<b>Агентство</b> – Space Agency (https://t.me/spaceagency1)

<b>Чат партнеров</b> – Админские Веселья (https://t.me/+qNqoUOqi3-gzM2Yy)
"""
    return start_message


def get_start_message_old(message: Message) -> str:
    start_message = f"""Привет, <b>{message.from_user.first_name}</b>! 👋
    
Я бот 🤖, который занимается проверкой мошеников, и могу предоставить тебе:
    
- Информацию о степени надежности и доверия к человеку, предоставляющего услуги в Telegram по ID ℹ👨‍💻️
    
- Возможность добавить скамера в базу мошенников ✍️🚫"""
    return start_message
