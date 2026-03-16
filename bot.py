"""
Простой бот для Simple Physics
Всё в одном файле для простоты понимания
"""

# Импорты
import os
import sys
import atexit
import sqlite3
from pathlib import Path
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto
from telegram.error import Conflict
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import logging

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Локальный контент из media/ (если модуль доступен)
try:
    from local_content_manager import (
        scan_local_content,
        get_local_content_count,
        send_local_content_item,
    )
    LOCAL_CONTENT_AVAILABLE = True
except Exception as e:
    logger.warning("Локальный контент недоступен: %s", e)
    LOCAL_CONTENT_AVAILABLE = False
    def scan_local_content():
        pass
    def get_local_content_count(category):
        return 0
    async def send_local_content_item(query, category, index, edit=False, config=None):
        pass

# Токен бота
BOT_TOKEN = "7146164928:AAFhYJS5MuYtF7-xMG2FHcnCb2tjnmXuRWo"

# ID администратора (получите его через @userinfobot)
ADMIN_ID = 729218232  # Ваш ID

# Пароль для режима модератора
MODERATOR_PASSWORD = "SimpPhysXRedactor123"

# ============================================================================
# РАБОТА С БАЗОЙ ДАННЫХ
# ============================================================================

def init_db():
    """Создаёт базу данных и таблицы при первом запуске"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    
    # Таблица комиксов (поддержка текста + картинки)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            file_id TEXT
        )
    ''')
    
    # Добавляем поле content если его нет
    try:
        cursor.execute('ALTER TABLE comics ADD COLUMN content TEXT')
    except sqlite3.OperationalError:
        pass  # Поле уже существует
    
    # Таблица карточек
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            file_id TEXT
        )
    ''')
    
    # Таблица видео
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT
        )
    ''')
    
    # Таблица мемов (поддержка текста + картинки)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            file_id TEXT
        )
    ''')
    
    # Добавляем поле content если его нет
    try:
        cursor.execute('ALTER TABLE memes ADD COLUMN content TEXT')
    except sqlite3.OperationalError:
        pass  # Поле уже существует
    
    # Таблица исторических справок (поддержка текста + картинки)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            file_id TEXT
        )
    ''')
    
    # Добавляем поле file_id если его нет
    try:
        cursor.execute('ALTER TABLE history ADD COLUMN file_id TEXT')
    except sqlite3.OperationalError:
        pass  # Поле уже существует
    
    # Таблица физики в фильмах (уже поддерживает текст + картинку)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            file_id TEXT
        )
    ''')
    
    # Таблица календарика (уже поддерживает текст + картинку)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calendar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            title TEXT,
            content TEXT,
            file_id TEXT
        )
    ''')
    
    # Таблица конспектов (поддержка текста + картинки)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            file_id TEXT
        )
    ''')
    
    # Добавляем поле content если его нет
    try:
        cursor.execute('ALTER TABLE notes ADD COLUMN content TEXT')
    except sqlite3.OperationalError:
        pass  # Поле уже существует
    
    conn.commit()
    conn.close()
    print("База данных создана!")

def add_comic(title, file_id, content=None):
    """Добавить комикс в базу"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comics (title, content, file_id) VALUES (?, ?, ?)", (title, content, file_id))
    conn.commit()
    conn.close()

def get_comics():
    """Получить все комиксы"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comics ORDER BY id")
    comics = cursor.fetchall()
    conn.close()
    return comics

def get_comic_by_index(index):
    """Получить комикс по индексу"""
    comics = get_comics()
    if comics and 0 <= index < len(comics):
        return comics[index], len(comics)
    return None, len(comics) if comics else 0

def add_card(title, file_id):
    """Добавить карточку в базу"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cards (title, file_id) VALUES (?, ?)", (title, file_id))
    conn.commit()
    conn.close()

def get_cards():
    """Получить все карточки"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cards ORDER BY id")
    cards = cursor.fetchall()
    conn.close()
    return cards

def get_card_by_index(index):
    """Получить карточку по индексу"""
    cards = get_cards()
    if cards and 0 <= index < len(cards):
        return cards[index], len(cards)
    return None, len(cards) if cards else 0

def add_video(title, url):
    """Добавить видео в базу"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO videos (title, url) VALUES (?, ?)", (title, url))
    conn.commit()
    conn.close()

def get_videos():
    """Получить все видео"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videos ORDER BY id DESC LIMIT 5")
    videos = cursor.fetchall()
    conn.close()
    return videos

def add_meme(title, file_id, content=None):
    """Добавить мем в базу"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO memes (title, content, file_id) VALUES (?, ?, ?)", (title, content, file_id))
    conn.commit()
    conn.close()

def get_memes():
    """Получить все мемы"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM memes ORDER BY id")
    memes = cursor.fetchall()
    conn.close()
    return memes

def get_meme_by_index(index):
    """Получить мем по индексу"""
    memes = get_memes()
    if memes and 0 <= index < len(memes):
        return memes[index], len(memes)
    return None, len(memes) if memes else 0

def add_history(title, content, file_id=None):
    """Добавить историческую справку в базу"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO history (title, content, file_id) VALUES (?, ?, ?)", (title, content, file_id))
    conn.commit()
    conn.close()

def get_history():
    """Получить все исторические справки"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history ORDER BY id")
    history = cursor.fetchall()
    conn.close()
    return history

def get_history_by_index(index):
    """Получить историческую справку по индексу"""
    history = get_history()
    if history and 0 <= index < len(history):
        return history[index], len(history)
    return None, len(history) if history else 0

def add_movie(title, content, file_id=None):
    """Добавить физику в фильмах в базу"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO movies (title, content, file_id) VALUES (?, ?, ?)", (title, content, file_id))
    conn.commit()
    conn.close()

def get_movies():
    """Получить все записи о физике в фильмах"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies ORDER BY id")
    movies = cursor.fetchall()
    conn.close()
    return movies

def get_movie_by_index(index):
    """Получить запись о физике в фильмах по индексу"""
    movies = get_movies()
    if movies and 0 <= index < len(movies):
        return movies[index], len(movies)
    return None, len(movies) if movies else 0

def add_calendar(date, title, content, file_id=None):
    """Добавить запись в календарик"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO calendar (date, title, content, file_id) VALUES (?, ?, ?, ?)", (date, title, content, file_id))
    conn.commit()
    conn.close()

def get_calendar():
    """Получить все записи календарика"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM calendar ORDER BY id")
    calendar = cursor.fetchall()
    conn.close()
    return calendar

def get_calendar_by_index(index):
    """Получить запись календарика по индексу"""
    calendar = get_calendar()
    if calendar and 0 <= index < len(calendar):
        return calendar[index], len(calendar)
    return None, len(calendar) if calendar else 0

def add_note(title, file_id, content=None):
    """Добавить конспект в базу"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (title, content, file_id) VALUES (?, ?, ?)", (title, content, file_id))
    conn.commit()
    conn.close()

