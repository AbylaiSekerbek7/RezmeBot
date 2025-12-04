# handlers/admin.py
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import get_settings
from keyboards import main_menu_kb
from db import (
    get_users_count,
    get_bookings_count,
    get_reviews_count,
    get_all_users,
    get_last_bookings,
    get_last_reviews,
)
from venues import (
    get_all_venues,
    add_venue,
    delete_venue,
    get_venue_by_id,
)

router = Router()


def _is_admin(user_id: int) -> bool:
    """Проверяем, что user_id совпадает с ADMIN_ID из .env"""
    settings = get_settings()
    admin_env = settings.admin_id

    if admin_env is None:
        return False

    try:
        admin_id = int(admin_env)
    except (TypeError, ValueError):
        return False

    return user_id == admin_id


# ---------- клавиатуры ----------

def admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats")],
            [InlineKeyboardButton(text="👥 Пользователи", callback_data="admin:users")],
            [InlineKeyboardButton(text="📅 Брони", callback_data="admin:bookings")],
            [InlineKeyboardButton(text="⭐️ Отзывы", callback_data="admin:reviews")],
            [InlineKeyboardButton(text="🏬 Заведения", callback_data="admin:venues")],
            [
                InlineKeyboardButton(
                    text="➕ Добавить заведение", callback_data="admin:add_venue"
                ),
                InlineKeyboardButton(
                    text="🗑 Удалить заведение", callback_data="admin:del_venue"
                ),
            ],
        ]
    )


