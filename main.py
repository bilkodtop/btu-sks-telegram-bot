import getmenu
import scrape
from model import Models
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram import Update
import logging
import datetime
import os
import time
import requests

try:
  menuList = getmenu.Menu().getFormattedMenu()
except:
  scrape.ScrapeMenu().getPdf()
  menuList = getmenu.Menu().getFormattedMenu()

Token = "6831215537:AAG3Ha42FvltfW0epXagBj7q8Z-7OsWpKBE"

models = Models()
models.create_table()


logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  level=logging.INFO
)

async def getMenu(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if context.args == []:
     userInput = datetime.datetime.now().day
  else:
     userInput = context.args[0]
  if (int(userInput) > 0):
      daysMenu = menuList[int(userInput)-1]
      await context.bot.send_message(chat_id=update.effective_chat.id, text = daysMenu)
  info = update.message
  messages_to_add(info)

async def yemekhane(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user = update.message.from_user
  print('You talk with user {} and his user ID: {} and his name is {}'.format(
    user['username'], user['id'], user['first_name']))
  reply_text = """
    /menu gün -> girdiğiniz günün menüsünü görebilirsiniz, gün girmezseniz içinde olduğunuz günün menüsünü görebilirsiniz.\n\n/abonelik  -> botumuzda abonelik başlatarak her gün saat 09.00'da botumuzdan menüyü telegram'dan özel mesaj olarak alabilirsiniz.(Sadece /abonelik yazarak günlük mesaj alamazsınız botun kendisine tıklayıp mesajlaşma başlatmanız gerekmektedir)\n\n/abonelikiptal -> aboneliğinizi iptal eder.
    """
  await context.bot.send_message(chat_id=update.effective_chat.id, text = reply_text)
  info = update.message
  messages_to_add(info)
   
async def restartEveryDay():
  global menuList, date
  os.system("rm pdf0.pdf")
  time.sleep(1)
  scrape.ScrapeMenu().getPdf()
  menuList = getmenu.Menu().getFormattedMenu()   

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text2 = "Bursa Teknik Üniversitesi Yemekhane Telegram botuna hoşgeldiniz. /help yazarak komutlara erişebilirsiniz.!"
  await context.bot.send_message(chat_id=update.effective_chat.id, text = text2)
  info = update.message
  messages_to_add(info)  

async def duyurular(update: Update, context: ContextTypes.DEFAULT_TYPE):
  admin_id = update.effective_user.id
  admin_list = os.getenv("ADMIN_LIST")

  if admin_id in admin_list:
    await context.bot.send_message(chat_id=update.effective_chat.id, text = "Duyuru yapmak için /duyuru <mesaj> komutunu kullanın")
  else:
    await context.bot.send_message(chat_id=update.effective_chat.id, text = "Bu komutu kullanmaya yetkiniz yok")

def sendDaysMenu(context: ContextTypes.DEFAULT_TYPE):
  kayitliKisiListesi = models.check_all()
  userInput = datetime.datetime.now().day
  daysDate = (date[int(userInput)] + " Tarihli Günün Menüsü")
  daysMenu = menuList[int(userInput)]
  daysMenuText = daysDate + "\n" + daysMenu

  for eachPerson in range(len(kayitliKisiListesi)):
    telegramId = kayitliKisiListesi[eachPerson][0]
    try:
      url = f"https://api.telegram.org/bot{Token}/sendMessage?chat_id={telegramId}&text={daysMenuText}"
      requests.get(url).json()
    except:
      print(f"{telegramId} abone olmus ama yetki vermemis")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user = update.message.from_user
  print('You talk with user {} and his user ID: {} and his name is {}'.format(
    user['username'], user['id'], user['first_name']))
  message = """
    /menu gün -> girdiğiniz günün menüsünü görebilirsiniz, gün girmezseniz içinde olduğunuz günün menüsünü görebilirsiniz.\n\n/abonelik  -> botumuzda abonelik başlatarak her gün saat 09.00'da botumuzdan menüyü telegram'dan özel mesaj olarak alabilirsiniz.(Sadece /abonelik yazarak günlük mesaj alamazsınız botun kendisine tıklayıp mesajlaşma başlatmanız gerekmektedir)\n\n/abonelikiptal -> aboneliğinizi iptal eder.
    """
  await context.bot.send_message(chat_id=update.effective_chat.id, text = message)
  info = update.message
  messages_to_add(info)

def messages_to_add(info):
  user = info.from_user
  first_name = user["first_name"]
  last_name = user["last_name"]
  telegramId = user["id"]
  message = info.text
  models.add_message(telegramId, first_name, last_name, message)


if __name__ == '__main__':
    application = ApplicationBuilder().token(Token).build()
    menu_handler = CommandHandler('menu', getMenu)
    start_handler = CommandHandler('start', start)
    yemekhane_handler = CommandHandler('yemekhane', yemekhane)
    help_handler = CommandHandler('help', help)
 
    application.add_handler(start_handler)
    application.add_handler(menu_handler)
    application.add_handler(yemekhane_handler)
    application.add_handler(help_handler)

    application.run_polling()