def get_notes():
    """Получить все конспекты"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes ORDER BY id")
    notes = cursor.fetchall()
    conn.close()
    return notes

def get_note_by_index(index):
    """Получить конспект по индексу"""
    notes = get_notes()
    if notes and 0 <= index < len(notes):
        return notes[index], len(notes)
    return None, len(notes) if notes else 0

# ============================================================================
# ФУНКЦИИ ДЛЯ МОДЕРАТОРА
# ============================================================================

def delete_comic(comic_id):
    """Удалить комикс по ID"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM comics WHERE id = ?", (comic_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def get_comic_by_id(comic_id):
    """Получить комикс по ID"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM comics WHERE id = ?", (comic_id,))
    comic = cursor.fetchone()
    conn.close()
    return comic

def update_comic(comic_id, title=None, content=None, file_id=None):
    """Обновить комикс"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    updates = []
    params = []
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if content is not None:
        updates.append("content = ?")
        params.append(content)
    if file_id is not None:
        updates.append("file_id = ?")
        params.append(file_id)
    if updates:
        params.append(comic_id)
        cursor.execute(f"UPDATE comics SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
    conn.close()

def delete_meme(meme_id):
    """Удалить мем по ID"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM memes WHERE id = ?", (meme_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def get_meme_by_id(meme_id):
    """Получить мем по ID"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM memes WHERE id = ?", (meme_id,))
    meme = cursor.fetchone()
    conn.close()
    return meme

def update_meme(meme_id, title=None, content=None, file_id=None):
    """Обновить мем"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    updates = []
    params = []
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if content is not None:
        updates.append("content = ?")
        params.append(content)
    if file_id is not None:
        updates.append("file_id = ?")
        params.append(file_id)
    if updates:
        params.append(meme_id)
        cursor.execute(f"UPDATE memes SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
    conn.close()

def delete_history(history_id):
    """Удалить историческую справку по ID"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history WHERE id = ?", (history_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def get_history_by_id(history_id):
    """Получить историческую справку по ID"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history WHERE id = ?", (history_id,))
    history = cursor.fetchone()
    conn.close()
    return history

def update_history(history_id, title=None, content=None, file_id=None):
    """Обновить историческую справку"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    updates = []
    params = []
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if content is not None:
        updates.append("content = ?")
        params.append(content)
    if file_id is not None:
        updates.append("file_id = ?")
        params.append(file_id)
    if updates:
        params.append(history_id)
        cursor.execute(f"UPDATE history SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
    conn.close()

def delete_movie(movie_id):
    """Удалить запись о фильме по ID"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def get_movie_by_id(movie_id):
    """Получить запись о фильме по ID"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    movie = cursor.fetchone()
    conn.close()
    return movie

def update_movie(movie_id, title=None, content=None, file_id=None):
    """Обновить запись о фильме"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    updates = []
    params = []
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if content is not None:
        updates.append("content = ?")
        params.append(content)
    if file_id is not None:
        updates.append("file_id = ?")
        params.append(file_id)
    if updates:
        params.append(movie_id)
        cursor.execute(f"UPDATE movies SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
    conn.close()

def delete_calendar(calendar_id):
    """Удалить запись календарика по ID"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM calendar WHERE id = ?", (calendar_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def get_calendar_by_id(calendar_id):
    """Получить запись календарика по ID"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM calendar WHERE id = ?", (calendar_id,))
    calendar = cursor.fetchone()
    conn.close()
    return calendar

def update_calendar(calendar_id, date=None, title=None, content=None, file_id=None):
    """Обновить запись календарика"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    updates = []
    params = []
    if date is not None:
        updates.append("date = ?")
        params.append(date)
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if content is not None:
        updates.append("content = ?")
        params.append(content)
    if file_id is not None:
        updates.append("file_id = ?")
        params.append(file_id)
    if updates:
        params.append(calendar_id)
        cursor.execute(f"UPDATE calendar SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
    conn.close()

def delete_note(note_id):
    """Удалить конспект по ID"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def get_note_by_id(note_id):
    """Получить конспект по ID"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    note = cursor.fetchone()
    conn.close()
    return note

def update_note(note_id, title=None, content=None, file_id=None):
    """Обновить конспект"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    updates = []
    params = []
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if content is not None:
        updates.append("content = ?")
        params.append(content)
    if file_id is not None:
        updates.append("file_id = ?")
        params.append(file_id)
    if updates:
        params.append(note_id)
        cursor.execute(f"UPDATE notes SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
    conn.close()

# ============================================================================
# ЛОКАЛЬНЫЙ КОНТЕНТ ДЛЯ КАТЕГОРИЙ
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent

CATEGORY_CONTENT = {
    "comics": [
        {"file": "Комиксы1.png", "title": "Комикс №1"},
        {"file": "Комиксы2.jpg", "title": "Комикс №2"},
        {"file": "Комиксы3.jpg", "title": "Комикс №3"},
        {"file": "Комиксы4.jpg", "title": "Комикс №4"},
        {"file": "Комиксы5.jpg", "title": "Комикс №5"},
        {"file": "Комиксы6.jpg", "title": "Комикс №6"},
        {"file": "Комиксы7.jpg", "title": "Комикс №7"},
        {"file": "Комиксы8.jpg", "title": "Комикс №8"},
    ],
    "memes": [
        {"file": "Мемы1.jpg", "title": "Мем №1"},
        {"file": "Мемы2.jpg", "title": "Мем №2"},
    ],
    "history": [
        {"file": "Исторические1.jpg", "title": "Историческая справка №1"},
        {"file": "Исторические2.jpg", "title": "Историческая справка №2"},
    ],
    "movies": [
        {"file": "физика0.jpg", "title": "Физика в фильмах №1"},
        {"file": "Физика1.jpg", "title": "Физика в фильмах №2"},
        {"file": "Физика2.jpg", "title": "Физика в фильмах №3"},
        {"file": "физика3.jpg", "title": "Физика в фильмах №4"},
        {"file": "Физика4.jpg", "title": "Физика в фильмах №5"},
    ],
    "calendar": [
        {"file": "календарь1.png", "title": "Запись календарика №1"},
        {"file": "Календарик2.png", "title": "Запись календарика №2"},
        {"file": "календарь3.png", "title": "Запись календарика №3"},
        {"file": "календарь4.png", "title": "Запись календарика №4"},
        {"file": "календарь5.png", "title": "Запись календарика №5"},
    ],
    "notes": [
        {"file": "Конспект1.jpg", "title": "Конспект №1"},
        {"file": "Конспект2.jpg", "title": "Конспект №2"},
    ],
    "formulas": [
        {"file": "формулы1.jpg", "title": "Формулы №1"},
        {"file": "формулы2.jpg", "title": "Формулы №2"},
        {"file": "формулы3.jpg", "title": "Формулы №3"},
        {"file": "формулы4.jpg", "title": "Формулы №4"},
    ],
}

CATEGORY_CONFIG = {
    "comics": {
        "emoji": "🎨",
        "singular": "Комикс",
        "prev_label": "◀️ Предыдущий комикс",
        "next_label": "Следующий комикс ▶️",
        "empty_text": "😔 Комиксов пока нет. Возвращайтесь позже!",
    },
    "memes": {
        "emoji": "😂",
        "singular": "Мем",
        "prev_label": "◀️ Предыдущий мем",
        "next_label": "Следующий мем ▶️",
        "empty_text": "😔 Мемов пока нет. Возвращайтесь позже!",
    },
    "history": {
        "emoji": "📚",
        "singular": "Справка",
        "prev_label": "◀️ Предыдущая справка",
        "next_label": "Следующая справка ▶️",
        "empty_text": "😔 Исторических справок пока нет. Возвращайтесь позже!",
    },
    "movies": {
        "emoji": "🎬",
        "singular": "Запись",
        "prev_label": "◀️ Предыдущая запись",
        "next_label": "Следующая запись ▶️",
        "empty_text": "😔 Записей о физике в фильмах пока нет. Возвращайтесь позже!",
    },
    "calendar": {
        "emoji": "📅",
        "singular": "Запись календарика",
        "prev_label": "◀️ Предыдущая запись",
        "next_label": "Следующая запись ▶️",
        "empty_text": "😔 Записей в календарике пока нет. Возвращайтесь позже!",
    },
    "notes": {
        "emoji": "📝",
        "singular": "Конспект",
        "prev_label": "◀️ Предыдущий конспект",
        "next_label": "Следующий конспект ▶️",
        "empty_text": "😔 Конспектов пока нет. Возвращайтесь позже!",
    },
    "formulas": {
        "emoji": "📐",
        "singular": "Формулы",
        "prev_label": "◀️ Предыдущие",
        "next_label": "Следующие ▶️",
        "empty_text": "😔 Формул пока нет. Возвращайтесь позже!",
    },
}

MEDIA_CACHE = {}
FILE_ID_CACHE = {category: [None] * len(items) for category, items in CATEGORY_CONTENT.items()}
LOCK_FILE = BASE_DIR / "bot.lock"
LOCK_FILE_HANDLE = None


def acquire_instance_lock():
    """Гарантирует, что бот запущен только в одном экземпляре."""
    global LOCK_FILE_HANDLE
    if LOCK_FILE_HANDLE:
        return True

    try:
        LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    try:
        lock_handle = open(LOCK_FILE, "a+")
        try:
            if os.name == "nt":
                import msvcrt

                lock_handle.seek(0)
                msvcrt.locking(lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

            lock_handle.seek(0)
            lock_handle.truncate()
            lock_handle.write(str(os.getpid()))
            lock_handle.flush()
            LOCK_FILE_HANDLE = lock_handle
            atexit.register(release_instance_lock)
            return True
        except (BlockingIOError, OSError) as err:
            logger.error("Бот уже запущен (не удалось получить блокировку): %s", err)
            lock_handle.close()
            return False
    except Exception as err:
        logger.error(f"Не удалось открыть файл блокировки {LOCK_FILE}: {err}")
        return False


def release_instance_lock():
    """Освобождает файл блокировки при завершении работы."""
    global LOCK_FILE_HANDLE
    if not LOCK_FILE_HANDLE:
        return
    try:
        if os.name == "nt":
            import msvcrt

            LOCK_FILE_HANDLE.seek(0)
            msvcrt.locking(LOCK_FILE_HANDLE.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(LOCK_FILE_HANDLE.fileno(), fcntl.LOCK_UN)
    except Exception as err:
        logger.error(f"Не удалось освободить блокировку: {err}")
    finally:
        try:
            LOCK_FILE_HANDLE.close()
        except Exception:
            pass
        LOCK_FILE_HANDLE = None
        try:
            LOCK_FILE.unlink(missing_ok=True)
        except Exception:
            pass

def _load_media(file_name: str):
    """Загружает файл в память и возвращает байты либо None."""
    if file_name in MEDIA_CACHE:
        return MEDIA_CACHE[file_name]

    file_path = BASE_DIR / file_name
    if not file_path.exists():
        logger.error(f"Файл {file_path} не найден при загрузке в кэш")
        MEDIA_CACHE[file_name] = None
        return None

    try:
        MEDIA_CACHE[file_name] = file_path.read_bytes()
    except Exception as e:
        logger.error(f"Не удалось прочитать файл {file_path}: {e}")
        MEDIA_CACHE[file_name] = None
    return MEDIA_CACHE[file_name]

# Прогреваем кэш сразу при старте
for items in CATEGORY_CONTENT.values():
    for item in items:
        _load_media(item["file"])


async def send_category_item_from_db(query, category, index, edit=False):
    """Показать элемент категории из базы данных или локальных файлов"""
    config = CATEGORY_CONFIG.get(category)
    
    back_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_menu")]]
    )

    if not config:
        logger.error(f"Не найдена конфигурация категории: {category}")
        try:
            if edit:
                await query.message.edit_text(
                    "⚠️ Ошибка конфигурации категории.", reply_markup=back_keyboard
                )
            else:
                await query.message.reply_text(
                    "⚠️ Ошибка конфигурации категории.", reply_markup=back_keyboard
                )
        except Exception as e:
            logger.error(e)
        return
    
    # Сначала проверяем базу данных
    item = None
    total = 0
    
    if category == "comics":
        item, total = get_comic_by_index(index)
    elif category == "memes":
        item, total = get_meme_by_index(index)
    elif category == "history":
        item, total = get_history_by_index(index)
    elif category == "movies":
        item, total = get_movie_by_index(index)
    elif category == "calendar":
        item, total = get_calendar_by_index(index)
    elif category == "notes":
        item, total = get_note_by_index(index)
    elif category == "formulas":
        item, total = None, 0  # только локальные файлы из media/formulas
    
    # Если в БД нет записей, пробуем локальные файлы
    if total == 0 and LOCAL_CONTENT_AVAILABLE:
        local_count = get_local_content_count(category)
        if local_count > 0:
            await send_local_content_item(query, category, index, edit, config)
            return
    
    # Если нет ни в БД, ни локальных файлов
    if total == 0:
        try:
            if edit:
                await query.message.edit_text(config["empty_text"], reply_markup=back_keyboard)
            else:
                await query.message.reply_text(config["empty_text"], reply_markup=back_keyboard)
        except Exception as e:
            logger.error(e)
        return

    if not item:
        try:
            if edit:
                await query.message.edit_text(config["empty_text"], reply_markup=back_keyboard)
            else:
                await query.message.reply_text(config["empty_text"], reply_markup=back_keyboard)
        except Exception as e:
            logger.error(e)
        return

    # Сначала проверяем базу данных
    item = None
    total = 0
    
    if category == "comics":
        item, total = get_comic_by_index(index)
    elif category == "memes":
        item, total = get_meme_by_index(index)
    elif category == "history":
        item, total = get_history_by_index(index)
    elif category == "movies":
        item, total = get_movie_by_index(index)
    elif category == "calendar":
        item, total = get_calendar_by_index(index)
    elif category == "notes":
        item, total = get_note_by_index(index)
    elif category == "formulas":
        item, total = None, 0
    else:
        logger.error(f"Неизвестная категория: {category}")
        try:
            if edit:
                await query.message.edit_text(
                    "⚠️ Неизвестная категория.", reply_markup=back_keyboard
                )
            else:
                await query.message.reply_text(
                    "⚠️ Неизвестная категория.", reply_markup=back_keyboard
                )
        except Exception as e:
            logger.error(e)
        return
    
    # Если в БД нет записей, пробуем локальные файлы
    if total == 0 and LOCAL_CONTENT_AVAILABLE:
        try:
            local_count = get_local_content_count(category)
            if local_count > 0:
                await send_local_content_item(query, category, index, edit, config)
                return
        except Exception as e:
            logger.error(f"Ошибка при загрузке локального контента: {e}")

    if total == 0:
        try:
            if edit:
                await query.message.edit_text(config["empty_text"], reply_markup=back_keyboard)
            else:
                await query.message.reply_text(config["empty_text"], reply_markup=back_keyboard)
        except Exception as e:
            logger.error(e)
        return

    if not item:
        try:
            if edit:
                await query.message.edit_text(config["empty_text"], reply_markup=back_keyboard)
            else:
                await query.message.reply_text(config["empty_text"], reply_markup=back_keyboard)
        except Exception as e:
            logger.error(e)
        return

    # Парсим данные из БД
    # Структура: comics/memes/notes: (id, title, content, file_id)
    # history/movies: (id, title, content, file_id)
    # calendar: (id, date, title, content, file_id)
    
    if category == "calendar":
        item_id, date, title, content, file_id = item
    else:
        # Для старых записей может не быть content, поэтому проверяем длину
        if len(item) >= 4:
            item_id, title, content, file_id = item[:4]
        else:
            # Старая структура без content (id, title, file_id)
            item_id, title = item[:2]
            file_id = item[2] if len(item) > 2 else None
            content = None
        date = None

    # Формируем навигационные кнопки
    nav_buttons = []
    if total > 1:
        prev_index = (index - 1) % total
        next_index = (index + 1) % total
        nav_buttons.append(
            InlineKeyboardButton(
                config["prev_label"], callback_data=f"{category}_prev_{prev_index}"
            )
        )
        nav_buttons.append(
            InlineKeyboardButton(
                config["next_label"], callback_data=f"{category}_next_{next_index}"
            )
        )

    keyboard_layout = []
    if nav_buttons:
        keyboard_layout.append(nav_buttons)
    keyboard_layout.append([InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_menu")])
    keyboard = InlineKeyboardMarkup(keyboard_layout)

    # Формируем текст для отображения
    caption_lines = []
    if date:
        caption_lines.append(f"{config['emoji']} {date}")
    caption_lines.append(f"📌 {title}")
    if content:
        caption_lines.append(f"\n{content}")
    caption_lines.append(f"\n\n📊 {config['singular']} {index + 1} из {total}")
    caption = "\n".join(caption_lines)

    try:
        # Если есть картинка (проверяем что file_id не None и не пустая строка)
        # Также проверяем, что это не просто текст (file_id должен быть валидным)
        if file_id and file_id.strip() and len(file_id) > 20:  # file_id обычно длинный
            try:
                if edit:
                    try:
                        await query.message.edit_media(
                            media=InputMediaPhoto(file_id, caption=caption),
                            reply_markup=keyboard,
                        )
                    except Exception:
                        # Если не удалось отредактировать медиа, отправляем новое сообщение
                        await query.message.delete()
                        await query.message.reply_photo(
                            photo=file_id,
                            caption=caption,
                            reply_markup=keyboard,
                        )
                else:
                    await query.message.reply_photo(
                        photo=file_id,
                        caption=caption,
                        reply_markup=keyboard,
                    )
            except Exception as photo_error:
                # Если не удалось отправить фото (неверный file_id), отправляем только текст
                logger.error(f"Ошибка при отправке фото: {photo_error}")
                if edit:
                    try:
                        await query.message.edit_text(
                            caption,
                            reply_markup=keyboard,
                        )
                    except Exception:
                        await query.message.delete()
                        await query.message.reply_text(
                            caption,
                            reply_markup=keyboard,
                        )
                else:
                    await query.message.reply_text(
                        caption,
                        reply_markup=keyboard,
                    )
        else:
            # Если нет картинки, отправляем только текст
            if edit:
                try:
                    await query.message.edit_text(
                        caption,
                        reply_markup=keyboard,
                    )
                except Exception:
                    # Если не удалось отредактировать, отправляем новое сообщение
                    await query.message.delete()
                    await query.message.reply_text(
                        caption,
                        reply_markup=keyboard,
                    )
            else:
                await query.message.reply_text(
                    caption,
                    reply_markup=keyboard,
                )
    except Exception as e:
        logger.error(f"Ошибка при отправке элемента категории {category}: {e}")
        try:
            if edit:
                await query.message.edit_text(
                    "⚠️ Не удалось отправить элемент.",
                    reply_markup=keyboard,
                )
            else:
                await query.message.reply_text(
                    "⚠️ Не удалось отправить элемент.",
                    reply_markup=keyboard,
                )
        except Exception as inner_e:
            logger.error(inner_e)

# ============================================================================
# КЛАВИАТУРЫ
# ============================================================================

def get_main_menu():
    """Главное меню с кнопками в сообщении"""
    keyboard = [
        [InlineKeyboardButton("🎨 Комиксы", callback_data="comics")],
        [InlineKeyboardButton("🎥 Видео", callback_data="videos")],
        [InlineKeyboardButton("😂 Мемы", callback_data="memes")],
        [InlineKeyboardButton("📚 Историческая справка", callback_data="history")],
        [InlineKeyboardButton("🎬 Физика в фильмах", callback_data="movies")],
        [InlineKeyboardButton("📅 Календарик", callback_data="calendar")],
        [InlineKeyboardButton("📝 Конспекты", callback_data="notes")],
        [InlineKeyboardButton("📐 Формулы", callback_data="formulas")],
        [InlineKeyboardButton("ℹ️ О проекте", callback_data="about")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_moderator_menu():
    """Меню модератора с разделами"""
    keyboard = [
        [InlineKeyboardButton("🎨 Комиксы", callback_data="mod_comics")],
        [InlineKeyboardButton("😂 Мемы", callback_data="mod_memes")],
        [InlineKeyboardButton("📚 Исторические справки", callback_data="mod_history")],
        [InlineKeyboardButton("🎬 Физика в фильмах", callback_data="mod_movies")],
        [InlineKeyboardButton("📅 Календарик", callback_data="mod_calendar")],
        [InlineKeyboardButton("📝 Конспекты", callback_data="mod_notes")],
        [InlineKeyboardButton("📐 Формулы", callback_data="mod_formulas")],
        [InlineKeyboardButton("🚪 Выйти из режима модератора", callback_data="mod_exit")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_moderator_section_menu(category):
    """Меню действий для раздела модератора"""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить", callback_data=f"mod_add_{category}")],
        [InlineKeyboardButton("🗑️ Удалить", callback_data=f"mod_delete_{category}")],
        [InlineKeyboardButton("👁️ Посмотреть все", callback_data=f"mod_view_{category}")],
        [InlineKeyboardButton("✏️ Редактировать", callback_data=f"mod_edit_{category}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="mod_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ============================================================================
# ОБРАБОТЧИКИ КОМАНД
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    # Убираем клавиатуру снизу и показываем кнопки в сообщении
    await update.message.reply_text(
        "🌟 Добро пожаловать в Simple Physics!\n\nВыберите раздел:",
        reply_markup=ReplyKeyboardRemove()  # Убираем нижние кнопки
    )
    # Сохраняем ID сообщения с меню для последующего удаления
    menu_message = await update.message.reply_text(
        "👇 Нажмите на кнопку:",
        reply_markup=get_main_menu()
    )
    # Сохраняем ID последнего меню в контексте пользователя
    if 'last_menu_message_id' in context.user_data:
        try:
            # Пытаемся удалить предыдущее меню
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data['last_menu_message_id']
            )
        except Exception:
            pass  # Игнорируем ошибки удаления
    context.user_data['last_menu_message_id'] = menu_message.message_id

async def moderator_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для входа в режим модератора"""
    context.user_data['moderator_waiting_password'] = True
    await update.message.reply_text(
        "🔐 Введите пароль для входа в режим модератора:"
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('CALLBACK_HANDLER_START', update)
    logger.info('CALLBACK_HANDLER_START: обработчик вызван')
    query = update.callback_query
    data = query.data
    
    logger.info(f"Получен callback: {data}")

    # Навигация по категориям из БД или локальных файлов
    categories = ["comics", "memes", "history", "movies", "calendar", "notes", "formulas"]
    for category in categories:
        next_prefix = f"{category}_next_"
        prev_prefix = f"{category}_prev_"
        if data.startswith(next_prefix) or data.startswith(prev_prefix):
            try:
                target_index = int(data.split("_")[-1])
                await send_category_item_from_db(query, category, target_index, edit=True)
            except (ValueError, IndexError) as e:
                logger.error(f"Не удалось распарсить индекс для {data}: {e}")
                await send_category_item_from_db(query, category, 0, edit=True)
            try:
                await query.answer()
            except Exception:
                pass
            return

    # Комиксы
    if data == "comics":
        await send_category_item_from_db(query, "comics", 0)
        try:
            await query.answer()
        except Exception:
            pass
    
    # Видео
    elif data == "videos":
        videos = get_videos()
        if videos:
            video_text = "📹 Видео:\n\n"
            for video in videos:
                video_text += f"• {video[1]}\n{video[2]}\n\n"
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_menu")]])
            try:
                await query.message.edit_text(video_text, reply_markup=keyboard)
            except Exception as e:
                logger.error(e)
                await query.message.reply_text(video_text, reply_markup=keyboard)
        else:
            try:
                await query.message.edit_text(
                    "😔 Видео пока нет. Возвращайтесь позже!",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_menu")]])
                )
            except Exception as e:
                logger.error(e)
        try:
            await query.answer()
        except Exception:
            pass
    
    # Мемы
    elif data == "memes":
        await send_category_item_from_db(query, "memes", 0)
        try:
            await query.answer()
        except Exception:
            pass
    
    # Возврат в главное меню
    elif data == "back_to_menu":
        try:
            await query.message.delete()
        except Exception as e:
            logger.error(f"Не удалось удалить сообщение при возврате в меню: {e}")
        # Удаляем предыдущее меню если есть
        if 'last_menu_message_id' in context.user_data:
            try:
                await context.bot.delete_message(
                    chat_id=query.message.chat.id,
                    message_id=context.user_data['last_menu_message_id']
                )
            except Exception:
                pass  # Игнорируем ошибки удаления
        # Показываем главное меню
        try:
            menu_message = await query.message.reply_text(
                "👇 Нажмите на кнопку:",
                reply_markup=get_main_menu()
            )
            context.user_data['last_menu_message_id'] = menu_message.message_id
        except Exception as e:
            logger.error(f"Не удалось отправить главное меню: {e}")
        try:
            await query.answer()
        except Exception:
            pass
    
    # Историческая справка
    elif data == "history":
        await send_category_item_from_db(query, "history", 0)
        try:
            await query.answer()
        except Exception:
            pass
    
    # Физика в фильмах
    elif data == "movies":
        await send_category_item_from_db(query, "movies", 0)
        try:
            await query.answer()
        except Exception:
            pass
    
    # Календарик
    elif data == "calendar":
        await send_category_item_from_db(query, "calendar", 0)
        try:
            await query.answer()
        except Exception:
            pass
    
    # Конспекты
    elif data == "notes":
        await send_category_item_from_db(query, "notes", 0)
        try:
            await query.answer()
        except Exception:
            pass
    
    # Формулы
    elif data == "formulas":
        await send_category_item_from_db(query, "formulas", 0)
        try:
            await query.answer()
        except Exception:
            pass
    
    # Режим модератора
    elif data.startswith("mod_"):
        if not context.user_data.get('is_moderator'):
            await query.answer("❌ У вас нет доступа к режиму модератора", show_alert=True)
            return
        
        # Выход из режима модератора
        if data == "mod_exit":
            context.user_data['is_moderator'] = False
            context.user_data.pop('moderator_category', None)
            context.user_data.pop('moderator_action', None)
            context.user_data.pop('moderator_waiting_id', None)
            context.user_data.pop('moderator_waiting_text', None)
            context.user_data.pop('moderator_adding_photo', None)
            try:
                await query.message.edit_text(
                    "✅ Вы вышли из режима модератора.",
                    reply_markup=get_main_menu()
                )
            except Exception:
                await query.message.reply_text(
                    "✅ Вы вышли из режима модератора.",
                    reply_markup=get_main_menu()
                )
            await query.answer()
            return
        
        # Назад в меню модератора
        if data == "mod_back":
            try:
                await query.message.edit_text(
                    "🔧 Режим модератора\n\nВыберите раздел:",
                    reply_markup=get_moderator_menu()
                )
            except Exception:
                await query.message.reply_text(
                    "🔧 Режим модератора\n\nВыберите раздел:",
                    reply_markup=get_moderator_menu()
                )
            await query.answer()
            return
        
        # Выбор раздела
        if data == "mod_comics":
            context.user_data['moderator_category'] = 'comics'
            try:
                await query.message.edit_text(
                    "🎨 Комиксы\n\nВыберите действие:",
                    reply_markup=get_moderator_section_menu('comics')
                )
            except Exception:
                await query.message.reply_text(
                    "🎨 Комиксы\n\nВыберите действие:",
                    reply_markup=get_moderator_section_menu('comics')
                )
            await query.answer()
            return
        elif data == "mod_memes":
            context.user_data['moderator_category'] = 'memes'
            try:
                await query.message.edit_text(
                    "😂 Мемы\n\nВыберите действие:",
                    reply_markup=get_moderator_section_menu('memes')
                )
            except Exception:
                await query.message.reply_text(
                    "😂 Мемы\n\nВыберите действие:",
                    reply_markup=get_moderator_section_menu('memes')
                )
            await query.answer()
            return
        elif data == "mod_history":
            context.user_data['moderator_category'] = 'history'
            try:
                await query.message.edit_text(
                    "📚 Исторические справки\n\nВыберите действие:",
                    reply_markup=get_moderator_section_menu('history')
                )
            except Exception:
                await query.message.reply_text(
                    "📚 Исторические справки\n\nВыберите действие:",
                    reply_markup=get_moderator_section_menu('history')
                )
            await query.answer()
            return
        elif data == "mod_movies":
            context.user_data['moderator_category'] = 'movies'
            try:
                await query.message.edit_text(
                    "🎬 Физика в фильмах\n\nВыберите действие:",
                    reply_markup=get_moderator_section_menu('movies')
                )
            except Exception:
                await query.message.reply_text(
                    "🎬 Физика в фильмах\n\nВыберите действие:",
                    reply_markup=get_moderator_section_menu('movies')
                )
            await query.answer()
            return
        elif data == "mod_calendar":
            context.user_data['moderator_category'] = 'calendar'
            try:
                await query.message.edit_text(
                    "📅 Календарик\n\nВыберите действие:",
                    reply_markup=get_moderator_section_menu('calendar')
                )
            except Exception:
                await query.message.reply_text(
                    "📅 Календарик\n\nВыберите действие:",
                    reply_markup=get_moderator_section_menu('calendar')
                )
            await query.answer()
            return
        elif data == "mod_notes":
            context.user_data['moderator_category'] = 'notes'
            try:
                await query.message.edit_text(
                    "📝 Конспекты\n\nВыберите действие:",
                    reply_markup=get_moderator_section_menu('notes')
                )
            except Exception:
                await query.message.reply_text(
                    "📝 Конспекты\n\nВыберите действие:",
                    reply_markup=get_moderator_section_menu('notes')
                )
            await query.answer()
            return
        elif data == "mod_formulas":
            context.user_data['moderator_category'] = 'formulas'
            try:
                await query.message.edit_text(
                    "📐 Формулы\n\nВыберите действие:",
                    reply_markup=get_moderator_section_menu('formulas')
                )
            except Exception:
                await query.message.reply_text(
                    "📐 Формулы\n\nВыберите действие:",
                    reply_markup=get_moderator_section_menu('formulas')
                )
            await query.answer()
            return
        
        # Действия с разделами
        if data.startswith("mod_add_"):
            category = data.replace("mod_add_", "")
            context.user_data['moderator_category'] = category
            context.user_data['moderator_action'] = 'add'
            context.user_data['moderator_waiting_title'] = True
            try:
                await query.message.edit_text(
                    f"➕ Добавление в раздел '{category}'\n\n✏️ Введите название записи:"
                )
            except Exception:
                await query.message.reply_text(
                    f"➕ Добавление в раздел '{category}'\n\n✏️ Введите название записи:"
                )
            await query.answer()
            return
        
        # Пропуск фото
        if data == "mod_skip_photo":
            category = context.user_data.get('moderator_category')
            action = context.user_data.get('moderator_action')
            context.user_data['moderator_file_id'] = None
            context.user_data['moderator_adding_photo'] = False
            context.user_data['moderator_waiting_text'] = True
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("⏭️ Пропустить текст", callback_data="mod_skip_text")
            ]])
            try:
                await query.message.edit_text(
                    f"✏️ Отправьте текст для записи или нажмите 'Пропустить текст':",
                    reply_markup=keyboard
                )
            except Exception:
                await query.message.reply_text(
                    f"✏️ Отправьте текст для записи или нажмите 'Пропустить текст':",
                    reply_markup=keyboard
                )
            await query.answer()
            return
        
        # Пропуск текста
        if data == "mod_skip_text":
            category = context.user_data.get('moderator_category')
            action = context.user_data.get('moderator_action')
            file_id = context.user_data.get('moderator_file_id')
            title = context.user_data.get('moderator_title', 'Без названия')
            
            # Добавляем запись без текста
            if action == "add":
                if category == "comics":
                    add_comic(title, file_id, None)
                elif category == "memes":
                    add_meme(title, file_id, None)
                elif category == "history":
                    add_history(title, "", file_id)
                elif category == "movies":
                    add_movie(title, "", file_id)
                elif category == "calendar":
                    add_calendar("Дата", title, "", file_id)
                elif category == "notes":
                    add_note(title, file_id, None)
                elif category == "formulas":
                    await query.message.edit_text(
                        "В разделе «Формулы» используются только локальные файлы. Добавьте изображения в папку media/formulas и перезапустите бота."
                    )
                    context.user_data['moderator_waiting_text'] = False
                    context.user_data['moderator_adding_photo'] = False
                    context.user_data.pop('moderator_file_id', None)
                    context.user_data.pop('moderator_title', None)
                    try:
                        await query.message.reply_text(
                            "🔧 Режим модератора\n\nВыберите раздел:",
                            reply_markup=get_moderator_menu()
                        )
                    except Exception:
                        pass
                    await query.answer()
                    return
                
                await query.message.edit_text("✅ Запись успешно добавлена!")
            elif action == "edit":
                item_id = context.user_data.get('moderator_item_id')
                if category == "comics":
                    update_comic(item_id, file_id=file_id)
                elif category == "memes":
                    update_meme(item_id, file_id=file_id)
                elif category == "history":
                    update_history(item_id, file_id=file_id)
                elif category == "movies":
                    update_movie(item_id, file_id=file_id)
                elif category == "calendar":
                    update_calendar(item_id, file_id=file_id)
                elif category == "notes":
                    update_note(item_id, file_id=file_id)
                elif category == "formulas":
                    await query.message.edit_text(
                        "В разделе «Формулы» только локальные файлы. Редактирование через бота недоступно."
                    )
                    context.user_data['moderator_waiting_text'] = False
                    context.user_data['moderator_adding_photo'] = False
                    context.user_data.pop('moderator_file_id', None)
                    context.user_data.pop('moderator_item_id', None)
                    context.user_data.pop('moderator_title', None)
                    try:
                        await query.message.reply_text(
                            "🔧 Режим модератора\n\nВыберите раздел:",
                            reply_markup=get_moderator_menu()
                        )
                    except Exception:
                        pass
                    await query.answer()
                    return
                
                await query.message.edit_text(f"✅ Запись ID {item_id} успешно отредактирована!")
            
            context.user_data['moderator_waiting_text'] = False
            context.user_data['moderator_adding_photo'] = False
            context.user_data.pop('moderator_file_id', None)
            context.user_data.pop('moderator_item_id', None)
            context.user_data.pop('moderator_old_file_id', None)
            context.user_data.pop('moderator_title', None)
            
            try:
                await query.message.reply_text(
                    "🔧 Режим модератора\n\nВыберите раздел:",
                    reply_markup=get_moderator_menu()
                )
            except Exception:
                pass
            await query.answer()
            return
        
        if data.startswith("mod_delete_"):
            category = data.replace("mod_delete_", "")
            context.user_data['moderator_category'] = category
            context.user_data['moderator_action'] = 'delete'
            context.user_data['moderator_waiting_id'] = True
            try:
                await query.message.edit_text(
                    f"🗑️ Удаление из раздела '{category}'\n\nВведите ID записи для удаления:"
                )
            except Exception:
                await query.message.reply_text(
                    f"🗑️ Удаление из раздела '{category}'\n\nВведите ID записи для удаления:"
                )
            await query.answer()
            return
        
        if data.startswith("mod_view_"):
            category = data.replace("mod_view_", "")
            await show_all_items_moderator(query, category)
            await query.answer()
            return
        
        if data.startswith("mod_edit_"):
            category = data.replace("mod_edit_", "")
            context.user_data['moderator_category'] = category
            context.user_data['moderator_action'] = 'edit'
            context.user_data['moderator_waiting_id'] = True
            try:
                await query.message.edit_text(
                    f"✏️ Редактирование в разделе '{category}'\n\nВведите ID записи для редактирования:"
                )
            except Exception:
                await query.message.reply_text(
                    f"✏️ Редактирование в разделе '{category}'\n\nВведите ID записи для редактирования:"
                )
            await query.answer()
            return
    
    # О проекте
    elif data == "about":
        try:
            # Кнопки для социальных сетей
            buttons = [
                [InlineKeyboardButton("🌐 Сайт", url="https://simplephysics.ru")],
                [InlineKeyboardButton("🤖 Бот", url="https://t.me/simplephysicsbot")],
                [InlineKeyboardButton("📺 YouTube", url="https://youtube.com/@Simplephysics-mpu?si=vUpu2Xtzsi1KuwgK")],
                [InlineKeyboardButton("🎬 RuTube", url="https://rutube.ru/channel/43627801")],
                [InlineKeyboardButton("💬 ВКонтакте", url="https://vk.com/simplephysicsmp")],
                [InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_menu")]
            ]
            keyboard = InlineKeyboardMarkup(buttons)
            response = """Привет👋\n\nМы команда \"Simple Physics\" из Московского Политеха. Мы уверены, что физика намного интереснее, чем ты думаешь, поэтому хотим показать тебе это воочию😲\n\nЗдесь ты сможешь найти много полезного и интересного материала, который поможет тебе сдать ЕГЭ на максимум баллов😮\n\nНе упусти шанс готовиться к экзамену с нами — ПРИСОЕДИНЯЙСЯ❗️"""
            logger.info("Пытаемся отправить сообщение 'О проекте'")
            try:
                await query.message.edit_text(response, reply_markup=keyboard)
            except Exception as e:
                logger.error(e)
            try:
                await query.answer()
            except:
                pass
        except Exception as e:
            logger.error(f"Ошибка при обработке 'О проекте': {e}")
            await query.message.reply_text("⚠️ Произошла ошибка при обработке 'О проекте'. Попробуйте еще раз или сообщите админу.")

async def show_all_items_moderator(query, category):
    """Показать все записи раздела модератору"""
    items = []
    category_name = ""
    
    if category == "comics":
        items = get_comics()
        category_name = "Комиксы"
    elif category == "memes":
        items = get_memes()
        category_name = "Мемы"
    elif category == "history":
        items = get_history()
        category_name = "Исторические справки"
    elif category == "movies":
        items = get_movies()
        category_name = "Физика в фильмах"
    elif category == "calendar":
        items = get_calendar()
        category_name = "Календарик"
    elif category == "notes":
        items = get_notes()
        category_name = "Конспекты"
    elif category == "formulas":
        items = []
        category_name = "Формулы (только локальные файлы из media/formulas)"
    
    if not items:
        text = f"📋 {category_name}\n\nЗаписей нет."
    else:
        text = f"📋 {category_name} (всего: {len(items)})\n\n"
        for item in items:
            if category == "calendar":
                item_id, date, title, content, file_id = item
                text += f"ID: {item_id} | {date} - {title}\n"
            else:
                item_id, title = item[:2]
                text += f"ID: {item_id} | {title}\n"
    
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="mod_back")]])
    try:
        await query.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        await query.message.reply_text(text, reply_markup=keyboard)

