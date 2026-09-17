# -*- coding: utf-8 -*-
# ============================================================
#  NooB ExPeRiMeNt — бот для получения карточек (v2.0)
# ============================================================

import os
import re
import time
import random
import sqlite3
import threading
import traceback
from datetime import datetime

import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException

# ========================= НАСТРОЙКИ =========================
TOKEN = "8957173270:AAGUT83h7ekSR1T9xiH4Y2HqqJy8RU6vpoY"
CREATORS = [5679778859, 7035855233]
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "noob_bot.db")
BOT_VERSION = "2.3"

BONUS_COOLDOWN = 24 * 3600
CARD_COOLDOWN = 2 * 3600
BATTLE_COOLDOWN = 3600
CASE_OPEN_COOLDOWN = 5          # кулдаун между открытиями кейсов
LEVEL_STEP = 100
CHAT_LINK = "https://t.me/+up2GX2ehKvs4Zjhi"
CARD_WORD = "эксперимент"

PRIVILEGES = {
    "Игрок":               {"card_cd": CARD_COOLDOWN, "coin_mult": 1, "battle_cd": BATTLE_COOLDOWN},
    "Leader of the noobs": {"card_cd": CARD_COOLDOWN - 1800, "coin_mult": 2, "battle_cd": BATTLE_COOLDOWN - 300},
    "Бета Тестер":         {"card_cd": 1800, "coin_mult": 2, "battle_cd": BATTLE_COOLDOWN - 300},
}

# ========================= МАГАЗИН =========================
SHOP_ITEMS = [
    {"key": "leader", "name": "Leader of the noobs", "price": 5,
     "desc": "1. −30 минут к ожиданию карты\n2. −5 минут к битве карт\n3. х2 монеты с бонуса"},
]

# Шансы редкостей для команды "эксперимент"
RARITY_CHANCES = [
    ("Обычная", 30), ("Необычная", 25), ("Редкая", 20), ("Эпическая", 15),
    ("Легендарная", 5), ("Мифическая", 4.5), ("Секретная", 0.5),
]
RARITY_ORDER = ["Обычная", "Необычная", "Редкая", "Эпическая",
                "Легендарная", "Мифическая", "Секретная", "Эксклюзивный"]

CARDS = [
    ("Noob", "Обычная", 10, 5, "https://www.image2url.com/r2/default/images/1789617350350-eb3f7fd8-4cfe-497a-9ac7-58518ef6c458.jpg"),
    ("Dual Sword Noob", "Необычная", 25, 5, "https://www.image2url.com/r2/default/images/1789617233534-b8a8a05c-7e1c-40e2-8cb7-60935d5997f7.jpg"),
    ("Guest", "Редкая", 35, 15, "https://www.image2url.com/r2/default/images/1789617312553-a69c6870-65a3-4b29-95a8-760626c2b0b8.jpg"),
    ("Titan Noob", "Мифическая", 155, 50, "https://www.image2url.com/r2/default/images/1789448954658-bc28bd52-c380-4893-a0ec-eedd6c7cf9d6.jpg"),
    ("Noob Mech", "Легендарная", 85, 35, "https://www.image2url.com/r2/default/images/1789449432807-0e657c4f-24c1-452d-8edb-d108abf90bb6.jpg"),
    ("Multiverse Upgraded Titan Noob 2.0", "Секретная", 285, 100, "https://www.image2url.com/r2/default/images/1789452434416-10e4eb31-66a4-41e8-a2fc-b00b34aeaf2c.jpg"),
    ("Titan Guest", "Мифическая", 160, 50, "https://www.image2url.com/r2/default/images/1789452927535-c9ea9f4e-e9a6-4759-ac4f-09d767153137.jpg"),
    ("The Last Guest", "Мифическая", 180, 50, "https://www.image2url.com/r2/default/images/1789452843577-21d57094-7176-4e69-8617-86e087a30c78.jpg"),
    ("Flippidee", "Секретная", 260, 100, "https://www.image2url.com/r2/default/images/1789453441277-65bb8e42-013d-4ec7-bdd0-8163994110d5.jpg"),
    ("Dummy", "Эпическая", 50, 20, "https://www.image2url.com/r2/default/images/1789453882846-cc8f7d9c-d435-4e77-8e20-d5ce98b9f1f2.jpg"),
    ("Grappler Noob", "Эпическая", 55, 20, "https://www.image2url.com/r2/default/images/1789453905749-917bb5f3-7e94-49b0-b1df-ca8f85a54b0a.jpg"),
    ("Upgraded Big Noob", "Легендарная", 105, 35, "https://kommodo.ai/i/NzYJcX7EBYjwAgk4P7GS"),
    ("Upgraded Titan Guest 2.0", "Секретная", 310, 100, "https://kommodo.ai/i/3K2CwBtGsDvTdyN1SMzL"),
    ("Wars Upgraded Titan Noob", "Эксклюзивный", 350, 100, "https://kommodo.ai/i/skagyLjUuI8YUYsqSd7x"),
    ("Multiverse Titan Guest 2.0", "Эксклюзивный", 300, 100, "https://kommodo.ai/i/SnTBeC3ezv41GbNXmKEh"),
    ("Prototype Mech", "Эксклюзивный", 250, 100, "https://kommodo.ai/i/r5bDhbCkDkkTY3qLjEkH"),
    ("Nova Mech", "Эксклюзивный", 190, 100, "https://kommodo.ai/i/f0zCNBACRLy7RwCjxnOG"),
    ("Spider Noob 2.0", "Эксклюзивный", 125, 100, "https://kommodo.ai/i/jcfZMq9CCgEiNfmsfmuG"),
    ("Guest Woman", "Эксклюзивный", 105, 100, "https://kommodo.ai/i/Jqq6TwsfSF6kCNSIwzm4"),
    ("Upgraded Large Noob", "Эксклюзивный", 45, 100, "https://www.image2url.com/r2/default/images/1789617233534-b8a8a05c-7e1c-40e2-8cb7-60935d5997f7.jpg"),
]

RARITY_FIX = {
    "обычный": "Обычная", "обычная": "Обычная",
    "необычный": "Необычная", "необычная": "Необычная",
    "редкий": "Редкая", "редкая": "Редкая",
    "эпический": "Эпическая", "эпическая": "Эпическая",
    "легендарный": "Легендарная", "легендарная": "Легендарная",
    "мифический": "Мифическая", "мифическая": "Мифическая",
    "секретный": "Секретная", "секретная": "Секретная",
    "эксклюзивный": "Эксклюзивный", "эксклюзивная": "Эксклюзивный",
}
CARDS = [(n, RARITY_FIX.get(r.lower(), r), s, c, u) for n, r, s, c, u in CARDS]

CASES = [
    {
        "name": "Upgraded Crate!",
        "cost": 500,
        "items": [
            ("Upgraded Large Noob", 40), ("Guest Woman", 25), ("Spider Noob 2.0", 20),
            ("Nova Mech", 10), ("Prototype Mech", 2.5), ("Multiverse Titan Guest 2.0", 1.5),
            ("Wars Upgraded Titan Noob", 0.5),
        ],
    },
]

def pick_case_item(case):
    r = random.uniform(0, 100)
    acc = 0
    for name, ch in case["items"]:
        acc += ch
        if r < acc:
            return name, ch
    return case["items"][0][0], case["items"][0][1]

db_lock = threading.Lock()

# ========================= БАЗА ДАННЫХ + МИГРАЦИИ =========================
def db():
    conn = sqlite3.connect(DB_NAME, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_table(conn, name, create_sql):
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    if not cur.fetchone():
        conn.execute(create_sql)
        conn.commit()

def ensure_columns(conn, table, columns):
    existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    for col, ddl in columns.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {ddl}")
            conn.commit()

def get_meta(conn, key, default=None):
    row = conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default

def set_meta(conn, key, value):
    conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?,?)", (key, str(value)))
    conn.commit()

