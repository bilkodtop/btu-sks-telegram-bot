import fitz
import os

dosya_dizini = os.path.dirname(os.path.abspath(__file__))
dosya_adi = "pdf0.pdf"
dosya_yolu = os.path.join(dosya_dizini, dosya_adi)

class Menu():
    def __init__(self):
      pass
    def getFormattedMenu(self):
      doc = fitz.open(dosya_yolu)
      page = doc.load_page(0)
      text = page.get_text("blocks")
      liste = []
      kontrol = 0
      for a in range(2,len(text)):
          kontrol += 1
          if kontrol == 32:
              break
          try: 
              int(text[a][4][0:2]) 
          except:
              break
          liste.append(text[a][4])
      return liste
