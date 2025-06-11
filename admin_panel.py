import sqlite3
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

DB_PATH = "users.db"

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total = cur.fetchone()[0]

    today = datetime.now().date()
    cur.execute("SELECT COUNT(*) FROM users WHERE date(created_at) = ?", (today,))
    today_count = cur.fetchone()[0]

    week_ago = today - timedelta(days=7)
    cur.execute("SELECT COUNT(*) FROM users WHERE date(created_at) >= ?", (week_ago,))
    week_count = cur.fetchone()[0]

    month_ago = today - timedelta(days=30)
    cur.execute("SELECT COUNT(*) FROM users WHERE date(created_at) >= ?", (month_ago,))
    month_count = cur.fetchone()[0]

    conn.close()

    return total, today_count, week_count, month_count

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total, today, week, month = get_stats()
    await update.message.reply_text(
        f"""📊 Статистика:
👥 Пользователей всего: {total}
📅 Сегодня: {today}
📈 За неделю: {week}
🗓️ За месяц: {month}"""
    )

def setup_admin_handlers(app):
    app.add_handler(CommandHandler("admin", show_admin_panel))