def migrate():
    """Пошаговые миграции. Старые данные сохраняются."""
    conn = db()
    ensure_table(conn, "meta", "CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    ensure_table(conn, "users", """
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY, username TEXT DEFAULT '', nickname TEXT DEFAULT 'Игрок',
            privilege TEXT DEFAULT 'Игрок', coins INTEGER DEFAULT 0, level INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0, strength INTEGER DEFAULT 0, cards_received INTEGER DEFAULT 0,
            last_bonus REAL DEFAULT 0, last_card REAL DEFAULT 0, created REAL DEFAULT 0
        )""")
    ensure_table(conn, "user_cards", """
        CREATE TABLE user_cards (
            user_id INTEGER, card_id INTEGER, count INTEGER DEFAULT 1,
            PRIMARY KEY (user_id, card_id)
        )""")
    ensure_table(conn, "promo", """
        CREATE TABLE promo (
            code TEXT PRIMARY KEY, reward TEXT, rlimit INTEGER DEFAULT 0,
            used INTEGER DEFAULT 0, active INTEGER DEFAULT 1, created REAL DEFAULT 0
        )""")
    ensure_table(conn, "promo_used", "CREATE TABLE promo_used (code TEXT, user_id INTEGER, PRIMARY KEY (code, user_id))")
    ensure_table(conn, "chats", "CREATE TABLE chats (chat_id INTEGER PRIMARY KEY, title TEXT DEFAULT '', username TEXT DEFAULT '', ctype TEXT DEFAULT '')")

    ensure_columns(conn, "users", {
        "username": "TEXT DEFAULT ''", "nickname": "TEXT DEFAULT 'Игрок'",
        "privilege": "TEXT DEFAULT 'Игрок'", "coins": "INTEGER DEFAULT 0",
        "level": "INTEGER DEFAULT 0", "points": "INTEGER DEFAULT 0",
        "strength": "INTEGER DEFAULT 0", "cards_received": "INTEGER DEFAULT 0",
        "last_bonus": "REAL DEFAULT 0", "last_card": "REAL DEFAULT 0", "created": "REAL DEFAULT 0",
    })
    ensure_columns(conn, "promo", {
        "rlimit": "INTEGER DEFAULT 0", "used": "INTEGER DEFAULT 0",
        "active": "INTEGER DEFAULT 1", "created": "REAL DEFAULT 0",
    })

    # ФИКС: нормализация «битых» таймстемпов (из-за них кулдауны были 12–38 часов)
    now = time.time()
    conn.execute("UPDATE users SET last_bonus=0 WHERE last_bonus > ?", (now + 600,))
    conn.execute("UPDATE users SET last_card=0 WHERE last_card > ?", (now + 600,))
    conn.commit()

    prev_ver = get_meta(conn, "version")
    if prev_ver != BOT_VERSION:
        # просто обновляем версию — данные игроков не трогаем
        set_meta(conn, "version", BOT_VERSION)
    conn.close()

migrate()

def get_user(user_id):
    conn = db()
    row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return row

def register_user(message):
    """Регистрация/обновление пользователя. Привилегию НИКОГДА не понижаем."""
    if not message.from_user:
        return None
    if message.from_user.is_bot:
        return None  # у ботов нет профиля
    uid = message.from_user.id
    nick = message.from_user.first_name or message.from_user.username or "Игрок"
    uname = message.from_user.username or ""
    with db_lock:
        conn = db()
        row = conn.execute("SELECT privilege FROM users WHERE user_id=?", (uid,)).fetchone()
        if not row:
            priv = "Создатель" if uid in CREATORS else "Игрок"
            conn.execute(
                "INSERT OR IGNORE INTO users (user_id, username, nickname, privilege, created) VALUES (?,?,?,?,?)",
                (uid, uname, nick, priv, time.time()))
        else:
            # ФИКС: привилегию не трогаем, только ник/юзернейм
            conn.execute("UPDATE users SET username=?, nickname=? WHERE user_id=?",
                         (uname, nick, uid))
        conn.commit()
        conn.close()
    return get_user(uid)

def ensure_user_exists(uid, nickname="Игрок"):
    with db_lock:
        conn = db()
        row = conn.execute("SELECT user_id FROM users WHERE user_id=?", (uid,)).fetchone()
        if not row:
            conn.execute(
                "INSERT OR IGNORE INTO users (user_id, username, nickname, privilege, created) VALUES (?,?,?,?,?)",
                (uid, "", nickname, "Создатель" if uid in CREATORS else "Игрок", time.time()))
            conn.commit()
        conn.close()
    return get_user(uid)

def register_chat(message):
    try:
        chat = message.chat
        title = chat.title or (message.from_user.first_name if message.from_user else "ЛС") or "Чат"
        uname = chat.username or ""
        with db_lock:
            conn = db()
            conn.execute("INSERT OR REPLACE INTO chats (chat_id, title, username, ctype) VALUES (?,?,?,?)",
                         (chat.id, str(title), uname, chat.type))
            conn.commit()
            conn.close()
    except Exception:
        pass

def upd_user(uid, **fields):
    if not fields:
        return
    sets = ", ".join(f"{k}=?" for k in fields)
    vals = list(fields.values()) + [uid]
    with db_lock:
        conn = db()
        conn.execute(f"UPDATE users SET {sets} WHERE user_id=?", vals)
        conn.commit()
        conn.close()

def add_points(uid, pts):
    u = get_user(uid)
    if not u:
        return False, 0
    new_points = u["points"] + pts
    new_level = max(u["level"], new_points // LEVEL_STEP)
    leveled = new_level > u["level"]
    upd_user(uid, points=new_points, level=new_level)
    return leveled, new_level

def add_card(uid, card_id, n=1):
    with db_lock:
        conn = db()
        row = conn.execute("SELECT count FROM user_cards WHERE user_id=? AND card_id=?", (uid, card_id)).fetchone()
        if row:
            conn.execute("UPDATE user_cards SET count=count+? WHERE user_id=? AND card_id=?", (n, uid, card_id))
        else:
            conn.execute("INSERT OR IGNORE INTO user_cards (user_id, card_id, count) VALUES (?,?,?)", (uid, card_id, n))
        conn.execute("UPDATE users SET cards_received=cards_received+? WHERE user_id=?", (n, uid))
        conn.commit()
        conn.close()

def remove_card(uid, card_id, n=1):
    """Снимает n копий карты. True если хватило."""
    with db_lock:
        conn = db()
        row = conn.execute("SELECT count FROM user_cards WHERE user_id=? AND card_id=?", (uid, card_id)).fetchone()
        if not row or row["count"] < n:
            conn.close()
            return False
        if row["count"] == n:
            conn.execute("DELETE FROM user_cards WHERE user_id=? AND card_id=?", (uid, card_id))
        else:
            conn.execute("UPDATE user_cards SET count=count-? WHERE user_id=? AND card_id=?", (n, uid, card_id))
        conn.commit()
        conn.close()
        return True

def get_user_cards(uid):
    conn = db()
    rows = conn.execute("SELECT card_id, count FROM user_cards WHERE user_id=? ORDER BY card_id", (uid,)).fetchall()
    conn.close()
    return rows

def find_card(name):
    low = name.strip().lower()
    for i, c in enumerate(CARDS):
        if c[0].lower() == low:
            return i
    for i, c in enumerate(CARDS):
        if low in c[0].lower():
            return i
    return None

# ========================= БОТ + SAFE-ОБЁРТКИ =========================
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

def safe_call(func, *args, **kwargs):
    """[safe] повтор при flood/сетевых ошибках"""
    for attempt in range(6):
        try:
            return func(*args, **kwargs)
        except ApiTelegramException as e:
            s = str(e)
            if "Too Many Requests" in s or "retry after" in s.lower():
                m = re.search(r"retry after (\d+)", s)
                time.sleep(int(m.group(1)) + 1 if m else 4)
                continue
            if "message can't be edited" in s or "MESSAGE_NOT_MODIFIED" in s:
                return None
            raise
        except (ConnectionError, OSError):
            time.sleep(3)
            continue
    return None

def safe_edit(chat_id, message_id, text, reply_markup=None):
    """[safe] редактирование с защитой от «нельзя отредактировать»"""
    try:
        return safe_call(bot.edit_message_text, text, chat_id=chat_id,
                         message_id=message_id, reply_markup=reply_markup)
    except Exception:
        return None

def guard(func):
    """[safe] любое падение внутри обработчика не убивает бота"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            traceback.print_exc()
            try:
                msg = args[0]
                if hasattr(msg, "message_id") and hasattr(msg, "chat"):
                    bot.reply_to(msg, "⚠️ Произошла ошибка, попробуй ещё раз.")
            except Exception:
                pass
    wrapper.__name__ = func.__name__
    return wrapper

def fmt_time(sec):
    sec = max(0, int(sec))
    h, sec = divmod(sec, 3600)
    m, s = divmod(sec, 60)
    if h:
        return f"{h}ч {m}мин"
    if m:
        return f"{m}мин {s}сек"
    return f"{s}сек"

def fmt_human(sec):
    sec = int(sec)
    h, sec = divmod(sec, 3600)
    m = sec // 60
    parts = []
    if h:
        parts.append("1 Час" if h == 1 else (f"{h} Часа" if h < 5 else f"{h} Часов"))
    if m:
        parts.append(f"{m} Мин")
    return " ".join(parts) or "0 Мин"

def fmt_chance(ch):
    return str(int(ch)) if float(ch).is_integer() else str(ch)

def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

try:
    BOT_USERNAME = (bot.get_me().username or "").lower()
except Exception:
    BOT_USERNAME = ""

ADMIN_STATE = {}
CARD_VIEW = {}
CASE_LAST_OPEN = {}          # uid -> время последнего открытия кейса
INV_PAGES = {}               # uid -> message_id страницы инвентаря

# ========================= КЛАВИАТУРЫ =========================
BADGE_USERS = {7884553468: "✅"}

def nick_badged(uid, nick):
    b = BADGE_USERS.get(uid)
    return f"{nick} {b}" if b else str(nick)

def kb_start():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("💬 Наша Беседа", url=CHAT_LINK))
    return kb

def kb_top_menu():
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton("💰 Топ Монет", callback_data="top:coins"),
        types.InlineKeyboardButton("🔋 Топ Уровня", callback_data="top:level"),
        types.InlineKeyboardButton("🌟 Топ Очков", callback_data="top:points"),
    )
    return kb

def kb_cases():
    kb = types.InlineKeyboardMarkup()
    for i, c in enumerate(CASES):
        kb.add(types.InlineKeyboardButton(f"🧿 {c['name']} — {c['cost']}$",
                                          callback_data=f"case:buy:{i}"))
    return kb

def kb_admin_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🎟 Промокоды", callback_data="admin:promo"),
        types.InlineKeyboardButton("📊 Статистика", callback_data="admin:stats"),
        types.InlineKeyboardButton("📢 Рассылка", callback_data="admin:broadcast"),
        types.InlineKeyboardButton("🎁 Выдача", callback_data="admin:give"),
        types.InlineKeyboardButton("🃏 Карты", callback_data="admin:cards"),
        types.InlineKeyboardButton("⬅️ Выйти", callback_data="back:help"),
    )
    return kb

def kb_admin_back():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="admin:menu"))
    return kb

def kb_rarities():
    kb = types.InlineKeyboardMarkup(row_width=3)
    rars = [r for r in RARITY_ORDER if any(c[1] == r for c in CARDS)]
    extra = sorted({c[1] for c in CARDS} - set(rars))
    rars += extra
    buttons = [types.InlineKeyboardButton(r, callback_data=f"admin:cardlist:{r}") for r in rars]
    for i in range(0, len(buttons), 3):
        kb.add(*buttons[i:i+3])
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="admin:menu"))
    return kb

