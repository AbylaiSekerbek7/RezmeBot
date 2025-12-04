from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔔 Забронировать")],
        [KeyboardButton(text="📍 Все заведения")],
        [KeyboardButton(text="✍️ Оставить отзыв")],
        [KeyboardButton(text="Для бизнесов (Если вы хотите добавить свое заведение в нашу базу)")],
        [KeyboardButton(text="Новости и обновления"), KeyboardButton(text="Наш Instagram")],
        [KeyboardButton(text="Связаться с ИИ-помощником")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие из меню 👇",
)

phone_request_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📱 Отправить номер", request_contact=True
            )
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Нажмите кнопку, чтобы отправить номер",
)
