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

SYSTEM_PROMPT = """Ty menedzher prodazh TRINITY CONCEPT. Otvechaesh EN potom RU. Golos tyoplyy bez davleniya, kazhdyy otvet zakanchivaetsya voprosom. Bez tire. Konstruktor: https://trinityconstructor.netlify.app upominat vsegda. Tsenu tolko posle vybora kamnya i formy. Katalog tolko esli prosyat. Kamni: Ametist(vnutrenniy golos), Zelenyy ametist(prinyatie), Rozovyy kvarts(lyubov k sebe), Tsitrin(uverennost), Sky Blue Topaz(svoboda), Swiss Blue Topaz(sila golosa), Dymchatyy kvarts(zazemlenie). Sky Blue svetlee. Swiss Blue glubzhe. Formy: Trillion Pear Heart Oval Cushion. Razmery S 9mm ot 199, M 13mm ot 325, L 16mm ot 450. Baza Dubai, dostavka otdelno, drop iyun."""

user_histories = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Trinity Sales Bot\nPrishli soobshchenie klienta - otvecyu skriptom EN i RU.\n/new - novyy klient")


async def new_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_histories[update.effective_user.id] = []
    await update.message.reply_text("Novyy dialog nachat!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_histories:
        user_histories[user_id] = []
    user_histories[user_id].append({"role": "user", "content": update.message.text})
    if len(user_histories[user_id]) > 20:
        user_histories[user_id] = user_histories[user_id][-20:]
    thinking = await update.message.reply_text("Sostavlyayu otvet...")
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=user_histories[user_id]
        )
        reply = response.content[0].text
        user_histories[user_id].append({"role": "assistant", "content": reply})
        await thinking.delete()
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Error: {e}")
        await thinking.edit_text(f"Oshibka: {str(e)}")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new", new_conversation))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot started!")
    app.run_polling()


if __name__ == "__main__":
    main()