def kb_inventory(uid, page):
    rows = get_user_cards(uid)
    per_page = 8
    total_pages = max(1, (len(rows) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    kb = types.InlineKeyboardMarkup(row_width=3)
    nav = []
    if page > 0:
        nav.append(types.InlineKeyboardButton("◀️", callback_data=f"inv:{page-1}"))
    nav.append(types.InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="inv:noop"))
    if page < total_pages - 1:
        nav.append(types.InlineKeyboardButton("▶️", callback_data=f"inv:{page+1}"))
    kb.add(*nav)
    return kb, page, rows, per_page

# ========================= ТЕКСТЫ =========================
def txt_start(nick):
    return (f"🤖 Йоу, {esc(nick)}, ты в <b>NooB ExPeRiMeNt</b>!\n\n"
            f"Заходи, располагайся. Тут просто куча всего, чтобы убить время. "
            f"Карточки, приколы, команды — выбирай, что зайдет. 🃏\n\n"
            f"🔍 Пиши Помощь, там всё основное")

def txt_help():
    # ФИКС: без кнопки «Назад» (она вызывала ошибку редактирования)
    return ("📋 <b>Список Всех Команд:</b>\n"
            "════════════════════════════\n"
            "/start — Запуск Бота.\n"
            "Помощь — Все Команды.\n"
            "Профиль — Профиль.\n"
            "Бонус (каждые 24 часа) — Ежедневный Бонус.\n"
            "Топ / Топс — Топы (💰 Монеты / 🔋 Уровни / 🌟 Очки).\n"
            "Магазин — Донат-магазин привилегий.\n"
            "Кейсы — Кейсы.\n"
            "Инвентарь — Инвентарь С Картами (страницы).\n"
            "🎟 Промо [код] — Активировать Промокод.\n"
            "🔄 Обмен [сумма] / Обмен карта [название] — ответом на сообщение игрока, обмен в ЛС.\n"
            "🃏 Напиши «эксперимент» — получить карточку (раз в 2 часа).")

def txt_profile(u):
    return (f"{nick_badged(u['user_id'], esc(u['nickname']))}, Ваш Профиль:\n"
            "════════════════════════════\n"
            f"📱 Ник: {nick_badged(u['user_id'], esc(u['nickname']))}\n"
            f"🪪 ID: {u['user_id']}\n"
            f"👑 Привилегия: {esc(u['privilege'])}\n"
            f"💰 Монеты: {u['coins']}$\n"
            f"🔋 Уровень: {u['level']}\n"
            f"🌟 Очки: {u['points']}\n"
            f"💪 Сила: {u['strength']}\n"
            f"🎲 Всего Получено Карт: {u['cards_received']}")

def txt_shop():
    return ("🛒 <b>Магазин привилегий</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Покупай привилегии за монеты 👇")

SHOP_ITEMS_DICT = {it["key"]: it for it in SHOP_ITEMS}

def kb_shop():
    kb = types.InlineKeyboardMarkup()
    for it in SHOP_ITEMS:
        kb.add(types.InlineKeyboardButton(f"👑 {it['name']} — ⭐ {it['price']}",
                                          callback_data=f"shop:view:{it['key']}"))
    return kb

def kb_shop_item(key):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(f"🛒 Купить за ⭐ {SHOP_ITEMS_DICT[key]['price']}",
                                      callback_data=f"shop:buy:{key}"))
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="shop:back"))
    return kb

def txt_admin_menu():
    return ("🛠 <b>Меню Нуб (панель разработчика)</b>\n"
            "════════════════════════════\n"
            "Выбери категорию ниже 👇")

def txt_admin_promo():
    return ("🎟 <b>ПРОМОКОДЫ</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "▫️ промо создать [код] [награда] [лимит]\n"
            "   награда: монеты 5000 | сила 50 | уровень 2 | карты (название) | очки 2 | кейс название 2\n"
            "▫️ промо удалить [код]\n"
            "▫️ промо ред [код] награда [новая награда]\n"
            "▫️ промо ред [код] лимит [число]\n"
            "▫️ промо ред [код] статус вкл/выкл\n"
            "▫️ промо список / промо инфо [код]\n\n"
            "Игроки активируют командой «промо [код]».")

def txt_admin_broadcast():
    return ("📢 <b>РАССЫЛКА</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "▫️ рассылка @чат/ссылка/ID — в одну группу\n"
            "▫️ рассылка общий — во все чаты\n"
            "▫️ рассылка список — список групп (только в ЛС)\n\n"
            "Следующим сообщением скинь контент (текст/фото/GIF/стикер/видео).")

def txt_admin_give():
    return ("🎁 <b>ВЫДАЧА</b> (ответом на сообщение игрока)\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "▫️ проф — профиль игрока\n"
            "▫️ вд карта [имя]\n"
            "▫️ вд монеты/очки/уровни/сила [сумма]\n"
            "▫️ вд привилегия [название] (без названия — снять)\n\n"
            "👑 Leader of the noobs:\n"
            "1. −30 минут к ожиданию карты\n"
            "2. −5 минут к битве карт [ещё не добавлена]\n"
            "3. х2 деньги")

# ========================= КАРТОЧКИ =========================
def pick_card_id():
    r = random.uniform(0, 100)
    acc = 0
    for rar, ch in RARITY_CHANCES:
        acc += ch
        if r < acc:
            pool = [i for i, c in enumerate(CARDS) if c[1] == rar]
            if pool:
                return random.choice(pool)
    return random.randrange(len(CARDS))

def card_drop_text(u, card, count, cooldown):
    name, rar, strength, cost, url = card
    extra = f" (x{count})" if count and count > 1 else ""
    return (f"<b>👤 {esc(u['nickname'])}\n"
            f"🃏 Получена Новая Карта {esc(name)}{extra}\n\n"
            f"♈️ Редкость: {rar}.\n"
            f"💪 Сила: {strength}.\n"
            f"💰 Стоимость: {cost}$\n\n"
            f"🎁 Следущая Карта Через {fmt_human(cooldown)}.</b>"), url

def give_card(uid, card_id):
    add_card(uid, card_id)
    strength = CARDS[card_id][2]
    leveled, new_level = add_points(uid, strength)
    return leveled, new_level

def case_win_text(u, card, chance, case_name):
    name, rar, strength, cost, url = card
    return (f"<b>👤 {esc(u['nickname'])}\n"
            f"🃏 Получена Новая Карта {esc(name)}\n\n"
            f"♈️ Редкость: {rar}.\n"
            f"💪 Сила: {strength}.\n"
            f"📊 Шанс: {fmt_chance(chance)}%\n\n"
            f"🧿 Кейс: {esc(case_name)}</b>"), url

# ========================= ПРОМОКОДЫ =========================
def valid_reward(rw):
    parts = rw.split()
    if not parts:
        return False
    t = parts[0].lower()
    if t in ("монеты", "очки", "сила", "уровни", "уровень"):
        return len(parts) == 2 and parts[1].isdigit()
    if t in ("карта", "карты"):
        return len(parts) >= 2 and find_card(" ".join(parts[1:])) is not None
    if t == "кейс":
        return len(parts) >= 2
    return False

def apply_reward(uid, rw):
    parts = rw.split()
    t = parts[0].lower()
    if t in ("монеты", "очки", "сила", "уровни", "уровень"):
        val = int(parts[1])
        col = {"монеты": "coins", "очки": "points", "сила": "strength",
               "уровни": "level", "уровень": "level"}[t]
        u = get_user(uid)
        new_val = u[col] + val
        fields = {col: new_val}
        leveled = False
        if t == "очки":
            new_level = max(u["level"], new_val // LEVEL_STEP)
            leveled = new_level > u["level"]
            fields["level"] = new_level
        upd_user(uid, **fields)
        names = {"монеты": "💰 Монеты", "очки": "🌟 Очки", "сила": "💪 Сила",
                 "уровни": "🔋 Уровни", "уровень": "🔋 Уровни"}
        msg = f"🎟 Активировано: {names[t]} +{val}!"
        if leveled:
            msg += f"\n🔋 Новый уровень: {fields['level']}!"
        return msg
    if t in ("карта", "карты"):
        card_id = find_card(" ".join(parts[1:]))
        if card_id is None:
            return "⚠️ Карта не найдена."
        leveled, new_level = give_card(uid, card_id)
        u = get_user(uid)
        cnt = 0
        for cid, c in get_user_cards(uid):
            if cid == card_id:
                cnt = c
        text, url = card_drop_text(u, CARDS[card_id], cnt, get_priv(u)["card_cd"])
        return ("CARD", text, url)
    if t == "кейс":
        cnt = 1
        if parts[-1].isdigit():
            cnt = int(parts[-1])
        return f"🧿 Получен Кейс {' '.join(parts[1:-1] if parts[-1].isdigit() else parts[1:])} x{cnt}! (скоро откроется...)"
    return "⚠️ Неизвестная награда."

def get_priv(u):
    return PRIVILEGES.get(u["privilege"], PRIVILEGES["Игрок"])

def promo_info(code):
    conn = db()
    row = conn.execute("SELECT * FROM promo WHERE code=?", (code.upper(),)).fetchone()
    conn.close()
    return row

# ========================= РАССЫЛКА =========================
def parse_chat_arg(arg):
    arg = arg.strip()
    if re.fullmatch(r"-?\d+", arg):
        return int(arg)
    m = re.search(r"t\.me/(\+?[\w\d_]+)", arg)
    if m:
        name = m.group(1)
        return "@" + name if not name.startswith("+") else "https://t.me/" + name
    if arg.startswith("@"):
        return arg
    if arg.startswith("https://t.me/"):
        return arg
    return None

def get_all_chats():
    conn = db()
    rows = conn.execute("SELECT chat_id, title, username, ctype FROM chats ORDER BY ctype, title").fetchall()
    conn.close()
    return rows

def do_broadcast(message, target):
    """Рассылка: copy_message с fallback на forward_message. Возвращает (ok, fail)."""
    if target == "all":
        ids = [r["chat_id"] for r in get_all_chats()]
    else:
        ids = [target]
    ok, fail = 0, 0
    src_chat = message.chat.id
    src_mid = message.message_id
    for cid in ids:
        sent = False
        # Попытка 1: copy_message (без "Переслано от...")
        try:
            result = safe_call(bot.copy_message, cid, src_chat, src_mid)
            if result:
                ok += 1
                sent = True
        except Exception:
            pass
        # Fallback: forward_message
        if not sent:
            try:
                result = safe_call(bot.forward_message, cid, src_chat, src_mid)
                if result:
                    ok += 1
                    sent = True
            except Exception:
                pass
        if not sent:
            fail += 1
        time.sleep(0.40)  # антиспам: не более ~2.5 сообщений/сек
    return ok, fail

# ========================= ОБМЕН v2 (оба участника что-то дают) =========================
TRADE_SETUP = {}   # uid -> {"expires": ts}  ждём @username/ID цели
TRADE_STATE = {}   # uid -> {"tid": tid, "step": "coins", "expires": ts}  ждём ввод в ЛС
TRADE_ROOMS = {}   # tid -> комната обмена
ROOM_SEQ = [0]

def trade_other(room, uid):
    return room["b"] if room["a"] == uid else room["a"]

def card_count(uid, card_id):
    for cid, c in get_user_cards(uid):
        if cid == card_id:
            return c
    return 0

def fmt_offer_short(offer):
    parts = []
    if offer["coins"] > 0:
        parts.append(f"💰 {offer['coins']} монет")
    for cid, n in sorted(offer["cards"].items()):
        parts.append(f"🃏 {esc(CARDS[cid][0])} x{n}")
    return " + ".join(parts) if parts else "—"

def trade_reset_ready(room, uid):
    other = trade_other(room, uid)
    room["ready"][uid] = False
    room["ready"][other] = False
    room["confirm"][uid] = False
    room["confirm"][other] = False
    room["phase"] = "build"

def trade_room_text(room, uid):
    tid = room["tid"]
    other = trade_other(room, uid)
    uo = get_user(other)
    oname = nick_badged(other, esc(uo["nickname"])) if uo else str(other)
    banner = ""
    if room["phase"] == "confirm":
        banner = "⚠️ <b>Оба готовы!</b> Проверь предметы и подтверди обмен.\n\n"
    my_r = room["ready"].get(uid)
    op_r = room["ready"].get(other)
    return (f"{banner}🔄 <b>Обмен #{tid}</b> с {oname}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🎁 Ты отдаёшь: <b>{fmt_offer_short(room['offers'][uid])}</b>\n"
            f"📥 Ты получишь: <b>{fmt_offer_short(room['offers'][other])}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{'✅' if my_r else '⏳'} Ты: <b>{'готов' if my_r else 'не готов'}</b>   "
            f"{'✅' if op_r else '⏳'} {oname}: <b>{'готов' if op_r else 'не готов'}</b>")

def trade_kb_build(tid):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("💰 Добавить монеты", callback_data=f"trade2:coins:{tid}"),
           types.InlineKeyboardButton("🃏 Добавить карту", callback_data=f"trade2:cards:{tid}"))
    kb.row(types.InlineKeyboardButton("🗑 Очистить вклад", callback_data=f"trade2:clear:{tid}"))
    kb.row(types.InlineKeyboardButton("✅ Готов", callback_data=f"trade2:ready:{tid}"),
           types.InlineKeyboardButton("❌ Отменить", callback_data=f"trade2:cancel:{tid}"))
    return kb