async def handle_moderator_id_input(update, context, category, action, item_id):
    """Обработка ввода ID модератором"""
    if action == "delete":
        deleted = False
        if category == "comics":
            deleted = delete_comic(item_id)
        elif category == "memes":
            deleted = delete_meme(item_id)
        elif category == "history":
            deleted = delete_history(item_id)
        elif category == "movies":
            deleted = delete_movie(item_id)
        elif category == "calendar":
            deleted = delete_calendar(item_id)
        elif category == "notes":
            deleted = delete_note(item_id)
        elif category == "formulas":
            await update.message.reply_text(
                "В разделе «Формулы» показываются только локальные файлы из media/formulas. Удаление через бота недоступно."
            )
            context.user_data['moderator_waiting_id'] = False
            await update.message.reply_text(
                "🔧 Режим модератора\n\nВыберите раздел:",
                reply_markup=get_moderator_menu()
            )
            return
        
        if deleted:
            await update.message.reply_text(f"✅ Запись с ID {item_id} успешно удалена.")
        else:
            await update.message.reply_text(f"❌ Запись с ID {item_id} не найдена.")
        context.user_data['moderator_waiting_id'] = False
        await update.message.reply_text(
            "🔧 Режим модератора\n\nВыберите раздел:",
            reply_markup=get_moderator_menu()
        )
    
    elif action == "edit":
        item = None
        if category == "comics":
            item = get_comic_by_id(item_id)
        elif category == "memes":
            item = get_meme_by_id(item_id)
        elif category == "history":
            item = get_history_by_id(item_id)
        elif category == "movies":
            item = get_movie_by_id(item_id)
        elif category == "calendar":
            item = get_calendar_by_id(item_id)
        elif category == "notes":
            item = get_note_by_id(item_id)
        elif category == "formulas":
            await update.message.reply_text(
                "В разделе «Формулы» только локальные файлы из media/formulas. Редактирование по ID недоступно."
            )
            context.user_data['moderator_waiting_id'] = False
            await update.message.reply_text(
                "🔧 Режим модератора\n\nВыберите раздел:",
                reply_markup=get_moderator_menu()
            )
            return
        
        if not item:
            await update.message.reply_text(f"❌ Запись с ID {item_id} не найдена.")
            context.user_data['moderator_waiting_id'] = False
            await update.message.reply_text(
                "🔧 Режим модератора\n\nВыберите раздел:",
                reply_markup=get_moderator_menu()
            )
            return
        
        # Сохраняем старое фото для случая пропуска
        if category == "calendar":
            context.user_data['moderator_old_file_id'] = item[4] if len(item) > 4 else None
        else:
            context.user_data['moderator_old_file_id'] = item[3] if len(item) > 3 else None
        
        context.user_data['moderator_item_id'] = item_id
        context.user_data['moderator_waiting_id'] = False
        context.user_data['moderator_adding_photo'] = True
        await update.message.reply_text(
            f"✏️ Редактирование записи ID {item_id}\n\n📸 Отправьте новое фото (или отправьте 'пропустить' чтобы оставить старое):"
        )

