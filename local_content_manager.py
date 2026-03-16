"""
Менеджер локального контента для демонстрации
Позволяет использовать локальные файлы из папки media/ для показа в боте.
История и конспекты: группировка по первой цифре в имени (исторические11,12 → одна справка).
"""

from pathlib import Path
from io import BytesIO
from telegram import InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup

BASE_DIR = Path(__file__).resolve().parent
MEDIA_DIR = BASE_DIR / "media"

# Структура локального контента (items заполняются при сканировании)
LOCAL_CONTENT = {
    "comics": {"dir": MEDIA_DIR / "comics", "items": []},
    "memes": {"dir": MEDIA_DIR / "memes", "items": []},
    "history": {"dir": MEDIA_DIR / "history", "items": []},
    "movies": {"dir": MEDIA_DIR / "movies", "items": []},
    "calendar": {"dir": MEDIA_DIR / "calendar", "items": []},
    "notes": {"dir": MEDIA_DIR / "notes", "items": []},
    "formulas": {"dir": MEDIA_DIR / "formulas", "items": []},
}

# Тексты для календаря (5 записей по датам)
CALENDAR_CAPTIONS = [
    """🌸Май — месяц, когда природа пробуждается, и так же, как весенние цветы, физика раскрывает свои тайны.

Смотрите наш календарь и делитесь с друзьями!

Simple physics 3 мая
--
#SimplePhysics""",
    """Ждали его❓
А вот и календарь с физическими датами на октябрь! Отмечайте, что интересного прочитали😂

💭Simple Physics 3 октября 
--
#SimplePhysics""",
    """А вы готовы увидеть финальный календарь 2025 года? Быстрее смотрите💋

💭Simple physics 3 декабря
--
#ФизическийКалендарь""",
    """Поздравляем всех с наступившим Новым Годом и желаем вам успешного и счастливого 2026 года🎉

➡️Пока мы готовимся к сессии и экзаменам - читайте календарь и отмечайте для себя важное

💭Simple physics 3 января
--
#ФизическийКалендарь""",
    """В марте вообще-то не только Международный женский день празднуем, а ещё и…
смотрите наш физический календарь и отмечайте красным у себя🤭

💭Simple physics 4 марта
--
#ФизическийКалендарь""",
]

# Имена файлов календаря по порядку (проверяем с разными расширениями)
CALENDAR_FILENAMES = [
    ["календарь1.png", "календарь1.jpg", "Календарь1.png", "Календарь1.jpg"],
    ["Календарик2.png", "Календарик2.jpg", "календарик2.png", "календарик2.jpg"],
    ["календарь3.png", "календарь3.jpg", "Календарь3.png", "Календарь3.jpg"],
    ["календарь4.png", "календарь4.jpg", "Календарь4.png", "Календарь4.jpg"],
    ["календарь5.png", "календарь5.jpg", "Календарь5.png", "Календарь5.jpg"],
]

# =============================================================================
# ТЕКСТЫ ДЛЯ «ФИЗИКА В ФИЛЬМАХ» — вставьте свои тексты вместо кодов ниже
# Файл: local_content_manager.py, список PHYSICS_CAPTIONS
# Замените каждую строку [ТЕКСТ_ФИЗИКА_N] на нужный текст для картинки.
# =============================================================================
PHYSICS_CAPTIONS = [
    "[ТЕКСТ_ФИЗИКА_0]",  # подпись к физика0.jpg
    "[ТЕКСТ_ФИЗИКА_1]",  # подпись к Физика1.jpg
    "[ТЕКСТ_ФИЗИКА_2]",  # подпись к Физика2.jpg
    "[ТЕКСТ_ФИЗИКА_3]",  # подпись к физика3.jpg
    "[ТЕКСТ_ФИЗИКА_4]",  # подпись к Физика4.jpg
]

PHYSICS_FILENAMES = [
    ["физика0.jpg", "физика0.png", "Физика0.jpg", "Физика0.png"],
    ["Физика1.jpg", "Физика1.png", "физика1.jpg", "физика1.png"],
    ["Физика2.jpg", "Физика2.png", "физика2.jpg", "физика2.png"],
    ["физика3.jpg", "физика3.png", "Физика3.jpg", "Физика3.png"],
    ["Физика4.jpg", "Физика4.png", "физика4.jpg", "физика4.png"],
]

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def _find_file_in_dir(media_dir, name_variants):
    """Ищет файл в папке по списку возможных имён."""
    if not media_dir.exists():
        return None
    for name in name_variants:
        p = media_dir / name
        if p.is_file():
            return p
    return None