def trade_kb_confirm(tid):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"trade2:confirm:{tid}"),
           types.InlineKeyboardButton("✏️ Изменить", callback_data=f"trade2:edit:{tid}"))
    kb.row(types.InlineKeyboardButton("❌ Отменить", callback_data=f"trade2:cancel:{tid}"))
    return kb

def trade_kb_cards(tid, uid):
    kb = types.InlineKeyboardMarkup(row_width=1)
    owned = dict(get_user_cards(uid))
    used = TRADE_ROOMS[tid]["offers"][uid]["cards"]
    added = 0
    for cid in sorted(owned):
        left = owned[cid] - used.get(cid, 0)
        if left <= 0:
            continue
        added += 1
        kb.add(types.InlineKeyboardButton(f"🃏 {CARDS[cid][0]} (доступно: {left})",
                                          callback_data=f"trade2:addcard:{tid}:{cid}"))
    if not added:
        kb.add(types.InlineKeyboardButton("— все карты уже добавлены —", callback_data="trade2:noop"))
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"trade2:back:{tid}"))
    return kb

def trade_push(room):
    for puid, mid in list(room["msgs"].items()):
        kb = trade_kb_confirm(room["tid"]) if room["phase"] == "confirm" else trade_kb_build(room["tid"])
        safe_edit(room["chats"][puid], mid, trade_room_text(room, puid), reply_markup=kb)

def trade_finish_msgs(room, ok, err=""):
    tid = room["tid"]
    for puid, mid in list(room["msgs"].items()):
        other = trade_other(room, puid)
        if ok:
            txt = (f"✅ <b>Обмен #{tid} завершён!</b>\n"
                   "━━━━━━━━━━━━━━━━━━━━\n"
                   f"📤 Ты отдал: <b>{fmt_offer_short(room['offers'][puid])}</b>\n"
                   f"📥 Ты получил: <b>{fmt_offer_short(room['offers'][other])}</b>")
        else:
            txt = (f"⚠️ <b>Обмен #{tid} не состоялся.</b>\n{esc(err)}\n"
                   f"Предметы возвращены — обмен сброшен, можно продолжать.")
        safe_edit(room["chats"][puid], mid, txt, reply_markup=None)

def find_user_by_ref(ref):
    ref = ref.strip().lstrip("@")
    conn = db()
    if ref.isdigit():
        row = conn.execute("SELECT * FROM users WHERE user_id=?", (int(ref),)).fetchone()
    else:
        row = conn.execute("SELECT * FROM users WHERE LOWER(username)=LOWER(?)", (ref,)).fetchone()
    conn.close()
    return row

def user_in_trade(uid):
    for r in TRADE_ROOMS.values():
        if uid in (r["a"], r["b"]) and r["phase"] != "done":
            return True
    return False

def start_trade_room(a, b):
    ROOM_SEQ[0] += 1
    tid = ROOM_SEQ[0]
    room = {"tid": tid, "a": a, "b": b,
            "offers": {a: {"coins": 0, "cards": {}}, b: {"coins": 0, "cards": {}}},
            "ready": {a: False, b: False}, "confirm": {a: False, b: False},
            "msgs": {}, "chats": {}, "phase": "build",
            "expires": time.time() + 300}
    TRADE_ROOMS[tid] = room
    ua, ub = get_user(a), get_user(b)
    aname = esc(ua["nickname"]) if ua else str(a)
    bname = esc(ub["nickname"]) if ub else str(b)
    try:
        ma = safe_call(bot.send_message, a,
                       f"🔄 <b>Обмен создан!</b> С кем: {bname}.\n"
                       f"Добавь свои предметы кнопками ниже 👇\n\n" + trade_room_text(room, a),
                       reply_markup=trade_kb_build(tid))
        if not ma:
            raise RuntimeError("no dm A")
        room["msgs"][a] = ma.message_id
        room["chats"][a] = ma.chat.id
        mb = safe_call(bot.send_message, b,
                       f"🔄 <b>{aname}</b> предлагает тебе обмен!\n"
                       f"Добавь свои предметы кнопками ниже 👇\n\n" + trade_room_text(room, b),
                       reply_markup=trade_kb_build(tid))
        if not mb:
            raise RuntimeError("no dm B")
        room["msgs"][b] = mb.message_id
        room["chats"][b] = mb.chat.id
    except Exception:
        TRADE_ROOMS.pop(tid, None)
        safe_call(bot.send_message, a,
                  "❌ Не удалось написать игроку в ЛС. Пусть он сначала запустит бота (/start).")
        return None
    return tid

def execute_trade_room(tid):
    room = TRADE_ROOMS.get(tid)
    if not room:
        return False, "Обмен не найден."
    a, b = room["a"], room["b"]
    ua, ub = get_user(a), get_user(b)
    if not ua or not ub:
        return False, "Один из игроков не найден."
    oa, ob = room["offers"][a], room["offers"][b]
    if ua["coins"] < oa["coins"]:
        return False, f"У {ua['nickname']} не хватает монет."
    if ub["coins"] < ob["coins"]:
        return False, f"У {ub['nickname']} не хватает монет."
    for cid, n in oa["cards"].items():
        if card_count(a, cid) < n:
            return False, f"У {ua['nickname']} не хватает карты «{CARDS[cid][0]}»."
    for cid, n in ob["cards"].items():
        if card_count(b, cid) < n:
            return False, f"У {ub['nickname']} не хватает карты «{CARDS[cid][0]}»."
    upd_user(a, coins=ua["coins"] - oa["coins"] + ob["coins"])
    upd_user(b, coins=ub["coins"] - ob["coins"] + oa["coins"])
    for cid, n in oa["cards"].items():
        remove_card(a, cid, n)
        add_card(b, cid, n)
    for cid, n in ob["cards"].items():
        remove_card(b, cid, n)
        add_card(a, cid, n)
    return True, "ok"

def cleanup_trades():
    now = time.time()
    for tid, room in list(TRADE_ROOMS.items()):
        if room["phase"] != "done" and room["expires"] < now:
            TRADE_ROOMS.pop(tid, None)
            for puid, mid in list(room["msgs"].items()):
                safe_edit(room["chats"][puid], mid,
                          f"🔄 <b>Обмен #{tid}</b>\n\n⏳ Обмен истёк.", reply_markup=None)
    for store in (TRADE_SETUP, TRADE_STATE):
        for puid, st in list(store.items()):
            if st.get("expires", 0) < now:
                store.pop(puid, None)

