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

    def __init__(self, url="https://sks.btu.edu.tr/tr/duyuru/birim/108",ann_list=[],new_content=[]):
        self.url = url
        self.ann_list = ann_list
        self.new_content=new_content
        

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

    def check_for_new_content(self):
        site_list = self.scrape_announcements()
        database_list = models.check_all_announcements()
        new_content = []  # Yeni eklenen duyuruları takip etmek için liste

        # Sitedeki duyuruları döngüye alın
        for site_announcement in site_list:
            found = False

            # Veritabanındaki duyuruları döngüye alın
            for database_announcement in database_list:
                if site_announcement.id == database_announcement[0] and site_announcement.title == database_announcement[1]:
                    found = True
                    break  # Eşleşme bulundu, iç içe döngüyü sonlandır

            # Eğer site duyurusu veritabanında bulunmuyorsa, yeni duyuruyu ekleyin
            if not found:
                try:
                    models.add_announcement(site_announcement.id, site_announcement.title, site_announcement.link, site_announcement.date)
                    new_content.append(site_announcement)
                    print(f"Announcement added id:{site_announcement.id} title:{site_announcement.title} link:{site_announcement.link} date:{site_announcement.date}")
                except:
                    pass
        return new_content
