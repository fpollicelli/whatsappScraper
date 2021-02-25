from datetime import datetime, date
from time import gmtime, strftime
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
        else:language = 'italian'
    except:
        language = 'italian'
    return

def findChromeDriver():
    for root, dirs, files in os.walk(chromeDriverPath):
        if "chromedriver.exe" in files:
            return os.path.join(root, "chromedriver.exe")


def openChrome():
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
    #'''
    options.add_argument(
        "user-data-dir=C:\\Users\\" + user + "\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1")  # crea un nuovo profilo utente in chrome per scansionare il qw
    #'''
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
            text ='impossibile connettersi a WhatsApp Web'
        else: text ='unable to connect to WhatsApp Web'
        output_label_2.configure(text=text)
        log_dict[getDateTime()] = text
        window.update()
        f_hash = open(dir + 'hashing.csv', 'a', encoding='utf-8')
        for key, value in log_dict.items():
            f_hash.write('\n'+value+','+key+',,')
        f_hash.flush();
        f_hash.close()
        driver.close()
    return driver

def readMessages(name, driver):
    if language == 'italian':
        text="scraping dei messaggi in corso..."
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
                        (By.XPATH, ".//div[contains(@title,'Scarica')]")))
                else:
                    button = WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located(
                        (By.XPATH, ".//div[contains(@title,'Download')]")))
                button.click()
            except:
                pass
        try:
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
                tree.insert("", 0, values=(data, ora, mittente, trimMessage + '...'))
            else:
                tree.insert("", 0, values=(data, ora, mittente, message))
            finalMessage = data + "," + ora + "," + mittente + "," + message
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
                        tree.insert("", 0, values=(data, ora, mittente, trimMessage + '...'))
                    else:
                        tree.insert("", 0, values=(data, ora, mittente, message))
                    finalMessage = data + "," + ora + "," + mittente + "," + message
                    window.update()
                    f.write(finalMessage)
                    f.write('\n')
            except NoSuchElementException:
                pass
    f.close()
    if language == 'italian':
        text="generazione del doppio hash della chat in corso..."
    else:
        text = 'generating double hash...'
    output_label_2.configure(text=text)
    log_dict[getDateTime()] = text
    window.update()
    hashing(pyExePath + '\\Scraped\\Chat\\' + name, '.csv')  # Creazione del doppio hash del file contenente le chat
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

def hashing(name, extension):
    dateTime = getDateTime()
    hash_md5 = hashlib.md5()
    has_sha512 = hashlib.sha512()
    with open(name + extension, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    md5Digest = hash_md5.hexdigest()
    with open(name + extension, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            has_sha512.update(chunk)
    sha512_digest = has_sha512.hexdigest()
    dir = pyExePath + '\\Scraped\\Hash\\'
    if not os.path.exists(dir):
        os.makedirs(dir)
        f_hash = open(dir + 'hashing.csv','w', encoding='utf-8')
        if language == 'italian':
            f_hash.write("Nome file,timestamp,md5,sha512")
            f_hash.flush()
            f_hash.close()
        else:
            f_hash.write("File name,timestamp,md5,sha512")
            f_hash.flush()
            f_hash.close()

    f_hash = open(dir + 'hashing.csv','a', encoding='utf-8')
    f_hash.write('\n'+name+extension+','+dateTime+','+md5Digest+','+sha512_digest)
    f_hash.flush(); f_hash.close()
    return

def getChatLabels():

    if language == 'italian':
        text="apertura di WhatsApp Web in corso..."
    else:
        text = 'opening WhatsApp Web...'

    output_label_2.configure(text=text)
    log_dict[getDateTime()] = text
    tree.delete(*tree.get_children())
    driver = openChrome()
    chatLabels = []
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
                        text="errore: contatto non trovato"
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
            text="scraping terminato con successo"
        else:
            text = "scraping successfully completed"

        output_label_2.configure(text=text)
        log_dict[getDateTime()] = text
        choose_label.configure(text="")
        window.update()
        f_hash = open(dir + 'hashing.csv', 'a', encoding='utf-8')
        for key, value in log_dict.items():
            f_hash.write('\n'+value+','+key+',,')
        f_hash.flush()
        f_hash.close()
        driver.close()
        path = pyExePath + '/Scraped'
        path = os.path.realpath(path)
        os.startfile(path)
        del NAMES[:]
        return

    if (archiviate.get() == 1):
        if language == 'italian':
            text="spostamento delle chat archiviate in generali in corso..."
        else:
            text = "moving archived chats in general..."
        output_label_2.configure(text=text)
        log_dict[getDateTime()] = text
        window.update()
        chatLabelsDeArch = moveArchiviate(driver)

    recentList = driver.find_elements_by_xpath('//*[@id="pane-side"]/div[1]/div/div/div')
    for label in recentList:
        chatLabels.append(label)
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
    dir = pyExePath + '\\Scraped\\Hash\\'
    f_hash = open(dir + 'hashing.csv', 'a', encoding='utf-8')
    for key, value in log_dict.items():
        f_hash.write('\n'+value+','+key+',,')
    f_hash.flush()
    f_hash.close()
    driver.close()
    path = pyExePath + '/Scraped'
    path = os.path.realpath(path)
    os.startfile(path)
    del NAMES[:]
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
                hashingMedia()
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
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@title,'Info gruppo')]"))
            )
            info = driver.find_element_by_xpath("//div[contains(@title,'Info gruppo')]")
            info.click()
        else:
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@title,'Group info')]"))
            )
            info = driver.find_element_by_xpath("//div[contains(@title,'Group info')]")
            info.click()
    except:
        try:
            if language == 'italian':
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@title,'Info contatto')]"))
                )
                info = driver.find_element_by_xpath("//div[contains(@title,'Info contatto')]")
                info.click()
            else:
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@title,'Contact info')]"))
                )
                info = driver.find_element_by_xpath("//div[contains(@title,'Contact info')]")
                info.click()
        except:
            try:
                if language == 'italian':
                    element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[contains(@title,'Info lista broadcast')]"))
                    )
                    info = driver.find_element_by_xpath("//div[contains(@title,'Info lista broadcast')]")
                    info.click()
                else:
                    element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[contains(@title,'Broadcast list info')]"))
                    )
                    info = driver.find_element_by_xpath("//div[contains(@title,'Broadcast list info')]")
                    info.click()
            except:
                if language == 'italian':
                    text="impossibile localizzare le info"
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
            text="impossibile localizzare i media"
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
        text="apertura dei media in corso..."
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
                    downloadXpath = "//div[@title='Scarica']"
                else:
                    downloadXpath = "//div[@title='Download']"

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

