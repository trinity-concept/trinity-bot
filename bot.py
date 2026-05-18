import os,logging
from telegram import Update
from telegram.ext import Application,MessageHandler,CommandHandler,filters,ContextTypes
import anthropic
TELEGRAM_TOKEN=os.environ.get('TELEGRAM_TOKEN','')
ANTHROPIC_API_KEY=os.environ.get('ANTHROPIC_API_KEY','')
logging.basicConfig(level=logging.INFO)
client=anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
P="""Ты менеджер продаж TRINITY CONCEPT. Отвечаешь EN потом RU. Голос теплый без давления, каждый ответ заканчивается вопросом. Без тире. Писать: что притянуло взгляд, что ближе прямо сейчас, какой камень притягивает. Конструктор: https://trinityconstructor.netlify.app — упоминать всегда. Цену только после выбора камня и формы. Каталог только если просят. Камни: Аметист(внутренний голос), Зеленый аметист(принятие), Розовый кварц(любовь к себе), Цитрин(уверенность), Sky Blue Topaz(свобода), Swiss Blue Topaz(сила голоса), Дымчатый кварц(заземление). Sky Blue светлее, Swiss Blue глубже. Формы: Trillion/Треугольник Pear/Капля Heart/Сердце Oval/Овал Cushion/Кушон. Размеры: S 9мм от 199 M 13мм от 325 L 16мм от 450. База Дубай, доставка отдельно, дроп июнь."""
H={}
async def start(u,c):await u.message.reply_text("Trinity Sales Bot\nПришли сообщение клиента - отвечу скриптом EN+RU\n/new - новый клиент")
async def new_conv(u,c):H[u.effective_user.id]=[];await u.message.reply_text("Новый диалог!")
async def msg(u,c):
 i=u.effective_user.id
 if i not in H:H[i]=[]
 H[i].append({"role":"user","content":u.message.text})
 if len(H[i])>20:H[i]=H[i][-20:]
 t=await u.message.reply_text("Составляю ответ...")
 try:
  r=client.messages.create(model="claude-sonnet-4-20250514",max_tokens=1500,system=P,messages=H[i])
  reply=r.content[0].text
  H[i].append({"role":"assistant","content":reply})
  await t.delete()
  await u.message.reply_text(reply)
 except Exception as e:await t.edit_text(f"Ошибка: {e}")
def main():
 app=Application.builder().token(TELEGRAM_TOKEN).build()
 app.add_handler(CommandHandler("start",start))
 app.add_handler(CommandHandler("new",new_conv))
 app.add_handler(MessageHandler(filters.TEXT&~filters.COMMAND,msg))
 app.run_polling()
if __name__=="__main__":main()