# ========================= ОБРАБОТЧИК ТЕКСТА (ИГРОКИ) =========================
def handle_text(message):
    # ФИКС: боты не регистрируются и не получают ответы
    if message.from_user and message.from_user.is_bot:
        register_chat(message)
        return

    u = register_user(message)
    register_chat(message)

    if getattr(message, "is_automatic_forward", False):
        safe_call(bot.reply_to, message,
                  "🎴 Напиши <b>Эксперимент</b>, чтобы получить карточку!")
        return

    raw = (message.text or message.caption or "").strip()
    if not raw:
        return

    clean = re.sub(r"^/([a-zа-яё_]+)@\S+", r"/\1", raw, flags=re.I).strip()
    if BOT_USERNAME:
        clean = re.sub(r"^@" + re.escape(BOT_USERNAME) + r"\b\s*", "", clean, flags=re.I)
    low = clean.lower()
    uid = message.from_user.id if message.from_user else 0

    # админ: ожидание текста рассылки
    if uid in ADMIN_STATE:
        if low in ("отмена", "cancel"):
            ADMIN_STATE.pop(uid, None)
            safe_call(bot.reply_to, message, "❌ Рассылка отменена.")
            return
        st = ADMIN_STATE.pop(uid)
        ok, fail = do_broadcast(message, st["target"])
        safe_call(bot.reply_to, message,
                  f"✅ Рассылка завершена!\n📤 Отправлено: {ok}\n❌ Ошибок: {fail}")
        return

    # ---------- обмен v2: ожидание ввода ----------
    if uid in TRADE_STATE and message.chat.type == "private":
        st = TRADE_STATE.pop(uid)
        if low in ("отмена", "cancel"):
            safe_call(bot.reply_to, message, "❌ Ввод отменён.")
            return
        room = TRADE_ROOMS.get(st["tid"])
        if not room or uid not in (room["a"], room["b"]) or room["phase"] == "done":
            safe_call(bot.reply_to, message, "⚠️ Обмен уже неактивен.")
            return
        if st["step"] == "coins":
            if not clean.isdigit():
                safe_call(bot.reply_to, message, "❌ Напиши сумму числом.")
                return
            val = int(clean)
            u = get_user(uid)
            free = u["coins"] - room["offers"][uid]["coins"]
            if val <= 0 or val > free:
                safe_call(bot.reply_to, message, f"❌ Нельзя добавить. Свободно: {free}$.")
                return
            room["offers"][uid]["coins"] += val
            trade_reset_ready(room, uid)
            trade_push(room)
            safe_call(bot.reply_to, message, "✅ Монеты добавлены! Смотри панель выше.")
            return

    if uid in TRADE_SETUP:
        st = TRADE_SETUP.get(uid)
        if low in ("обмен", "трейд", "trade"):
            safe_call(bot.reply_to, message,
                      "🔄 Напиши <b>@username или ID</b> игрока, с которым хочешь обменяться.\n"
                      "«отмена» — отменить.")
            return
        TRADE_SETUP.pop(uid)
        if st and st.get("expires", 0) < time.time():
            pass  # состояние протухло — продолжаем обычную обработку
        elif low in ("отмена", "cancel"):
            safe_call(bot.reply_to, message, "❌ Обмен отменён.")
            return
        else:
            target = find_user_by_ref(clean)
            if not target:
                safe_call(bot.reply_to, message,
                          "❌ Игрок не найден. Проверь @username/ID — игрок должен был запускать бота (/start).")
                return
            if target["user_id"] == uid:
                safe_call(bot.reply_to, message, "❌ С самим собой обменяться нельзя.")
                return
            if user_in_trade(uid) or user_in_trade(target["user_id"]):
                safe_call(bot.reply_to, message,
                          "⚠️ У вас уже есть активный обмен. Сначала заверши его.")
                return
            safe_call(bot.reply_to, message,
                      f"✅ Игрок найден: <b>{esc(target['nickname'])}</b>!\n"
                      f"Зайди в ЛС бота — там панель обмена. У вас 5 минут.")
            start_trade_room(uid, target["user_id"])
            return

    if low in ("/start", "старт"):
        u = u or get_user(uid)
        safe_call(bot.reply_to, message, txt_start(u["nickname"]), reply_markup=kb_start())
        return

    if low in ("помощь", "нпом", "нпомощь", "help", "/help"):
        safe_call(bot.reply_to, message, txt_help())   # ФИКС: без кнопки «Назад»
        return

    if low in ("профиль", "проф", "profile"):
        u = get_user(uid)
        if not u:
            safe_call(bot.reply_to, message, "⚠️ Профиль недоступен.")
            return
        safe_call(bot.reply_to, message, txt_profile(u))
        return

    if low in ("бонус", "bonus"):
        u = get_user(uid)
        now = time.time()
        ts = u["last_bonus"] if u["last_bonus"] <= now else 0  # защита от битых таймстемпов
        left = BONUS_COOLDOWN - (now - ts)
        if left > 0:
            safe_call(bot.reply_to, message,
                      f"⏳ Бонус будет доступен через <b>{fmt_time(left)}</b>.")
            return
        mult = get_priv(u)["coin_mult"]
        coins = random.randint(100, 300) * mult
        pts = random.randint(20, 60) + u["level"] * 10
        upd_user(uid, coins=u["coins"] + coins, last_bonus=now)
        leveled, new_level = add_points(uid, pts)
        msg = f"🎁 Успешно! Получено <b>{pts} Очков</b> и <b>{coins} Монет</b> 💰"
        if leveled:
            msg += f"\n🔋 Новый уровень: <b>{new_level}</b>!"
        safe_call(bot.reply_to, message, msg)
        return

    if low in ("топ", "топс", "top"):
        safe_call(bot.reply_to, message,
                  f"{nick_badged(uid, esc(u['nickname']))}, выберите ниже топ который хотите открыть:",
                  reply_markup=kb_top_menu())
        return

    if low in ("магазин", "shop", "донат", "donate"):
        safe_call(bot.reply_to, message, txt_shop(), reply_markup=kb_shop())
        return

    if low in ("кейсы", "кейс", "cases"):
        safe_call(bot.reply_to, message,
                  "🧿 <b>Кейсы:</b>\nВыбери кейс, чтобы открыть его 👇",
                  reply_markup=kb_cases())
        return

    if low in ("инвентарь", "инв", "inv"):
        rows = get_user_cards(uid)
        if not rows:
            safe_call(bot.reply_to, message,
                      "🎒 <b>Инвентарь пуст.</b>\nНапиши «эксперимент», чтобы получить карточку!")
            return
        kb, page, rows, per_page = kb_inventory(uid, 0)
        start = page * per_page
        lines = [f"🎒 <b>Ваш Инвентарь:</b> <i>стр. {page+1}</i>\n════════════════════════════"]
        for cid, cnt in rows[start:start + per_page]:
            c = CARDS[cid]
            lines.append(f"🃏 {esc(c[0])} — {c[1]} (x{cnt}) | 💪 {c[2]} | 💰 {c[3]}$")
        msg = safe_call(bot.reply_to, message, "\n".join(lines), reply_markup=kb)
        if msg:
            INV_PAGES[uid] = msg.message_id
        return

    if low in ("обмен", "трейд", "trade"):
        if user_in_trade(uid):
            safe_call(bot.reply_to, message,
                      "⚠️ У тебя уже есть активный обмен. Заверши его (или отмень) в ЛС бота и попробуй снова.")
            return
        TRADE_SETUP[uid] = {"expires": time.time() + 120}
        safe_call(bot.reply_to, message,
                  "🔄 <b>Обмен</b>\nНапиши <b>@username или ID</b> игрока, с которым хочешь обменяться.\n"
                  "«отмена» — отменить. У тебя 2 минуты.")
        return

    # ---------- промокод игрока ----------
    m = re.match(r"^промо\s+(\S+)$", low)
    if m:
        code = m.group(1).upper()
        p = promo_info(code)
        if not p:
            safe_call(bot.reply_to, message, "❌ Промокод не найден.")
            return
        if not p["active"]:
            safe_call(bot.reply_to, message, "❌ Промокод деактивирован.")
            return
        if p["rlimit"] > 0 and p["used"] >= p["rlimit"]:
            safe_call(bot.reply_to, message, "❌ Лимит активаций исчерпан.")
            return
        conn = db()
        already = conn.execute("SELECT 1 FROM promo_used WHERE code=? AND user_id=?", (code, uid)).fetchone()
        conn.close()
        if already:
            safe_call(bot.reply_to, message, "❌ Ты уже активировал этот промокод.")
            return
        result = apply_reward(uid, p["reward"])
        with db_lock:
            conn = db()
            conn.execute("INSERT OR IGNORE INTO promo_used (code, user_id) VALUES (?,?)", (code, uid))
            conn.execute("UPDATE promo SET used=used+1 WHERE code=?", (code,))
            conn.commit()
            conn.close()
        if isinstance(result, tuple) and result[0] == "CARD":
            safe_call(bot.send_photo, message.chat.id, result[2], caption=result[1],
                      reply_to_message_id=message.message_id)
        else:
            safe_call(bot.reply_to, message, f"✅ {result}")
        return

    # ---------- карта по слову "эксперимент" ----------
    if CARD_WORD in low:
        u = get_user(uid)
        now = time.time()
        cd = get_priv(u)["card_cd"]
        ts = u["last_card"] if u["last_card"] <= now else 0
        left = cd - (now - ts)
        if left > 0:
            safe_call(bot.reply_to, message,
                      f"⏳ Следующая карта через <b>{fmt_time(left)}</b>.")
            return
        card_id = pick_card_id()
        leveled, new_level = give_card(uid, card_id)
        u = get_user(uid)
        cnt = 0
        for cid, c in get_user_cards(uid):
            if cid == card_id:
                cnt = c
        text, url = card_drop_text(u, CARDS[card_id], cnt, cd)
        if leveled:
            text = text.replace("</b>", f"\n🔋 Новый уровень: <b>{new_level}</b>!</b>")
        upd_user(uid, last_card=now)
        safe_call(bot.send_photo, message.chat.id, url, caption=text,
                  reply_to_message_id=message.message_id)
        return

# ========================= АДМИН-КОМАНДЫ =========================
def is_admin(uid):
    return uid in CREATORS

