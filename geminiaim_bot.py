
def action_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✍️ Спросить", callback_data="ask_gpt")],
        [InlineKeyboardButton("🖼 Картинка", callback_data="gen_image")],
        [InlineKeyboardButton("📜 История", callback_data="show_history")],
        [InlineKeyboardButton("💳 Купить подписку $1", url="https://t.me/send?start=IVUYDUSQ5khw")]
    ])
