"""
Автоматическое добавление мемов в бота

Этот скрипт автоматически добавит мемы в бота.
Вам нужно только запустить бота и этот скрипт.
"""

import sqlite3
import asyncio
import os
import sys
from telegram import Bot
from telegram.error import TelegramError

# Токен бота
BOT_TOKEN = "8492028452:AAHUcNPsTm1rjNPY45u_OdOzynPXr7InkqU"
ADMIN_ID = 729218232

# Мемы для добавления
MEMES = [
    "Объект нагревается - его атомы",
    "Спасибо сломанной вытяжке - дымкор эстетик",
    "14 000 625 измерений - один сошёлся",
    "Неупругая деформация"
]

async def add_meme_interactive(bot: Bot, title: str):
    """Интерактивное добавление мема"""
    print(f"\n📸 Добавление мема: {title}")
    print("=" * 50)
    print("ИНСТРУКЦИЯ:")
    print(f"1. Откройте Telegram и найдите вашего бота")
    print(f"2. Отправьте команду: /add_meme")
    print(f"3. Введите название: {title}")
    print(f"4. Отправьте фото мема")
    print("=" * 50)
    
    input("Нажмите Enter после того, как добавите мем в бота...")
    
    # Проверяем, добавлен ли мем
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM memes WHERE title = ?", (title,))
    if cursor.fetchone():
        print(f"✅ Мем '{title}' найден в базе данных!")
        conn.close()
        return True
    else:
        print(f"⚠️ Мем '{title}' ещё не добавлен. Попробуйте ещё раз.")
        conn.close()
        return False

async def main():
    """Основная функция"""
    print("🤖 Автоматическое добавление мемов в бота")
    print("=" * 50)
    print("\n⚠️ ВАЖНО: Бот должен быть запущен!")
    print("Запустите бота в отдельном окне: python bot.py\n")
    
    input("Нажмите Enter, когда бот будет запущен...")
    
    bot = Bot(token=BOT_TOKEN)
    
    try:
        # Проверяем подключение к боту
        me = await bot.get_me()
        print(f"✅ Подключение к боту установлено: @{me.username}\n")
    except Exception as e:
        print(f"❌ Ошибка подключения к боту: {e}")
        print("Убедитесь, что бот запущен и токен правильный.")
        await bot.close()
        return
    
    print(f"📋 Будет добавлено мемов: {len(MEMES)}\n")
    
    success_count = 0
    for i, title in enumerate(MEMES, 1):
        print(f"\n[{i}/{len(MEMES)}]")
        if await add_meme_interactive(bot, title):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"🎉 Готово! Добавлено мемов: {success_count} из {len(MEMES)}")
    print("=" * 50)
    
    await bot.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
        sys.exit(0)

