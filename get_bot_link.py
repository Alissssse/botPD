"""
Получение ссылки на бота
"""

import asyncio
from telegram import Bot

# Токен бота
BOT_TOKEN = "8492028452:AAHUcNPsTm1rjNPY45u_OdOzynPXr7InkqU"

async def get_bot_info():
    """Получает информацию о боте и создаёт ссылку"""
    bot = Bot(token=BOT_TOKEN)
    
    try:
        me = await bot.get_me()
        username = me.username
        first_name = me.first_name
        
        if username:
            bot_link = f"https://t.me/{username}"
            print("=" * 60)
            print("ИНФОРМАЦИЯ О БОТЕ")
            print("=" * 60)
            print(f"Имя: {first_name}")
            print(f"Username: @{username}")
            print(f"\n🔗 Ссылка на бота:")
            print(f"{bot_link}")
            print("=" * 60)
            print(f"\nСкопируйте эту ссылку и откройте в Telegram!")
        else:
            print("⚠️ У бота нет username. Настройте username в @BotFather")
            print("Затем используйте поиск по имени бота в Telegram")
        
        await bot.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("Проверьте правильность токена бота")

if __name__ == '__main__':
    asyncio.run(get_bot_info())

