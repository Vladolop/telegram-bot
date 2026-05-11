import random
import logging
import json
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==============================
# НАЛАШТУВАННЯ
# ==============================
BOT_TOKEN = "8751213088:AAHHhEa5CoTcxjPDIuA-0FtX3zAsH3TzBzA"
SAVE_FILE = "messages.json"  # файл де зберігаються повідомлення

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ==============================
# ЗАВАНТАЖЕННЯ / ЗБЕРЕЖЕННЯ
# ==============================
def load_messages():
    """Завантажує повідомлення з файлу при старті."""
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_messages(messages):
    """Зберігає повідомлення у файл."""
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

# Завантажуємо при старті програми
saved_messages = load_messages()

# ==============================
# КОМАНДИ
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привіт! Я запам'ятовую всі повідомлення у цьому чаті.\n\n"
        "📌 Команди:\n"
        "/rand_msg — переслати випадкове повідомлення\n"
        "/count — скільки повідомлень збережено\n"
        "/clear — очистити всі збережені повідомлення"
    )

async def rand_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пересилає випадкове збережене повідомлення."""
    if not saved_messages:
        await update.message.reply_text(
            "😅 Ще немає жодного збереженого повідомлення. Поспілкуйтесь трохи!"
        )
        return

    # Вибираємо випадкове збережене повідомлення
    msg = random.choice(saved_messages)
    chat_id = msg["chat_id"]
    message_id = msg["message_id"]

    try:
        # Пересилаємо оригінальне повідомлення (як forward)
        await context.bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=chat_id,
            message_id=message_id
        )
    except Exception:
        # Якщо повідомлення вже видалено — прибираємо з списку
        saved_messages.remove(msg)
        save_messages(saved_messages)
        await update.message.reply_text(
            "⚠️ Це повідомлення було видалено. Спробуй ще раз /rand_msg"
        )

async def count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показує кількість збережених повідомлень."""
    n = len(saved_messages)
    await update.message.reply_text(f"📊 Збережено повідомлень: {n}")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очищає всі збережені повідомлення."""
    global saved_messages
    saved_messages = []
    save_messages(saved_messages)
    await update.message.reply_text("🗑️ Всі повідомлення очищено.")
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 Бот працює!")

# ==============================
# ЗБЕРЕЖЕННЯ ПОВІДОМЛЕНЬ
# ==============================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Зберігає кожне повідомлення з чату."""
    msg = update.message
    if not msg:
        return

    # Зберігаємо chat_id і message_id — цього достатньо для пересилання
    entry = {
        "chat_id": msg.chat_id,
        "message_id": msg.message_id,
    }

    saved_messages.append(entry)
    save_messages(saved_messages)  # одразу пишемо у файл
    logging.info(f"Збережено: chat={msg.chat_id} msg={msg.message_id}")

# ==============================
# ЗАПУСК
# ==============================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rand_msg", rand_msg))
    app.add_handler(CommandHandler("count", count))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("ping", ping))

    # Зберігає всі типи повідомлень: текст, фото, стікери, гіфки тощо
    app.add_handler(MessageHandler(
        filters.ALL & ~filters.COMMAND,
        handle_message
    ))

    print("✅ Бот запущений! Ctrl+C щоб зупинити.")
    app.run_polling()

if __name__ == "__main__":
    main()