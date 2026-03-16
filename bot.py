"""
Простой бот для Simple Physics
Всё в одном файле для простоты понимания
"""

# Импорты
import os
import sys
import atexit
import sqlite3
import random
from pathlib import Path
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto
from telegram.error import Conflict
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import logging

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота берём из переменной окружения,
# чтобы не хранить его в открытом виде в коде.
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ID администратора (получите его через @userinfobot)
ADMIN_ID = 729218232  # Ваш ID

# ============================================================================
# РАБОТА С БАЗОЙ ДАННЫХ
# ============================================================================

def init_db():
    """Создаёт базу данных и таблицы при первом запуске"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            file_id TEXT
        )
    ''')
    
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
    
    # Таблица мемов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            file_id TEXT
        )
    ''')
    
    # Таблица исторических справок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT
        )
    ''')
    
    # Таблица физики в фильмах
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            file_id TEXT
        )
    ''')
    
    # Таблица календарика
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calendar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            title TEXT,
            content TEXT,
            file_id TEXT
        )
    ''')
    
    # Таблица конспектов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            file_id TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("База данных создана!")

def add_comic(title, file_id):
    """Добавить комикс в базу"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comics (title, file_id) VALUES (?, ?)", (title, file_id))
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

def add_meme(title, file_id):
    """Добавить мем в базу"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO memes (title, file_id) VALUES (?, ?)", (title, file_id))
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

def add_history(title, content):
    """Добавить историческую справку в базу"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO history (title, content) VALUES (?, ?)", (title, content))
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

