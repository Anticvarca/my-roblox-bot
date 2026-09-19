import os
import asyncio
from telethon import TelegramClient, events
import time

# ================= НАСТРОЙКИ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ =================
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
DESTINATION_CHANNEL = os.environ.get("DESTINATION_CHANNEL", "")

# Считываем чаты-источники (в Bothost мы передадим их одной строкой через запятую)
SOURCE_CHATS_RAW = os.environ.get("SOURCE_CHATS", "")
SOURCE_CHATS = [chat.strip() for chat in SOURCE_CHATS_RAW.split(",") if chat.strip()]

SESSION_NAME = "parser_session" # Имя файла сессии

# Ключевые слова
KEYWORDS = ['roblox.com/share']

# ================= ЛОГИКА =================
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

last_forward_time = 0
COOLDOWN_SECONDS = 30

@client.on(events.NewMessage(chats=SOURCE_CHATS))
async def handler(event):
    global last_forward_time
    
    message_text = event.message.message
    if not message_text:
        return

    text_lower = message_text.lower()
    
    if any(keyword.lower() in text_lower for keyword in KEYWORDS):
        current_time = time.time()
        if current_time - last_forward_time < COOLDOWN_SECONDS:
            return

        print(f"Найдено совпадение! Пересылаю в {DESTINATION_CHANNEL}...")
        
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
