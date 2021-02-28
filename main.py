import shutil
from datetime import datetime, date
from time import gmtime, strftime
import zipfile
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import tkinter.ttk as ttk
from tkinter import filedialog
import os
import hashlib
import tkinter as tk
import threading
from xlwt import Workbook
import pandas

user = os.environ["USERNAME"]
window = tk.Tk()
window.geometry("900x625")
window.title("WhatsApp Scraper")
window.grid_columnconfigure(0, weight=1)
window.resizable(False, False)
chromeDriverPath = os.path.dirname(os.path.abspath(__file__))
pyExePath = os.path.dirname(os.path.abspath(__file__))
NAMES = []
log_dict = {}
language = 'italian'
window.iconbitmap('whatsapp.ico')
wb = Workbook()
sheet1 = wb.add_sheet('Hash')
nRow=3

sheet1.write(0, 0, 'WhatsappScraper_v.1')
sheet1.write(0, 1, 'https://github.com/fpollicelli/whatsappScraper.git')
sheet1.write(0, 2, 'Authors: Francesca Pollicelli')
sheet1.write(0, 3, 'Domenico Palmisano')
sheet1.write(1, 0, 'File')
sheet1.write(1, 1, 'Timestamp')
sheet1.write(1, 2, 'MD5')
sheet1.write(1, 3, 'SHA512')
wb.save(pyExePath + '\log.xls')


def detectLanguage(driver):
    global language
    try:
        element = WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[4]/div/div/div[2]/h1'))
        )
        welcome = driver.find_element_by_xpath('//*[@id="app"]/div/div/div[4]/div/div/div[2]/h1')
        welcome = welcome.get_attribute("innerHTML")
        if welcome == 'Keep your phone connected':
            language = 'english'
        else:
            language = 'italian'
    except:
        language = 'italian'
    return


def findChromeDriver():
    for root, dirs, files in os.walk(chromeDriverPath):
        if "chromedriver.exe" in files:
            return os.path.join(root, "chromedriver.exe")


def openChrome():
    global nRow
    options = webdriver.ChromeOptions()  # stabilire connessione con whatsapp web
    options.add_experimental_option("prefs", {
        "download.default_directory": pyExePath + "\\Scraped\\Media",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    options.add_argument("--remote-debugging-port=9222")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # CREAZIONE PROFILO SOLO PER DEBUG
    # '''
    options.add_argument(
        "user-data-dir=C:\\Users\\" + user + "\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1")  # crea un nuovo profilo utente in chrome per scansionare il qw
    # '''
    args = ["hide_console", ]
    driver = webdriver.Chrome(options=options, executable_path=findChromeDriver(), service_args=args)

    # apre whatsapp nel browser
    driver.get('http://web.whatsapp.com')
    try:
        element = WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="side"]/header/div[1]/div/img'))
        )
    except:
        if language == 'italian':
            text = 'impossibile connettersi a WhatsApp Web'
        else:
            text = 'unable to connect to WhatsApp Web'
        output_label_2.configure(text=text)
        log_dict[getDateTime()] = text
        window.update()
        for key, value in log_dict.items():
            sheet1.write(nRow, 0, value)
            sheet1.write(nRow, 1, key)
            nRow = nRow + 1
        driver.close()
        wb.save(pyExePath + '\log.xls')

    return driver