def delete_venues_kb() -> InlineKeyboardMarkup:
    venues = get_all_venues()
    buttons: list[list[InlineKeyboardButton]] = []
    for v in venues:
        text = f"🗑 {v.get('name', 'Без названия')} (id={v.get('id')})"
        buttons.append(
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"admin_del_venue:{v.get('id')}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ---------- состояния для /add_venue ----------

class AddVenueStates(StatesGroup):
    waiting_name = State()
    waiting_category = State()
    waiting_district = State()
    waiting_address = State()
    waiting_phone = State()
    waiting_instagram = State()


# ---------- хелперы-рендеры (без проверки прав) ----------

async def _send_stats(message: types.Message):
    users = await get_users_count()
    bookings = await get_bookings_count()
    reviews = await get_reviews_count()

    text = (
        "📊 <b>Статистика</b>\n\n"
        f"👥 Пользователи: <b>{users}</b>\n"
        f"📅 Брони: <b>{bookings}</b>\n"
        f"⭐️ Отзывы: <b>{reviews}</b>\n"
    )
    await message.answer(text, reply_markup=admin_menu_kb())


async def _send_users(message: types.Message):
    users = await get_all_users()
    if not users:
        await message.answer("Пользователей пока нет.")
        return

    lines = []
    for u in users[:50]:
        line = (
            f"• <b>{u['first_name'] or ''}</b> "
            f"(@{u['username'] or '—'}, id={u['tg_id']})\n"
            f"  Телефон: {u['phone'] or '—'}\n"
            f"  Дата регистрации: {u['created_at']}"
        )
        lines.append(line)

    text = "👥 <b>Пользователи</b> (последние)\n\n" + "\n\n".join(lines)
    await message.answer(text)


async def _send_bookings(message: types.Message):
    bookings = await get_last_bookings(limit=30)
    if not bookings:
        await message.answer("Броней пока нет.")
        return

    lines = []
    for b in bookings:
        venue = get_venue_by_id(b["venue_id"]) if b["venue_id"] else None
        venue_name = venue.get("name") if venue else "—"
        line = (
            f"• Пользователь id={b['tg_id']}\n"
            f"  Заведение: {venue_name}\n"
            f"  Категория/фильтр: {b['category']}\n"
            f"  Дата/время: {b['date']} {b['time']}\n"
            f"  Людей: {b['people_count']}\n"
            f"  Комментарий: {b['comment'] or '—'}\n"
            f"  Создано: {b['created_at']}"
        )
        lines.append(line)

    text = "📅 <b>Последние брони</b>\n\n" + "\n\n".join(lines)
    await message.answer(text)


async def _send_reviews(message: types.Message):
    reviews = await get_last_reviews(limit=30)
    if not reviews:
        await message.answer("Отзывов пока нет.")
        return

    lines = []
    for r in reviews:
        venue = get_venue_by_id(r["venue_id"]) if r["venue_id"] else None
        venue_name = venue.get("name") if venue else "—"
        line = (
            f"• Пользователь id={r['tg_id']}\n"
            f"  Заведение: {venue_name}\n"
            f"  Оценка: {r['rating']}⭐️\n"
            f"  Отзыв: {r['text'] or '—'}\n"
            f"  Дата: {r['created_at']}"
        )
        lines.append(line)

    text = "⭐️ <b>Последние отзывы</b>\n\n" + "\n\n".join(lines)
    await message.answer(text)


async def _send_venues(message: types.Message):
    venues = get_all_venues()
    if not venues:
        await message.answer("Заведений в базе пока нет.")
        return

    lines = []
    for v in venues:
        line = (
            f"ID: <b>{v.get('id')}</b>\n"
            f"Название: <b>{v.get('name')}</b>\n"
            f"Категория: {v.get('category')}\n"
            f"Район: {v.get('district', '—')}\n"
            f"Адрес: {v.get('address')}\n"
            f"Телефон: {v.get('phone')}\n"
            f"Instagram: {v.get('instagram') or '—'}"
        )
        lines.append(line)

    text = "🏬 <b>Заведения</b>\n\n" + "\n\n".join(lines)
    await message.answer(text)

async def _start_add_venue(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(AddVenueStates.waiting_name)
    await message.answer(
        "Добавление нового заведения.\n\n"
        "1/6. Введите <b>название</b> заведения:",
        reply_markup=main_menu_kb,
    )

# ---------- /admin ----------

@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if not _is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к админ-панели.")
        return

    users = await get_users_count()
    bookings = await get_bookings_count()
    reviews = await get_reviews_count()

    text = (
        "🛠 <b>Админ-панель</b>\n\n"
        f"👥 Пользователи: <b>{users}</b>\n"
        f"📅 Брони: <b>{bookings}</b>\n"
        f"⭐️ Отзывы: <b>{reviews}</b>\n\n"
        "Выберите раздел 👇"
    )

    await message.answer(text, reply_markup=admin_menu_kb())


# ---------- коллбек «Статистика» ----------

@router.callback_query(F.data == "admin:stats")
async def admin_stats_cb(callback: types.CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return

    # Просто отправляем новое сообщение (не edit_text — чтобы не ловить ошибку "message is not modified")
    await _send_stats(callback.message)
    await callback.answer()


# ---------- пользователи ----------

@router.message(Command("admin_users"))
async def admin_users(message: types.Message):
    if not _is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return
    await _send_users(message)


@router.callback_query(F.data == "admin:users")
async def admin_users_cb(callback: types.CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return
    await _send_users(callback.message)
    await callback.answer()


# ---------- брони ----------

@router.message(Command("admin_bookings"))
async def admin_bookings(message: types.Message):
    if not _is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return
    await _send_bookings(message)


@router.callback_query(F.data == "admin:bookings")
async def admin_bookings_cb(callback: types.CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return
    await _send_bookings(callback.message)
    await callback.answer()


# ---------- отзывы ----------

@router.message(Command("admin_reviews"))
async def admin_reviews(message: types.Message):
    if not _is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return
    await _send_reviews(message)


@router.callback_query(F.data == "admin:reviews")
async def admin_reviews_cb(callback: types.CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return
    await _send_reviews(callback.message)
    await callback.answer()


# ---------- список заведений ----------

@router.message(Command("admin_venues"))
async def admin_venues(message: types.Message):
    if not _is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return
    await _send_venues(message)


@router.callback_query(F.data == "admin:venues")
async def admin_venues_cb(callback: types.CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return
    await _send_venues(callback.message)
    await callback.answer()


# ---------- добавление заведения (FSM) ----------

@router.message(Command("add_venue"))
async def add_venue_start(message: types.Message, state: FSMContext):
    # здесь проверяем уже ТЕБЯ (по команде)
    if not _is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа.")
        return

    await _start_add_venue(message, state)


@router.callback_query(F.data == "admin:add_venue")
async def add_venue_from_menu(callback: types.CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return

    # тут уже НЕ вызываем add_venue_start (он снова проверяет message.from_user),
    # а сразу стартуем через внутренний хелпер
    await _start_add_venue(callback.message, state)
    await callback.answer()


@router.message(AddVenueStates.waiting_name)
async def add_venue_name(message: types.Message, state: FSMContext):
    await state.update_data(name=(message.text or "").strip())
    await state.set_state(AddVenueStates.waiting_category)
    await message.answer("2/6. Введите <b>категорию</b> (например, Кафе/Рестораны):")


@router.message(AddVenueStates.waiting_category)
async def add_venue_category(message: types.Message, state: FSMContext):
    await state.update_data(category=(message.text or "").strip())
    await state.set_state(AddVenueStates.waiting_district)
    await message.answer("3/6. Введите <b>район</b>:")


@router.message(AddVenueStates.waiting_district)
async def add_venue_district(message: types.Message, state: FSMContext):
    await state.update_data(district=(message.text or "").strip())
    await state.set_state(AddVenueStates.waiting_address)
    await message.answer("4/6. Введите <b>адрес</b>:")


@router.message(AddVenueStates.waiting_address)
async def add_venue_address(message: types.Message, state: FSMContext):
    await state.update_data(address=(message.text or "").strip())
    await state.set_state(AddVenueStates.waiting_phone)
    await message.answer("5/6. Введите <b>телефон</b>:")


@router.message(AddVenueStates.waiting_phone)
async def add_venue_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=(message.text or "").strip())
    await state.set_state(AddVenueStates.waiting_instagram)
    await message.answer(
        "6/6. Введите ссылку на <b>Instagram</b> (или напишите «нет»):"
    )


@router.message(AddVenueStates.waiting_instagram)
async def add_venue_instagram(message: types.Message, state: FSMContext):
    insta = (message.text or "").strip()
    if insta.lower() in ("нет", "no", "не"):
        insta = ""

    data = await state.get_data()
    venue = add_venue(
        name=data["name"],
        category=data["category"],
        district=data["district"],
        address=data["address"],
        phone=data["phone"],
        instagram=insta,
    )

    await message.answer(
        "✅ Заведение добавлено!\n\n"
        f"ID: <b>{venue['id']}</b>\n"
        f"Название: <b>{venue['name']}</b>\n"
        f"Категория: {venue['category']}\n"
        f"Район: {venue['district']}\n"
        f"Адрес: {venue['address']}\n"
        f"Телефон: {venue['phone']}\n"
        f"Instagram: {venue['instagram'] or '—'}",
        reply_markup=main_menu_kb,
    )
    await state.clear()


# ---------- удаление заведения (по названию / списку) ----------

@router.callback_query(F.data == "admin:del_venue")
async def admin_del_venue_menu(callback: types.CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return

    venues = get_all_venues()
    if not venues:
        await callback.message.answer("Заведений в базе пока нет.")
        await callback.answer()
        return

    await callback.message.answer(
        "Выберите заведение, которое хотите удалить:",
        reply_markup=delete_venues_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_del_venue:"))
async def admin_delete_venue_cb(callback: types.CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return

    venue_id = int(callback.data.split(":", 1)[1])
    venue = get_venue_by_id(venue_id)
    ok = delete_venue(venue_id)
    if not ok:
        await callback.answer("Заведение не найдено.", show_alert=True)
        return

    name = venue.get("name") if venue else str(venue_id)
    await callback.message.answer(f"✅ Заведение «{name}» удалено.")
    await callback.answer()
