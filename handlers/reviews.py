# handlers/reviews.py
from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards import main_menu_kb
from db import (
    get_user_venue_ids,
    user_has_booking_for_venue,
    add_review,
)
from venues import get_venue_by_id

router = Router()


class ReviewStates(StatesGroup):
    choosing_venue = State()
    choosing_rating = State()
    typing_text = State()


def _venues_for_review_keyboard(venue_ids: list[int]) -> InlineKeyboardMarkup:
    buttons = []
    for vid in venue_ids:
        v = get_venue_by_id(vid)
        if not v:
            continue
        buttons.append(
            [InlineKeyboardButton(text=v["name"], callback_data=f"rev_venue:{vid}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def _rating_keyboard() -> InlineKeyboardMarkup:
    row = [
        InlineKeyboardButton(text="⭐️1", callback_data="rev_rate:1"),
        InlineKeyboardButton(text="⭐️2", callback_data="rev_rate:2"),
        InlineKeyboardButton(text="⭐️3", callback_data="rev_rate:3"),
        InlineKeyboardButton(text="⭐️4", callback_data="rev_rate:4"),
        InlineKeyboardButton(text="⭐️5", callback_data="rev_rate:5"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[row])


@router.message(F.text == "✍️ Оставить отзыв")
async def review_start(message: types.Message, state: FSMContext):
    venue_ids = await get_user_venue_ids(message.from_user.id)
    if not venue_ids:
        await message.answer(
            "У вас пока нет броней в наших заведениях, "
            "поэтому оставить отзыв нельзя 🙂",
            reply_markup=main_menu_kb,
        )
        await state.clear()
        return

    await state.set_state(ReviewStates.choosing_venue)
    await message.answer(
        "Выберите заведение, о котором хотите оставить отзыв 👇",
        reply_markup=_venues_for_review_keyboard(venue_ids),
    )


@router.callback_query(ReviewStates.choosing_venue, F.data.startswith("rev_venue:"))
async def review_venue_chosen(callback: types.CallbackQuery, state: FSMContext):
    venue_id = int(callback.data.split(":", 1)[1])
    venue = get_venue_by_id(venue_id)
    if not venue:
        await callback.answer("Заведение не найдено", show_alert=True)
        return

    # на всякий случай ещё раз проверим право
    has_booking = await user_has_booking_for_venue(callback.from_user.id, venue_id)
    if not has_booking:
        await callback.answer(
            "У вас не было брони в этом заведении, отзыв оставить нельзя.",
            show_alert=True,
        )
        return

    await state.update_data(venue_id=venue_id)
    await state.set_state(ReviewStates.choosing_rating)

    await callback.answer()
    await callback.message.edit_text(
        f"Заведение: <b>{venue['name']}</b>\n\n"
        "Поставьте, пожалуйста, оценку от 1 до 5 ⭐️",
        reply_markup=_rating_keyboard(),
    )


@router.callback_query(ReviewStates.choosing_rating, F.data.startswith("rev_rate:"))
async def review_rating_chosen(callback: types.CallbackQuery, state: FSMContext):
    rating = int(callback.data.split(":", 1)[1])
    await state.update_data(rating=rating)

    await callback.answer()
    await callback.message.edit_text(
        f"Оценка: <b>{rating}⭐️</b>\n\n"
        "Теперь напишите ваш отзыв текстом.\n"
        "Если хотите оставить только оценку — напишите «нет».",
    )

    await state.set_state(ReviewStates.typing_text)


@router.message(ReviewStates.typing_text)
async def review_text_received(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()
    if text.lower() in ("нет", "no", "не", "без комментариев"):
        text = ""

    data = await state.get_data()
    venue_id = data["venue_id"]
    rating = data["rating"]

    venue = get_venue_by_id(venue_id)
    if not venue:
        await message.answer("Ошибка: заведение не найдено.", reply_markup=main_menu_kb)
        await state.clear()
        return

    await add_review(
        tg_id=message.from_user.id,
        venue_id=venue_id,
        rating=rating,
        text=text,
    )

    await message.answer(
        "Спасибо! Ваш отзыв сохранён 🙌\n\n"
        f"Заведение: <b>{venue['name']}</b>\n"
        f"Оценка: <b>{rating}⭐️</b>\n"
        f"Отзыв: <b>{text or 'без текста'}</b>",
        reply_markup=main_menu_kb,
    )
    await state.clear()