def handle_admin(message, low, uid):
    if low in ("меню нуб", "нуб меню", "admin", "админ"):
        safe_call(bot.reply_to, message, txt_admin_menu(), reply_markup=kb_admin_menu())
        return True

    if low == "стата":
        conn = db()
        players = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_coins = conn.execute("SELECT COALESCE(SUM(coins),0) FROM users").fetchone()[0]
        conn.close()
        safe_call(bot.reply_to, message,
                  f"📊 <b>Статистика бота:</b>\n"
                  f"👤 Игроков: {players}\n"
                  f"💰 Монет в игре: {total_coins}\n"
                  f"😶‍🌫️ Статус Бота: Активный ✅")
        return True

    if low == "рассылка список":
        if message.chat.type != "private":
            safe_call(bot.reply_to, message, "❌ Эту команду пиши мне в ЛС.")
            return True
        rows = get_all_chats()
        if not rows:
            safe_call(bot.reply_to, message, "📭 Список чатов пуст.")
            return True
        lines = ["📋 <b>Список чатов для рассылки:</b>\n════════════════════════════"]
        for r in rows:
            ident = r["username"] or r["chat_id"]
            lines.append(f"▫️ {esc(r['title'])} — {ident} ({r['ctype']})")
        safe_call(bot.reply_to, message, "\n".join(lines))
        return True

    if low == "рассылка общий":
        ADMIN_STATE[uid] = {"target": "all"}
        safe_call(bot.reply_to, message,
                  "📨 Рассылка во <b>ВСЕ</b> чаты.\nСкинь следующим сообщением контент.\n"
                  "Напиши «отмена» для отмены.")
        return True

    m = re.match(r"^рассылка\s+(.+)$", low)
    if m:
        arg = m.group(1).strip()
        if arg == "список":
            return False
        target = parse_chat_arg(arg)
        if target is None:
            safe_call(bot.reply_to, message, "❌ Не удалось распознать чат. Используй @чат, ссылку или ID.")
            return True
        ADMIN_STATE[uid] = {"target": target}
        safe_call(bot.reply_to, message,
                  f"📨 Рассылка в чат: <b>{esc(arg)}</b>.\nСкинь следующим сообщением контент.\n"
                  f"Напиши «отмена» для отмены.")
        return True

    if low == "проф":
        if not message.reply_to_message or not message.reply_to_message.from_user:
            safe_call(bot.reply_to, message, "❌ Ответь на сообщение игрока.")
            return True
        if message.reply_to_message.from_user.is_bot:
            safe_call(bot.reply_to, message, "🤖 У ботов нет профиля.")
            return True
        tuid = message.reply_to_message.from_user.id
        u = ensure_user_exists(tuid, message.reply_to_message.from_user.first_name or "Игрок")
        safe_call(bot.reply_to, message, txt_profile(u))
        return True

    m = re.match(r"^вд\s+карта\s+(.+)$", low)
    if m:
        if not message.reply_to_message or not message.reply_to_message.from_user:
            safe_call(bot.reply_to, message, "❌ Ответь на сообщение игрока.")
            return True
        if message.reply_to_message.from_user.is_bot:
            safe_call(bot.reply_to, message, "🤖 У ботов нет профиля.")
            return True
        tuid = message.reply_to_message.from_user.id
        name = m.group(1).strip()
        card_id = find_card(name)
        if card_id is None:
            safe_call(bot.reply_to, message, "❌ Карта не найдена.")
            return True
        leveled, new_level = give_card(tuid, card_id)
        u = ensure_user_exists(tuid, message.reply_to_message.from_user.first_name or "Игрок")
        cnt = 0
        for cid, c in get_user_cards(tuid):
            if cid == card_id:
                cnt = c
        text, url = card_drop_text(u, CARDS[card_id], cnt, get_priv(u)["card_cd"])
        if leveled:
            text = text.replace("</b>", f"\n🔋 Новый уровень: <b>{new_level}</b>!</b>")
        safe_call(bot.send_photo, message.chat.id, url, caption=text,
                  reply_to_message_id=message.message_id)
        return True

    m = re.match(r"^вд\s+(монеты|очки|уровни|сила)\s+(\d+)$", low)
    if m:
        if not message.reply_to_message or not message.reply_to_message.from_user:
            safe_call(bot.reply_to, message, "❌ Ответь на сообщение игрока.")
            return True
        if message.reply_to_message.from_user.is_bot:
            safe_call(bot.reply_to, message, "🤖 У ботов нет профиля.")
            return True
        tuid = message.reply_to_message.from_user.id
        typ = m.group(1)
        val = int(m.group(2))
        u = ensure_user_exists(tuid, message.reply_to_message.from_user.first_name or "Игрок")
        if typ == "монеты":
            upd_user(tuid, coins=u["coins"] + val)
        elif typ == "очки":
            add_points(tuid, val)
        elif typ == "уровни":
            upd_user(tuid, level=u["level"] + val)
        elif typ == "сила":
            upd_user(tuid, strength=u["strength"] + val)
        safe_call(bot.reply_to, message, f"✅ Выдано <b>{esc(typ)} +{val}</b> игроку.")
        return True

    m = re.match(r"^вд\s+привилегия(?:\s+(.+))?$", low)
    if m:
        if not message.reply_to_message or not message.reply_to_message.from_user:
            safe_call(bot.reply_to, message, "❌ Ответь на сообщение игрока.")
            return True
        if message.reply_to_message.from_user.is_bot:
            safe_call(bot.reply_to, message, "🤖 У ботов нет профиля.")
            return True
        tuid = message.reply_to_message.from_user.id
        name = (m.group(1) or "").strip()
        u = ensure_user_exists(tuid, message.reply_to_message.from_user.first_name or "Игрок")
        if not name:
            upd_user(tuid, privilege="Игрок")
            safe_call(bot.reply_to, message, f"✅ Привилегия снята. Теперь: <b>Игрок</b>")
            return True
        canon = None
        for p in PRIVILEGES:
            if p.lower() == name.lower():
                canon = p
                break
        if canon is None:
            avail = " | ".join(PRIVILEGES.keys())
            safe_call(bot.reply_to, message,
                      f"❌ Такой привилегии нет.\nДоступные: <b>{esc(avail)}</b>")
            return True
        upd_user(tuid, privilege=canon)
        safe_call(bot.reply_to, message, f"✅ Игроку выдана привилегия: <b>{esc(canon)}</b>")
        return True

    if low == "карты список":
        safe_call(bot.reply_to, message, "🃏 <b>Выберите редкость:</b>",
                  reply_markup=kb_rarities())
        return True

    m = re.match(r"^промо\s+создать\s+(.+)$", low)
    if m:
        parts = m.group(1).strip().split()
        if len(parts) < 3:
            safe_call(bot.reply_to, message, "❌ Формат: промо создать КОД награда ... [лимит]")
            return True
        code = parts[0].upper()
        limit = 0
        reward = " ".join(parts[1:])
        if parts[-1].isdigit():
            test_reward = " ".join(parts[1:-1])
            if valid_reward(test_reward):
                limit = int(parts[-1])
                reward = test_reward
        if not valid_reward(reward):
            safe_call(bot.reply_to, message, "❌ Неверная награда.")
            return True
        with db_lock:
            conn = db()
            conn.execute("INSERT OR REPLACE INTO promo (code, reward, rlimit, used, active, created) VALUES (?,?,?,?,?,?)",
                         (code, reward, limit, 0, 1, time.time()))
            conn.commit()
            conn.close()
        safe_call(bot.reply_to, message, f"✅ Промокод <b>{esc(code)}</b> создан!\nНаграда: {esc(reward)} | Лимит: {limit or '∞'}")
        return True

    m = re.match(r"^промо\s+удалить\s+(\S+)$", low)
    if m:
        code = m.group(1).upper()
        with db_lock:
            conn = db()
            conn.execute("DELETE FROM promo WHERE code=?", (code,))
            conn.execute("DELETE FROM promo_used WHERE code=?", (code,))
            conn.commit()
            conn.close()
        safe_call(bot.reply_to, message, f"🗑 Промокод <b>{esc(code)}</b> удалён.")
        return True

    m = re.match(r"^промо\s+ред\s+(\S+)\s+награда\s+(.+)$", low)
    if m:
        code = m.group(1).upper()
        rw = m.group(2).strip()
        if not valid_reward(rw):
            safe_call(bot.reply_to, message, "❌ Неверная награда.")
            return True
        with db_lock:
            conn = db()
            conn.execute("UPDATE promo SET reward=? WHERE code=?", (rw, code))
            conn.commit()
            conn.close()
        safe_call(bot.reply_to, message, f"✅ Промокод <b>{esc(code)}</b> обновлён.")
        return True

    m = re.match(r"^промо\s+ред\s+(\S+)\s+лимит\s+(\d+)$", low)
    if m:
        code = m.group(1).upper()
        lim = int(m.group(2))
        with db_lock:
            conn = db()
            conn.execute("UPDATE promo SET rlimit=? WHERE code=?", (lim, code))
            conn.commit()
            conn.close()
        safe_call(bot.reply_to, message, f"✅ Лимит промокода <b>{esc(code)}</b> = {lim}")
        return True

    m = re.match(r"^промо\s+ред\s+(\S+)\s+статус\s+(вкл|выкл)$", low)
    if m:
        code = m.group(1).upper()
        st = 1 if m.group(2) == "вкл" else 0
        with db_lock:
            conn = db()
            conn.execute("UPDATE promo SET active=? WHERE code=?", (st, code))
            conn.commit()
            conn.close()
        safe_call(bot.reply_to, message, f"✅ Промокод <b>{esc(code)}</b> — {'включён' if st else 'выключен'}.")
        return True

    if low == "промо список":
        conn = db()
        rows = conn.execute("SELECT code, reward, rlimit, used, active FROM promo ORDER BY code").fetchall()
        conn.close()
        if not rows:
            safe_call(bot.reply_to, message, "📭 Промокодов нет.")
            return True
        lines = ["🎟 <b>ПРОМОКОДЫ</b>\n━━━━━━━━━━━━━━━━━━━━"]
        for r in rows:
            status = "🟢" if r["active"] else "🔴"
            lim = f"{r['used']}/{r['rlimit']}" if r["rlimit"] > 0 else f"{r['used']}/∞"
            lines.append(f"{status} <b>{esc(r['code'])}</b> — {esc(r['reward'])} — {lim}")
        safe_call(bot.reply_to, message, "\n".join(lines))
        return True

    m = re.match(r"^промо\s+инфо\s+(\S+)$", low)
    if m:
        code = m.group(1).upper()
        p = promo_info(code)
        if not p:
            safe_call(bot.reply_to, message, "❌ Промокод не найден.")
            return True
        status = "🟢 Активен" if p["active"] else "🔴 Выключен"
        lim = f"{p['used']}/{p['rlimit']}" if p["rlimit"] > 0 else f"{p['used']}/∞"
        safe_call(bot.reply_to, message,
                  f"🎟 <b>{esc(code)}</b>\nНаграда: {esc(p['reward'])}\nЛимит: {lim}\nСтатус: {status}")
        return True

    return False

