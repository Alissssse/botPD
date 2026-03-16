"""
Скрипт для автоматической загрузки мемов в бота

ИНСТРУКЦИЯ:
1. Создайте папку 'memes' в той же директории, где находится этот скрипт
2. Поместите изображения мемов в папку 'memes' с названиями:
   - meme1.jpg (или .png) - "Объект нагревается - его атомы"
   - meme2.jpg - "Спасибо сломанной вытяжке - дымкор эстетик"
   - meme3.jpg - "14 000 625 измерений - один сошёлся"
   - meme4.jpg - "Неупругая деформация"
3. Запустите скрипт: python upload_memes.py
4. Скрипт автоматически загрузит изображения боту и добавит их в базу данных
"""

import sqlite3
import asyncio
import os
from telegram import Bot
from telegram.error import TelegramError

# Токен бота (из bot.py)
BOT_TOKEN = "8492028452:AAHUcNPsTm1rjNPY45u_OdOzynPXr7InkqU"

# ID администратора (для отправки сообщений)
ADMIN_ID = 729218232

# Названия мемов (будут использованы по порядку для найденных изображений)
MEME_TITLES = [
    "Объект нагревается - его атомы",
    "Спасибо сломанной вытяжке - дымкор эстетик",
    "14 000 625 измерений - один сошёлся",
    "Неупругая деформация"
]

# Или используйте конкретные файлы (раскомментируйте, если нужно)
# MEMES = [
#     {
#         "title": "Объект нагревается - его атомы",
#         "file": "memes/meme1.jpg"
#     },
#     {
#         "title": "Спасибо сломанной вытяжке - дымкор эстетик",
#         "file": "memes/meme2.jpg"
#     },
#     {
#         "title": "14 000 625 измерений - один сошёлся",
#         "file": "memes/meme3.jpg"
#     },
#     {
#         "title": "Неупругая деформация",
#         "file": "memes/meme4.jpg"
#     }
# ]

async def upload_and_add_meme(bot: Bot, meme_info: dict):
    """Загружает изображение боту и добавляет в базу данных"""
    file_path = meme_info["file"]
    title = meme_info["title"]
    
    # Проверяем существование файла
    if not os.path.exists(file_path):
        # Пробуем разные расширения
        base_path = file_path.rsplit('.', 1)[0]
        found = False
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            test_path = base_path + ext
            if os.path.exists(test_path):
                file_path = test_path
                found = True
                break
        
        if not found:
            print(f"❌ Файл не найден: {meme_info['file']}")
            return False
    
    try:
        # Отправляем изображение боту
        with open(file_path, 'rb') as photo:
            message = await bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo,
                caption=f"Загрузка: {title}"
            )
        
        # Получаем file_id
        file_id = message.photo[-1].file_id
        
        # Добавляем в базу данных
        conn = sqlite3.connect('physics_bot.db')
        cursor = conn.cursor()
        
        # Проверяем, не существует ли уже такой мем
        cursor.execute("SELECT id FROM memes WHERE title = ?", (title,))
        if cursor.fetchone():
            print(f"⚠️ Мем уже существует: {title}")
            conn.close()
            return False
        
        cursor.execute("INSERT INTO memes (title, file_id) VALUES (?, ?)", (title, file_id))
        conn.commit()
        conn.close()
        
        print(f"✅ Добавлен мем: {title}")
        return True
        
    except TelegramError as e:
        print(f"❌ Ошибка при загрузке {title}: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def find_image_files(directory='memes'):
    """Находит все изображения в указанной директории"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    image_files = []
    
    if not os.path.exists(directory):
        return []
    
    for filename in sorted(os.listdir(directory)):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(filename.lower())
            if ext in image_extensions:
                image_files.append(file_path)
    
    return image_files

async def main():
    """Основная функция"""
    print("🚀 Начинаю загрузку мемов...\n")
    
    # Создаём бота
    bot = Bot(token=BOT_TOKEN)
    
    # Проверяем существование папки memes
    if not os.path.exists('memes'):
        print("❌ Папка 'memes' не найдена!")
        print("📁 Создайте папку 'memes' и поместите туда изображения мемов")
        await bot.close()
        return
    
    # Находим все изображения
    image_files = find_image_files('memes')
    
    if not image_files:
        print("❌ Изображения не найдены в папке 'memes'!")
        print("📁 Поместите изображения (.jpg, .png и т.д.) в папку 'memes'")
        await bot.close()
        return
    
    print(f"📸 Найдено изображений: {len(image_files)}\n")
    
    # Загружаем каждый мем
    success_count = 0
    for i, image_file in enumerate(image_files):
        # Используем название из списка или имя файла
        if i < len(MEME_TITLES):
            title = MEME_TITLES[i]
        else:
            # Используем имя файла без расширения
            title = os.path.splitext(os.path.basename(image_file))[0]
        
        meme_info = {
            "title": title,
            "file": image_file
        }
        
        if await upload_and_add_meme(bot, meme_info):
            success_count += 1
        await asyncio.sleep(1)  # Небольшая задержка между загрузками
    
    print(f"\n🎉 Готово! Загружено мемов: {success_count} из {len(image_files)}")
    
    # Закрываем сессию бота
    await bot.close()

if __name__ == '__main__':
    asyncio.run(main())