async def handle_moderator_text_input(update, context, category, action, text):
    """Обработка ввода текста модератором"""
    item_id = context.user_data.get('moderator_item_id')
    file_id = context.user_data.get('moderator_file_id')
    title = context.user_data.get('moderator_title', 'Без названия')
    
    if action == "add":
        # Добавление новой записи
        if category == "comics":
            add_comic(title, file_id, text)
        elif category == "memes":
            add_meme(title, file_id, text)
        elif category == "history":
            add_history(title, text, file_id)
        elif category == "movies":
            add_movie(title, text, file_id)
        elif category == "calendar":
            add_calendar("Дата", title, text, file_id)
        elif category == "notes":
            add_note(title, file_id, text)
        elif category == "formulas":
            await update.message.reply_text(
                "В разделе «Формулы» используются только локальные файлы. Добавьте изображения в папку media/formulas и перезапустите бота."
            )
            context.user_data['moderator_waiting_text'] = False
            context.user_data['moderator_adding_photo'] = False
            context.user_data.pop('moderator_file_id', None)
            await update.message.reply_text(
                "🔧 Режим модератора\n\nВыберите раздел:",
                reply_markup=get_moderator_menu()
            )
            return
        
        await update.message.reply_text("✅ Запись успешно добавлена!")
        context.user_data['moderator_waiting_text'] = False
        context.user_data['moderator_adding_photo'] = False
        context.user_data.pop('moderator_file_id', None)
        context.user_data.pop('moderator_title', None)
        await update.message.reply_text(
            "🔧 Режим модератора\n\nВыберите раздел:",
            reply_markup=get_moderator_menu()
        )
    
    elif action == "edit":
        # Редактирование существующей записи
        if category == "comics":
            update_comic(item_id, content=text, file_id=file_id)
        elif category == "memes":
            update_meme(item_id, content=text, file_id=file_id)
        elif category == "history":
            update_history(item_id, content=text, file_id=file_id)
        elif category == "movies":
            update_movie(item_id, content=text, file_id=file_id)
        elif category == "calendar":
            update_calendar(item_id, content=text, file_id=file_id)
        elif category == "notes":
            update_note(item_id, content=text, file_id=file_id)
        elif category == "formulas":
            await update.message.reply_text(
                "В разделе «Формулы» только локальные файлы. Редактирование через бота недоступно."
            )
            context.user_data['moderator_waiting_text'] = False
            context.user_data['moderator_adding_photo'] = False
            await update.message.reply_text(
                "🔧 Режим модератора\n\nВыберите раздел:",
                reply_markup=get_moderator_menu()
            )
            return
        
        await update.message.reply_text(f"✅ Запись ID {item_id} успешно отредактирована!")
        context.user_data['moderator_waiting_text'] = False
        context.user_data['moderator_adding_photo'] = False
        context.user_data.pop('moderator_file_id', None)
        context.user_data.pop('moderator_item_id', None)
        await update.message.reply_text(
            "🔧 Режим модератора\n\nВыберите раздел:",
            reply_markup=get_moderator_menu()
        )