def readMessages(name, driver):
    timezone = strftime("GMT%z", gmtime())
    timezone = timezone[:-2]
    list_audio = []
    list_img = []
    list_video = []
    count_audio = 0
    count_img = 0
    count_video = 0
    if language == 'italian':
        text = "scraping dei messaggi in corso..."
    else:
        text = 'scraping messages in progress'
    output_label_2.configure(text=text)
    log_dict[getDateTime()] = text
    window.update()
    dir = pyExePath + '/Scraped/Chat/'
    if not os.path.exists(dir):
        os.makedirs(dir)
    f = open(dir + name + '.csv', 'w', encoding='utf-8')
    if language == 'italian':
        f.write('Data,Ora,Mittente,Messaggio\n')
    else:
        f.write('Date,Time,Sender,Message\n')
    trovato = False
    while trovato == False:
        try:
            element = driver.find_element_by_xpath("//*[@id='main']/div[3]/div/div/div[2]/div[2]/div/div/div/span/span")
            trovato = True
        except:
            trovato = False
            driver.find_element_by_xpath("//*[@id='main']/div[3]/div/div").send_keys(Keys.CONTROL + Keys.HOME)

    messageContainer = driver.find_elements_by_xpath("//div[contains(@class,'message-')]")
    for messages in messageContainer:
        if (save_media.get() == 1):
            if language == 'italian':
                text = "salvataggio degli audio in corso..."
            else:
                text = 'scraping audio...'
            output_label_2.configure(text=text)
            log_dict[getDateTime()] = text
            window.update()
            try:
                vocal = messages.find_element_by_xpath(".//span[contains(@data-testid,'ptt-status')]")
                vocal.click()
                try:
                    time.sleep(5)
                    down = messages.find_element_by_xpath(".//span[contains(@data-testid,'audio-download')]")
                    down.click()
                    time.sleep(5)
                    try:
                        element = WebDriverWait(driver, 50).until(
                            EC.presence_of_element_located(
                                (By.XPATH, ".//span[contains(@data-testid,'audio-play')]"))
                        )
                    except:
                        if language == 'italian':
                            text = "impossibile scaricare l'audio"
                        else:
                            text = 'unable to download the audio'
                        output_label_2.configure(text=text)
                        log_dict[getDateTime()] = text
                        window.update()
                except:
                    pass
                downContext = messages.find_element_by_xpath(".//span[contains(@data-testid,'down-context')]")
                downContext.click()
                if language == 'italian':
                    button = WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located(
                        (By.XPATH, ".//div[contains(@aria-label,'Scarica')]")))
                else:
                    button = WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located(
                        (By.XPATH, ".//div[contains(@aria-label,'Download')]")))
                button.click()
            except:
                pass

        try:
            try:  # SALVATAGGIO DI DOC IN CSV
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//button[contains(@title,"Scarica")]'))
                )
                download = messages.find_element_by_xpath(
                    ".//button[contains(@title,'Scarica')]")

                oraData = info[info.find('[') + 1: info.find(']') + 1]
                if language == 'english':
                    data = oraData[oraData.find(' ') + 4: oraData.find(']')]
                else:
                    data = oraData[oraData.find(' ') + 1: oraData.find(']')]
                ora = oraData[oraData.find('[') + 1: oraData.find(',')]
                mittente = info.split(']')[1].strip()
                mittente = mittente.split(':')[0].strip()

                download = download.get_attribute('title')
                if language == 'italian':
                    download = download[9:-1]
                else:
                    download = download[10:-1]
                if len(download) > 90:
                    download = download[:90]
                    tree.insert("", 0, values=(data, ora+" "+timezone, mittente, "Doc: " + download + '...'))
                else:
                    tree.insert("", 0, values=(data, ora+" "+timezone, mittente, "Doc: " + download))
                finalMessage = data + "," + ora+" "+timezone + "," + mittente + "," + "Doc: " + download
                window.update()
                f.write(finalMessage)
                f.write('\n')
            except:
                pass

            try:  # SALVATAGGIO DI AUDIO IN CSV

                audio = messages.find_element_by_xpath(".//span[contains(@data-testid,'ptt-status')]")
                # WhatsApp Ptt 2021-02-17 at 17.17.26.ogg

                oraData = info[info.find('[') + 1: info.find(']') + 1]
                if language == 'english':
                    data = oraData[oraData.find(' ') + 4: oraData.find(']')]
                else:
                    data = oraData[oraData.find(' ') + 1: oraData.find(']')]
                ora = oraData[oraData.find('[') + 1: oraData.find(',')]
                mittente = info.split(']')[1].strip()
                mittente = mittente.split(':')[0].strip()

                audio_name = "WhatsApp Ptt " + data + " at " + ora + ".ogg"
                if len(list_audio) == 0:
                    list_audio.append(audio_name)
                    count_audio += 1
                else:
                    for audioname in list_audio:
                        if audioname == audio_name:
                            audio_name = audio_name + " (" + count_audio + ")"
                    list_audio.append(audio_name)
                    count_audio += 1
                if len(audio_name) > 90:
                    audio_name = audio_name[:90]
                    tree.insert("", 0, values=(data, ora+" "+timezone, mittente, "Audio: " + audio_name + '...'))
                else:
                    tree.insert("", 0, values=(data, ora+" "+timezone, mittente, "Audio: " + audio_name))
                finalMessage = data + "," + ora+" "+timezone + "," + mittente + "," + "Audio: " + audio_name
                window.update()
                f.write(finalMessage)
                f.write('\n')
            except:
                pass

            try:  # SALVATAGGIO DI IMG IN CSV
                img = messages.find_element_by_xpath(".//img[contains(@src,'blob')]")

                oraData = info[info.find('[') + 1: info.find(']') + 1]
                if language == 'english':
                    data = oraData[oraData.find(' ') + 4: oraData.find(']')]
                else:
                    data = oraData[oraData.find(' ') + 1: oraData.find(']')]
                ora = oraData[oraData.find('[') + 1: oraData.find(',')]
                mittente = info.split(']')[1].strip()
                mittente = mittente.split(':')[0].strip()

                img_name = "WhatsApp Image " + data + " at " + ora + ".jpeg"
                if len(list_img) == 0:
                    list_img.append(list_img)
                    count_img += 1
                else:
                    for imgage in list_img:
                        if imgage == img_name:
                            img_name = img_name + " (" + count_img + ")"
                    list_img.append(img_name)
                    count_img += 1
                if len(img_name) > 90:
                    img_name = img_name[:90]
                    tree.insert("", 0, values=(data, ora+" "+timezone, mittente, "Img: " + img_name + '...'))
                else:
                    tree.insert("", 0, values=(data, ora+" "+timezone, mittente, "Img: " + img_name))
                finalMessage = data + "," + ora+" "+timezone + "," + mittente + "," + "Img: " + img_name
                window.update()
                f.write(finalMessage)
                f.write('\n')
            except:
                pass

            try:  # SALVATAGGIO DI VIDEO IN CSV
                video = messages.find_element_by_xpath(".//span[contains(@data-testid,'media')]")

                oraData = info[info.find('[') + 1: info.find(']') + 1]
                if language == 'english':
                    data = oraData[oraData.find(' ') + 4: oraData.find(']')]
                else:
                    data = oraData[oraData.find(' ') + 1: oraData.find(']')]
                ora = oraData[oraData.find('[') + 1: oraData.find(',')]
                mittente = info.split(']')[1].strip()
                mittente = mittente.split(':')[0].strip()

                video_name = "WhatsApp Video " + data + " at " + ora + ".mp4"
                if len(list_video) == 0:
                    list_img.append(list_img)
                    count_video += 1
                else:
                    for videoname in list_video:
                        if videoname == video_name:
                            video_name = video_name + " (" + count_video + ")"
                    list_img.append(video_name)
                if len(video_name) > 90:
                    video_name = video_name[:90]
                    tree.insert("", 0, values=(data, ora+" "+timezone, mittente, "Img: " + video_name + '...'))
                else:
                    tree.insert("", 0, values=(data, ora+" "+timezone, mittente, "Img: " + video_name))
                finalMessage = data + "," + ora+" "+timezone + "," + mittente + "," + "Img: " + video_name
                window.update()
                f.write(finalMessage)
                f.write('\n')
            except:
                pass

            message = messages.find_element_by_xpath(
                ".//span[contains(@class,'selectable-text copyable-text')]"
            ).text
            emojis = messages.find_elements_by_xpath(
                ".//img[contains(@class,'selectable-text copyable-text')]")

            if len(emojis) != 0:
                for emoji in emojis:
                    message = message + emoji.get_attribute("data-plain-text")
            info = messages.find_element_by_xpath(".//div[contains(@data-pre-plain-text,'[')]")
            info = info.get_attribute("data-pre-plain-text")
            oraData = info[info.find('[') + 1: info.find(']') + 1]
            if language == 'english':
                data = oraData[oraData.find(' ') + 4: oraData.find(']')]
            else:
                data = oraData[oraData.find(' ') + 1: oraData.find(']')]
            ora = oraData[oraData.find('[') + 1: oraData.find(',')]
            mittente = info.split(']')[1].strip()
            mittente = mittente.split(':')[0].strip()
            message = message.replace("\n", " ")
            if len(message) > 90:
                trimMessage = message[:90]
                tree.insert("", 0, values=(data, ora+" "+timezone, mittente, trimMessage + '...'))
            else:
                tree.insert("", 0, values=(data, ora+" "+timezone, mittente, message))
            finalMessage = data + "," + ora+" "+timezone + "," + mittente + "," + message
            window.update()
            f.write(finalMessage)
            f.write('\n')

        # only emojis in the message
        except NoSuchElementException:
            try:
                for emoji in messages.find_elements_by_xpath(
                        ".//img[contains(@class,'selectable-text copyable-text')]"):
                    info = messages.find_element_by_xpath(".//div[contains(@data-pre-plain-text,'[')]")
                    info = info.get_attribute("data-pre-plain-text")
                    message = emoji.get_attribute("data-plain-text")

                    oraData = info[info.find('[') + 1: info.find(']') + 1]
                    ora = oraData[oraData.find('[') + 1: oraData.find(',')]
                    data = oraData[oraData.find(' ') + 1: oraData.find(']')]
                    mittente = info.split(']')[1].strip()
                    mittente = mittente.split(':')[0].strip()
                    message = message.replace("\n", " ")
                    if len(message) > 90:
                        trimMessage = message[:90]
                        tree.insert("", 0, values=(data, ora+" "+timezone, mittente, trimMessage + '...'))
                    else:
                        tree.insert("", 0, values=(data, ora+" "+timezone, mittente, message))
                    finalMessage = data + "," + ora+" "+timezone + "," + mittente + "," + message
                    window.update()
                    f.write(finalMessage)
                    f.write('\n')
            except NoSuchElementException:
                pass
    f.close()
    if language == 'italian':
        text = "generazione del doppio hash della chat in corso..."
    else:
        text = 'generating double hash...'
    output_label_2.configure(text=text)
    log_dict[getDateTime()] = text
    window.update()
    return


