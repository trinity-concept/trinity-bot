import os
import logging
import httpx
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import anthropic

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY,
    http_client=httpx.Client()
)

SYSTEM_PROMPT = (
    "You are an experienced sales manager for TRINITY CONCEPT jewelry brand. "
    "You ALWAYS respond in TWO languages: first English, then Russian. "
    "Separate them with a blank line. "
    "BRAND VOICE: warm, sensual, no pressure. Short phrases. Every message ends with a question. "
    "No long dashes. Never write: what caught your eye, what resonates. "
    "Instead write: what drew your eye, what feels closer right now, which crystal draws you in. "
    "Address as you/ty. Use emojis 🤍 💎 ✨ moderately. "
    "RULES: Send catalog only if asked. Name price only after client chose crystal and shape. "
    "Always mention constructor: https://trinityconstructor.netlify.app "
    "Always mention pieces are transformers worn multiple ways. "
    "CRYSTALS: Amethyst(inner voice), Green amethyst(acceptance), Rose quartz(self-love), "
    "Citrine(confidence), Sky Blue Topaz(freedom), Swiss Blue Topaz(voice power), "
    "Smoky quartz(grounding). Sky Blue lighter. Swiss Blue deeper. "
    "SHAPES: Trillion/Treugolnik, Pear/Kaplya, Heart/Serdtse, Oval, Cushion/Kushon. "
    "SIZES: S 9mm from 199, M 13mm from 325, L 16mm from 450. "
    "Base Dubai, shipping separate, drop June, website in development. "
    "NEVER leave message without question."
)

user_histories = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Trinity Sales Assistant 🤍\n\n"
        "Пришли сообщение клиента — отвечу скриптом на EN и RU.\n\n"
        "/new — новый клиент\n"
        "/help — помощь"
    )


async def new_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_histories[update.effective_user.id] = []
    await update.message.reply_text("Новый диалог начат!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "1. Пришли сообщение клиента\n"
        "2. Получи скрипт на EN и RU\n"
        "3. /new — новый клиент"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append({
        "role": "user",
        "content": update.message.text
    })

    if len(user_histories[user_id]) > 20:
        user_histories[user_id] = user_histories[user_id][-20:]

    thinking = await update.message.reply_text("Составляю ответ...")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=user_histories[user_id]
        )
        reply = response.content[0].text
        user_histories[user_id].append({
            "role": "assistant",
            "content": reply
        })
        await thinking.delete()
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Error: {e}")
        await thinking.edit_text(f"Ошибка: {str(e)}")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new", new_conversation))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot started!")
    app.run_polling()


if __name__ == "__main__":
    main()
