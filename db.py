# db.py
import aiosqlite

DB_PATH = "rezme.db"

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER UNIQUE,
    username TEXT,
    first_name TEXT,
    phone TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_BOOKINGS_TABLE = """
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER,
    venue_id INTEGER,
    category TEXT,
    date TEXT,
    time TEXT,
    people_count INTEGER,
    comment TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_REVIEWS_TABLE = """
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER,
    venue_id INTEGER,
    rating INTEGER,
    text TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


async def init_db():
    """Создаём таблицы и добавляем недостающие колонки, если нужно."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_USERS_TABLE)
        await db.execute(CREATE_BOOKINGS_TABLE)
        await db.execute(CREATE_REVIEWS_TABLE)

        # добавляем phone в users, если его нет
        try:
            await db.execute("ALTER TABLE users ADD COLUMN phone TEXT;")
        except Exception:
            pass

        # добавляем venue_id в bookings, если его нет
        try:
            await db.execute("ALTER TABLE bookings ADD COLUMN venue_id INTEGER;")
        except Exception:
            pass

        await db.commit()


# ---------- USERS ----------

async def upsert_user(
    tg_id: int,
    username: str | None,
    first_name: str | None,
    phone: str | None = None,
):
    """Сохраняем пользователя (если уже есть — не трогаем)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO users (tg_id, username, first_name, phone)
            VALUES (?, ?, ?, ?)
            """,
            (tg_id, username, first_name, phone),
        )
        await db.commit()


async def get_user_phone(tg_id: int) -> str | None:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT phone FROM users WHERE tg_id = ?", (tg_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0]
    return None


async def update_user_phone(tg_id: int, phone: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET phone = ? WHERE tg_id = ?",
            (phone, tg_id),
        )
        await db.commit()


async def get_users_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def get_all_users() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT tg_id, username, first_name, phone, created_at
            FROM users
            ORDER BY created_at DESC
            """
        ) as cursor:
            rows = await cursor.fetchall()

    result: list[dict] = []
    for tg_id, username, first_name, phone, created_at in rows:
        result.append(
            {
                "tg_id": tg_id,
                "username": username,
                "first_name": first_name,
                "phone": phone,
                "created_at": created_at,
            }
        )
    return result


# ---------- BOOKINGS ----------

async def create_booking(
    tg_id: int,
    venue_id: int | None,
    category: str,
    date: str,
    time: str,
    people_count: int,
    comment: str,
):
    """Создаём запись о брони."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO bookings (tg_id, venue_id, category, date, time, people_count, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (tg_id, venue_id, category, date, time, people_count, comment),
        )
        await db.commit()


async def get_bookings_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM bookings") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def get_last_bookings(limit: int = 20) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT tg_id, venue_id, category, date, time, people_count, comment, created_at
            FROM bookings
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ) as cursor:
            rows = await cursor.fetchall()

    result: list[dict] = []
    for tg_id, venue_id, category, date_, time_, people_count, comment, created_at in rows:
        result.append(
            {
                "tg_id": tg_id,
                "venue_id": venue_id,
                "category": category,
                "date": date_,
                "time": time_,
                "people_count": people_count,
                "comment": comment,
                "created_at": created_at,
            }
        )
    return result


# ---------- REVIEWS ----------

async def get_user_venue_ids(tg_id: int) -> list[int]:
    """Все заведения, которые этот пользователь когда-либо бронировал."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT DISTINCT venue_id
            FROM bookings
            WHERE tg_id = ? AND venue_id IS NOT NULL
            """,
            (tg_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows if row[0] is not None]


async def user_has_booking_for_venue(tg_id: int, venue_id: int) -> bool:
    """Есть ли у пользователя хоть одна бронь по этому заведению."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT 1 FROM bookings
            WHERE tg_id = ? AND venue_id = ?
            LIMIT 1
            """,
            (tg_id, venue_id),
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None


async def add_review(
    tg_id: int,
    venue_id: int,
    rating: int,
    text: str,
):
    """Добавляем отзыв."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO reviews (tg_id, venue_id, rating, text)
            VALUES (?, ?, ?, ?)
            """,
            (tg_id, venue_id, rating, text),
        )
        await db.commit()


async def get_reviews_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM reviews") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def get_last_reviews(limit: int = 20) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT tg_id, venue_id, rating, text, created_at
            FROM reviews
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ) as cursor:
            rows = await cursor.fetchall()

    result: list[dict] = []
    for tg_id, venue_id, rating, text, created_at in rows:
        result.append(
            {
                "tg_id": tg_id,
                "venue_id": venue_id,
                "rating": rating,
                "text": text,
                "created_at": created_at,
            }
        )
    return result