# ========================= CALLBACKS =========================
@bot.callback_query_handler(func=lambda call: True)
@guard
def callback_handler(call):
    data = call.data
    uid = call.from_user.id
    chat_id = call.message.chat.id

    # ---------- защита админ-панели от обычных игроков ----------
    if data.startswith("admin:"):
        if not is_admin(uid):
            safe_call(bot.answer_callback_query, call.id,
                      "❌ Нет доступа. Это панель администратора.", show_alert=True)
            return

    # ---------- покупка кейса + анимация ----------
    if data.startswith("case:buy:"):
        safe_call(bot.answer_callback_query, call.id)
        idx = int(data.split(":")[2])
        case = CASES[idx]

        # кулдаун 3 сек на открытие
        now = time.time()
        left = CASE_OPEN_COOLDOWN - (now - CASE_LAST_OPEN.get(uid, 0))
        if left > 0:
            safe_call(bot.answer_callback_query, call.id,
                      f"⏳ Подожди {left:.1f} сек перед следующим открытием.", show_alert=True)
            return
        CASE_LAST_OPEN[uid] = now

        u = get_user(uid) or ensure_user_exists(uid, call.from_user.first_name or "Игрок")
        cost = case["cost"]
        if u["coins"] < cost:
            safe_call(bot.answer_callback_query, call.id,
                      f"Не хватает монет! Нужно {cost}$", show_alert=True)
            return
        upd_user(uid, coins=u["coins"] - cost)

        card_name, chance = pick_case_item(case)
        card_id = find_card(card_name)

        # Выдаём карту сразу — до анимации, чтобы не блокировать поток
        leveled, new_level = give_card(uid, card_id)
        u = get_user(uid)
        text, url = case_win_text(u, CARDS[card_id], chance, case["name"])
        if leveled:
            text = text.replace("</b>", f"\n🔋 Новый уровень: <b>{new_level}</b>!</b>")

        # АНИМАЦИЯ: запускаем в отдельном потоке — не блокируем polling
        _reply_mid = call.message.message_id
        _case_name = case["name"]
        _text = text
        _url = url
        _chat_id = chat_id

        def _run_anim(chat_id_=_chat_id, case_name_=_case_name, text_=_text,
                      url_=_url, reply_mid_=_reply_mid):
            try:
                anim = safe_call(bot.send_message, chat_id_,
                                 f"🧿 <b>Открываем {esc(case_name_)}...</b>\n[░░░░░░░░░░] 0%")
                if anim:
                    for pct in range(25, 101, 25):
                        filled = pct // 10
                        bar = "█" * filled + "░" * (10 - filled)
                        safe_edit(chat_id_, anim.message_id,
                                  f"🧿 <b>Открываем {esc(case_name_)}...</b>\n[{bar}] {pct}%")
                        time.sleep(0.25)
                    try:
                        bot.delete_message(chat_id_, anim.message_id)
                    except Exception:
                        pass
            except Exception:
                pass
            safe_call(bot.send_photo, chat_id_, url_, caption=text_,
                      reply_to_message_id=reply_mid_)

        threading.Thread(target=_run_anim, daemon=True).start()
        return

    # ---------- инвентарь: страницы ----------
    if data == "inv:noop":
        safe_call(bot.answer_callback_query, call.id)
        return

    m = re.match(r"^inv:(\d+)$", data)
    if m:
        page = int(m.group(1))
        rows = get_user_cards(uid)
        if not rows:
            safe_call(bot.answer_callback_query, call.id, "Инвентарь пуст.")
            return
        kb, page, rows, per_page = kb_inventory(uid, page)
        start = page * per_page
        lines = [f"🎒 <b>Ваш Инвентарь:</b> <i>стр. {page+1}</i>\n════════════════════════════"]
        for cid, cnt in rows[start:start + per_page]:
            c = CARDS[cid]
            lines.append(f"🃏 {esc(c[0])} — {c[1]} (x{cnt}) | 💪 {c[2]} | 💰 {c[3]}$")
        res = safe_edit(chat_id, call.message.message_id, "\n".join(lines), reply_markup=kb)
        if res is None:
            # если редактировать нельзя — шлём новое сообщение
            msg = safe_call(bot.send_message, chat_id, "\n".join(lines), reply_markup=kb)
            if msg:
                INV_PAGES[uid] = msg.message_id
        safe_call(bot.answer_callback_query, call.id)
        return

    # ---------- обмен v2 ----------
    if data == "trade2:noop":
        safe_call(bot.answer_callback_query, call.id)
        return

    m = re.match(r"^trade2:(coins|cards|clear|ready|edit|cancel|back):(\d+)$", data)
    if m:
        act, tid = m.group(1), int(m.group(2))
        room = TRADE_ROOMS.get(tid)
        if not room or uid not in (room["a"], room["b"]) or room["phase"] == "done":
            safe_call(bot.answer_callback_query, call.id, "⏳ Обмен неактивен.", show_alert=True)
            return
        other = trade_other(room, uid)

        if act == "coins":
            safe_call(bot.answer_callback_query, call.id)
            u = get_user(uid)
            free = u["coins"] - room["offers"][uid]["coins"]
            TRADE_STATE[uid] = {"tid": tid, "step": "coins", "expires": time.time() + 60}
            safe_call(bot.send_message, uid,
                      f"💰 Сколько монет добавить в обмен?\nСвободно: {free}$\n"
                      f"Напиши числом. «отмена» — отменить.")
            return

        if act == "cards":
            safe_call(bot.answer_callback_query, call.id)
            safe_edit(chat_id, call.message.message_id,
                      f"🃏 <b>Выбери карту для обмена #{tid}:</b>",
                      reply_markup=trade_kb_cards(tid, uid))
            return

        if act == "clear":
            room["offers"][uid] = {"coins": 0, "cards": {}}
            trade_reset_ready(room, uid)
            trade_push(room)
            safe_call(bot.answer_callback_query, call.id, "🗑 Вклад очищен.")
            return

        if act == "ready":
            room["ready"][uid] = True
            safe_call(bot.answer_callback_query, call.id, "✅ Ты готов!")
            if room["ready"].get(other):
                room["phase"] = "confirm"
                room["confirm"][uid] = False
                room["confirm"][other] = False
            trade_push(room)
            return

        if act == "edit":
            room["phase"] = "build"
            room["ready"][uid] = False
            room["confirm"][uid] = False
            room["confirm"][other] = False
            trade_push(room)
            safe_call(bot.answer_callback_query, call.id, "✏️ Можешь менять вклад.")
            return

        if act == "cancel":
            TRADE_ROOMS.pop(tid, None)
            TRADE_STATE.pop(room["a"], None)
            TRADE_STATE.pop(room["b"], None)
            for puid, mid in list(room["msgs"].items()):
                safe_edit(room["chats"][puid], mid,
                          f"🔄 <b>Обмен #{tid}</b>\n\n❌ Обмен отменён.", reply_markup=None)
            safe_call(bot.answer_callback_query, call.id, "❌ Отменено.")
            return

        if act == "back":
            safe_call(bot.answer_callback_query, call.id)
            trade_push(room)
            return
        return

    m = re.match(r"^trade2:addcard:(\d+):(\d+)$", data)
    if m:
        tid, cid = int(m.group(1)), int(m.group(2))
        room = TRADE_ROOMS.get(tid)
        if not room or uid not in (room["a"], room["b"]) or room["phase"] == "done":
            safe_call(bot.answer_callback_query, call.id, "⏳ Обмен неактивен.", show_alert=True)
            return
        owned = card_count(uid, cid)
        used = room["offers"][uid]["cards"].get(cid, 0)
        if owned - used <= 0:
            safe_call(bot.answer_callback_query, call.id, "❌ Нет свободных копий.", show_alert=True)
            return
        room["offers"][uid]["cards"][cid] = used + 1
        trade_reset_ready(room, uid)
        safe_edit(chat_id, call.message.message_id,
                  f"🃏 <b>Выбери карту для обмена #{tid}:</b>",
                  reply_markup=trade_kb_cards(tid, uid))
        safe_call(bot.answer_callback_query, call.id, f"🃏 {CARDS[cid][0]} +1")
        return

    m = re.match(r"^trade2:confirm:(\d+)$", data)
    if m:
        tid = int(m.group(1))
        room = TRADE_ROOMS.get(tid)
        if not room or uid not in (room["a"], room["b"]):
            safe_call(bot.answer_callback_query, call.id, "⏳ Обмен неактивен.", show_alert=True)
            return
        if room["phase"] != "confirm":
            safe_call(bot.answer_callback_query, call.id,
                      "❌ Сначала оба должны нажать «Готов».", show_alert=True)
            return
        room["confirm"][uid] = True
        other = trade_other(room, uid)
        if room["confirm"].get(other):
            ok, resmsg = execute_trade_room(tid)
            if ok:
                room["phase"] = "done"
                trade_finish_msgs(room, True)
                TRADE_ROOMS.pop(tid, None)
                safe_call(bot.answer_callback_query, call.id, "✅ Обмен завершён!")
            else:
                trade_finish_msgs(room, False, resmsg)
                room["phase"] = "build"
                room["ready"][room["a"]] = False
                room["ready"][room["b"]] = False
                room["confirm"][room["a"]] = False
                room["confirm"][room["b"]] = False
                trade_push(room)
                safe_call(bot.answer_callback_query, call.id, "⚠️ Ошибка, обмен сброшен.", show_alert=True)
        else:
            trade_push(room)
            safe_call(bot.answer_callback_query, call.id, "✅ Ждём подтверждения второго игрока...")
        return

    # ---------- магазин ----------
    if data == "shop:back":
        safe_edit(chat_id, call.message.message_id, txt_shop(), reply_markup=kb_shop())
        return

    m = re.match(r"^shop:view:(\w+)$", data)
    if m:
        it = next((x for x in SHOP_ITEMS if x["key"] == m.group(1)), None)
        if not it:
            safe_call(bot.answer_callback_query, call.id, "❌ Товар не найден.", show_alert=True)
            return
        safe_edit(chat_id, call.message.message_id,
                  f"👑 <b>{esc(it['name'])}</b>\n"
                  "━━━━━━━━━━━━━━━━━━━━\n"
                  f"💰 Цена: <b>⭐ {it['price']}</b>\n"
                  f"📋 Что даёт:\n{esc(it['desc'])}\n\n"
                  f"После оплаты привилегия активируется автоматически.",
                  reply_markup=kb_shop_item(it["key"]))
        return

    m = re.match(r"^shop:buy:(\w+)$", data)
    if m:
        it = next((x for x in SHOP_ITEMS if x["key"] == m.group(1)), None)
        safe_call(bot.answer_callback_query, call.id)
        if not it:
            return
        u = get_user(uid)
        if u and u["privilege"] == it["name"]:
            safe_call(bot.send_message, uid,
                      f"👑 У тебя уже есть привилегия <b>{esc(it['name'])}</b>!")
            return
        # Stars-инвойс ВСЕГДА уходит в ЛС юзера (uid), а не в группу —
        # Telegram Stars не принимаются прямо из групповых чатов.
        try:
            desc = it["desc"].replace("\n", " | ")[:255]
            inv = bot.send_invoice(
                uid,
                title=f"👑 {it['name']}",
                description=desc,
                payload=f"shop:{it['key']}:{uid}",
                provider_token="",
                currency="XTR",
                prices=[types.LabeledPrice(it['name'], int(it['price']))],
            )
            # если пишем из группы — сказать игроку проверить ЛС
            if chat_id != uid:
                safe_call(bot.send_message, chat_id,
                          f"💳 {esc(u['nickname'])}, счёт на оплату отправлен тебе в "
                          f"<b>личные сообщения</b> с ботом. Открой ЛС и нажми «Оплатить» 👇")
        except ApiTelegramException as e:
            err = str(e)
            # бот ещё не писал этому юзеру — объясняем
            if "bot can\'t initiate conversation" in err.lower() or "chat not found" in err.lower():
                safe_call(bot.send_message, chat_id,
                          "❌ Не могу написать тебе в ЛС.\n"
                          "Запусти бота в личных сообщениях командой /start и попробуй снова.")
            else:
                safe_call(bot.send_message, chat_id,
                          f"❌ Ошибка при создании счёта.\nПопробуй ещё раз или напиши в поддержку.\n"
                          f"<code>{esc(err[:120])}</code>")
        return

    # ---------- админ ----------
    if data == "admin:menu":
        safe_edit(chat_id, call.message.message_id, txt_admin_menu(), reply_markup=kb_admin_menu())
        return

    if data == "admin:promo":
        safe_edit(chat_id, call.message.message_id, txt_admin_promo(), reply_markup=kb_admin_back())
        return

    if data == "admin:stats":
        conn = db()
        players = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_coins = conn.execute("SELECT COALESCE(SUM(coins),0) FROM users").fetchone()[0]
        conn.close()
        safe_edit(chat_id, call.message.message_id,
                  f"📊 <b>Статистика бота:</b>\n👤 Игроков: {players}\n"
                  f"💰 Монет в игре: {total_coins}\n😶‍🌫️ Статус Бота: Активный ✅",
                  reply_markup=kb_admin_back())
        return

    if data == "admin:broadcast":
        safe_edit(chat_id, call.message.message_id, txt_admin_broadcast(), reply_markup=kb_admin_back())
        return

    if data == "admin:give":
        safe_edit(chat_id, call.message.message_id, txt_admin_give(), reply_markup=kb_admin_back())
        return

    if data == "admin:cards":
        safe_edit(chat_id, call.message.message_id, "🃏 <b>Выберите редкость:</b>",
                  reply_markup=kb_rarities())
        return

    if data.startswith("admin:cardlist:"):
        rar = data.split(":", 2)[2]
        safe_call(bot.answer_callback_query, call.id, f"🃏 {rar}")
        ids = []
        for i, c in enumerate(CARDS):
            if c[1] == rar:
                msg = safe_call(bot.send_photo, chat_id, c[4],
                                caption=f"<b>{esc(c[0])}</b>\n{c[1]} | 💪 {c[2]} | 💰 {c[3]}$")
                if msg:
                    ids.append(msg.message_id)
                time.sleep(0.35)
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="admin:cardback"))
        msg = safe_call(bot.send_message, chat_id,
                        f"🃏 <b>{esc(rar)}</b> — карт: {len(ids)}",
                        reply_markup=kb)
        if msg:
            ids.append(msg.message_id)
        CARD_VIEW[uid] = ids
        return

    if data == "admin:cardback":
        ids = CARD_VIEW.pop(uid, [])
        for mid in ids:
            try:
                bot.delete_message(chat_id, mid)
            except Exception:
                pass
        safe_call(bot.send_message, chat_id, txt_admin_menu(), reply_markup=kb_admin_menu())
        return

    # ---------- топ ----------
    if data.startswith("top:"):
        kind = data.split(":", 1)[1]
        col = {"coins": "coins", "level": "level", "points": "points"}[kind]
        emoji = {"coins": "💰", "level": "🔋", "points": "🌟"}[kind]
        conn = db()
        rows = conn.execute(f"SELECT nickname, {col} AS v, user_id FROM users ORDER BY {col} DESC, user_id ASC LIMIT 10").fetchall()
        conn.close()
        medals = ["🥇", "🥈", "🥉"] + ["▫️"] * 7
        lines = [f"{emoji} <b>Топ по {'Монетам' if kind=='coins' else 'Уровню' if kind=='level' else 'Очкам'}</b>\n════════════════════════════"]
        for i, r in enumerate(rows):
            lines.append(f"{medals[i]} {nick_badged(r['user_id'], esc(r['nickname']))} — <b>{r['v']}</b>")
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="back:topmenu"))
        safe_edit(chat_id, call.message.message_id, "\n".join(lines), reply_markup=kb)
        return

    if data == "back:topmenu":
        u = get_user(uid)
        if u:
            safe_edit(chat_id, call.message.message_id,
                      f"{esc(u['nickname'])}, выберите ниже топ который хотите открыть:",
                      reply_markup=kb_top_menu())
        return

    # back:help больше не используется, но оставим безопасный ответ
    if data == "back:help":
        safe_call(bot.answer_callback_query, call.id, "Используй команду «Помощь».")
        return

    safe_call(bot.answer_callback_query, call.id, "...")