def getDateTime():
    now = datetime.now()
    if language == 'english':
        today = date.today().strftime("%m/%d/%Y")
    else:
        today = date.today().strftime("%d/%m/%Y")
    current_time = now.strftime("%H:%M:%S")
    timezone = strftime("GMT%z", gmtime())
    dateTime = today + ' ' + current_time + ' ' + timezone
    return dateTime



def getChatLabels():
    global nRow
    if language == 'italian':
        text = "apertura di WhatsApp Web in corso..."
    else:
        text = 'opening WhatsApp Web...'
    try:
        f = open(pyExePath+"/chat.zip", 'r')
    except:
        pass
    else:
        f.close()
        os.remove(pyExePath + "/chat.zip")

    try:
        f = open(pyExePath+"/hashing.csv", 'r')
    except:
        pass
    else:
        f.close()
        os.remove(pyExePath + "/hashing.csv")

    try:
        f = open(pyExePath+"/media.zip", 'r')
    except:
        pass
    else:
        f.close()
        os.remove(pyExePath + "/media.zip")

    try:
        f = open(pyExePath+"/log.xls", 'r')
    except:
        pass
    else:
        f.close()
        os.remove(pyExePath + "/log.xls")

    log_dict.clear()
    output_label_2.configure(text=text)
    log_dict[getDateTime()] = text
    tree.delete(*tree.get_children())
    driver = openChrome()
    chatLabels = []
    chatName = []
    chatLabels_nodups = []
    archiviat = 0
    toArch = []
    detectLanguage(driver)
    if len(NAMES) != 0:
        for i in range(0, len(NAMES)):
            if 'str' in NAMES[i]:
                break
            try:
                found = driver.find_element_by_xpath(".//span[contains(@title,'" + NAMES[i] + "')]")
                chatLabels.append(found)
            except:
                pass
        try:
            menuDots = driver.find_element_by_xpath("//*[@id='side']/header/div[2]/div/span/div[3]/div/span")
            menuDots.click()
            archiv = driver.find_element_by_xpath("//*[@id='side']/header/div[2]/div/span/div[3]/span/div/ul/li[4]/div")
            archiv.click()
            for i in range(0, len(NAMES)):
                try:
                    recent = driver.find_element_by_xpath(
                        ('//*[@id="app"]/div/div/div[2]/div[1]/span/div/span/div/div'))
                    found = recent.find_element_by_xpath(".//span[contains(@title,'" + NAMES[i] + "')]")
                    actionChains = ActionChains(driver)
                    actionChains.context_click(found).perform()
                    estrai = driver.find_element_by_xpath('//*[@id="app"]/div/span[4]/div/ul/li[1]/div')
                    estrai.click()
                    time.sleep(10)
                    toArch.append(NAMES[i])
                    archiviat = 1
                except:
                    if language == 'italian':
                        text = "errore: contatto non trovato"
                    else:
                        text = "error: can't find the contact"

                    output_label_2.configure(text=text)
                    log_dict[getDateTime()] = text

            goBack = driver.find_element_by_xpath(
                '//*[@id="app"]/div/div/div[2]/div[1]/span/div/span/div/header/div/div[1]/button/span')
            goBack.click()
            for i in range(0, len(toArch)):
                found = driver.find_element_by_xpath(".//span[contains(@title,'" + toArch[i] + "')]")
                chatLabels.append(found)
        except:
            pass
        iterChatList(chatLabels, driver)
        if archiviat == 1:
            if language == 'italian':
                text = "spostamento delle chat de-archiviate in archivio in corso..."
            else:
                text = "moving de-archived chats to archive..."
            output_label_2.configure(text=text)
            log_dict[getDateTime()] = text
            window.update()
            archiviaChat(toArch, driver)
        if language == 'italian':
            text = "scraping terminato con successo"
        else:
            text = "scraping successfully completed"

        output_label_2.configure(text=text)
        log_dict[getDateTime()] = text
        choose_label.configure(text="")
        window.update()

        driver.close()
        wb.save(pyExePath + '\log.xls')
        path = pyExePath
        path = os.path.realpath(path)
        os.startfile(path)
        del NAMES[:]
        return

    if (archiviate.get() == 1):
        if language == 'italian':
            text = "spostamento delle chat archiviate in generali in corso..."
        else:
            text = "moving archived chats in general..."
        output_label_2.configure(text=text)
        log_dict[getDateTime()] = text
        window.update()
        chatLabelsDeArch = moveArchiviate(driver)

    recentList = driver.find_elements_by_xpath('//*[@id="pane-side"]/div[1]/div/div/div')

    for list in recentList:
        chatLabels.append(list)
        label = list.find_elements_by_xpath('.//span[contains(@dir,"auto")]')
        #time
        chatName.append(label[0].get_attribute('title'))
    chatLabels.sort(key=lambda x: int(x.get_attribute('style').split("translateY(")[1].split('px')[0]),
                               reverse=False)
    #ne ho n
    for x in chatLabels:
        driver.execute_script("arguments[0].scrollIntoView();", x)
        recentList_scrolled = driver.find_elements_by_xpath('//*[@id="pane-side"]/div[1]/div/div/div')
    #li ho scrollati
    for list_scrolled in recentList_scrolled:
        chatLabels.append(list_scrolled)
        label = list_scrolled.find_elements_by_xpath('.//span[contains(@dir,"auto")]')
        chatName.append(label[0].get_attribute('title'))

    inds = []
    seen = set()
    for i, ele in enumerate(chatName):
        if ele not in seen:
            inds.append(i)
        seen.add(ele)
    chatLabels = [i for j, i in enumerate(chatLabels) if j in inds]

    chatLabels.sort(key=lambda x: int(x.get_attribute('style').split("translateY(")[1].split('px')[0]), reverse=False)
    iterChatList(chatLabels, driver)
    if (archiviate.get() == 1):
        if language == 'italian':
            text = "spostamento delle chat de-archiviate in archivio in corso..."
        else:
            text = "moving de-archived chats to archive..."
        output_label_2.configure(text=text)
        log_dict[getDateTime()] = text
        window.update()
        archiviaChat(chatLabelsDeArch, driver)
    if language == 'italian':
        text = "scraping terminato con successo"
    else:
        text = "scraping successfully completed"
    output_label_2.configure(text=text)
    log_dict[getDateTime()] = text
    choose_label.configure(text="")
    window.update()
    for key, value in log_dict.items():
        sheet1.write(nRow, 0, value)
        sheet1.write(nRow, 1, key)
        nRow = nRow + 1
    driver.close()
    wb.save(pyExePath+'\log.xls')
    path = pyExePath + '/Scraped'
    create_zip(path, 'chat.zip')
    zip_hasher('chat.zip')
    if save_media.get() == 1:
        create_zip(path, 'media.zip')
        zip_hasher('media.zip')
    shutil.rmtree(path)
    open_folder = os.path.realpath(pyExePath)
    os.startfile(open_folder)
    del NAMES[:]

    read_file = pandas.read_excel(pyExePath+'/log.xls')
    read_file.to_csv(pyExePath+'/hashing.csv', index=None, header=True)
    return