def add_note(title, file_id):
    """Добавить конспект в базу"""
    conn = sqlite3.connect('physics_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (title, file_id) VALUES (?, ?)", (title, file_id))
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
# ЛОКАЛЬНЫЙ КОНТЕНТ ДЛЯ КАТЕГОРИЙ
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent

MOVIE_DRAGONS_LONG_TEXT = (
    "#ФизикаВФильмах\n\n"
    "😍 «Физика драконов»: кто из них мог бы летать в реальности?\n\n"
    "Мы сравниваем драконов из «Игры престолов», «Хоббита» и «Гарри Поттера» с реальными птерозаврами: "
    "смотрим на массу, площадь крыльев и то, могут ли они вообще оторваться от земли. "
    "Оказывается, гиганты вроде Смауга физически почти без шансов, а вот дракон из «Гарри Поттера» выглядит "
    "наиболее правдоподобно — хотя и с серьёзными допущениями.\n\n"
    "Подробные расчёты и больше примеров можно посмотреть в статье: https://dzen.ru/a/aTsWpLv5jxE0GBX4"
)

CATEGORY_CONTENT = {
    "comics": [
        {"file": "комиксы/Комиксы2.jpg", "title": "Комикс №1"},
        {"file": "комиксы/комиксы3.jpg", "title": "Комикс №2"},
    ],
    "memes": [
        {"file": "memes/Мемы1.jpg", "title": "Мем №1"},
        {"file": "memes/Мемы2.jpg", "title": "Мем №2"},
    ],
    "history": [
        {"file": "история/Исторические1.jpg", "title": "Историческая справка №1"},
        {"file": "история/Исторические2.jpg", "title": "Историческая справка №2"},
    ],
    "movies": [
        {
            "file": "физика/Физика0.jpg",
            "title": "«Физика драконов»: кто из них мог бы летать в реальности?",
            "caption_text": MOVIE_DRAGONS_LONG_TEXT,
        },
        {"file": "физика/Физика1.jpg", "title": "Физика в фильмах №1"},
        {"file": "физика/Физика2.jpg", "title": "Физика в фильмах №2"},
    ],
    "calendar": [
        {"file": "календарь/календарь1.jpg", "title": "Запись календарика №1"},
        {"file": "календарь/Календарик2.jpg", "title": "Запись календарика №2"},
    ],
    "notes": [
        {"file": "конспекты/Конспект1.jpg", "title": "Конспект №1"},
        {"file": "конспекты/Конспект2.jpg", "title": "Конспект №2"},
    ],
}

CATEGORY_CONFIG = {
    "comics": {
        "emoji": "🎨",
        "singular": "Комикс",
        "description": (
            "Короткие истории в картинках, которые объясняют физику через знакомые жизненные ситуации. "
            "Помогают увидеть формулы «в действии», а не только в тетради. "
            "Можно просто полистать для настроения или закрепить тему после решения задач."
        ),
        "prev_label": "◀️ Предыдущий комикс",
        "next_label": "Следующий комикс ▶️",
        "empty_text": "😔 Комиксов пока нет. Возвращайтесь позже!",
    },
    "memes": {
        "emoji": "😂",
        "singular": "Мем",
        "description": (
            "Короткие шутки и мемы про физику, учёбу и экзамены. "
            "Они помогают немного разгрузить голову, но при этом всё равно держат тебя в контексте предмета. "
            "Хороший вариант для перерыва между задачами или перед сном."
        ),
        "prev_label": "◀️ Предыдущий мем",
        "next_label": "Следующий мем ▶️",
        "empty_text": "😔 Мемов пока нет. Возвращайтесь позже!",
    },
    "history": {
        "emoji": "📚",
        "singular": "Справка",
        "description": (
            "Короткие истории о людях, идеях и экспериментах, благодаря которым появилась современная физика. "
            "Помогают почувствовать, что за формулами стоят живые сюжеты и иногда очень необычные события. "
            "Такие тексты можно использовать как примеры и интересные факты для устных ответов."
        ),
        "prev_label": "◀️ Предыдущая справка",
        "next_label": "Следующая справка ▶️",
        "empty_text": "😔 Исторических справок пока нет. Возвращайтесь позже!",
    },
    "movies": {
        "emoji": "🎬",
        "singular": "Запись",
        "description": (
            "Записи о том, как законы физики работают (или не работают) в любимых фильмах и сериалах. "
            "Каждая история — повод вспомнить теорию и посмотреть на привычные сцены с научной стороны."
        ),
        "prev_label": "◀️ Предыдущая запись",
        "next_label": "Следующая запись ▶️",
        "empty_text": "😔 Записей о физике в фильмах пока нет. Возвращайтесь позже!",
    },
    "calendar": {
        "emoji": "📅",
        "singular": "Запись календарика",
        "description": (
            "Календарь событий из мира физики: даты открытий, юбилеи учёных и просто любопытные поводы. "
            "Такие заметки помогают увидеть, что физика развивается каждый год, а не живёт только в учебнике. "
            "Можно использовать как идеи для мини‑докладов или записывать важные даты в свой ежедневник."
        ),
        "prev_label": "◀️ Предыдущая запись",
        "next_label": "Следующая запись ▶️",
        "empty_text": "😔 Записей в календарике пока нет. Возвращайтесь позже!",
    },
    "notes": {
        "emoji": "📝",
        "singular": "Конспект",
        "description": (
            "Краткие и структурированные конспекты по важным темам физики. "
            "В них собраны основные формулы, ключевые идеи и типовые примеры без лишней воды. "
            "Удобно пролистать перед контрольной, зачётом или экзаменом, чтобы быстро освежить главные мысли."
        ),
        "prev_label": "◀️ Предыдущий конспект",
        "next_label": "Следующий конспект ▶️",
        "empty_text": "😔 Конспектов пока нет. Возвращайтесь позже!",
    },
}

# Директории с локальными файлами для категорий
CATEGORY_DIRS = {
    "comics": "комиксы",
    "memes": "memes",
    "history": "история",
    "movies": "физика",
    "calendar": "календарь",
    "notes": "конспекты",
}

def _get_category_items(category: str):
    """Возвращает список элементов категории на основе файлов в папке."""
    folder_name = CATEGORY_DIRS.get(category)
    if not folder_name:
        return []

    folder_path = BASE_DIR / folder_name
    if not folder_path.exists() or not folder_path.is_dir():
        return []

    exts = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    files = sorted(
        [
            f
            for f in folder_path.iterdir()
            if f.is_file() and f.suffix.lower() in exts
        ],
        key=lambda p: p.name.lower(),
    )

    items = []
    for f in files:
        rel_path = f"{folder_name}/{f.name}"

        # Заголовок по умолчанию — без нумерации вида «1 из N»
        base_title = f.stem

        item = {"file": rel_path, "title": base_title}

        # Для фильмов особый длинный текст для файла с драконами
        if category == "movies" and "физика0" in f.name.lower():
            item["caption_text"] = MOVIE_DRAGONS_LONG_TEXT

        items.append(item)

    return items

QUIZ_QUESTIONS = [
    {
        "id": "q1",
        "text": "Представь: ты подпрыгнул вертикально вверх. Пока ты летишь вверх, какие силы действуют на тебя?",
        "options": [
            "Только сила тяжести",
            "Сила тяжести и сила инерции",
            "Сила тяжести и сила Архимеда",
        ],
        "correct": 0,
        "explanation": "После отрыва от поверхности тебя тянет только Земля (сила тяжести). Никакой отдельной «силы инерции» нет — инерция это свойство, а не сила.",
    },
    {
        "id": "q2",
        "text": "Почему космонавты на орбите кажутся невесомыми?",
        "options": [
            "Потому что гравитации там почти нет",
            "Потому что они и корабль падают вместе вокруг Земли",
            "Потому что там действует сила Архимеда",
        ],
        "correct": 1,
        "explanation": "На орбите гравитация почти такая же, как у поверхности. Но космонавты и корабль находятся в свободном падении, поэтому опора на них не давит — возникает состояние невесомости.",
    },
    {
        "id": "q3",
        "text": "Шарик катится по горизонтальному столу. Что нужно, чтобы он продолжал двигаться равномерно и прямолинейно?",
        "options": [
            "Нужно постоянно толкать шарик вперёд",
            "Ничего — без трения он сам будет катиться",
            "Нужно уравновесить силы: тянуть вперёд и назад одновременно",
        ],
        "correct": 1,
        "explanation": "По первому закону Ньютона, если на тело не действуют силы (например, нет трения), оно движется равномерно и прямолинейно без «подталкиваний».",
    },
]


FORMULA_CARDS = [
    {
        "id": "mech_uniform_motion",
        "title": "Механика: равномерное прямолинейное движение",
        "content": (
            "🔹 Тело движется с постоянной скоростью по прямой, ускорение равно нулю.\n"
            "🔹 Основные формулы:\n"
            "   • s = v · t — путь при равномерном движении.\n"
            "   • v = s / t — средняя скорость на участке пути.\n"
            "🔹 Если на тело не действуют силы (или они уравновешены), такое движение описывает первый закон Ньютона.\n"
            "🔹 В задачах часто важно аккуратно перевести километры в метры и часы в секунды, чтобы правильно подставить значения."
        ),
    },
    {
        "id": "mech_acc_motion",
        "title": "Механика: равноускоренное движение без начальной скорости",
        "content": (
            "🔹 Тело стартует из состояния покоя и движется с постоянным ускорением a.\n"
            "🔹 Основные формулы (v₀ = 0):\n"
            "   • v = a · t — скорость через время t.\n"
            "   • s = (a · t²) / 2 — путь за время t.\n"
            "🔹 Эти формулы используют, например, при свободном падении без учёта сопротивления воздуха (a = g).\n"
            "🔹 Важно не путать мгновенную скорость v и среднюю скорость, а также понимать, в какую сторону направлено ускорение."
        ),
    },
    {
        "id": "mech_dynamics_energy",
        "title": "Механика: силы и энергия",
        "content": (
            "🔹 Второй закон Ньютона связывает силу, массу и ускорение: F = m · a.\n"
            "🔹 Кинетическая энергия тела: Eₖ = (m · v²) / 2 — чем больше масса и скорость, тем сильнее «разогнано» тело.\n"
            "🔹 Потенциальная энергия в поле тяжести (у поверхности Земли): Eₚ = m · g · h, где h — высота над уровнем отсчёта.\n"
            "🔹 В задачах часто используют закон сохранения энергии: сумма кинетической и потенциальной энергии "
            "замкнутой системы остаётся постоянной, если нет потерь на трение и другие силы сопротивления."
        ),
    },
]


async def send_quiz(chat):
    """Отправляет один вопрос квиза с вариантами ответов."""
    question = random.choice(QUIZ_QUESTIONS)
    # Текст вариантов показываем в сообщении, а на кнопках — только номера,
    # чтобы ничего не обрезалось.
    options_lines = [
        "🧠 Вопрос дня — небольшая задачка, чтобы размять мозг и вспомнить базовые идеи из физики.",
        "Можно просто попробовать ответить, а можно обсудить вопрос с друзьями или учителем.",
        "",
        question["text"],
        "",
    ]
    for idx, option in enumerate(question["options"], start=1):
        options_lines.append(f"{idx}) {option}")

    buttons = [
        [
            InlineKeyboardButton(
                str(idx + 1),
                callback_data=f"quiz_ans_{question['id']}_{idx}",
            )
            for idx in range(len(question["options"]))
        ],
        [InlineKeyboardButton("🏠 В меню", callback_data="back_to_menu")],
    ]
    await chat.send_message(
        "\n".join(options_lines),
        reply_markup=InlineKeyboardMarkup(buttons),
    )

MEDIA_CACHE = {}
FILE_ID_CACHE = {}
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

async def send_category_item(query, category, index, edit=False):
    """Показать элемент категории из локальных файлов"""
    config = CATEGORY_CONFIG.get(category)
    items = _get_category_items(category)
    total = len(items)

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
                await query.message.edit_text(
                    "⚠️ Ошибка конфигурации категории.", reply_markup=back_keyboard
                )
        except Exception as e:
            logger.error(e)
        return

    if total == 0:
        try:
            if edit:
                await query.message.edit_text(config["empty_text"], reply_markup=back_keyboard)
            else:
                await query.message.edit_text(config["empty_text"], reply_markup=back_keyboard)
        except Exception as e:
            logger.error(e)
        return

    index = index % total
    item = items[index]

    # Инициализируем кэш file_id под реальное количество файлов
    file_ids = FILE_ID_CACHE.get(category)
    if not file_ids or len(file_ids) != total:
        file_ids = [None] * total
        FILE_ID_CACHE[category] = file_ids
    cached_file_id = file_ids[index]

    media_bytes = None
    if not cached_file_id:
        media_bytes = _load_media(item["file"])

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

    caption_lines = [f"{config['emoji']} {item['title']}"]
    extra_caption = item.get("caption_text")
    if extra_caption:
        caption_lines.append(extra_caption)
    elif "description" in config:
        caption_lines.append(config["description"])
    # Убираем подпись вида «Мем 1 из 2»
    caption = "\n\n".join(caption_lines)

    if not cached_file_id and not media_bytes:
        logger.error(f"Файл {item['file']} не найден или не загружен")
        try:
            if edit:
                await query.message.edit_text(
                    f"{config['emoji']} Файл {item['file']} не найден на сервере.",
                    reply_markup=keyboard,
                )
            else:
                await query.message.reply_text(
                    f"{config['emoji']} Файл {item['file']} не найден на сервере.",
                    reply_markup=keyboard,
                )
        except Exception as e:
            logger.error(e)
        return

    try:
        if cached_file_id:
            media = cached_file_id
            if edit:
                message = await query.message.edit_media(
                    media=InputMediaPhoto(media, caption=caption),
                    reply_markup=keyboard,
                )
            else:
                message = await query.message.reply_photo(
                    photo=media,
                    caption=caption,
                    reply_markup=keyboard,
                )
        else:
            photo = BytesIO(media_bytes)
            photo.name = item["file"]
            if edit:
                message = await query.message.edit_media(
                    media=InputMediaPhoto(photo, caption=caption),
                    reply_markup=keyboard,
                )
            else:
                message = await query.message.reply_photo(
                    photo=photo,
                    caption=caption,
                    reply_markup=keyboard,
                )
            try:
                new_id = None
                if message and getattr(message, "photo", None):
                    new_id = message.photo[-1].file_id
                elif hasattr(message, "result") and getattr(message.result, "photo", None):
                    new_id = message.result.photo[-1].file_id
                if new_id:
                    file_ids[index] = new_id
            except Exception as cache_error:
                logger.error(f"Не удалось сохранить file_id для {item['file']}: {cache_error}")

    except Exception as e:
        logger.error(f"Ошибка при отправке изображения {item['file']}: {e}")


async def send_formula_item(query, index: int, edit: bool = False):
    """Показать карточку с формулами из заранее подготовленного списка."""
    total = len(FORMULA_CARDS)
    back_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🏠 В меню", callback_data="back_to_menu")]]
    )

    if total == 0:
        try:
            if edit:
                await query.message.edit_text(
                    "Пока здесь нет ни одной подборки формул. Загляните позже.",
                    reply_markup=back_keyboard,
                )
            else:
                await query.message.reply_text(
                    "Пока здесь нет ни одной подборки формул. Загляните позже.",
                    reply_markup=back_keyboard,
                )
        except Exception as e:
            logger.error(e)
        return

    index = index % total
    card = FORMULA_CARDS[index]

    nav_buttons = []
    if total > 1:
        prev_index = (index - 1) % total
        next_index = (index + 1) % total
        nav_buttons.append(
            InlineKeyboardButton(
                "◀️ Предыдущая тема", callback_data=f"formulas_prev_{prev_index}"
            )
        )
        nav_buttons.append(
            InlineKeyboardButton(
                "Следующая тема ▶️", callback_data=f"formulas_next_{next_index}"
            )
        )

    keyboard_layout = []
    if nav_buttons:
        keyboard_layout.append(nav_buttons)
    keyboard_layout.append([InlineKeyboardButton("🏠 В меню", callback_data="back_to_menu")])
    keyboard = InlineKeyboardMarkup(keyboard_layout)

    text = (
        f"📐 {card['title']}\n\n"
        f"{card['content']}\n\n"
        f"📊 Тема {index + 1} из {total}"
    )

    try:
        if edit:
            await query.message.edit_text(text, reply_markup=keyboard)
        else:
            await query.message.edit_text(text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка при отправке формул: {e}")

# ============================================================================
# КЛАВИАТУРЫ
# ============================================================================

def get_main_menu():
    """Главное меню с кнопками в сообщении"""
    keyboard = [
        [
            InlineKeyboardButton("🎭 Развлекательное", callback_data="fun_mode"),
            InlineKeyboardButton("📚 Учебное", callback_data="study_mode"),
        ],
        [
            InlineKeyboardButton("📅 Календарик", callback_data="calendar"),
            InlineKeyboardButton("🧠 Вопрос дня", callback_data="quiz_today"),
        ],
        [InlineKeyboardButton("ℹ️ О проекте", callback_data="about")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ============================================================================
# ОБЩИЙ ТЕКСТ ПРИВЕТСТВИЯ И ОБРАБОТЧИКИ КОМАНД
# ============================================================================

WELCOME_TEXT_HTML = (
    "🌟 Добро пожаловать в Simple Physics!\n\n"
    "Это пространство, где школьная программа по физике соединяется с комиксами, мемами и реальной жизнью. "
    "Здесь можно и готовиться к экзамену, и просто смотреть интересные штуки про наш мир.\n\n"
    "🎭 <b>Развлекательное</b> — комиксы, мемы и физика в фильмах, которые помогают увидеть задачи глазами героев и шуток.\n"
    "📚 <b>Учебное</b> — конспекты, история и тексты, которые поддержат на пути к высоким баллам.\n"
    "📅 <b>Календарик</b> — важные даты, открытия и люди, с которыми связана физика.\n"
    "🧠 <b>Вопрос дня</b> — один короткий вопрос для быстрой интеллектуальной зарядки.\n\n"
    "👇 Выберите раздел и нажмите на кнопку:"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        WELCOME_TEXT_HTML,
        reply_markup=get_main_menu(),
        parse_mode="HTML",
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info('CALLBACK_HANDLER_START: обработчик вызван')
    query = update.callback_query
    data = query.data
    
    logger.info(f"Получен callback: {data}")

    # Ответы на квизы
    if data.startswith("quiz_ans_"):
        try:
            _, _, quiz_id, option_index = data.split("_", 3)
            chosen_index = int(option_index)
        except Exception as parse_err:
            logger.error(f"Не удалось распарсить callback квиза {data}: {parse_err}")
            try:
                await query.answer("Что‑то пошло не так, попробуйте ещё раз.", show_alert=True)
            except Exception:
                pass
            return

        question = next((q for q in QUIZ_QUESTIONS if q["id"] == quiz_id), None)
        if not question:
            try:
                await query.answer("Этот вопрос устарел. Нажмите /start для нового вопроса.", show_alert=True)
            except Exception:
                pass
            return

        correct_index = question["correct"]
        correct_text = question["options"][correct_index]

        if chosen_index == correct_index:
            result_text = f"✅ Верно!\n\n{question['explanation']}"
        else:
            chosen_text = question["options"][chosen_index] if 0 <= chosen_index < len(question["options"]) else "—"
            result_text = (
                "❌ Не совсем так.\n\n"
                f"Ты выбрал: {chosen_text}\n"
                f"Правильный ответ: {correct_text}\n\n"
                f"{question['explanation']}"
            )

        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🏠 В меню", callback_data="back_to_menu")],
            ]
        )
        try:
            await query.message.edit_text(result_text, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Не удалось отредактировать сообщение с результатом квиза: {e}")
        try:
            await query.answer()
        except Exception:
            pass
        return

    if data == "quiz_today":
        try:
            await send_quiz(query.message.chat)
        except Exception as e:
            logger.error(f"Не удалось отправить вопрос дня по кнопке: {e}")
        try:
            await query.answer()
        except Exception:
            pass
        return

    # Навигация по локальному контенту
    for category in CATEGORY_CONTENT.keys():
        next_prefix = f"{category}_next_"
        prev_prefix = f"{category}_prev_"
        if data.startswith(next_prefix) or data.startswith(prev_prefix):
            items = _get_category_items(category)
            total = len(items)
            if total == 0:
                await send_category_item(query, category, 0, edit=True)
            else:
                try:
                    target_index = int(data.split("_")[-1])
                except (ValueError, IndexError):
                    logger.error(f"Не удалось распарсить индекс для {data}")
                    target_index = 0

                await send_category_item(query, category, target_index, edit=True)
            try:
                await query.answer()
            except Exception:
                pass
            return

    # Режимы «Развлекательное» и «Учебное»
    if data == "fun_mode":
        try:
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🎨 Комиксы", callback_data="comics"),
                        InlineKeyboardButton("😂 Мемы", callback_data="memes"),
                    ],
                    [
                        InlineKeyboardButton("🎬 Физика в фильмах", callback_data="movies"),
                    ],
                    [InlineKeyboardButton("🏠 В меню", callback_data="back_to_menu")],
                ]
            )
            await query.message.edit_text(
                "🎭 Развлекательный режим.\n\n"
                "Здесь физика подаётся через юмор, визуальные истории и любимые фильмы. "
                "Можно начать с лёгких мемов, перейти к комиксам с короткими сюжетами или посмотреть, "
                "как законы сохранения и сила трения работают (или не работают) в кино.\n\n"
                "Выбери, с чего начнём:",
                reply_markup=keyboard,
            )
        except Exception as e:
            logger.error(f"Не удалось открыть развлекательный режим: {e}")
        try:
            await query.answer()
        except Exception:
            pass
        return

    if data == "study_mode":
        try:
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("📚 История физики", callback_data="history"),
                        InlineKeyboardButton("📝 Конспекты", callback_data="notes"),
                    ],
                    [
                        InlineKeyboardButton("📐 Формулы", callback_data="formulas"),
                    ],
                    [
                        InlineKeyboardButton("📅 Календарик", callback_data="calendar"),
                    ],
                    [InlineKeyboardButton("🏠 В меню", callback_data="back_to_menu")],
                ]
            )
            await query.message.edit_text(
                "📚 Учебный режим.\n\n"
                "Здесь собраны материалы, которые помогают не просто выучить формулы, а понять, откуда они берутся и как использовать их в задачах. "
                "Исторические заметки добавляют живых примеров, конспекты дают структуру, а календарик подсказывает, когда происходили важные открытия.\n\n"
                "Выберите, с чего начать работу:",
                reply_markup=keyboard,
            )
        except Exception as e:
            logger.error(f"Не удалось открыть учебный режим: {e}")
        try:
            await query.answer()
        except Exception:
            pass
        return

    # Формулы: показ и навигация
    if data == "formulas":
        await send_formula_item(query, 0, edit=False)
        try:
            await query.answer()
        except Exception:
            pass
        return

    if data.startswith("formulas_next_") or data.startswith("formulas_prev_"):
        total = len(FORMULA_CARDS)
        if total == 0:
            try:
                await query.answer("Формулы пока не добавлены.", show_alert=True)
            except Exception:
                pass
            return
        try:
            target_index = int(data.split("_")[-1]) % total
        except (ValueError, IndexError):
            logger.error(f"Не удалось распарсить индекс формул для {data}")
            target_index = 0
        await send_formula_item(query, target_index, edit=True)
        try:
            await query.answer()
        except Exception:
            pass
        return

    # Комиксы
    if data == "comics":
        await send_category_item(query, "comics", 0)
        try:
            await query.answer()
        except Exception:
            pass
    
    # Видео
    elif data == "videos":
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
        await send_category_item(query, "memes", 0)
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
        try:
            await query.message.chat.send_message(
                WELCOME_TEXT_HTML,
                reply_markup=get_main_menu(),
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(f"Не удалось отправить главное меню при возврате: {e}")
        try:
            await query.answer()
        except Exception:
            pass
    
    # Историческая справка
    elif data == "history":
        await send_category_item(query, "history", 0)
        try:
            await query.answer()
        except Exception:
            pass
    
    # Физика в фильмах
    elif data == "movies":
        await send_category_item(query, "movies", 0)
        try:
            await query.answer()
        except Exception:
            pass
    
    # Календарик
    elif data == "calendar":
        await send_category_item(query, "calendar", 0)
        try:
            await query.answer()
        except Exception:
            pass
    
    # Конспекты
    elif data == "notes":
        await send_category_item(query, "notes", 0)
        try:
            await query.answer()
        except Exception:
            pass
    
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

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    await update.message.reply_text(
        WELCOME_TEXT_HTML,
        reply_markup=get_main_menu(),
        parse_mode="HTML",
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
        "Отправляйте название комикса, затем фото.\n"
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
        "Отправляйте название справки, затем содержание.\n"
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
        "Отправляйте название конспекта, затем фото.\n"
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
            title = context.user_data.get('history_title')
            content = update.message.text
            add_history(title, content)
            context.user_data['history_counter'] = context.user_data.get('history_counter', 0) + 1
            context.user_data['waiting_for_history_content'] = False
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
            await update.message.reply_text("📸 Теперь отправьте фото конспекта")
        return
    
    state = context.user_data.get('adding')
    
    if state == 'comic_title':
        # Сохраняем название и ждём фото
        context.user_data['comic_title'] = update.message.text
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
        add_history(title, content)
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
        context.user_data['adding'] = 'note_photo'
        await update.message.reply_text("📸 Отправьте фото конспекта")
    
    elif state == 'note_photo':
        # Фото обрабатывается в handle_admin_photo
        pass

async def handle_admin_photo(update, context):
    user_id = update.effective_user.id
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
        add_comic(title, photo.file_id)
        context.user_data['comic_counter'] = context.user_data.get('comic_counter', 0) + 1
        context.user_data['waiting_for_comic_title'] = True
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
    # Пакетное добавление конспектов
    if context.user_data.get('batch_adding_notes') and not context.user_data.get('waiting_for_note_title'):
        title = context.user_data.get('note_title')
        add_note(title, photo.file_id)
        context.user_data['note_counter'] = context.user_data.get('note_counter', 0) + 1
        context.user_data['waiting_for_note_title'] = True
        await update.message.reply_text(f'✅ Конспект добавлен: {title}\n\nОтправьте следующее название или /stop_batch чтобы остановить.')
        return
    # Обработка фото при добавлении контента
    if state == 'comic_photo':
        title = context.user_data.get('comic_title')
        add_comic(title, photo.file_id)
        await update.message.reply_text('✅ Комикс добавлен!')
        context.user_data['adding'] = None
    elif state == 'meme_photo':
        title = context.user_data.get('meme_title')
        add_meme(title, photo.file_id)
        await update.message.reply_text('✅ Мем добавлен!')
        context.user_data['adding'] = None
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
        add_note(title, photo.file_id)
        await update.message.reply_text('✅ Конспект добавлен!')
        context.user_data['adding'] = None

# ============================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================================

def main():
    """Запуск бота"""
    if not acquire_instance_lock():
        print("Внимание: бот уже запущен в другой сессии. Завершение.")
        return

    # Создаём базу данных
    init_db()
    
    # Создаём бота
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
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
    # Обычный обработчик текстовых сообщений (остальные пользователи)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Запускаем бота
    logger.info("Бот запущен!")
    try:
        app.run_polling()
    except Conflict as exc:
        logger.error(f"Конфликт запуска бота: {exc}")
        print("Telegram сообщает, что бот уже запущен в другом месте. Проверьте другие сессии.")
    finally:
        release_instance_lock()

if __name__ == '__main__':
    if '--menu-test' in sys.argv:
        from telegram.ext import Application, CallbackQueryHandler, CommandHandler
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
        if not acquire_instance_lock():
            print("Внимание: бот уже запущен в другой сессии. Тестовое меню не будет запущено.")
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