# ========================= ХЕНДЛЕРЫ =========================
# ========================= ОПЛАТА (TELEGRAM STARS) =========================
@bot.pre_checkout_query_handler(func=lambda q: True)
@guard
def on_pre_checkout(query):
    safe_call(bot.answer_pre_checkout_query, query.id, ok=True)

@bot.message_handler(content_types=["successful_payment"])
@guard
def on_successful_payment(message):
    uid = message.from_user.id if message.from_user else 0
    if not uid:
        return
    sp = getattr(message, "successful_payment", None)
    payload = getattr(sp, "invoice_payload", "") if sp else ""
    m = re.match(r"^shop:(\w+):(\d+)$", payload or "")
    if not m:
        return
    key, puid = m.group(1), int(m.group(2))
    it = SHOP_ITEMS_DICT.get(key)
    if not it or puid != uid:
        safe_call(bot.send_message, uid, "⚠️ Ошибка платежа: счёт не найден. Напиши администратору.")
        return
    # регистрируем юзера на случай если его ещё нет
    u = ensure_user_exists(uid, message.from_user.first_name or "Игрок")
    if not u:
        return
    if u["privilege"] == it["name"]:
        safe_call(bot.send_message, uid,
                  f"👑 У тебя уже есть привилегия <b>{esc(it['name'])}</b>!")
        return
    upd_user(uid, privilege=it["name"])
    priv_info = PRIVILEGES.get(it["name"], {})
    cd_min = priv_info.get("card_cd", CARD_COOLDOWN) // 60
    safe_call(bot.send_message, uid,
              f"✅ <b>Оплата прошла! Спасибо за поддержку! ❤️</b>\n\n"
              f"👑 Привилегия: <b>{esc(it['name'])}</b>\n"
              f"━━━━━━━━━━━━━━━━━━━━\n"
              f"{esc(it['desc'])}\n\n"
              f"⏱ Кулдаун карты теперь: <b>{cd_min} мин</b>")

@bot.message_handler(func=lambda m: True)
@guard
def on_message(message):
    if not message.from_user:
        return
    uid = message.from_user.id
    raw = (message.text or "").strip()
    clean = re.sub(r"^/([a-zа-яё_]+)@\S+", r"/\1", raw, flags=re.I).strip()
    if BOT_USERNAME:
        clean = re.sub(r"^@" + re.escape(BOT_USERNAME) + r"\b\s*", "", clean, flags=re.I)
    low = clean.lower()

    if is_admin(uid):
        if handle_admin(message, low, uid):
            return

    handle_text(message)

@bot.message_handler(content_types=["photo", "video", "animation", "document", "sticker", "voice"])
@guard
def on_media(message):
    register_chat(message)
    if getattr(message, "is_automatic_forward", False):
        safe_call(bot.reply_to, message,
                  "🎴 Напиши <b>Эксперимент</b>, чтобы получить карточку!")
        return
    if message.from_user and message.from_user.id in ADMIN_STATE:
        handle_text(message)

# фоновая очистка трейдов
def trades_gc():
    while True:
        try:
            cleanup_trades()
        except Exception:
            pass
        time.sleep(30)

# ========================= ЗАПУСК =========================
if __name__ == "__main__":
    print("[NooB Bot] Запуск v" + BOT_VERSION + "...")
    threading.Thread(target=trades_gc, daemon=True).start()
    for _row in get_all_chats():
        try:
            bot.send_message(_row["chat_id"], "✅ Бот запущен и готов к работе.")
        except Exception:
            pass
        time.sleep(0.40)
    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
        except Exception:
            traceback.print_exc()
            time.sleep(5)
