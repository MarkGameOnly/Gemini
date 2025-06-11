
import asyncio
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, CallbackQueryHandler, filters
)

# --- Загрузка .env ---
load_dotenv()

# --- Переменные ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FREE_LIMIT = 10
ADMINS = [1082828397]

# --- Инициализация ---
logging.basicConfig(level=logging.INFO)
user_usage = {}
user_history = {}
subscribed_users = set()
client = OpenAI(api_key=OPENAI_API_KEY)

# --- Подписка ---
def is_subscribed(user_id):
    return user_id in ADMINS or user_id in subscribed_users

# --- Функции ---
def check_user_access(user_id):
    return is_subscribed(user_id) or user_usage.get(user_id, 0) < FREE_LIMIT

def track_usage(user_id):
    user_usage[user_id] = user_usage.get(user_id, 0) + 1

def add_to_history(user_id, action):
    if user_id not in user_history:
        user_history[user_id] = []
    user_history[user_id].append(f"[{datetime.now().strftime('%H:%M:%S')}] {action}")

def action_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✍️ Спросить", callback_data="ask_gpt")],
        [InlineKeyboardButton("🖼 Картинка", callback_data="gen_image")],
        [InlineKeyboardButton("📜 История", callback_data="show_history")]
    ])

def generate_image(prompt="futuristic AI assistant with glowing circuits, 8k, ultra-detailed"):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        return response.data[0].url
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return f"❌ Ошибка генерации изображения: {e}"

def ask_chatgpt(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Gemini, a friendly AI assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Ошибка общения с Gemini: {e}"

# --- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Добро пожаловать в Gemini AI Assistant!

Я помогу тебе с вопросами, идеями и изображениями.",
        reply_markup=action_buttons()
    )

# --- Обработка кнопок ---
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "ask_gpt":
        await query.message.reply_text("✍️ Напиши свой вопрос для Gemini:")
        context.user_data["awaiting_gpt"] = True

    elif query.data == "gen_image":
        if not check_user_access(user_id):
            await query.message.reply_text("🔒 Лимит генераций исчерпан или отсутствует подписка.")
            return
        prompt = "futuristic robot standing in neon city, artstation, ultra-detailed"
        url = generate_image(prompt)
        track_usage(user_id)
        add_to_history(user_id, "🖼 Картинка")
        if url.startswith("http"):
            await query.message.reply_photo(url, caption="🖼 Картинка от Gemini")
        else:
            await query.message.reply_text(url)

    elif query.data == "show_history":
        hist = user_history.get(user_id, [])
        if hist:
            await query.message.reply_text("📜 История:
" + "\n".join(hist))
        else:
            await query.message.reply_text("История пуста.")

# --- Текстовые сообщения ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.user_data.get("awaiting_gpt"):
        prompt = update.message.text
        if not check_user_access(user_id):
            await update.message.reply_text("🔒 Лимит исчерпан или нет подписки.")
            return
        result = ask_chatgpt(prompt)
        track_usage(user_id)
        add_to_history(user_id, f"✍️ Запрос: {prompt}")
        await update.message.reply_text(result)
        context.user_data["awaiting_gpt"] = False
    else:
        await update.message.reply_text("Нажми /start чтобы начать общение с Gemini")

# --- Запуск ---
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    from admin_panel import setup_admin_handlers
    setup_admin_handlers(app)

    print("🤖 Gemini ассистент запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