def archiviaChat(chatLabelsDeArch, driver):
    for chat in chatLabelsDeArch:
        chatElement = driver.find_element_by_xpath("//span[contains(@title,'" + chat + "')]")
        actionChains = ActionChains(driver)
        actionChains.context_click(chatElement).perform()
        archivia = driver.find_element_by_xpath('//*[@id="app"]/div/span[4]/div/ul/li[1]/div')
        archivia.click()
        time.sleep(10)
    return


def iterChatList(chatLabels, driver):
    if language == 'italian':
        text = "caricamento delle chat in corso..."
    else:
        text = "loading chats..."
    output_label_2.configure(text=text)
    log_dict[getDateTime()] = text
    window.update()
    for chat in chatLabels:
        chat.click()
        try:
            element = WebDriverWait(driver, 40).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/header/div[2]/div[1]/div/span'))
            )
            label = chat.find_elements_by_xpath('//*[@id="main"]/header/div[2]/div[1]/div/span')
            chatName = label[0].get_attribute('title')
            if len(chatName) == 0:
                label = chat.find_elements_by_xpath(
                    '//*[@id="main"]/header/div[2]/div[1]/div/span/span')  # se il nome contiene un'emoji, va nello span di sotto
                chatName = label[0].get_attribute('title')
            readMessages(chatName, driver)
            if (save_media.get() == 1):
                saveMedia(chatName, driver)

                if language == 'italian':
                    text = "generazione del doppio hash della chat in corso..."
                else:
                    text = 'generating double hash...'
                output_label_2.configure(text=text)
                log_dict[getDateTime()] = text
                window.update()
        except:
            if language == 'italian':
                text = "impossibile caricare le chat"
            else:
                text = 'failed loading chats'
            output_label_2.configure(text=text)
            log_dict[getDateTime()] = text
            window.update()
    return


