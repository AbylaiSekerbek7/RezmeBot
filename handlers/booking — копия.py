# handlers/booking.py
from datetime import datetime, date
import calendar as cal

from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards import main_menu_kb, phone_request_kb
from db import (
    create_booking,
    get_user_phone,
    update_user_phone,
    upsert_user,
)
from venues import (
    get_venues_by_category,
    get_venues_by_district,
    get_all_venues,
    get_districts,
    get_venue_by_id,
)
from config import get_settings

router = Router()


class BookingStates(StatesGroup):
    waiting_phone = State()
    choosing_mode = State()       # по категории / по району
    choosing_category = State()
    choosing_district = State()
    choosing_date = State()
    choosing_time = State()
    choosing_people = State()
    typing_comment = State()
    choosing_venue = State()      # выбор конкретного заведения


# ====== ВСПОМОГАТЕЛЬНЫЕ КЛАВИАТУРЫ ======


def booking_mode_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Выбрать категорию / вид заведения",
                    callback_data="mode:category",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Выбрать заведение по району",
                    callback_data="mode:district",
                )
            ],
        ]
    )


def categories_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Кафе/Рестораны",
                    callback_data="cat:Кафе/Рестораны",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Караоке",
                    callback_data="cat:Караоке",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Боулинг",
                    callback_data="cat:Боулинг",
                )
            ],
        ]
    )
    return kb


def districts_keyboard() -> InlineKeyboardMarkup:
    districts = get_districts()
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []

    for d in districts:
        row.append(
            InlineKeyboardButton(
                text=d,
                callback_data=f"district:{d}",
            )
        )
        if len(row) == 2:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    return InlineKeyboardMarkup(inline_keyboard=rows)


