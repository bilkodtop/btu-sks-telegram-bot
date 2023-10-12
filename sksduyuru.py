import requests
from bs4 import BeautifulSoup
from datetime import datetime
from model import Models

models = Models()
models.create_table()

class DUYURU:
    class Announcement:
        def __init__(self, link, title, date,id):
            self.link = link
            self.title = title
            self.date = date
            self.id = id

    def __init__(self, url="https://sks.btu.edu.tr/tr/duyuru/birim/108",ann_list=[]):
        self.url = url
        self.ann_list = ann_list

    def scrape_announcements(self):
        response = requests.get(self.url)
        page = BeautifulSoup(response.content, "html.parser")
        content = page.find("div", class_="ann-list")
        announcements = content.find_all("li")

        for ann in announcements:
            try:    
                link = ann.find("a")["href"]
                title = ann.find("strong").text
                date = ann.find("span").text
                id = ann.find("a")["href"].split("/")[6]
                
                updated_date = datetime.strptime(date, "%d.%m.%Y")
                formatted_date = updated_date.strftime("%Y-%m-%d")
                
                self.ann_list.append(self.Announcement(link, title, formatted_date,id))
            except:
                print("Hata oluştu. Duyuru id'si: " + id)
        return self.ann_list

    def add_to_db(self, ann_list):
        for ann in ann_list:
            models.add_announcement(ann.id, ann.title, ann.link, ann.date)

    def check_for_new_content(self):
        site_list = self.scrape_announcements()
        database_list = models.check_all_announcements()
        
        for i in range(len(site_list)):
            if (site_list[i].id != database_list[i][0] and site_list[i].title != database_list[i][1]):
                models.add_announcement(site_list[i].id, site_list[i].title,
                                        site_list[i].link, site_list[i].date)

        for i in range(len(database_list)):
            if (database_list[i][0] != site_list[i].id and database_list[i][1] != site_list[i].title):
                models.delete_announcement(database_list[i][0])
                
if __name__ == "__main__":
    duyuru_instance = DUYURU()
    duyuru_instance.scrape_announcements()
    duyuru_instance.add_to_db(duyuru_instance.ann_list) 