def saveMedia(name, driver):
    menu = driver.find_element_by_xpath("(//div[@title='Menu'])[2]")
    menu.click()
    info = driver.find_element_by_xpath('//*[@id="main"]')
    try:
        if language == 'italian':
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@aria-label,'Info gruppo')]"))
            )
            info = driver.find_element_by_xpath("//div[contains(@aria-label,'Info gruppo')]")
            info.click()
        else:
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@aria-label,'Group info')]"))
            )
            info = driver.find_element_by_xpath("//div[contains(@aria-label,'Group info')]")
            info.click()
    except:
        try:
            if language == 'italian':
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@aria-label,'Info contatto')]"))
                )
                info = driver.find_element_by_xpath("//div[contains(@aria-label,'Info contatto')]")
                info.click()
            else:
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@aria-label,'Contact info')]"))
                )
                info = driver.find_element_by_xpath("//div[contains(@aria-label,'Contact info')]")
                info.click()
        except:
            try:
                if language == 'italian':
                    element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[contains(@aria-label,'Info lista broadcast')]"))
                    )
                    info = driver.find_element_by_xpath("//div[contains(@aria-label,'Info lista broadcast')]")
                    info.click()
                else:
                    element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[contains(@aria-label,'Broadcast list info')]"))
                    )
                    info = driver.find_element_by_xpath("//div[contains(@aria-label,'Broadcast list info')]")
                    info.click()
            except:
                if language == 'italian':
                    text = "impossibile localizzare le info"
                else:
                    text = "can't locate info"
                output_label_2.configure(text=text)
                log_dict[getDateTime()] = text
                window.update()

    try:
        if language == 'italian':
            element = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Media, link e documenti']"))
            )
            media = driver.find_element_by_xpath("//span[text()='Media, link e documenti']")
            media.click()
        else:
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@title,'Media, Links and Docs')]"))
            )
            media = driver.find_element_by_xpath("//div[contains(@title,'Media, Links and Docs')]")
            media.click()
        saveImgVidAud(name, driver)
        saveDoc(name, driver)
    except:
        if language == 'italian':
            text = "impossibile localizzare i media"
        else:
            text = "can't locate media"
        output_label_2.configure(text=text)
        log_dict[getDateTime()] = text
        window.update()
    return


