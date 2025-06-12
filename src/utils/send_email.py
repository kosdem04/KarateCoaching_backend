import os
from email.message import EmailMessage
from aiosmtplib import SMTP
from src.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

async def send_registration_email(to_email: str, password: str):
    message = EmailMessage()
    message["From"] = SMTP_USER
    message["To"] = to_email
    message["Subject"] = "Добро пожаловать в Karate Coaching!"

    message.set_content(
        f"""Здравствуйте!

Ваш аккаунт на сайте https://karate-coaching.ru был успешно создан.
Ваши данные для входа:

Логин: {to_email}
Пароль: {password}

"""
    )

    smtp = SMTP(hostname=SMTP_HOST, port=SMTP_PORT, use_tls=True)

    await smtp.connect()
    await smtp.login(SMTP_USER, SMTP_PASSWORD)
    await smtp.send_message(message)
    await smtp.quit()



async def send_reset_password_email(to_email: str, code: str):
    message = EmailMessage()
    message["From"] = SMTP_USER
    message["To"] = to_email
    message["Subject"] = "Смена пароля на сайте Karate Coaching!"

    message.set_content(
        f"""Здравствуйте!

Вы запросили смену пароля на сайте https://karate-coaching.ru
Ваш код для смены пароля: {code}

P.S. Если вы получили это сообщение по ошибке, просто удалите его.

"""
    )

    smtp = SMTP(hostname=SMTP_HOST, port=SMTP_PORT, use_tls=True)

    await smtp.connect()
    await smtp.login(SMTP_USER, SMTP_PASSWORD)
    await smtp.send_message(message)
    await smtp.quit()