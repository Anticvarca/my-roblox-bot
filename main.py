import os
import asyncio
import time
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityTextUrl

# ================= НАСТРОЙКИ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ =================
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
DESTINATION_CHANNEL = os.environ.get("DESTINATION_CHANNEL", "")

# Считываем чаты-источники (в Bothost мы передадим их одной строкой через запятую)
SOURCE_CHATS_RAW = os.environ.get("SOURCE_CHATS", "")
SOURCE_CHATS = [chat.strip() for chat in SOURCE_CHATS_RAW.split(",") if chat.strip()]

SESSION_NAME = "parser_session" # Имя файла сессии

# ================= ЛОГИКА =================
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

last_forward_time = 0
COOLDOWN_SECONDS = 30

@client.on(events.NewMessage(chats=SOURCE_CHATS))
async def handler(event):
    global last_forward_time
    
    message_text = event.message.message or ""
    has_roblox_link = False

    # 1. Проверяем обычный текст (если ссылка написана прямо в сообщении)
    if 'roblox.com/share' in message_text.lower():
        has_roblox_link = True

    # 2. Проверяем скрытые ссылки (когда ссылка спрятана за словом "тык", "тут" и т.д.)
    if event.message.entities:
        for entity in event.message.entities:
            # Проверяем, является ли сущность скрытой ссылкой
            if isinstance(entity, MessageEntityTextUrl):
                # Проверяем, ведет ли эта скрытая ссылка на Roblox
                if entity.url and 'roblox.com/share' in entity.url.lower():
                    has_roblox_link = True
                    break

    # Если нашли ссылку (видимую или скрытую) - пересылаем
    if has_roblox_link:
        current_time = time.time()
        
        # Проверка задержки (чтобы не спамить)
        if current_time - last_forward_time < COOLDOWN_SECONDS:
            return

        print(f"Найдена ссылка! Пересылаю в {DESTINATION_CHANNEL}...")
        
        try:
            await event.message.forward_to(DESTINATION_CHANNEL)
            last_forward_time = current_time
            print("Успешно переслано!")
        except Exception as e:
            print(f"Ошибка при пересылке: {e}")

async def main():
    print("Запуск бота на Bothost...")
    # Запускаем клиент. Если файл .session загружен, ввод данных не потребуется.
    await client.start()
    print("Бот успешно запущен и слушает новые сообщения!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