def saveDoc(name, driver):
    if language == 'italian':
        text = "salvataggio dei documenti in corso..."
    else:
        text = "saving documents..."
    output_label_2.configure(text=text)
    log_dict[getDateTime()] = text
    window.update()
    time.sleep(3)

    if language == 'italian':
        docs_xpath = '//button[text()="Documenti"]'
    else:
        docs_xpath = '//button[text()="DOCS"]'

    docs = driver.find_element_by_xpath(docs_xpath)
    docs.click()
    dir = pyExePath + '/Scraped/Media/'
    noMedia = False
    if not os.path.exists(dir):
        os.makedirs(dir)
    try:
        element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH,
                                        "//*[@id='app']/div/div/div[2]/div[3]/span/div/span/div/div[2]/span/div/div/div/div/div/div/div/div"))
        )
        doc_list = driver.find_elements_by_xpath(
            "//*[@id='app']/div/div/div[2]/div[3]/span/div/span/div/div[2]/span/div/div/div/div/div/div/div/div")
        for document in doc_list:
            document.click()
    except:
        noMedia = True
    return


def saveImgVidAud(name, driver):
    if language == 'italian':
        text = "apertura dei media in corso..."
    else:
        text = "opening media..."
    output_label_2.configure(text=text)
    log_dict[getDateTime()] = text
    window.update()
    dir = pyExePath + '/Scraped/Media/'
    noMedia = False
    if not os.path.exists(dir):
        os.makedirs(dir)
    try:
        element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@style,'background-image')]"))
        )
        image = driver.find_element_by_xpath("//div[contains(@style,'background-image')]")
        noMedia = False
        lastimg = 'false'
        driver.execute_script("arguments[0].click();", image)
        while (lastimg == 'false'):
            try:
                if language == 'italian':
                    downloadXpath = "//div[@aria-label='Scarica']"
                else:
                    downloadXpath = "//div[@aria-label='Download']"

                download = driver.find_element_by_xpath(downloadXpath)
                download.click()
            except:
                pass
            try:
                element = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//*[@id="app"]/div/span[3]/div/div/div[2]/div[2]/div[1]/div'))
                )
                nextButton = driver.find_element_by_xpath('//*[@id="app"]/div/span[3]/div/div/div[2]/div[2]/div[1]/div')
                lastimg = nextButton.get_attribute("aria-disabled")
                nextButton.click()
            except:
                lastimg = 'true'
    except:
        noMedia = True
    return


# SELECT FOLDER
def selectFolder():
    global pyExePath
    pyExePath = filedialog.askdirectory()
    choose_dest_label.configure(text=pyExePath)
    return


def getChatFromCSV():
    if language == 'italian':
        text = "ricerca delle chat selezionate in corso..."
    else:
        text = "searching for selected chats..."
    output_label_2.configure(text=text)
    log_dict[getDateTime()] = text
    tree.delete(*tree.get_children())
    if language == 'italian':
        text = "Seleziona un file"
    else:
        text = "Select a file"
    filename = filedialog.askopenfilename(initialdir="/", title=text,
                                          filetypes=(("CSV files", "*.csv*"), ("all files", "*.*")))
    nomeFile = os.path.basename(filename)
    if nomeFile != "":
        choose_label.configure(text=nomeFile)
        choose_label.configure(fg="black")
        f = open(filename, 'r')
        line = f.read()
        global NAMES
        NAMES = line.split(",")
    return


