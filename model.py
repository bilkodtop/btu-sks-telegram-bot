import sqlite3
from datetime import datetime
import requests
from dotenv import load_dotenv
import os
import getmenu

load_dotenv()
Token = os.getenv("TOKEN")
class Models:

  def __init__(self):
    self.db = sqlite3.connect('database.db', check_same_thread=False)
    self.cursor = self.db.cursor()
    self.create_table()

  def create_table(self):
    """Creates table if not exists"""
    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            chat_id TEXT PRIMARY KEY NOT NULL, 
            first_name TEXT DEFAULT "",
            last_name TEXT DEFAULT "",
            subsdate DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            chat_id TEXT NOT NULL, 
            first_name TEXT DEFAULT "",
            last_name TEXT DEFAULT "",
            message TEXT DEFAULT "",
            message_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY,
            title TEXT DEFAULT "",
            link TEXT DEFAULT "",
            publish_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    self.db.commit()

  def add_user(self, chat_id, first_name, last_name):
    """Adds people to database"""
    self.cursor.execute(
      '''
        INSERT INTO subscriptions (chat_id, first_name, last_name) VALUES (?, ?, ?)
        ''', (chat_id, first_name, last_name))
    self.db.commit()

  def delete_person(self, chat_id):
    """Deletes people from database"""
    self.cursor.execute(
      '''
        DELETE FROM subscriptions WHERE chat_id = ?
        ''', (chat_id, ))
    self.db.commit()

  def check_person(self, chat_id):
    """Checks if people exists"""
    self.cursor.execute(
      '''
        SELECT * FROM subscriptions WHERE chat_id = ?
        ''', (chat_id, ))
    return self.cursor.fetchone()

  def check_all(self):
    self.cursor.execute('''
        SELECT * FROM subscriptions 
        ''')
    return self.cursor.fetchall()

  def add_message(self, chat_id, first_name, last_name, message):
    self.cursor.execute(
      "INSERT INTO messages (chat_id, first_name, last_name,message) VALUES (?, ?, ?, ?)",
      (chat_id, first_name, last_name, message))
    self.db.commit()

  def get_all_messages(self):
    self.cursor.execute('''
        SELECT * FROM messages
        ''')
    return self.cursor.fetchall()

  
  def add_announcement(self,id,title, link,publish_date):
    """Adds announcements to database"""
    self.cursor.execute(
      '''
        INSERT INTO announcements (id, title, link,publish_date) VALUES (?, ?, ?, ?)
        ''', (id, title, link,publish_date))
    self.db.commit()
  def delete_announcement(self,id):
    """Deletes announcements from database"""
    self.cursor.execute(
      '''
        DELETE FROM announcements WHERE id = ?
        ''', (id,))
    self.db.commit()

  def check_all_announcements(self):
    self.cursor.execute('''
        SELECT id,title FROM announcements
        ''')
    return self.cursor.fetchall()
  
  def admin_get_all_announcement(self):
      self.cursor.execute('''
        SELECT * FROM announcements
        ''')
      return self.cursor.fetchall()

  def admin_send_one_announcement(self,id):

    self.cursor.execute('''
        SELECT * FROM announcements WHERE id = ?
        ''',(id,))
    return self.cursor.fetchone()

class Scripts:
  def __init__():
    pass

  def push_daily_message():
    model = Models()
    menuList, date = getmenu.Menu().getFormattedMenu()
    userInput = datetime.now().day
    daysDate = (date[int(userInput)] + " Tarihli Günün Menüsü")
    daysMenu = menuList[int(userInput)]
    daysMenuText = daysDate + "\n" + daysMenu
    all_subscribers = model.check_all()
    for eachPerson in range(len(all_subscribers)):
      telegramId = all_subscribers[eachPerson][0]
      try:
        url = f"https://api.telegram.org/bot{Token}/sendMessage?chat_id={telegramId}&text={daysMenuText}"
        req = requests.get(url).json()
      except:
        print(f"{telegramId} abone olmus ama yetki vermemis")