async def handle_moderator_photo(update, context):
    """Обработка фото модератором"""
    if not context.user_data.get('is_moderator'):
        return
    
    if not update.message.photo:
        return
    
    if not context.user_data.get('moderator_adding_photo'):
        return
    
    photo = update.message.photo[-1]
    category = context.user_data.get('moderator_category')
    action = context.user_data.get('moderator_action')
    
    context.user_data['moderator_file_id'] = photo.file_id
    context.user_data['moderator_adding_photo'] = False
    context.user_data['moderator_waiting_text'] = True
    
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("⏭️ Пропустить текст", callback_data="mod_skip_text")
    ]])
    
    if action == "add":
        await update.message.reply_text(
            "✏️ Отправьте текст для записи или нажмите 'Пропустить текст':",
            reply_markup=keyboard
        )
    elif action == "edit":
        await update.message.reply_text(
            "✏️ Отправьте новый текст для записи или нажмите 'Пропустить текст':",
            reply_markup=keyboard
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    # Проверка пароля модератора
    if context.user_data.get('moderator_waiting_password'):
        password = update.message.text
        if password == MODERATOR_PASSWORD:
            context.user_data['moderator_waiting_password'] = False
            context.user_data['is_moderator'] = True
            await update.message.reply_text(
                "✅ Пароль верный! Добро пожаловать в режим модератора.",
                reply_markup=get_moderator_menu()
            )
        else:
            await update.message.reply_text(
                "❌ Неверный пароль. Попробуйте еще раз или отправьте /moderator для повторной попытки."
            )
        return
    
    # Обработка действий модератора
    if context.user_data.get('is_moderator'):
        # Обработка ввода названия
        if context.user_data.get('moderator_waiting_title'):
            context.user_data['moderator_title'] = update.message.text
            context.user_data['moderator_waiting_title'] = False
            context.user_data['moderator_adding_photo'] = True
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("⏭️ Пропустить фото", callback_data="mod_skip_photo")
            ]])
            await update.message.reply_text(
                "📸 Отправьте фото или нажмите 'Пропустить фото':",
                reply_markup=keyboard
            )
            return
        
        # Обработка добавления контента (сначала фото, потом текст)
        if context.user_data.get('moderator_adding_photo'):
            # Проверка на "пропустить" при редактировании (только текст, не фото)
            if update.message.text and update.message.text.lower() == 'пропустить':
                category = context.user_data.get('moderator_category')
                action = context.user_data.get('moderator_action')
                if action == "edit":
                    # При редактировании без нового фото используем старое фото
                    old_file_id = context.user_data.get('moderator_old_file_id')
                    context.user_data['moderator_file_id'] = old_file_id
                    context.user_data['moderator_adding_photo'] = False
                    context.user_data['moderator_waiting_text'] = True
                    keyboard = InlineKeyboardMarkup([[
                        InlineKeyboardButton("⏭️ Пропустить текст", callback_data="mod_skip_text")
                    ]])
                    await update.message.reply_text(
                        "✏️ Отправьте новый текст для записи или нажмите 'Пропустить текст':",
                        reply_markup=keyboard
                    )
                return
            # Фото обрабатывается в handle_moderator_photo
            return
            # Проверка на "пропустить" при редактировании
            if update.message.text and update.message.text.lower() == 'пропустить':
                category = context.user_data.get('moderator_category')
                action = context.user_data.get('moderator_action')
                if action == "edit":
                    # При редактировании без нового фото используем старое фото
                    old_file_id = context.user_data.get('moderator_old_file_id')
                    context.user_data['moderator_file_id'] = old_file_id
                    context.user_data['moderator_adding_photo'] = False
                    context.user_data['moderator_waiting_text'] = True
                    await update.message.reply_text("✏️ Отправьте новый текст для записи:")
                return
            # Фото обрабатывается в handle_moderator_photo
            return
        
        # Обработка ввода ID для удаления/просмотра/редактирования
        if context.user_data.get('moderator_waiting_id'):
            category = context.user_data.get('moderator_category')
            action = context.user_data.get('moderator_action')
            try:
                item_id = int(update.message.text)
                await handle_moderator_id_input(update, context, category, action, item_id)
            except ValueError:
                await update.message.reply_text("❌ Неверный формат ID. Введите число.")
            return
        
        # Обработка ввода текста при добавлении/редактировании
        if context.user_data.get('moderator_waiting_text'):
            # Проверка на "пропустить"
            if update.message.text and update.message.text.lower() in ['пропустить', 'пропустить текст']:
                category = context.user_data.get('moderator_category')
                action = context.user_data.get('moderator_action')
                file_id = context.user_data.get('moderator_file_id')
                
                # Добавляем/редактируем запись без текста
                title = context.user_data.get('moderator_title', 'Без названия')
                if action == "add":
                    if category == "comics":
                        add_comic(title, file_id, None)
                    elif category == "memes":
                        add_meme(title, file_id, None)
                    elif category == "history":
                        add_history(title, "", file_id)
                    elif category == "movies":
                        add_movie(title, "", file_id)
                    elif category == "calendar":
                        add_calendar("Дата", title, "", file_id)
                    elif category == "notes":
                        add_note(title, file_id, None)
                    elif category == "formulas":
                        await update.message.reply_text(
                            "В разделе «Формулы» используются только локальные файлы. Добавьте изображения в папку media/formulas и перезапустите бота."
                        )
                        context.user_data['moderator_waiting_text'] = False
                        context.user_data['moderator_adding_photo'] = False
                        context.user_data.pop('moderator_file_id', None)
                        await update.message.reply_text(
                            "🔧 Режим модератора\n\nВыберите раздел:",
                            reply_markup=get_moderator_menu()
                        )
                        return
                    
                    await update.message.reply_text("✅ Запись успешно добавлена!")
                elif action == "edit":
                    item_id = context.user_data.get('moderator_item_id')
                    if category == "comics":
                        update_comic(item_id, file_id=file_id)
                    elif category == "memes":
                        update_meme(item_id, file_id=file_id)
                    elif category == "history":
                        update_history(item_id, file_id=file_id)
                    elif category == "movies":
                        update_movie(item_id, file_id=file_id)
                    elif category == "calendar":
                        update_calendar(item_id, file_id=file_id)
                    elif category == "notes":
                        update_note(item_id, file_id=file_id)
                    elif category == "formulas":
                        await update.message.reply_text(
                            "В разделе «Формулы» только локальные файлы. Редактирование через бота недоступно."
                        )
                        context.user_data['moderator_waiting_text'] = False
                        context.user_data['moderator_adding_photo'] = False
                        await update.message.reply_text(
                            "🔧 Режим модератора\n\nВыберите раздел:",
                            reply_markup=get_moderator_menu()
                        )
                        return
                    
                    await update.message.reply_text(f"✅ Запись ID {item_id} успешно отредактирована!")
                
                context.user_data['moderator_waiting_text'] = False
                context.user_data['moderator_adding_photo'] = False
                context.user_data.pop('moderator_file_id', None)
                context.user_data.pop('moderator_item_id', None)
                context.user_data.pop('moderator_old_file_id', None)
                context.user_data.pop('moderator_title', None)
                await update.message.reply_text(
                    "🔧 Режим модератора\n\nВыберите раздел:",
                    reply_markup=get_moderator_menu()
                )
                return
            
            category = context.user_data.get('moderator_category')
            action = context.user_data.get('moderator_action')
            text = update.message.text
            await handle_moderator_text_input(update, context, category, action, text)
            return
        
        # Если модератор в режиме, но не обрабатывается выше - игнорируем
        return
    
    # Просто показываем меню если написали текст
    await update.message.reply_text(
        "Выберите раздел:",
        reply_markup=get_main_menu()
    )

