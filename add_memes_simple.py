"""
ПРОСТОЙ СПОСОБ: Добавление мемов через команды бота

Этот скрипт поможет вам быстро добавить все мемы.
"""

import sqlite3

def check_memes():
    """Проверяет, какие мемы уже добавлены"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM memes")
    existing = [row[0] for row in cursor.fetchall()]
    conn.close()
    return existing

def main():
    print("=" * 60)
    print("ДОБАВЛЕНИЕ МЕМОВ В БОТА")
    print("=" * 60)
    print("\n📋 Мемы для добавления:")
    print("1. Объект нагревается - его атомы")
    print("2. Спасибо сломанной вытяжке - дымкор эстетик")
    print("3. 14 000 625 измерений - один сошёлся")
    print("4. Неупругая деформация")
    
    existing = check_memes()
    if existing:
        print(f"\n✅ Уже добавлено мемов: {len(existing)}")
        for title in existing:
            print(f"   - {title}")
    
    print("\n" + "=" * 60)
    print("ИНСТРУКЦИЯ:")
    print("=" * 60)
    print("\n1. Запустите бота: python bot.py")
    print("2. Откройте Telegram и найдите вашего бота")
    print("3. Для каждого мема выполните:")
    print("   - Отправьте: /add_meme")
    print("   - Введите название мема (скопируйте из списка выше)")
    print("   - Отправьте фото мема")
    print("\n4. После добавления всех мемов запустите этот скрипт снова")
    print("   для проверки: python add_memes_simple.py")
    print("\n" + "=" * 60)
    
    input("\nНажмите Enter для выхода...")

if __name__ == '__main__':
    main()