#SELECT FOLDER
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
    menuDots.click()
    archiv = driver.find_element_by_xpath("//*[@id='side']/header/div[2]/div/span/div[3]/span/div/ul/li[4]/div")
    archiv.click()
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

def hashingMedia():
    directory = pyExePath + '/Scraped/Media/'
    for filename in os.listdir(directory):
        file = os.path.splitext(filename)
        hashing(directory + file[0], file[1])
    return

def disableEvent(event):
    return "break"

it = ['Data','Ora','Mittente','Messaggio','scraper pronto',
            'Autori: Domenico Palmisano e Francesca Pollicelli','Opzioni',
            'Caricare lista contatti','Avvia scraper','Scraping chat archiviate','Cartella di destinazione']
en = ['Date','Time','Sender','Message','scraper ready',
            'Authors: Domenico Palmisano and Francesca Pollicelli','Options',
            'Load contact list','Start scraper','Scraping archived chats','Destination folder']

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

tree = ttk.Treeview(window, show="headings", columns=(it[0],it[1], it[2], it[3]), height=14)
tree.heading(it[0], text=it[0], anchor=tk.W)
tree.heading(it[1], text=it[1], anchor=tk.W)
tree.heading(it[2], text=it[2], anchor=tk.W)
tree.heading(it[3], text=it[3], anchor=tk.W)
tree.column('#1', minwidth=80, stretch=False, width=80)
tree.column('#2', minwidth=60, stretch=False, width=60)
tree.column('#3', minwidth=170, stretch=False, width=170)
tree.column('#4', minwidth=565, stretch=True, width=565)
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
v.trace('w',change_language)
comboLang = ttk.Combobox(window,textvar=v, state="readonly",
                            values=[
                                    "English",
                                    "Italian"])
comboLang.grid(row=0, column=0, sticky="W", padx=10, pady=10)
comboLang.set('Italian')
if __name__ == '__main__':
    window.mainloop()
    # per creazione eseguibile: rimuovere profilo 1, commentare per renderlo più generale
    # pyinstaller --noconsole --name WhatsAppScraper --onefile main.py

    #TODO:
    # 3) commentare codice + alleggerire codice (pulizia)  -- opzionale: test sonar





    #DONE:
    # push icona nel repo
    # 4) aggiungere pulsante per scegliere cartella Scraped -- in progress
    # 5) sistemare visualizzazione del percorso della cartella di destinazione
    # 1) hashing.csv
    # 2) intestazione hashing + log: NomeChat_timestamp_md5_sha512 con fuso
    # 5) doppio hash: sha,md5
    # 6) salvare log in hashing.csv (a fine scraping)
    # 7) creare esempio contatto.csv
    # 8) opzionale: scraper dal messaggio più recente (per non attendere)
        #NOTA: rimettere in ordine i messaggi nei csv?