def moveArchiviate(driver):
    menuDots = driver.find_element_by_xpath("//*[@id='side']/header/div[2]/div/span/div[3]/div/span")
    time.sleep(2)
    menuDots.click()
    time.sleep(2)
    archiv = driver.find_element_by_xpath("//*[@id='side']/header/div[2]/div/span/div[3]/span/div/ul/li[4]/div")
    archiv.click()
    time.sleep(2)
    chatLabels = []
    recentList = driver.find_elements_by_xpath(
        '//*[@id="app"]/div/div/div[2]/div[1]/span/div/span/div/div/div[1]/div/div/div')
    for label in recentList:
        chatLabels.append(label)
    chatLabels.sort(key=lambda x: int(x.get_attribute('style').split("translateY(")[1].split('px')[0]), reverse=False)

    chatNames = []
    for chat in chatLabels:
        label = chat.find_elements_by_xpath('.//span[contains(@dir,"auto")]')
        for labels in label:
            chatNames.append(labels.get_attribute('title'))
    for names in chatNames:
        if names == '':
            chatNames.remove(names)

    for chat in chatLabels:
        actionChains = ActionChains(driver)
        actionChains.context_click(chat).perform()
        estrai = driver.find_element_by_xpath('//*[@id="app"]/div/span[4]/div/ul/li[1]/div')
        estrai.click()
        time.sleep(4)
    goBack = driver.find_element_by_xpath(
        '//*[@id="app"]/div/div/div[2]/div[1]/span/div/span/div/header/div/div[1]/button/span')
    goBack.click()
    return chatNames




def disableEvent(event):
    return "break"


it = ['Data gg/mm/aaaa', 'Ora', 'Mittente', 'Messaggio', 'scraper pronto',
      'Autori: Domenico Palmisano e Francesca Pollicelli', 'Opzioni',
      'Caricare lista contatti', 'Avvia scraper', 'Scraping chat archiviate', 'Cartella di destinazione']
en = ['Date mm/gg/aaaa', 'Time', 'Sender', 'Message', 'scraper ready',
      'Authors: Domenico Palmisano and Francesca Pollicelli', 'Options',
      'Load contact list', 'Start scraper', 'Scraping archived chats', 'Destination folder']


def change_language(index, value, op):
    if comboLang.get() == 'English':
        tree.heading(0, text=en[0], anchor=tk.W)
        tree.heading(1, text=en[1], anchor=tk.W)
        tree.heading(2, text=en[2], anchor=tk.W)
        tree.heading(3, text=en[3], anchor=tk.W)
        output_label_2.config(text=en[4])
        credit_label.config(text=en[5])
        label.config(text=en[6])
        choose_1.config(text=en[7])
        choose_2.config(text=en[8])
        c2.config(text=en[9])
        choose_dest.config(text=en[10])

    else:
        tree.heading(0, text=it[0], anchor=tk.W)
        tree.heading(1, text=it[1], anchor=tk.W)
        tree.heading(2, text=it[2], anchor=tk.W)
        tree.heading(3, text=it[3], anchor=tk.W)
        output_label_2.config(text=it[4])
        credit_label.config(text=it[5])
        label.config(text=it[6])
        choose_1.config(text=it[7])
        choose_2.config(text=it[8])
        c2.config(text=it[9])
        choose_dest.config(text=it[10])
    return


def getfilesfrom(directory):
    return filter(lambda x:
                  not os.path.isdir(os.path.join(directory, x)),
                  os.listdir(directory))


def create_zip(directory, zip_name):
    zf = zipfile.ZipFile(pyExePath+"/"+zip_name, mode='w', compression=zipfile.ZIP_DEFLATED)
    filestozip = getfilesfrom(directory)
    for afile in filestozip:
        zf.write(os.path.join(directory, afile), afile)
    zf.close()
    return


def zip_hasher(zip_name):
    global nRow
    dateTime = getDateTime()
    with open(pyExePath+"/"+zip_name, "rb") as f:
        hash_md5 = hashlib.md5()
        hash_sha512 = hashlib.sha512()
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
            hash_sha512.update(chunk)
    md5_digest = hash_md5.hexdigest()
    sha512_digest = hash_sha512.hexdigest()
    if save_media.get() == 1:
        if zip_name == 'chat.zip':
            sheet1.write(2, 0, zip_name)
            sheet1.write(2, 1, dateTime)
            sheet1.write(2, 2, md5_digest)
            sheet1.write(2, 3, sha512_digest)
            wb.save(pyExePath+'\log.xls')
        else:
            sheet1.write(3, 0, zip_name)
            sheet1.write(3, 1, dateTime)
            sheet1.write(3, 2, md5_digest)
            sheet1.write(3, 3, sha512_digest)
            wb.save(pyExePath+'\log.xls')
            nRow = nRow +1
    else:
        sheet1.write(2, 0, zip_name)
        sheet1.write(2, 1, dateTime)
        sheet1.write(2, 2, md5_digest)
        sheet1.write(2, 3, sha512_digest)
        wb.save(pyExePath + '\log.xls')
    return