# ============================================================================
# АДМИН-КОМАНДЫ (только для администратора)
# ============================================================================

async def add_comic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для добавления комикса"""
    user_id = update.effective_user.id
    
    # Проверка прав администратора
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав!")
        return
    
    # Сохраняем состояние (что админ хочет добавить комикс)
    context.user_data['adding'] = 'comic_title'
    await update.message.reply_text("✏️ Введите название комикса:")


async def add_video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для добавления видео"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав!")
        return
    
    context.user_data['adding'] = 'video_title'
    await update.message.reply_text("✏️ Введите название видео:")

async def add_meme_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для добавления мема"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав!")
        return
    
    context.user_data['adding'] = 'meme_title'
    await update.message.reply_text("✏️ Введите название мема:")

async def add_memes_batch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для пакетного добавления мемов (просто отправляйте фото подряд)"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав!")
        return
    
    context.user_data['batch_adding_memes'] = True
    context.user_data['meme_counter'] = 0
    context.user_data['meme_titles'] = [
        "Объект нагревается - его атомы",
        "Спасибо сломанной вытяжке - дымкор эстетик",
        "14 000 625 измерений - один сошёлся",
        "Неупругая деформация"
    ]
    
    await update.message.reply_text(
        "📸 Режим пакетного добавления мемов активирован!\n\n"
        "Просто отправляйте фото мемов подряд, и они будут добавлены автоматически.\n\n"
        f"Ожидаемые мемы ({len(context.user_data['meme_titles'])}):\n" +
        "\n".join([f"{i+1}. {title}" for i, title in enumerate(context.user_data['meme_titles'])]) +
        "\n\nОтправьте /stop_batch чтобы остановить."
    )

async def add_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для добавления исторической справки"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав!")
        return
    
    context.user_data['adding'] = 'history_title'
    await update.message.reply_text("✏️ Введите название исторической справки:")

async def add_movie_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для добавления физики в фильмах"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав!")
        return
    
    context.user_data['adding'] = 'movie_title'
    await update.message.reply_text("✏️ Введите название фильма/сцены:")

async def add_calendar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для добавления записи в календарик"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав!")
        return
    
    context.user_data['adding'] = 'calendar_date'
    await update.message.reply_text("✏️ Введите дату (например: 15 января):")

async def add_note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для добавления конспекта"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав!")
        return
    
    context.user_data['adding'] = 'note_title'
    await update.message.reply_text("✏️ Введите название конспекта:")

async def add_comics_batch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для пакетного добавления комиксов"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав!")
        return
    
    context.user_data['batch_adding_comics'] = True
    context.user_data['comic_counter'] = 0
    context.user_data['comic_titles'] = []
    context.user_data['waiting_for_comic_title'] = True
    
    await update.message.reply_text(
        "📸 Режим пакетного добавления комиксов активирован!\n\n"
        "Для каждого комикса:\n"
        "1. Отправьте название комикса\n"
        "2. Отправьте описание (или 'пропустить')\n"
        "3. Отправьте фото\n"
        "Повторяйте для каждого комикса.\n\n"
        "Отправьте /stop_batch чтобы остановить."
    )

async def add_history_batch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для пакетного добавления исторических справок"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав!")
        return
    
    context.user_data['batch_adding_history'] = True
    context.user_data['history_counter'] = 0
    context.user_data['waiting_for_history_title'] = True
    
    await update.message.reply_text(
        "📚 Режим пакетного добавления исторических справок активирован!\n\n"
        "Для каждой справки:\n"
        "1. Отправьте название справки\n"
        "2. Отправьте содержание справки\n"
        "3. Отправьте фото (или 'пропустить')\n"
        "Повторяйте для каждой справки.\n\n"
        "Отправьте /stop_batch чтобы остановить."
    )

async def add_movies_batch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для пакетного добавления физики в фильмах"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав!")
        return
    
    context.user_data['batch_adding_movies'] = True
    context.user_data['movie_counter'] = 0
    context.user_data['waiting_for_movie_title'] = True
    
    await update.message.reply_text(
        "🎬 Режим пакетного добавления физики в фильмах активирован!\n\n"
        "Для каждой записи:\n"
        "1. Отправьте название фильма/сцены\n"
        "2. Отправьте описание физики\n"
        "3. Отправьте фото (или 'пропустить')\n\n"
        "Отправьте /stop_batch чтобы остановить."
    )

async def add_calendar_batch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для пакетного добавления записей в календарик"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав!")
        return
    
    context.user_data['batch_adding_calendar'] = True
    context.user_data['calendar_counter'] = 0
    context.user_data['waiting_for_calendar_date'] = True
    
    await update.message.reply_text(
        "📅 Режим пакетного добавления календарика активирован!\n\n"
        "Для каждой записи:\n"
        "1. Отправьте дату (например: 15 января)\n"
        "2. Отправьте заголовок события\n"
        "3. Отправьте описание события\n"
        "4. Отправьте фото (или 'пропустить')\n\n"
        "Отправьте /stop_batch чтобы остановить."
    )

async def add_notes_batch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для пакетного добавления конспектов"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав!")
        return
    
    context.user_data['batch_adding_notes'] = True
    context.user_data['note_counter'] = 0
    context.user_data['waiting_for_note_title'] = True
    
    await update.message.reply_text(
        "📝 Режим пакетного добавления конспектов активирован!\n\n"
        "Для каждого конспекта:\n"
        "1. Отправьте название конспекта\n"
        "2. Отправьте описание (или 'пропустить')\n"
        "3. Отправьте фото\n"
        "Повторяйте для каждого конспекта.\n\n"
        "Отправьте /stop_batch чтобы остановить."
    )

async def stop_batch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Остановка пакетного добавления"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав!")
        return
    
    # Останавливаем все режимы пакетного добавления
    stopped = []
    if context.user_data.get('batch_adding_memes'):
        count = context.user_data.get('meme_counter', 0)
        context.user_data['batch_adding_memes'] = False
        context.user_data['meme_counter'] = 0
        stopped.append(f"мемов: {count}")
    
    if context.user_data.get('batch_adding_comics'):
        count = context.user_data.get('comic_counter', 0)
        context.user_data['batch_adding_comics'] = False
        context.user_data['comic_counter'] = 0
        stopped.append(f"комиксов: {count}")
    
    if context.user_data.get('batch_adding_history'):
        count = context.user_data.get('history_counter', 0)
        context.user_data['batch_adding_history'] = False
        context.user_data['history_counter'] = 0
        stopped.append(f"исторических справок: {count}")
    
    if context.user_data.get('batch_adding_movies'):
        count = context.user_data.get('movie_counter', 0)
        context.user_data['batch_adding_movies'] = False
        context.user_data['movie_counter'] = 0
        stopped.append(f"записей о фильмах: {count}")
    
    if context.user_data.get('batch_adding_calendar'):
        count = context.user_data.get('calendar_counter', 0)
        context.user_data['batch_adding_calendar'] = False
        context.user_data['calendar_counter'] = 0
        stopped.append(f"записей календарика: {count}")
    
    if context.user_data.get('batch_adding_notes'):
        count = context.user_data.get('note_counter', 0)
        context.user_data['batch_adding_notes'] = False
        context.user_data['note_counter'] = 0
        stopped.append(f"конспектов: {count}")
    
    if stopped:
        await update.message.reply_text(f"✅ Пакетное добавление остановлено. Добавлено: {', '.join(stopped)}")
    else:
        await update.message.reply_text("⚠️ Пакетное добавление не активно")

async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для получения file_id изображения (для админа)"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав!")
        return
    
    # Устанавливаем флаг, что админ хочет получить file_id
    context.user_data['getting_file_id'] = True
    await update.message.reply_text("📸 Теперь отправьте изображение, и я покажу его file_id")

async def handle_admin_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка добавления контента админом"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        return  # Не админ - игнорируем
    
    # Проверяем, хочет ли админ получить file_id
    if context.user_data.get('getting_file_id'):
        if update.message.photo:
            photo = update.message.photo[-1]
            file_id = photo.file_id
            await update.message.reply_text(
                f"📋 File ID этого изображения:\n\n`{file_id}`\n\n"
                f"Используйте этот ID в скрипте add_memes.py или команде /add_meme",
                parse_mode='Markdown'
            )
            context.user_data['getting_file_id'] = False
        else:
            await update.message.reply_text("❌ Отправьте изображение, чтобы получить его file_id")
        return
    
    # Пакетное добавление комиксов
    if context.user_data.get('batch_adding_comics'):
        if context.user_data.get('waiting_for_comic_title'):
            context.user_data['comic_title'] = update.message.text
            context.user_data['waiting_for_comic_title'] = False
            context.user_data['waiting_for_comic_content'] = True
            await update.message.reply_text("✏️ Отправьте описание комикса (или 'пропустить' чтобы без описания)")
        elif context.user_data.get('waiting_for_comic_content'):
            context.user_data['comic_content'] = update.message.text if update.message.text.lower() != 'пропустить' else None
            context.user_data['waiting_for_comic_content'] = False
            await update.message.reply_text("📸 Теперь отправьте фото комикса")
        return
    
    # Пакетное добавление исторических справок
    if context.user_data.get('batch_adding_history'):
        if context.user_data.get('waiting_for_history_title'):
            context.user_data['history_title'] = update.message.text
            context.user_data['waiting_for_history_title'] = False
            context.user_data['waiting_for_history_content'] = True
            await update.message.reply_text("✏️ Теперь отправьте содержание исторической справки")
        elif context.user_data.get('waiting_for_history_content'):
            context.user_data['history_content'] = update.message.text
            context.user_data['waiting_for_history_content'] = False
            context.user_data['waiting_for_history_photo'] = True
            await update.message.reply_text("📸 Отправьте фото (или 'пропустить' чтобы без фото)")
        elif context.user_data.get('waiting_for_history_photo'):
            if update.message.text and update.message.text.lower() == 'пропустить':
                title = context.user_data.get('history_title')
                content = context.user_data.get('history_content')
                add_history(title, content, None)
                context.user_data['history_counter'] = context.user_data.get('history_counter', 0) + 1
                context.user_data['waiting_for_history_photo'] = False
                context.user_data['waiting_for_history_title'] = True
                await update.message.reply_text(
                    f"✅ Историческая справка добавлена: {title}\n\n"
                    f"Отправьте следующее название или /stop_batch чтобы остановить."
                )
        return
    
    # Пакетное добавление физики в фильмах
    if context.user_data.get('batch_adding_movies'):
        if context.user_data.get('waiting_for_movie_title'):
            context.user_data['movie_title'] = update.message.text
            context.user_data['waiting_for_movie_title'] = False
            context.user_data['waiting_for_movie_content'] = True
            await update.message.reply_text("✏️ Теперь отправьте описание физики в этом фильме")
        elif context.user_data.get('waiting_for_movie_content'):
            context.user_data['movie_content'] = update.message.text
            context.user_data['waiting_for_movie_content'] = False
            context.user_data['waiting_for_movie_photo'] = True
            await update.message.reply_text("📸 Отправьте фото (или 'пропустить' чтобы без фото)")
        elif context.user_data.get('waiting_for_movie_photo'):
            if update.message.text and update.message.text.lower() == 'пропустить':
                title = context.user_data.get('movie_title')
                content = context.user_data.get('movie_content')
                add_movie(title, content, None)
                context.user_data['movie_counter'] = context.user_data.get('movie_counter', 0) + 1
                context.user_data['waiting_for_movie_photo'] = False
                context.user_data['waiting_for_movie_title'] = True
                await update.message.reply_text(
                    f"✅ Запись добавлена: {title}\n\n"
                    f"Отправьте следующее название или /stop_batch чтобы остановить."
                )
        return
    
    # Пакетное добавление календарика
    if context.user_data.get('batch_adding_calendar'):
        if context.user_data.get('waiting_for_calendar_date'):
            context.user_data['calendar_date'] = update.message.text
            context.user_data['waiting_for_calendar_date'] = False
            context.user_data['waiting_for_calendar_title'] = True
            await update.message.reply_text("✏️ Теперь отправьте заголовок события")
        elif context.user_data.get('waiting_for_calendar_title'):
            context.user_data['calendar_title'] = update.message.text
            context.user_data['waiting_for_calendar_title'] = False
            context.user_data['waiting_for_calendar_content'] = True
            await update.message.reply_text("✏️ Теперь отправьте описание события")
        elif context.user_data.get('waiting_for_calendar_content'):
            context.user_data['calendar_content'] = update.message.text
            context.user_data['waiting_for_calendar_content'] = False
            context.user_data['waiting_for_calendar_photo'] = True
            await update.message.reply_text("📸 Отправьте фото (или 'пропустить' чтобы без фото)")
        elif context.user_data.get('waiting_for_calendar_photo'):
            if update.message.text and update.message.text.lower() == 'пропустить':
                date = context.user_data.get('calendar_date')
                title = context.user_data.get('calendar_title')
                content = context.user_data.get('calendar_content')
                add_calendar(date, title, content, None)
                context.user_data['calendar_counter'] = context.user_data.get('calendar_counter', 0) + 1
                context.user_data['waiting_for_calendar_photo'] = False
                context.user_data['waiting_for_calendar_date'] = True
                await update.message.reply_text(
                    f"✅ Запись добавлена: {date} - {title}\n\n"
                    f"Отправьте следующую дату или /stop_batch чтобы остановить."
                )
        return
    
    # Пакетное добавление конспектов
    if context.user_data.get('batch_adding_notes'):
        if context.user_data.get('waiting_for_note_title'):
            context.user_data['note_title'] = update.message.text
            context.user_data['waiting_for_note_title'] = False
            context.user_data['waiting_for_note_content'] = True
            await update.message.reply_text("✏️ Отправьте описание конспекта (или 'пропустить' чтобы без описания)")
        elif context.user_data.get('waiting_for_note_content'):
            context.user_data['note_content'] = update.message.text if update.message.text.lower() != 'пропустить' else None
            context.user_data['waiting_for_note_content'] = False
            await update.message.reply_text("📸 Теперь отправьте фото конспекта")
        return
    
    state = context.user_data.get('adding')
    
    if state == 'comic_title':
        # Сохраняем название и ждём описание
        context.user_data['comic_title'] = update.message.text
        context.user_data['adding'] = 'comic_content'
        await update.message.reply_text("✏️ Введите описание комикса (или отправьте 'пропустить' чтобы без описания):")
    
    elif state == 'comic_content':
        context.user_data['comic_content'] = update.message.text if update.message.text.lower() != 'пропустить' else None
        context.user_data['adding'] = 'comic_photo'
        await update.message.reply_text("📸 Отправьте фото комикса")
    
    elif state == 'comic_photo':
        # Фото обрабатывается в handle_admin_photo
        pass
    
    elif state == 'video_title':
        context.user_data['video_title'] = update.message.text
        context.user_data['adding'] = 'video_url'
        await update.message.reply_text("🔗 Отправьте ссылку на видео")
    
    elif state == 'video_url':
        title = context.user_data.get('video_title')
        url = update.message.text
        add_video(title, url)
        await update.message.reply_text("✅ Видео добавлено!")
        context.user_data['adding'] = None
    
    elif state == 'meme_title':
        context.user_data['meme_title'] = update.message.text
        context.user_data['adding'] = 'meme_content'
        await update.message.reply_text("✏️ Введите описание мема (или отправьте 'пропустить' чтобы без описания):")
    
    elif state == 'meme_content':
        context.user_data['meme_content'] = update.message.text if update.message.text.lower() != 'пропустить' else None
        context.user_data['adding'] = 'meme_photo'
        await update.message.reply_text("📸 Отправьте фото мема")
    
    elif state == 'meme_photo':
        # Фото обрабатывается в handle_admin_photo
        pass
    
    elif state == 'history_title':
        context.user_data['history_title'] = update.message.text
        context.user_data['adding'] = 'history_content'
        await update.message.reply_text("✏️ Введите содержание исторической справки:")
    
    elif state == 'history_content':
        title = context.user_data.get('history_title')
        content = update.message.text
        context.user_data['history_content'] = content
        context.user_data['adding'] = 'history_photo'
        await update.message.reply_text("📸 Отправьте фото (или отправьте 'пропустить' чтобы без фото):")
    
    elif state == 'history_photo':
        title = context.user_data.get('history_title')
        content = context.user_data.get('history_content')
        if update.message.text and update.message.text.lower() == 'пропустить':
            add_history(title, content, None)
            await update.message.reply_text("✅ Историческая справка добавлена!")
            context.user_data['adding'] = None
        elif update.message.photo:
            photo = update.message.photo[-1]
            add_history(title, content, photo.file_id)
            await update.message.reply_text("✅ Историческая справка добавлена!")
            context.user_data['adding'] = None
    
    elif state == 'movie_title':
        context.user_data['movie_title'] = update.message.text
        context.user_data['adding'] = 'movie_content'
        await update.message.reply_text("✏️ Введите описание физики в этом фильме:")
    
    elif state == 'movie_content':
        title = context.user_data.get('movie_title')
        content = update.message.text
        context.user_data['movie_content'] = content
        context.user_data['adding'] = 'movie_photo'
        await update.message.reply_text("📸 Отправьте фото (или отправьте 'пропустить' чтобы без фото):")
    
    elif state == 'movie_photo':
        title = context.user_data.get('movie_title')
        content = context.user_data.get('movie_content')
        if update.message.text and update.message.text.lower() == 'пропустить':
            add_movie(title, content, None)
            await update.message.reply_text("✅ Физика в фильмах добавлена!")
            context.user_data['adding'] = None
        elif update.message.photo:
            photo = update.message.photo[-1]
            add_movie(title, content, photo.file_id)
            await update.message.reply_text("✅ Физика в фильмах добавлена!")
            context.user_data['adding'] = None
    
    elif state == 'calendar_date':
        context.user_data['calendar_date'] = update.message.text
        context.user_data['adding'] = 'calendar_title'
        await update.message.reply_text("✏️ Введите заголовок события:")
    
    elif state == 'calendar_title':
        context.user_data['calendar_title'] = update.message.text
        context.user_data['adding'] = 'calendar_content'
        await update.message.reply_text("✏️ Введите описание события:")
    
    elif state == 'calendar_content':
        date = context.user_data.get('calendar_date')
        title = context.user_data.get('calendar_title')
        content = update.message.text
        context.user_data['calendar_content'] = content
        context.user_data['adding'] = 'calendar_photo'
        await update.message.reply_text("📸 Отправьте фото (или отправьте 'пропустить' чтобы без фото):")
    
    elif state == 'calendar_photo':
        date = context.user_data.get('calendar_date')
        title = context.user_data.get('calendar_title')
        content = context.user_data.get('calendar_content')
        if update.message.text and update.message.text.lower() == 'пропустить':
            add_calendar(date, title, content, None)
            await update.message.reply_text("✅ Запись в календарик добавлена!")
            context.user_data['adding'] = None
        elif update.message.photo:
            photo = update.message.photo[-1]
            add_calendar(date, title, content, photo.file_id)
            await update.message.reply_text("✅ Запись в календарик добавлена!")
            context.user_data['adding'] = None
    
    elif state == 'note_title':
        context.user_data['note_title'] = update.message.text
        context.user_data['adding'] = 'note_content'
        await update.message.reply_text("✏️ Введите описание конспекта (или отправьте 'пропустить' чтобы без описания):")
    
    elif state == 'note_content':
        context.user_data['note_content'] = update.message.text if update.message.text.lower() != 'пропустить' else None
        context.user_data['adding'] = 'note_photo'
        await update.message.reply_text("📸 Отправьте фото конспекта")
    
    elif state == 'note_photo':
        # Фото обрабатывается в handle_admin_photo
        pass

async def handle_admin_photo(update, context):
    user_id = update.effective_user.id
    
    # Обработка фото модератором
    if context.user_data.get('is_moderator') and context.user_data.get('moderator_adding_photo'):
        await handle_moderator_photo(update, context)
        return
    
    if user_id != ADMIN_ID:
        return
    if not update.message.photo:
        return
    photo = update.message.photo[-1]
    state = context.user_data.get('adding')
    # Пакетное добавление мемов
    if context.user_data.get('batch_adding_memes'):
        counter = context.user_data.get('meme_counter', 0)
        titles = context.user_data.get('meme_titles', [])
        if counter < len(titles):
            title = titles[counter]
            conn = sqlite3.connect('physics_bot.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, file_id FROM memes WHERE title = ?', (title,))
            existing = cursor.fetchone()
            if existing:
                cursor.execute('UPDATE memes SET file_id = ? WHERE title = ?', (photo.file_id, title))
                conn.commit()
                action = 'обновлён'
            else:
                cursor.execute('INSERT INTO memes (title, file_id) VALUES (?, ?)', (title, photo.file_id))
                conn.commit()
                action = 'добавлен'
            conn.close()
            context.user_data['meme_counter'] = counter + 1
            remaining = len(titles) - (counter + 1)
            if remaining > 0:
                await update.message.reply_text(f'✅ Мем {action}: {title}\n\nОсталось добавить: {remaining}')
            else:
                await update.message.reply_text(f'✅ Последний мем {action}: {title}\n\n🎉 Все мемы успешно добавлены!')
                context.user_data['batch_adding_memes'] = False
                context.user_data['meme_counter'] = 0
        else:
            await update.message.reply_text('⚠️ Все мемы уже добавлены. Отправьте /stop_batch чтобы выйти из режима.')
        return
    # Получить file_id
    if context.user_data.get('getting_file_id') and not state:
        file_id = photo.file_id
        await update.message.reply_text(
            f'📋 File ID этого изображения:\n\n`{file_id}`\n\nИспользуйте этот ID в скрипте add_memes.py или команде /add_meme',
            parse_mode='Markdown')
        context.user_data['getting_file_id'] = False
        return
    # Пакетное добавление комиксов
    if context.user_data.get('batch_adding_comics') and not context.user_data.get('waiting_for_comic_title'):
        title = context.user_data.get('comic_title')
        content = context.user_data.get('comic_content')
        add_comic(title, photo.file_id, content)
        context.user_data['comic_counter'] = context.user_data.get('comic_counter', 0) + 1
        context.user_data['waiting_for_comic_title'] = True
        context.user_data.pop('comic_content', None)
        await update.message.reply_text(f'✅ Комикс добавлен: {title}\n\nОтправьте следующее название или /stop_batch чтобы остановить.')
        return
    # Пакетное добавление фильмов (фото)
    if context.user_data.get('batch_adding_movies') and context.user_data.get('waiting_for_movie_photo'):
        title = context.user_data.get('movie_title')
        content = context.user_data.get('movie_content')
        add_movie(title, content, photo.file_id)
        context.user_data['movie_counter'] = context.user_data.get('movie_counter', 0) + 1
        context.user_data['waiting_for_movie_photo'] = False
        context.user_data['waiting_for_movie_title'] = True
        await update.message.reply_text(f'✅ Запись добавлена: {title}\n\nОтправьте следующее название или /stop_batch чтобы остановить.')
        return
    # Пакетное добавление календарика (фото)
    if context.user_data.get('batch_adding_calendar') and context.user_data.get('waiting_for_calendar_photo'):
        date = context.user_data.get('calendar_date')
        title = context.user_data.get('calendar_title')
        content = context.user_data.get('calendar_content')
        add_calendar(date, title, content, photo.file_id)
        context.user_data['calendar_counter'] = context.user_data.get('calendar_counter', 0) + 1
        context.user_data['waiting_for_calendar_photo'] = False
        context.user_data['waiting_for_calendar_date'] = True
        await update.message.reply_text(f'✅ Запись добавлена: {date} - {title}\n\nОтправьте следующую дату или /stop_batch чтобы остановить.')
        return
    # Пакетное добавление исторических справок (фото)
    if context.user_data.get('batch_adding_history') and context.user_data.get('waiting_for_history_photo'):
        title = context.user_data.get('history_title')
        content = context.user_data.get('history_content')
        add_history(title, content, photo.file_id)
        context.user_data['history_counter'] = context.user_data.get('history_counter', 0) + 1
        context.user_data['waiting_for_history_photo'] = False
        context.user_data['waiting_for_history_title'] = True
        await update.message.reply_text(f'✅ Историческая справка добавлена: {title}\n\nОтправьте следующее название или /stop_batch чтобы остановить.')
        return
    
    # Пакетное добавление конспектов
    if context.user_data.get('batch_adding_notes') and not context.user_data.get('waiting_for_note_title'):
        title = context.user_data.get('note_title')
        content = context.user_data.get('note_content')
        add_note(title, photo.file_id, content)
        context.user_data['note_counter'] = context.user_data.get('note_counter', 0) + 1
        context.user_data['waiting_for_note_title'] = True
        context.user_data.pop('note_content', None)
        await update.message.reply_text(f'✅ Конспект добавлен: {title}\n\nОтправьте следующее название или /stop_batch чтобы остановить.')
        return
    # Обработка фото при добавлении контента
    if state == 'comic_photo':
        title = context.user_data.get('comic_title')
        content = context.user_data.get('comic_content')
        add_comic(title, photo.file_id, content)
        await update.message.reply_text('✅ Комикс добавлен!')
        context.user_data['adding'] = None
        context.user_data.pop('comic_content', None)
    elif state == 'meme_photo':
        title = context.user_data.get('meme_title')
        content = context.user_data.get('meme_content')
        add_meme(title, photo.file_id, content)
        await update.message.reply_text('✅ Мем добавлен!')
        context.user_data['adding'] = None
        context.user_data.pop('meme_content', None)
    elif state == 'movie_photo':
        title = context.user_data.get('movie_title')
        content = context.user_data.get('movie_content')
        add_movie(title, content, photo.file_id)
        await update.message.reply_text('✅ Физика в фильмах добавлена!')
        context.user_data['adding'] = None
    elif state == 'calendar_photo':
        date = context.user_data.get('calendar_date')
        title = context.user_data.get('calendar_title')
        content = context.user_data.get('calendar_content')
        add_calendar(date, title, content, photo.file_id)
        await update.message.reply_text('✅ Запись в календарик добавлена!')
        context.user_data['adding'] = None
    elif state == 'note_photo':
        title = context.user_data.get('note_title')
        content = context.user_data.get('note_content')
        add_note(title, photo.file_id, content)
        await update.message.reply_text('✅ Конспект добавлен!')
        context.user_data['adding'] = None
        context.user_data.pop('note_content', None)
    elif state == 'history_photo':
        title = context.user_data.get('history_title')
        content = context.user_data.get('history_content')
        add_history(title, content, photo.file_id)
        await update.message.reply_text('✅ Историческая справка добавлена!')
        context.user_data['adding'] = None

# ============================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================================

def main():
    """Запуск бота"""
    if not acquire_instance_lock():
        print("⚠️ Бот уже запущен в другой сессии. Завершение.")
        return

    # Создаём базу данных
    init_db()
    
    # Сканируем локальный контент
    if LOCAL_CONTENT_AVAILABLE:
        try:
            scan_local_content()
            logger.info("Локальный контент загружен")
        except Exception as e:
            logger.error(f"Ошибка при загрузке локального контента: {e}")
    
    # Создаём бота
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("moderator", moderator_command))
    app.add_handler(CommandHandler("add_comic", add_comic_command))
    app.add_handler(CommandHandler("add_card", add_comic_command))
    app.add_handler(CommandHandler("add_video", add_video_command))
    app.add_handler(CommandHandler("add_meme", add_meme_command))
    app.add_handler(CommandHandler("add_memes_batch", add_memes_batch_command))
    app.add_handler(CommandHandler("add_comics_batch", add_comics_batch_command))
    app.add_handler(CommandHandler("add_history_batch", add_history_batch_command))
    app.add_handler(CommandHandler("add_movies_batch", add_movies_batch_command))
    app.add_handler(CommandHandler("add_calendar_batch", add_calendar_batch_command))
    app.add_handler(CommandHandler("add_notes_batch", add_notes_batch_command))
    app.add_handler(CommandHandler("stop_batch", stop_batch_command))
    app.add_handler(CommandHandler("add_history", add_history_command))
    app.add_handler(CommandHandler("add_movie", add_movie_command))
    app.add_handler(CommandHandler("add_calendar", add_calendar_command))
    app.add_handler(CommandHandler("add_note", add_note_command))
    app.add_handler(CommandHandler("get_file_id", get_file_id))
    
    # Обработчик кнопок в сообщении
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    # Обработчики сообщений (админ добавляет контент)
    app.add_handler(MessageHandler(filters.PHOTO & filters.User(ADMIN_ID), handle_admin_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID), handle_admin_add))
    # Обработчик фото для модератора (для всех пользователей, проверка внутри функции)
    app.add_handler(MessageHandler(filters.PHOTO, handle_admin_photo))
    # Обычный обработчик текстовых сообщений (остальные пользователи)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Запускаем бота
    logger.info("Бот запущен!")
    try:
        app.run_polling()
    except Conflict as exc:
        logger.error(f"Конфликт запуска бота: {exc}")
        print("⚠️ Telegram сообщает, что бот уже запущен в другом месте. Проверьте другие сессии.")
    finally:
        release_instance_lock()

if __name__ == '__main__':
    if '--menu-test' in sys.argv:
        from telegram.ext import Application, CallbackQueryHandler, CommandHandler
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
        if not acquire_instance_lock():
            print("⚠️ Бот уже запущен в другой сессии. Тестовое меню не будет запущено.")
            sys.exit(1)
        async def test_start(update: Update, context):
            keyboard = [[InlineKeyboardButton('О проекте', callback_data='about_test')]]
            await update.message.reply_text('Тест меню:', reply_markup=InlineKeyboardMarkup(keyboard))
        async def test_cb(update: Update, context):
            print('INLINE_CALLBACK_OK')
            await update.callback_query.answer('Callback работает!', show_alert=True)
            await update.callback_query.edit_message_text('Работает обработчик!')
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler('start', test_start))
        app.add_handler(CallbackQueryHandler(test_cb))
        try:
            app.run_polling()
        finally:
            release_instance_lock()
        sys.exit(0)
    main()

