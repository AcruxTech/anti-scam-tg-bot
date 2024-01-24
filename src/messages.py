from aiogram.types import Message


def get_start_message(message: Message) -> str:
    start_message = f"""
Наш надёжный <b>AntiSkamBot</b> служит мощным инструментом для проверки достоверности исполнителя услуг.

Узнавай больше про ТГ: @keroytg

Чат партнеров – <a href="https://t.me/+qNqoUOqi3-gzM2Yy">Админские Веселья</a>
"""
    return start_message


def get_start_message_old(message: Message) -> str:
    start_message = f"""Привет, <b>{message.from_user.first_name}</b>! 👋
    
Я бот 🤖, который занимается проверкой мошеников, и могу предоставить тебе:
    
- Информацию о степени надежности и доверия к человеку, предоставляющего услуги в Telegram по ID ℹ👨‍💻️
    
- Возможность добавить скамера в базу мошенников ✍️🚫"""
    return start_message
