import telegram.ext
import datetime
from telegram.ext import CallbackContext
from model import Models
import pytz
import requests
import getmenu
import scrape
import os
import time
import sksduyuru
import dotenv
dotenv.load_dotenv()


try:
  menuList, date = getmenu.Menu().getFormattedMenu()
except:
  scrape.ScrapeMenu().getPdf()
  scrape.ScrapeMenu().convertPdfToCsv()
  menuList, date = getmenu.Menu().getFormattedMenu()

Token = "TOKEN"

models = Models()
models.create_table()

updater = telegram.ext.Updater(Token, use_context=True)
dispatcher = updater.dispatcher
j = updater.job_queue



def restartEveryDay(context: CallbackContext):
  global menuList, date
  os.system("rm yemekhane.csv")
  time.sleep(1)
  os.system("rm pdf0.pdf")
  time.sleep(1)
  scrape.ScrapeMenu().getPdf()
  scrape.ScrapeMenu().convertPdfToCsv()
  menuList, date = getmenu.Menu().getFormattedMenu()


j.run_daily(restartEveryDay,
            datetime.time(hour=8,
                          minute=55,
                          tzinfo=pytz.timezone('Europe/Istanbul')),
                          days=("mon", "tue", "wed", "thu", "fri","sat","sun"))


def start(update, context):
  update.message.reply_text(
    "Bursa Teknik Üniversitesi Yemekhane Telegram botuna hoşgeldiniz. /help yazarak komutlara erişebilirsiniz.!"
  )
  info = update.message
  messages_to_add(info)

#admin-command
def duyurular(update,context):
  admin_id = update.message.from_user.id
  #admin_list will be crated in .env file
  if(admin_id in admin_list):
    all_announcements=models.admin_get_all_announcement()
    for i in range(len(all_announcements)):
      text=f"ID: {all_announcements[i][0]} \n DUYURU \n {all_announcements[i][1]} \n {all_announcements[i][2]} \n\n Daha fazla bilgi için [Tıklayınız]({all_announcements[i][3]})"
      data = {
        'chat_id':f"{admin_id}",
        'text': text,
        'parse_mode': 'Markdown',
    }
      requests.post(f'https://api.telegram.org/bot{Token}/sendMessage',data=data)
#admin-command
def yenidengonder(update,context):
  admin_id = update.message.from_user.id
  #admin_list will be crated in .env file
  if(admin_id in admin_list):
    announcement=models.admin_send_one_announcement()
    text=f"DUYURU \n {announcement[1]} \n {announcement[2]} \n\n Daha fazla bilgi için [Tıklayınız]({announcement[3]})"
    data = {
    'chat_id':"@BTU_SKS",
     'text': text,
     'parse_mode': 'Markdown',
 }
    requests.post(f'https://api.telegram.org/bot{Token}/sendMessage',data=data)



def yemekhane(update, context):
  user = update.message.from_user
  print('You talk with user {} and his user ID: {} and his name is {}'.format(
    user['username'], user['id'], user['first_name']))
  update.message.reply_text("""
    /menu gün -> girdiğiniz günün menüsünü görebilirsiniz, gün girmezseniz içinde olduğunuz günün menüsünü görebilirsiniz.\n\n/abonelik  -> botumuzda abonelik başlatarak her gün saat 09.00'da botumuzdan menüyü telegram'dan özel mesaj olarak alabilirsiniz.(Sadece /abonelik yazarak günlük mesaj alamazsınız botun kendisine tıklayıp mesajlaşma başlatmanız gerekmektedir)\n\n/abonelikiptal -> aboneliğinizi iptal eder.
    """)
  info = update.message
  messages_to_add(info)

def help(update, context):
  user = update.message.from_user
  print('You talk with user {} and his user ID: {} and his name is {}'.format(
    user['username'], user['id'], user['first_name']))
  update.message.reply_text("""
    /menu gün -> girdiğiniz günün menüsünü görebilirsiniz, gün girmezseniz içinde olduğunuz günün menüsünü görebilirsiniz.\n\n/abonelik  -> botumuzda abonelik başlatarak her gün saat 09.00'da botumuzdan menüyü telegram'dan özel mesaj olarak alabilirsiniz.(Sadece /abonelik yazarak günlük mesaj alamazsınız botun kendisine tıklayıp mesajlaşma başlatmanız gerekmektedir)\n\n/abonelikiptal -> aboneliğinizi iptal eder.
    """)
  info = update.message
  messages_to_add(info)