def venues_keyboard(venues: list[dict]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for v in venues:
        rows.append(
            [
                InlineKeyboardButton(
                    text=v["name"],
                    callback_data=f"venue:{v['id']}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _build_month_calendar(year: int, month: int) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = []

    month_name = datetime(year, month, 1).strftime("%b %Y")
    header_row = [
        InlineKeyboardButton(
            text="<",
            callback_data=f"cal:prev:{year}-{month:02d}",
        ),
        InlineKeyboardButton(
            text=month_name,
            callback_data="cal:ignore",
        ),
        InlineKeyboardButton(
            text=">",
            callback_data=f"cal:next:{year}-{month:02d}",
        ),
    ]
    keyboard.append(header_row)

    week_days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    keyboard.append(
        [
            InlineKeyboardButton(text=d, callback_data="cal:ignore")
            for d in week_days
        ]
    )

    cal_obj = cal.Calendar(firstweekday=0)
    for week in cal_obj.monthdayscalendar(year, month):
        row: list[InlineKeyboardButton] = []
        for day_num in week:
            if day_num == 0:
                row.append(
                    InlineKeyboardButton(
                        text=" ",
                        callback_data="cal:ignore",
                    )
                )
            else:
                d = date(year, month, day_num)
                row.append(
                    InlineKeyboardButton(
                        text=str(day_num),
                        callback_data=f"cal:day:{d.isoformat()}",
                    )
                )
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def _change_month(year: int, month: int, delta: int) -> tuple[int, int]:
    month += delta
    while month > 12:
        month -= 12
        year += 1
    while month < 1:
        month += 12
        year -= 1
    return year, month


def time_keyboard() -> InlineKeyboardMarkup:
    times = ["16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00"]
    buttons = []
    for t in times:
        buttons.append(
            InlineKeyboardButton(
                text=t,
                callback_data=f"time:{t}",
            )
        )
    rows = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def people_keyboard() -> InlineKeyboardMarkup:
    options = [1, 2, 3, 4, 5, 6]
    buttons = []
    for n in options:
        text = f"{n}" if n < 6 else "6+"
        buttons.append(
            InlineKeyboardButton(
                text=text,
                callback_data=f"people:{n}",
            )
        )
    rows = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ====== СТАРТ БРОНИ ======


@router.message(F.text == "🔔 Забронировать")
async def booking_start(message: types.Message, state: FSMContext):
    await state.clear()

    phone = await get_user_phone(message.from_user.id)
    if not phone:
        await state.set_state(BookingStates.waiting_phone)
        await message.answer(
            "📱 Перед бронированием отправьте, пожалуйста, номер телефона.\n\n"
            "Нажмите кнопку «📱 Отправить номер» ниже.",
            reply_markup=phone_request_kb,
        )
        return

    await state.set_state(BookingStates.choosing_mode)
    await message.answer(
        "Как будем подбирать заведение? 👇",
        reply_markup=booking_mode_keyboard(),
    )


# ====== ТЕЛЕФОН ======


@router.message(BookingStates.waiting_phone, F.contact)
async def phone_received(message: types.Message, state: FSMContext):
    contact = message.contact
    phone = contact.phone_number

    await update_user_phone(message.from_user.id, phone)
    await upsert_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        phone=phone,
    )

    await message.answer(
        "Спасибо! Сохранил ваш номер телефона ✅",
        reply_markup=main_menu_kb,
    )

    await state.set_state(BookingStates.choosing_mode)
    await message.answer(
        "Теперь выберите, как будем подбирать заведение 👇",
        reply_markup=booking_mode_keyboard(),
    )


@router.message(BookingStates.waiting_phone)
async def phone_waiting_wrong(message: types.Message, state: FSMContext):
    await message.answer(
        "Пожалуйста, нажмите кнопку «📱 Отправить номер» ниже 🙂",
        reply_markup=phone_request_kb,
    )


# ====== РЕЖИМ: КАТЕГОРИЯ / РАЙОН ======


@router.callback_query(BookingStates.choosing_mode, F.data == "mode:category")
async def mode_category(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(mode="category")
    await state.set_state(BookingStates.choosing_category)
    await callback.answer()
    await callback.message.edit_text(
        "Выберите категорию / вид заведения 👇",
        reply_markup=categories_keyboard(),
    )


@router.callback_query(BookingStates.choosing_mode, F.data == "mode:district")
async def mode_district(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(mode="district")
    await state.set_state(BookingStates.choosing_district)
    await callback.answer()
    await callback.message.edit_text(
        "Выберите район 👇",
        reply_markup=districts_keyboard(),
    )


# ====== ВЫБОР КАТЕГОРИИ / РАЙОНА ======


@router.callback_query(BookingStates.choosing_category, F.data.startswith("cat:"))
async def category_chosen(callback: types.CallbackQuery, state: FSMContext):
    category = callback.data.split(":", 1)[1]
    await state.update_data(category=category)

    today = date.today()
    await callback.answer()
    await callback.message.edit_text(
        f"Категория: <b>{category}</b>\n\nВыберите дату:",
        reply_markup=_build_month_calendar(today.year, today.month),
    )

    await state.set_state(BookingStates.choosing_date)


@router.callback_query(BookingStates.choosing_district, F.data.startswith("district:"))
async def district_chosen(callback: types.CallbackQuery, state: FSMContext):
    district = callback.data.split(":", 1)[1]
    await state.update_data(district=district)

    today = date.today()
    await callback.answer()
    await callback.message.edit_text(
        f"Район: <b>{district}</b>\n\nВыберите дату:",
        reply_markup=_build_month_calendar(today.year, today.month),
    )

    await state.set_state(BookingStates.choosing_date)


# ====== КАЛЕНДАРЬ ======


@router.callback_query(BookingStates.choosing_date, F.data.startswith("cal:prev:"))
async def calendar_prev(callback: types.CallbackQuery, state: FSMContext):
    _, _, ym = callback.data.split(":", 2)
    year, month = map(int, ym.split("-"))
    year, month = _change_month(year, month, -1)

    await callback.answer()
    await callback.message.edit_text(
        "Выберите дату:",
        reply_markup=_build_month_calendar(year, month),
    )


@router.callback_query(BookingStates.choosing_date, F.data.startswith("cal:next:"))
async def calendar_next(callback: types.CallbackQuery, state: FSMContext):
    _, _, ym = callback.data.split(":", 2)
    year, month = map(int, ym.split("-"))
    year, month = _change_month(year, month, +1)

    await callback.answer()
    await callback.message.edit_text(
        "Выберите дату:",
        reply_markup=_build_month_calendar(year, month),
    )


@router.callback_query(BookingStates.choosing_date, F.data == "cal:ignore")
async def calendar_ignore(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()


@router.callback_query(BookingStates.choosing_date, F.data.startswith("cal:day:"))
async def date_chosen(callback: types.CallbackQuery, state: FSMContext):
    date_iso = callback.data.split(":", 2)[2]
    date_obj = date.fromisoformat(date_iso)
    today = date.today()

    if date_obj < today:
        await callback.answer("❌ Нельзя выбрать прошедшую дату", show_alert=True)
        return

    date_human = date_obj.strftime("%d.%m.%Y")
    await state.update_data(date=date_iso)

    await callback.answer()
    await callback.message.edit_text(
        f"Дата: <b>{date_human}</b> ✅\n\nТеперь выбери время:",
        reply_markup=time_keyboard(),
    )

    await state.set_state(BookingStates.choosing_time)


# ====== ВРЕМЯ / ЛЮДИ / КОММЕНТ ======


@router.callback_query(BookingStates.choosing_time, F.data.startswith("time:"))
async def time_chosen(callback: types.CallbackQuery, state: FSMContext):
    time_str = callback.data.split(":", 1)[1]
    await state.update_data(time=time_str)

    await callback.answer()
    await callback.message.edit_text(
        f"Время: <b>{time_str}</b> ✅\n\nСколько человек будет?",
        reply_markup=people_keyboard(),
    )

    await state.set_state(BookingStates.choosing_people)


@router.callback_query(BookingStates.choosing_people, F.data.startswith("people:"))
async def people_chosen(callback: types.CallbackQuery, state: FSMContext):
    people = int(callback.data.split(":", 1)[1])
    await state.update_data(people=people)

    await callback.answer()
    await callback.message.edit_text(
        f"Количество человек: <b>{people if people < 6 else '6+'}</b> ✅\n\n"
        "Напиши, пожалуйста, комментарий к брони "
        "(повод, бюджет, предпочтения). Если без комментариев — напиши «нет».",
    )

    await state.set_state(BookingStates.typing_comment)


@router.message(BookingStates.typing_comment)
async def comment_received(message: types.Message, state: FSMContext):
    comment = (message.text or "").strip()
    if comment.lower() in ("нет", "no", "не", "без комментариев"):
        comment = ""

    data = await state.get_data()
    mode = data.get("mode")
    category = data.get("category")
    district = data.get("district")

    # сохраняем коммент в состоянии
    await state.update_data(comment=comment)

    # подбираем заведения
    if mode == "category" and category:
        venues = get_venues_by_category(category)
    elif mode == "district" and district:
        venues = get_venues_by_district(district)
    else:
        venues = []

    if not venues:
        await message.answer(
            "Пока нет заведений по выбранным параметрам 😔\n"
            "Мы всё равно свяжемся с вами при появлении подходящих вариантов.",
            reply_markup=main_menu_kb,
        )
        await state.clear()
        return

    # показываем список и просим выбрать конкретное заведение
    venues_text_parts = []
    for i, v in enumerate(venues, start=1):
        part = (
            f"{i}️⃣ <b>{v['name']}</b>\n"
            f"Категория: {v['category']}\n"
            f"Район: {v['district']}\n"
            f"📍 {v['address']}\n"
            f"📞 {v['phone']}"
        )
        if v.get("instagram"):
            part += f"\n🔗 {v['instagram']}"
        venues_text_parts.append(part)

    venues_text = "\n\n".join(venues_text_parts)

    await message.answer(
        "Варианты заведений:\n\n"
        f"{venues_text}\n\n"
        "Теперь выберите, для какого заведения оформить бронь 👇",
        reply_markup=venues_keyboard(venues),
    )

    await state.set_state(BookingStates.choosing_venue)


# ====== ВЫБОР КОНКРЕТНОГО ЗАВЕДЕНИЯ ======


@router.callback_query(BookingStates.choosing_venue, F.data.startswith("venue:"))
async def venue_chosen(callback: types.CallbackQuery, state: FSMContext):
    venue_id = int(callback.data.split(":", 1)[1])
    venue = get_venue_by_id(venue_id)
    if not venue:
        await callback.answer("Не удалось найти заведение", show_alert=True)
        return

    data = await state.get_data()
    mode = data.get("mode")
    category = data.get("category")
    district = data.get("district")
    date_iso = data["date"]
    time_str = data["time"]
    people = data["people"]
    comment = data.get("comment", "")

    date_obj = date.fromisoformat(date_iso)
    date_human = date_obj.strftime("%d.%m.%Y")

    # строка фильтра
    if mode == "category" and category:
        filter_line = f"• Тип заведения: <b>{category}</b>\n"
        booking_category = category
    elif mode == "district" and district:
        filter_line = f"• Район: <b>{district}</b>\n"
        booking_category = f"Район: {district}"
    else:
        filter_line = ""
        booking_category = venue["category"]

    # сохраняем бронь в БД
    await create_booking(
        tg_id=callback.from_user.id,
        venue_id=venue_id,
        category=booking_category,
        date=date_iso,
        time=time_str,
        people_count=people,
        comment=comment,
    )

    confirm_text = (
        "✅ Ваша заявка на бронь принята!\n\n"
        f"{filter_line}"
        f"• Заведение: <b>{venue['name']}</b>\n"
        f"• Дата: <b>{date_human}</b>\n"
        f"• Время: <b>{time_str}</b>\n"
        f"• Количество человек: <b>{people if people < 6 else '6+'}</b>\n"
        f"• Комментарий: <b>{comment or 'без комментариев'}</b>\n\n"
        "Мы свяжемся с заведением и сообщим вам о подтверждении.\n"
    )

    await callback.answer()
    await callback.message.edit_text(confirm_text)
    await callback.message.answer("Можете вернуться в меню 👇", reply_markup=main_menu_kb)
    await state.clear()

    # уведомление админу
    settings = get_settings()
    if settings.admin_id:
        phone = await get_user_phone(callback.from_user.id)
        admin_text = (
            "🔔 Новая заявка на бронь\n\n"
            f"Пользователь: @{callback.from_user.username or 'без юзернейма'} "
            f"({callback.from_user.id})\n"
            f"Имя: {callback.from_user.full_name}\n"
            f"Телефон: {phone or 'не указан'}\n\n"
            f"{filter_line.replace('• ', '')}"
            f"Заведение: {venue['name']}\n"
            f"Дата: {date_human}\n"
            f"Время: {time_str}\n"
            f"Людей: {people if people < 6 else '6+'}\n"
            f"Комментарий: {comment or 'без комментариев'}\n"
        )
        await callback.message.bot.send_message(settings.admin_id, admin_text)


# ====== «ВСЕ ЗАВЕДЕНИЯ» ======


@router.message(F.text == "📍 Все заведения")
async def all_venues_handler(message: types.Message):
    venues = get_all_venues()
    if not venues:
        await message.answer("Пока нет заведений в базе 🙂")
        return

    parts = []
    for i, v in enumerate(venues, start=1):
        part = (
            f"{i}️⃣ <b>{v['name']}</b>\n"
            f"Категория: {v['category']}\n"
            f"Район: {v['district']}\n"
            f"📍 {v['address']}\n"
            f"📞 {v['phone']}"
        )
        if v.get("instagram"):
            part += f"\n🔗 {v['instagram']}"
        parts.append(part)

    text = "Список заведений в нашей базе:\n\n" + "\n\n".join(parts)
    await message.answer(text)
