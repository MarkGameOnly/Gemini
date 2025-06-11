import sqlite3
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

ADMINS = [1082828397]  # Список ID админов

DB_PATH = "payments.db"

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM payments WHERE date(date) = ?", (today,))
    daily_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM payments WHERE date(date) >= ?", (week_ago,))
    weekly_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM payments WHERE date(date) >= ?", (month_ago,))
    monthly_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM payments")
    total_payments = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(amount) FROM payments")
    total_revenue = cursor.fetchone()[0] or 0

    conn.close()
    return daily_users, weekly_users, monthly_users, total_payments, total_revenue


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        return await update.message.reply_text("❌ У вас нет доступа.")

    daily, weekly, monthly, total, revenue = get_stats()

    text = (
        f"📊 Статистика:
"
        f"👥 За день: {daily} пользователей
"
        f"📆 За неделю: {weekly}
"
        f"🗓 За месяц: {monthly}
"
        f"💳 Всего оплат: {total}
"
        f"💰 Общая выручка: ${revenue:.2f}"
    )
    await update.message.reply_text(text)

def setup_admin_handlers(app):
    app.add_handler(CommandHandler("stats", admin_stats))