tree = ttk.Treeview(window, show="headings", columns=(it[0], it[1], it[2], it[3]), height=14)
tree.heading(it[0], text=it[0], anchor=tk.W)
tree.heading(it[1], text=it[1], anchor=tk.W)
tree.heading(it[2], text=it[2], anchor=tk.W)
tree.heading(it[3], text=it[3], anchor=tk.W)
tree.column('#1', minwidth=110, stretch=False, width=110)
tree.column('#2', minwidth=90, stretch=False, width=90)
tree.column('#3', minwidth=140, stretch=False, width=140)
tree.column('#4', minwidth=535, stretch=True, width=535)
style = ttk.Style(window)
tree.grid(row=5, column=0, padx=10, pady=10, stick='W')

vsbar = tk.Scrollbar(window, orient=tk.VERTICAL, command=tree.yview)
vsbar.place(x=868, y=279, height=280, width=20)
tree.configure(yscrollcommand=vsbar.set)

style.theme_use("clam")
style.configure("Treeview", background="white",
                fieldbackground="white", foreground="white")
tree.bind("<Button-1>", disableEvent)

title = tk.Label(window, text="WhatsApp Scraper", font=("Helvetica", 24))
title.grid(row=0, column=0, sticky="N", padx=20, pady=10)

output_label = tk.Label(text="Log: ")
output_label.grid(row=6, column=0, sticky="W", padx=10, pady=10)

output_label_2 = tk.Label(text=it[4], bg="white", fg="black", borderwidth=2, relief="groove", anchor='w')
output_label_2.configure(width=50)
output_label_2.grid(row=6, column=0, sticky="W", padx=45, pady=10)

credit_label = tk.Label(window, text=it[5])
credit_label.grid(row=6, column=0, stick="E", padx=10, pady=0)

xf = tk.Frame(window, relief=tk.GROOVE, borderwidth=2, width=920, height=70)
xf.grid(row=1, column=0, sticky="W", padx=10, pady=10)

label = tk.Label(xf, text=it[6])
label.place(relx=.06, rely=0.04, anchor=tk.W)

choose_1 = tk.Button(text=it[7], command=lambda: threading.Thread(target=getChatFromCSV).start())
choose_1.grid(row=1, column=0, sticky="W", padx=30, pady=10)

xf_2 = tk.Frame(window, relief=tk.GROOVE, borderwidth=2, width=920, height=70)
xf_2.grid(row=2, column=0, sticky="W", padx=10, pady=10)

choose_dest_label = tk.Label(text="", bg="white", fg="black", borderwidth=2, relief="groove", anchor='w')
choose_dest_label.configure(width=55)
choose_dest_label.grid(row=2, column=0, sticky="W", padx=185, pady=10)

choose_dest = tk.Button(text=it[10], command=lambda: threading.Thread(target=selectFolder).start())
choose_dest.grid(row=2, column=0, sticky="W", padx=30, pady=10)

choose_label = tk.Label(text="", bg="white", fg="black", borderwidth=2, relief="groove", anchor='w')
choose_label.configure(width=55)
choose_label.grid(row=1, column=0, sticky="W", padx=185, pady=10)

choose_2 = tk.Button(text=it[8], command=lambda: threading.Thread(target=getChatLabels).start())
choose_2.grid(row=2, column=0, sticky="E", padx=30, pady=10)

save_media = tk.IntVar()
c1 = tk.Checkbutton(window, text='Scraping media', variable=save_media, onvalue=1, offvalue=0)
c1.grid(row=1, column=0, stick="E", padx=200, pady=10)

archiviate = tk.IntVar()
c2 = tk.Checkbutton(window, text=it[9], variable=archiviate, onvalue=1, offvalue=0)
c2.grid(row=1, column=0, stick="E", padx=30, pady=10)

v = tk.StringVar()
v.trace('w', change_language)
comboLang = ttk.Combobox(window, textvar=v, state="readonly",
                         values=[
                             "English",
                             "Italian"])
comboLang.grid(row=0, column=0, sticky="W", padx=10, pady=10)
comboLang.set('Italian')

if __name__ == '__main__':
    window.mainloop()
    # done: rimuovere profilo 1, commentare per renderlo più generale
    # pyinstaller --noconsole --icon=whatsapp.ico --name WhatsAppScraper --onefile main.py
    # Whatsappscraper_v.1

    # TODO:

    # test su più media in csv
    # Whatsappscraper_v.1
    # 3) commentare codice + alleggerire codice (pulizia)  -- opzionale: test sonar

    # done:
    # orari con timezone
    # media scaricato che rimandi al media
    # zip con tutte le conversaz
    # zip con tutti i media
    # 1) gestire data e ora in anteprima con fuso orario e formato orario
    # file excel con log + hash ---> in progress
    # file csv con log + hash