def _group_by_first_digit(media_dir, prefix_lower):
    """
    Сканирует папку, находит файлы вида prefix+XY (латиница/кириллица), 
    группирует по первой цифре X. Возвращает список групп, каждая группа — список путей к файлам, отсортированных по Y.
    """
    if not media_dir.exists():
        return []
    prefix_len = len(prefix_lower)
    groups = {}  # group_id -> [(sub_id, path), ...]
    for path in media_dir.iterdir():
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        stem = path.stem
        if len(stem) <= prefix_len:
            continue
        if stem[:prefix_len].lower() != prefix_lower:
            continue
        tail = stem[prefix_len:]
        if not tail or not tail.isdigit():
            continue
        gid = int(tail[0])
        sid = int(tail[1:]) if len(tail) > 1 else 0
        if gid not in groups:
            groups[gid] = []
        groups[gid].append((sid, path))
    result = []
    for gid in sorted(groups.keys()):
        files_sorted = sorted(groups[gid], key=lambda x: x[0])
        result.append([p for _, p in files_sorted])
    return result


def scan_local_content():
    """Сканирует папки media/ и заполняет items с учётом группировки для history и notes."""
    for category, config in LOCAL_CONTENT.items():
        media_dir = config["dir"]
        if not media_dir.exists():
            media_dir.mkdir(parents=True, exist_ok=True)

        items = []

        if category == "history":
            groups = _group_by_first_digit(media_dir, "исторические")
            for i, paths in enumerate(groups):
                items.append({
                    "id": i,
                    "files": paths,
                    "file_path": paths[0],
                    "file_name": paths[0].name,
                    "title": f"Историческая справка №{i + 1}",
                    "group": True,
                })
            config["items"] = items
            print(f"📁 {category}: найдено {len(items)} справок (групп)")
            continue

        if category == "notes":
            groups = _group_by_first_digit(media_dir, "конспект")
            for i, paths in enumerate(groups):
                items.append({
                    "id": i,
                    "files": paths,
                    "file_path": paths[0],
                    "file_name": paths[0].name,
                    "title": f"Конспект №{i + 1}",
                    "group": True,
                })
            config["items"] = items
            print(f"📁 {category}: найдено {len(items)} конспектов (групп)")
            continue

        if category == "calendar":
            for i in range(5):
                path = _find_file_in_dir(media_dir, CALENDAR_FILENAMES[i])
                if path:
                    cap = CALENDAR_CAPTIONS[i] if i < len(CALENDAR_CAPTIONS) else ""
                    items.append({
                        "id": i,
                        "file_path": path,
                        "files": [path],
                        "file_name": path.name,
                        "title": f"Запись календарика №{i + 1}",
                        "caption": cap,
                        "group": False,
                    })
            config["items"] = items
            print(f"📁 {category}: найдено {len(items)} записей")
            continue

        if category == "movies":
            for i in range(5):
                path = _find_file_in_dir(media_dir, PHYSICS_FILENAMES[i])
                if path:
                    cap = PHYSICS_CAPTIONS[i] if i < len(PHYSICS_CAPTIONS) else ""
                    items.append({
                        "id": i,
                        "file_path": path,
                        "files": [path],
                        "file_name": path.name,
                        "title": f"Физика в фильмах №{i + 1}",
                        "caption": cap,
                        "group": False,
                    })
            config["items"] = items
            print(f"📁 {category}: найдено {len(items)} записей")
            continue

        # comics, memes, formulas — по одному файлу на элемент
        files = sorted(media_dir.glob("*")) if media_dir.exists() else []
        for idx, file_path in enumerate(files):
            if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
                items.append({
                    "id": idx,
                    "file_path": file_path,
                    "files": [file_path],
                    "file_name": file_path.name,
                    "title": file_path.stem,
                    "group": False,
                })
        config["items"] = items
        print(f"📁 {category}: найдено {len(items)} файлов")


def get_local_content_count(category):
    """Количество элементов (для history/notes — количество групп)."""
    return len(LOCAL_CONTENT.get(category, {}).get("items", []))


def get_local_content_by_index(category, index):
    """Элемент по индексу: один item или группа файлов."""
    items = LOCAL_CONTENT.get(category, {}).get("items", [])
    if items and 0 <= index < len(items):
        return items[index], len(items)
    return None, len(items) if items else 0


def load_local_file(file_path):
    try:
        if file_path.exists():
            return file_path.read_bytes()
    except Exception as e:
        print(f"Ошибка при загрузке файла {file_path}: {e}")
    return None


