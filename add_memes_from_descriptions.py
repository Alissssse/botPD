"""
Добавление мемов в базу данных на основе описаний

ВНИМАНИЕ: Этот скрипт создаст записи в базе данных, но для работы мемов
нужно будет добавить реальные file_id изображений через бота.

После запуска этого скрипта:
1. Запустите бота: python bot.py
2. Отправьте боту: /add_memes_batch
3. Отправьте фото мемов подряд
"""

import sqlite3

# Описания мемов, которые были присланы
MEMES = [
    {
        "title": "Объект нагревается - его атомы",
        "description": "Мем с текстом 'Объект: *нагревается*' и 'Его атомы:' с фото людей в движении"
    },
    {
        "title": "Спасибо сломанной вытяжке - дымкор эстетик",
        "description": "Мем про задымленный рабочий стол с электроникой и надписью 'Спасибо сломанной вытяжке'"
    },
    {
        "title": "14 000 625 измерений - один сошёлся",
        "description": "Мем с Доктором Стрэнджем и Тони Старком про измерения и теоретические данные"
    },
    {
        "title": "Неупругая деформация",
        "description": "Мем про кролика с пальцем на макушке, демонстрирующий неупругую деформацию"
    }
]

def init_db():
    """Инициализирует базу данных"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    
    # Создаём таблицу мемов, если её нет
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            file_id TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def add_meme_placeholders():
    """Добавляет заглушки для мемов в базу данных"""
    # Сначала инициализируем базу данных
    init_db()
    
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    
    # Проверяем существующие мемы
    cursor.execute("SELECT title FROM memes")
    existing_titles = [row[0] for row in cursor.fetchall()]
    
    added_count = 0
    skipped_count = 0
    
    print("=" * 60)
    print("ДОБАВЛЕНИЕ МЕМОВ В БАЗУ ДАННЫХ")
    print("=" * 60)
    print()
    
    for meme in MEMES:
        title = meme["title"]
        
        if title in existing_titles:
            print(f"⚠️ Мем уже существует: {title}")
            skipped_count += 1
        else:
            # Создаём запись с временным file_id (будет заменён при добавлении фото)
            # Используем специальный маркер, который можно будет найти и заменить
            temp_file_id = f"PLACEHOLDER_{title.replace(' ', '_')}"
            cursor.execute("INSERT INTO memes (title, file_id) VALUES (?, ?)", 
                          (title, temp_file_id))
            print(f"✅ Добавлена запись для мема: {title}")
            added_count += 1
    
    conn.commit()
    conn.close()
    
    print()
    print("=" * 60)
    print(f"Готово! Добавлено новых записей: {added_count}")
    print(f"Пропущено (уже существуют): {skipped_count}")
    print("=" * 60)
    print()
    print("📋 СЛЕДУЮЩИЕ ШАГИ:")
    print("1. Запустите бота: python bot.py")
    print("2. Отправьте боту команду: /add_memes_batch")
    print("3. Отправьте фото мемов подряд (в правильном порядке)")
    print("4. Бот автоматически заменит заглушки на реальные file_id")
    print()

if __name__ == '__main__':
    add_meme_placeholders()