def getmenu(update, context):
  if context.args == []:
    userInput = datetime.datetime.now().day
  else:
    userInput = context.args[0]
  if (int(userInput) > 0):
    daysDate = (date[int(userInput) - 2] + " Tarihli Günün Menüsü")
    daysMenu = menuList[int(userInput) - 2]
    daysMenuText = daysDate + "\n" + daysMenu
    update.message.reply_text(daysMenuText)
  #add message to database
  info = update.message
  messages_to_add(info)


def sendDaysMenu(context: CallbackContext):
  kayitliKisiListesi = models.check_all()
  userInput = datetime.datetime.now().day
  daysDate = (date[int(userInput) - 1] + " Tarihli Günün Menüsü")
  daysMenu = menuList[int(userInput) - 1]
  daysMenuText = daysDate + "\n" + daysMenu

  for eachPerson in range(len(kayitliKisiListesi)):
    telegramId = kayitliKisiListesi[eachPerson][0]
    try:
      url = f"https://api.telegram.org/bot{Token}/sendMessage?chat_id={telegramId}&text={daysMenuText}"
      requests.get(url).json()
      eachPerson += 1
    except:
      print(f"{telegramId} abone olmus ama yetki vermemis")
      eachPerson += 1

j.run_daily(sendDaysMenu,
            datetime.time(hour=9,
                          minute=0,
                          tzinfo=pytz.timezone('Europe/Istanbul')),
            days=("mon", "tue", "wed", "thu", "fri"))



def checkSksContent(context: CallbackContext):
  ann = sksduyuru.DUYURU("https://sks.btu.edu.tr/tr/duyuru/birim/108")
  new_content = ann.check_for_new_content()
  for content in new_content:
    text=f"DUYURU \n {content.title} \n {content.date} \n\n Daha fazla bilgi için [Tıklayınız]({content.link})"
    print(text)
    data = {
    'chat_id':"@BTU_SKS",
     'text': text,
     'parse_mode': 'Markdown',
 }
    requests.post(f'https://api.telegram.org/bot{Token}/sendMessage',data=data)

j.run_daily(checkSksContent,
             datetime.time(hour=22,
                           minute=14,
                           tzinfo=pytz.timezone('Europe/Istanbul')),
             days=("mon", "tue", "wed", "thu", "fri","sat","sun"))


def abonelik(update, context):
  user = update.message.from_user
  first_name = user["first_name"]
  last_name = user["last_name"]
  telegramId = user["id"]
  check_id = models.check_person(telegramId)
  if check_id is None:
    models.add_user(telegramId, first_name, last_name)
    text = "Abonelik kaydınız oluşturuldu! Her gün Saat 09:00'da günün menüsü sizinle paylaşılacaktır."
    url = f"https://api.telegram.org/bot{Token}/sendMessage?chat_id={telegramId}&text={text}"
    requests.get(url).json()
  else:
    text = "Zaten aboneliğiniz bulunmaktadır."
    url = f"https://api.telegram.org/bot{Token}/sendMessage?chat_id={telegramId}&text={text}"
    requests.get(url).json()
  info = update.message
  messages_to_add(info)


def abonelikiptal(update, context):
  user = update.message.from_user
  telegramId= user["id"]
  check_id = models.check_person(telegramId)
  print(check_id)
  if check_id is None:
    text = "Aboneliğiniz bulunmamaktadır."
    url = f"https://api.telegram.org/bot{Token}/sendMessage?chat_id={telegramId}&text={text}"
    requests.get(url).json()
  else:
    models.delete_person(id)
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


dispatcher.add_handler(telegram.ext.CommandHandler('start', start))
dispatcher.add_handler(telegram.ext.CommandHandler('duyurular', duyurular))
dispatcher.add_handler(telegram.ext.CommandHandler('duyurular', yenidengonder))
dispatcher.add_handler(telegram.ext.CommandHandler('menu', getmenu))
dispatcher.add_handler(telegram.ext.CommandHandler('yemekhane', yemekhane))
dispatcher.add_handler(telegram.ext.CommandHandler('abonelik', abonelik))
dispatcher.add_handler(
  telegram.ext.CommandHandler('abonelikiptal', abonelikiptal))
dispatcher.add_handler(telegram.ext.CommandHandler('help', help))
updater.start_polling()
updater.idle()
