from selenium import webdriver
from bs4 import BeautifulSoup
import time
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import re
import os
import requests
import tkinter as tk
from tkinter import filedialog as fd

def callbackBrandImage():
    global brandFile
    brandFile = fd.askopenfilename()
    print(brandFile)

def callbackList():
    global listOfArticles
    listOfArticles = fd.askopenfilename()
    print(listOfArticles)
    path, name = os.path.split(listOfArticles)
    artFileLabel.config(text="Ты выбрал файл: "+name)

def callbackProccess():
    global listOfArticles
    if listOfArticles == "Не установлено":
        tk.messagebox.showerror(title="Единственная ошибка которую можно было допустить", message="Укажите текстовый файл с артиклями пожалуйста, очень вас прошу. Без этого программа не может работать. Пример файла в папке с программой называется \"Тестовый файл.txt\"", type=tk.messagebox.OK)
        return
    brand = Image.open(os.path.abspath("шаблонище.png"))
    bg_stories = Image.open(os.path.abspath("сторис.png"))
    bg_insta = Image.open(os.path.abspath("инста.png"))
    myFont = ImageFont.truetype(os.path.abspath('Шрифт Нью Ёркер.ttf'), 35)
    with open(listOfArticles) as f:
        dataArray = f.read().splitlines()
    i = 0
    t = 0
    arts_fail = []
    while i < len(dataArray):
        art = dataArray[i]
        url = 'https://www.wildberries.ru/catalog/'+str(art)+'/detail.aspx'

        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=720,1080")
        options.add_argument("--headless")
        options.add_experimental_option(
            "prefs", {
                "profile.managed_default_content_settings.images": 2,
            }
        )
        options.set_capability('pageLoadStrategy', "eager")
        browser = webdriver.Chrome(options=options)
        browser.get(url)
        time.sleep(3)

        html = browser.page_source
        soup = BeautifulSoup(html, 'html.parser')

        price = soup.title.string.replace('\xa0', '')
        price_find = re.findall('купить за [0-9]+', price)
        while True:
            try:
                re.findall('[0-9]+', price_find[0])
                price_result = re.findall('[0-9]+', price_find[0])
                print(price_result[0])

                for link in soup.find_all(alt=" Вид 1."):
                    print(link.get('src'))
                    img = link.get('src')

                # browser.quit()

                r = requests.get(img, stream=True).raw
                img = Image.open(r)
                bg = Image.new('RGB', img.size, 'white')
                bg.paste(img)
                bg.save('картинки\\оригинал\\' + str(art) + ' оригинал.jpg')
                img = Image.open('картинки\\оригинал\\' + str(art) + ' оригинал.jpg')
                brand = brand.convert('RGBA')
                img = img.convert("RGBA")
                img.alpha_composite(brand, (0, 0))
                msg = "арт. WB:\n" + str(art) + "\nЦена: " + str(price_result[0]) + " Р"
                I1 = ImageDraw.Draw(img)
                I1.multiline_text((650, 1070), msg, font=myFont, fill=(0, 0, 0), align='center')
                img.save("картинки\\обработанные\\" + str(art) + " скартиненая картинка.png")
                bg_stories.paste(img, (0, 200))
                bg_stories.save("картинки\\сторис\\" + str(art) + " скартиненая картинка.png")
                bg_insta.paste(img, (150, 0))
                bg_insta.save("картинки\\инста\\" + str(art) + " скартиненая картинка.png")
                i = i + 1
                t = 0
                break
            except Exception:
                if t == 3:
                    t = 0
                    i = i + 1
                    print(art)
                    arts_fail.append(art)
                    break
                else:
                    t = t + 1
                    continue
    named_tuple = time.localtime()
    time_string = time.strftime("_%m-%d_%H-%M-%S", named_tuple)
    if arts_fail != []:
        with open("ошибки\\ошибки"+ str(time_string) + ".txt", "w") as file:
            for row in arts_fail:
                file.write(str(row) + '\n')



listOfArticles = "Не установлено"

root = tk.Tk()
root.title("Добавлятель одной картинки в другую.")
root.resizable(False,False)
root.geometry("350x120")

tk.Button(text='Выберете список Артикулов',
          command=callbackList).pack(fill=tk.X, pady = 10, padx=10)

artFileLabel = tk.Label(text="", anchor="w", justify="left")
artFileLabel.pack(fill=tk.X, padx=10)

tk.Button(text='Скартинить картинки',
          command=callbackProccess).pack(fill=tk.X, pady = 10, padx=10)


root.mainloop()