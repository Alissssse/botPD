"""
Скрипт для добавления мемов в базу данных бота

ИНСТРУКЦИЯ:
1. Запустите бота (python bot.py)
2. Отправьте каждое изображение мема боту с командой /get_file_id
   Например: отправьте фото и напишите /get_file_id
3. Бот вернёт file_id каждого изображения
4. Замените file_id в этом скрипте (ниже) на полученные значения
5. Запустите этот скрипт: python add_memes.py

АЛЬТЕРНАТИВНЫЙ СПОСОБ (через команды бота):
Можно использовать команду /add_meme для каждого мема по отдельности
"""

import sqlite3

# Мемы для добавления
# ИНСТРУКЦИЯ ПО ПОЛУЧЕНИЮ file_id:
# 1. Запустите бота (python bot.py)
# 2. Отправьте каждое изображение мема боту с командой /get_file_id
# 3. Бот вернёт file_id каждого изображения
# 4. Замените file_id ниже на полученные значения
# 5. Запустите этот скрипт: python add_memes.py

MEMES = [
    {
        "title": "Объект нагревается - его атомы",
        "file_id": "ЗАМЕНИТЕ_НА_FILE_ID_1"  # Мем про атомы при нагревании
    },
    {
        "title": "Спасибо сломанной вытяжке - дымкор эстетик",
        "file_id": "ЗАМЕНИТЕ_НА_FILE_ID_2"  # Мем про дым на рабочем столе с электроникой
    },
    {
        "title": "14 000 625 измерений - один сошёлся",
        "file_id": "ЗАМЕНИТЕ_НА_FILE_ID_3"  # Мем про Доктора Стрэнджа и измерения
    },
    {
        "title": "Неупругая деформация",
        "file_id": "ЗАМЕНИТЕ_НА_FILE_ID_4"  # Мем про кролика и неупругую деформацию
    }
]

def add_memes_to_db():
    """Добавляет мемы в базу данных"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    
    for meme in MEMES:
        # Проверяем, не существует ли уже такой мем
        cursor.execute("SELECT id FROM memes WHERE title = ? AND file_id = ?", 
                      (meme["title"], meme["file_id"]))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO memes (title, file_id) VALUES (?, ?)", 
                          (meme["title"], meme["file_id"]))
            print(f"✅ Добавлен мем: {meme['title']}")
        else:
            print(f"⚠️ Мем уже существует: {meme['title']}")
    
    conn.commit()
    conn.close()
    print("\n🎉 Все мемы добавлены!")

if __name__ == '__main__':
    print("Добавление мемов в базу данных...\n")
    add_memes_to_db()