async def send_local_content_item(query, category, index, edit=False, config=None):
    """Отправляет один элемент: одно фото или группу фото (media_group)."""
    item, total = get_local_content_by_index(category, index)
    back_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_menu")]]
    )
    empty_text = (config.get("empty_text", "😔 Контента пока нет.") if config else "😔 Контента пока нет.")

    if not item:
        try:
            if edit:
                await query.message.edit_text(empty_text, reply_markup=back_keyboard)
            else:
                await query.message.reply_text(empty_text, reply_markup=back_keyboard)
        except Exception as e:
            print(f"Ошибка при отправке: {e}")
        return

    emoji = config.get("emoji", "📄") if config else "📄"
    singular = config.get("singular", "Элемент") if config else "Элемент"
    nav_buttons = []
    if total > 1:
        prev_index = (index - 1) % total
        next_index = (index + 1) % total
        prev_label = config.get("prev_label", "◀️ Предыдущий") if config else "◀️ Предыдущий"
        next_label = config.get("next_label", "Следующий ▶️") if config else "Следующий ▶️"
        nav_buttons.append(
            InlineKeyboardButton(prev_label, callback_data=f"{category}_prev_{prev_index}")
        )
        nav_buttons.append(
            InlineKeyboardButton(next_label, callback_data=f"{category}_next_{next_index}")
        )
    keyboard_layout = []
    if nav_buttons:
        keyboard_layout.append(nav_buttons)
    keyboard_layout.append([InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_menu")])
    keyboard = InlineKeyboardMarkup(keyboard_layout)

    # Подпись: своя для calendar/movies или стандартная
    if item.get("caption") is not None and item.get("caption").strip():
        caption = f"{emoji} {item['title']}\n\n{item['caption']}\n\n📊 {singular} {index + 1} из {total}"
    else:
        caption = f"{emoji} {item['title']}\n\n📊 {singular} {index + 1} из {total}"

    files = item.get("files", [item["file_path"]])
    if not files:
        files = [item["file_path"]]

    # Одна картинка
    if len(files) == 1:
        file_bytes = load_local_file(files[0])
        if not file_bytes:
            try:
                if edit:
                    await query.message.edit_text(
                        f"⚠️ Не удалось загрузить файл: {item['file_name']}",
                        reply_markup=back_keyboard,
                    )
                else:
                    await query.message.reply_text(
                        f"⚠️ Не удалось загрузить файл: {item['file_name']}",
                        reply_markup=back_keyboard,
                    )
            except Exception as e:
                print(f"Ошибка: {e}")
            return
        photo = BytesIO(file_bytes)
        photo.name = files[0].name
        try:
            if edit:
                try:
                    await query.message.edit_media(
                        media=InputMediaPhoto(photo, caption=caption),
                        reply_markup=keyboard,
                    )
                except Exception:
                    await query.message.delete()
                    await query.message.reply_photo(
                        photo=photo,
                        caption=caption,
                        reply_markup=keyboard,
                    )
            else:
                await query.message.reply_photo(
                    photo=photo,
                    caption=caption,
                    reply_markup=keyboard,
                )
        except Exception as e:
            print(f"Ошибка при отправке фото: {e}")
            try:
                if edit:
                    await query.message.edit_text(
                        f"⚠️ Не удалось отправить изображение: {e}",
                        reply_markup=keyboard,
                    )
                else:
                    await query.message.reply_text(
                        f"⚠️ Не удалось отправить изображение: {e}",
                        reply_markup=keyboard,
                    )
            except Exception:
                pass
        return

    # Несколько картинок — отправляем медиа-группой (подпись только у первого)
    media_list = []
    for i, path in enumerate(files):
        data = load_local_file(path)
        if not data:
            continue
        bio = BytesIO(data)
        bio.name = path.name
        media_list.append(InputMediaPhoto(bio, caption=caption if i == 0 else ""))
    if not media_list:
        try:
            if edit:
                await query.message.edit_text(
                    "⚠️ Не удалось загрузить файлы.",
                    reply_markup=back_keyboard,
                )
            else:
                await query.message.reply_text(
                    "⚠️ Не удалось загрузить файлы.",
                    reply_markup=back_keyboard,
                )
        except Exception as e:
            print(f"Ошибка: {e}")
        return
    try:
        if edit:
            try:
                await query.message.delete()
            except Exception:
                pass
        await query.message.reply_media_group(media=media_list)
        # После медиа-группы отправляем кнопки отдельным сообщением (Telegram не даёт прикрепить к группе)
        await query.message.reply_text("👇", reply_markup=keyboard)
    except Exception as e:
        print(f"Ошибка при отправке медиа-группы: {e}")
        try:
            if edit:
                await query.message.edit_text(
                    f"⚠️ Не удалось отправить: {e}",
                    reply_markup=keyboard,
                )
            else:
                await query.message.reply_text(
                    f"⚠️ Не удалось отправить: {e}",
                    reply_markup=keyboard,
                )
        except Exception:
            pass


# Инициализация при импорте
scan_local_content()
