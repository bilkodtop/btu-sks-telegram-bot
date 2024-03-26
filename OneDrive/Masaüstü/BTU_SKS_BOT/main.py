import getmenu
import scrape
from model import Models
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackContext
from telegram import Update
import logging
import datetime
import os
from datetime import time
import requests
import dotenv
dotenv.load_dotenv()

try:
  menuList = getmenu.Menu().getFormattedMenu()
except:
  scrape.ScrapeMenu().getPdf()
  menuList = getmenu.Menu().getFormattedMenu()

Token = os.getenv("TOKEN")

models = Models()
models.create_table()

logging.basicConfig(
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  level=logging.INFO
)

def restartEveryDay():
  global menuList
  os.system("rm pdf0.pdf")
  time.sleep(1)
  scrape.ScrapeMenu().getPdf()
  menuList = getmenu.Menu().getFormattedMenu()

def callbackRestartEveryday(context: CallbackContext):
  timer = time(hour=6, minute=0)
  context.job_queue.run_daily(restartEveryDay, timer, days=(0,1,2,3,4,5,6))
                              
async def getMenu(update: Update, context: ContextTypes.DEFAULT_TYPE):
  try:
    if context.args == []:
      userInput = datetime.datetime.now().day
    else:
      userInput = context.args[0]
    if (int(userInput) > 0):
        daysMenu = menuList[int(userInput)-1]
        lines = daysMenu.split("\n")
        formattedDaysMenu = f"{lines[0]} - {lines[1]}\n" + "\n".join(lines[2:])
        daysMenuText = formattedDaysMenu
        await context.bot.send_message(chat_id=update.effective_chat.id, text = daysMenuText)
  except(IndexError, ValueError):
    await context.bot.send_message(chat_id=update.effective_chat.id, text = "Lütfen geçerli bir gün giriniz.")
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

async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(chat_id=update.effective_chat.id, text = "Bu bir text mesajıdır")
  

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

def sendDaysMenu():
  kayitliKisiListesi = models.check_all()
  userInput = datetime.datetime.now().day
  daysMenu = menuList[int(userInput)-1]
  ines = daysMenu.split("\n")
  formattedDaysMenu = f"{lines[0]} - {lines[1]}\n" + "\n".join(lines[2:])
  daysMenuText = formattedDaysMenu

  for eachPerson in range(len(kayitliKisiListesi)):
    telegramId = kayitliKisiListesi[eachPerson][0]
    try:
      url = f"https://api.telegram.org/bot{Token}/sendMessage?chat_id={telegramId}&text={daysMenuText}"
      requests.get(url).json()
    except:
      text1 = f"{telegramId} abone olmus ama yetki vermemis"
      print(text1)
  
def callbackMenu(context: CallbackContext):
  timer = time(hour=9, minute=34)
  context.job_queue.run_daily(sendDaysMenu, timer, days=(0,1,2,3,4,5,6))
  

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

def abonelik(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user = update.message.from_user
  first_name = user["first_name"]
  last_name = user["last_name"]
  telegramId = user["id"]
  print(type(telegramId))
  check_id = models.check_person(telegramId)
  try:  
    if check_id is None:
      models.add_user(telegramId, first_name, last_name)
      text = "Abonelik kaydınız oluşturuldu! Her gün Saat 09:00'da günün menüsü sizinle paylaşılacaktır."
      url = f"https://api.telegram.org/bot{Token}/sendMessage?chat_id={telegramId}&text={text}"
      requests.get(url).json()
    else:
      text = "Zaten aboneliğiniz bulunmaktadır."
      url = f"https://api.telegram.org/bot{Token}/sendMessage?chat_id={telegramId}&text={text}"
      requests.get(url).json()
  except(TypeError):
    print("hata")
  info = update.message
  messages_to_add(info)

def abonelikiptal(update:Update, context:ContextTypes.DEFAULT_TYPE):
  user = update.message.from_user
  telegramId= user["id"]
  print(telegramId)
  check_id = models.check_person(telegramId)
  print(check_id)
  if check_id is None:
    text = "Aboneliğiniz bulunmamaktadır."
    url = f"https://api.telegram.org/bot{Token}/sendMessage?chat_id={telegramId}&text={text}"
    requests.get(url).json()
  else:
    models.delete_person(telegramId)
    text = "Aboneliğiniz iptal edilmiştir."
    url = f"https://api.telegram.org/bot{Token}/sendMessage?chat_id={telegramId}&text={text}"
    requests.get(url).json()
  info = update.message
  messages_to_add(info)

def messages_to_add(info):
  user = info.from_user
  first_name = user["first_name"]
  last_name = user["last_name"]
  telegramId = user["id"]
  message = info.text
  models.add_message(telegramId, first_name, last_name, message)

def main():
  app = ApplicationBuilder().token(Token).build()
  app.add_handler(CommandHandler("start", start))
  app.add_handler(CommandHandler('help',help))
  app.add_handler(CommandHandler('menu',getMenu))
  app.add_handler(CommandHandler('yemekhane',yemekhane))
  app.add_handler(CommandHandler('abonelik',abonelik))
  app.add_handler(CommandHandler('abonelikiptal',abonelikiptal))
  callbackRestartEveryday(app)
  callbackMenu(app)
  app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
  main()
