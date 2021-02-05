import shutil
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import time
import base64
import os
from datetime import datetime
import urllib.request
import hashlib
import tkinter as tk

WAIT_FOR_CHAT_TO_LOAD = 20  # in secondi
SAVE_MEDIA = True
message_dic = {}

user = os.environ["USERNAME"]


def openChrome():
    options = webdriver.ChromeOptions()  # stabilire connessione con whatsapp web
    options.add_experimental_option("prefs", {
        "download.default_directory": r"C:\Users" + "\\" + user + "\PycharmProjects\\whatsappScraperProgetto\\Download",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument(
        "user-data-dir=C:\\Users\\" + user + "\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1")  # crea un nuovo profilo utente in chrome per scansionare il qw
    driver = webdriver.Chrome(options=options, executable_path='chromedriver.exe')

    # apre whatsapp nel browser
    driver.get('http://web.whatsapp.com')
    wait = WebDriverWait(driver, 600)
    time.sleep(15)
    return driver


def readMessages(name, driver):
    message_dic[name] = []
    f = open(name+'.csv', 'w', encoding='utf-8')
    f.write('Data,Ora,Mittente,Messaggio')
    #scroll  = driver.find_element_by_xpath("//*[@id='main']/div[3]/div/div").send_keys(Keys.CONTROL + Keys.HOME) #funziona parz
    trovato = False
    while trovato == False:
        try:
            element = driver.find_element_by_xpath("//*[@id='main']/div[3]/div/div/div[2]/div[2]/div/div/div/span/span")
            trovato = True
        except:
            driver.find_element_by_xpath("//*[@id='main']/div[3]/div/div").send_keys(Keys.CONTROL + Keys.HOME)
            trovato = False
    #driver.execute_script("return arguments[0].scrollIntoView(true);", element)

    messageContainer = driver.find_elements_by_xpath("//div[contains(@class,'message-')]")
    for messages in messageContainer:
        if SAVE_MEDIA == True:
            try:
                vocal = messages.find_element_by_xpath(".//span[contains(@data-testid,'ptt-status')]")
                vocal.click()
                downContext = messages.find_element_by_xpath(".//span[contains(@data-testid,'down-context')]")
                downContext.click()
                button = WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located(
                    (By.XPATH, "//*[@id='app']/div/span[4]/div/ul/li[3]/div")))
                button.click()
                # MOVE DEGLI AUDIO NELLA CARTELLA GIUSTA
                # time.sleep(5)
                # src = r"C:\Users" + "\\" + user + "\\Download\\"
                # dest = 'Scraped/' + name + '/Media/'
                # if not os.path.exists(dest):
                #     os.makedirs(dest)
                # files = os.listdir(src)
                # for audio in files:
                #     shutil.move(src + audio, dest)
            except:pass
        try:
            message = messages.find_element_by_xpath(
                ".//span[contains(@class,'selectable-text invisible-space copyable-text')]"
            ).text
            emojis = messages.find_elements_by_xpath(
                ".//img[contains(@class,'selectable-text invisible-space copyable-text')]")

            if len(emojis) != 0:
                for emoji in emojis:
                    message = message + emoji.get_attribute("data-plain-text")
            info = messages.find_element_by_xpath(".//div[contains(@data-pre-plain-text,'[')]")
            info = info.get_attribute("data-pre-plain-text")
            finalMessage = csvCreator(info,message)
            f.write(finalMessage)
            f.write('\n')
            message_dic[name].append(finalMessage)

        except NoSuchElementException:  # solo emoji nel messaggio
            try:
                for emoji in messages.find_elements_by_xpath(
                        ".//img[contains(@class,'selectable-text invisible-space copyable-text')]"
                ):
                    info = messages.find_element_by_xpath(".//div[contains(@data-pre-plain-text,'[')]")
                    info = info.get_attribute("data-pre-plain-text")
                    message = emoji.get_attribute("data-plain-text")
                    finalMessage = csvCreator(info,message)
                    message_dic[name].append(finalMessage)
            except NoSuchElementException:
                pass
    f.close()
    hashing(name,'.csv')   #Creazione del doppio hash del file contenente le chat

    return

def hashing(name,extension):
    hash_md5 = hashlib.md5()
    sha512 = hashlib.sha512()
    with open(name+extension, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    md5Digest = hash_md5.hexdigest()
    sha512.update(md5Digest.encode('utf-8'))
    sha512_digest = sha512.hexdigest()
    f_hash = open('hashing.txt', 'a', encoding='utf-8')
    f_hash.write(name+extension+","+sha512_digest)
    f_hash.write('\n')
    return


def csvCreator(info,message):
    oraData = info[info.find('[') + 1: info.find(']')+1]
    ora = oraData[oraData.find('[') + 1: oraData.find(',')]
    data = oraData[oraData.find(' ')+ 1: oraData.find(']')]
    mittente =  info.split(']')[1].strip()
    mittente = mittente.split(':')[0].strip()
    finalMessage = data+","+ora+","+mittente+","+message
    return finalMessage

def getChatLabels():
    driver = openChrome()
    chatLabels = []
    recentList = driver.find_elements_by_xpath('//*[@id="pane-side"]/div[1]/div/div/div')
    for label in recentList:
        chatLabels.append(label)
    chatLabels.sort(key=lambda x: int(x.get_attribute('style').split("translateY(")[1].split('px')[0]), reverse=False)
    iterChatList(chatLabels, driver)
    driver.close()

    resultLabel = tk.Label(window, text="Scraping terminato con successo!", font=("Helvetica", 10))
    resultLabel.grid(row=4, column=0, stick="W", padx=10, pady=10)

    return


def iterChatList(chatLabels, driver):
    for chat in chatLabels:
        chat.click()
        time.sleep(WAIT_FOR_CHAT_TO_LOAD)
        label = chat.find_elements_by_xpath('//*[@id="main"]/header/div[2]/div[1]/div/span')
        chatName = label[0].get_attribute('title')
        if len(chatName) == 0:
            label = chat.find_elements_by_xpath('//*[@id="main"]/header/div[2]/div[1]/div/span/span') # se il nome contiene un'emoji, va nello span di sotto
            chatName = label[0].get_attribute('title')
        readMessages(chatName, driver)
        if SAVE_MEDIA == True:
            saveMedia(chatName, driver)
    return


def saveMedia(name, driver):
    menu = driver.find_element_by_xpath("(//div[@title=\"Menu\"])[2]")
    menu.click()
    # time.sleep(20)
    try:
        info = driver.find_element_by_xpath("//div[@title=\"Info gruppo\"]")
    except:
        info = driver.find_element_by_xpath("//div[@title=\"Info contatto\"]")
    time.sleep(5)
    info.click()
    media_xpath = '//span[text()="Media, link e documenti"]'
    media = driver.find_element_by_xpath(media_xpath)
    media.click()
    saveImgVidAud(name, driver)
    saveDoc(name, driver)

    return


def saveDoc(name, driver):
    docs_xpath = '//button[text()="Documenti"]'
    docs = driver.find_element_by_xpath(docs_xpath)
    docs.click()
    dir = 'Scraped/' + name + '/Docs/'
    if not os.path.exists(dir):
        os.makedirs(dir)
    try:
        noMedia_xpath ="//span[text()='Nessun documento']"
        time.sleep(5)
        WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(noMedia_xpath))
        noMedia = True
    except:
        noMedia = False

    if noMedia == False:
        try:
            doc_list= driver.find_elements_by_xpath("//*[@id='app']/div/div/div[2]/div[3]/span/div/span/div/div[2]/span/div/div/div/div/div/div/div/div/div/a/div[1]")
        except:
            print("Impossibile scaricare il file")
        for document in doc_list :
            a_tag = document.find_element_by_xpath("..") #prende il tag <a> superiore che contiene il nome del file
            fileName = a_tag.get_attribute("Title")
            fileName = fileName[9:-1] #il tag <a> contiene la parola Scarica, la rimuovo per ottenere solo il noe del file
            document.click()
            time.sleep(5)
            nameWithoutExt = fileName[:-4]
            hashing('Download/'+ nameWithoutExt, '.pdf')
            #move_to_download_folder("C:\\Users\\"+user+"\\Download\\", fileName, dir) #lo salva in download, quindi lo sposto nella cartella giusta
    return
#REMOVE
def move_to_download_folder(downloadPath, FileName, dest):
    got_file = False
    while got_file == False:
        try:
            currentFile = downloadPath+FileName
            got_file = True
        except:
            print ("Attendere il completamento del download")
    time.sleep(5)
    fileDestination = dest+FileName
    os.rename(currentFile, fileDestination)
    return


def saveImgVidAud(name, driver):
    dir = 'Scraped/'+ name + '/Media/'
    if not os.path.exists(dir):
        os.makedirs(dir)
    try:
        noMedia_xpath ="//span[text()='Nessun media']"
        time.sleep(5)
        WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(noMedia_xpath))
        noMedia = True
    except:
        noMedia = False

    if noMedia == False:
        try:
            image_xpath = "//*[@id='app']/div/div/div[2]/div[3]/span/div/span/div/div[2]/span/div/div/div/div[1]/div[2]/div/div[1]/div" #1 media
            image = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(image_xpath))
        except:
            try:
                image_xpath = "//*[@id='app']/div/div/div[2]/div[3]/span/div/span/div/div[2]/span/div/div/div/div[1]/div[2]" #2 media
                image = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(image_xpath))
            except:
                image_xpath = "//*[@id='app']/div/div/div[2]/div[3]/span/div/span/div/div[2]/span/div/div/div/div[1]/div[2]/div" #diversi media
                image = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(image_xpath))

        lastimg = 'false'
        driver.execute_script("arguments[0].click();", image)

        while (lastimg == 'false'):
            i = datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
            try:
                image_xpath = "//*[@id='app']/div/span[3]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div[2]/img"
                image = driver.find_element_by_xpath(image_xpath)
                mediaType = '.jpg'
            except:
                try:
                    image_xpath = "//*[@id='app']/div/span[3]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div[1]/video"
                    image = driver.find_element_by_xpath(image_xpath)
                    mediaType = '.mp4'
                except:
                    try:
                        audio_xpath = "//*[@id='app']/div/span[3]/div/div/div[2]/div[2]/div[2]/audio"
                        image = driver.find_element_by_xpath(audio_xpath)
                        mediaType = '.mpeg'
                    except:
                        noMedia = True
                        print("altro tipo di media")
            if noMedia == False:
                image_src = image.get_attribute("src")
                final_image = get_file_content_chrome(driver, image_src)
                time.sleep(5)
                filename = dir + str(i) + mediaType
                base64_img_bytes = final_image.encode('utf-8')
                with open(filename, 'wb') as file_to_save:
                    decoded_image_data = base64.decodebytes(base64_img_bytes)
                    file_to_save.write(decoded_image_data)
                    hashing('Scraped/'+ name + '/Media/'+str(i),mediaType)
                nextButton = driver.find_element_by_xpath('//*[@id="app"]/div/span[3]/div/div/div[2]/div[2]/div[1]/div')
                lastimg = nextButton.get_attribute("aria-disabled")
                nextButton.click()
            else:
                lastimg = True
        close_image_button = driver.find_element_by_xpath('//div[@title="Chiudi"]')
        close_image_button.click()
        return

def get_file_content_chrome(driver, uri):
    result = driver.execute_async_script("""
    var uri = arguments[0];
    var callback = arguments[1];
    var toBase64 = function(buffer){for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)};
    var xhr = new XMLHttpRequest();
    xhr.responseType = 'arraybuffer';
    xhr.onload = function(){ callback(toBase64(xhr.response)) };
    xhr.onerror = function(){ callback(xhr.status) };
    xhr.open('GET', uri);
    xhr.send();
    """, uri)
    if type(result) == int:
        raise Exception("Request failed with status %s" % result)
    return result

def getChatFromCSV(path, driver):
    recentList = driver.find_elements_by_xpath('//*[@id="pane-side"]/div[1]/div/div/div')
    chatLabels = []
    f = open(path, 'r')
    line = f.read()
    name = line.split(",")
    for i in range (0, len(name)):
        if 'str' in name[i]:
            break
        for chat in recentList:
            chat.click()
            time.sleep(WAIT_FOR_CHAT_TO_LOAD)
            label = chat.find_elements_by_xpath('//*[@id="main"]/header/div[2]/div[1]/div/span')
            chatName = label[0].get_attribute('title')
            if name[i] in chatName:
                chatLabels.append(chat)
    chatLabels.sort(key=lambda x: int(x.get_attribute('style').split("translateY(")[1].split('px')[0]),
                         reverse=False)
    return chatLabels


window = tk.Tk()
window.geometry("900x550")
window.title("Whatapp Scraper")
window.grid_columnconfigure(0, weight=1)
window.resizable(False, False)

title = tk.Label(window, text="Whatapp Scraper", font=("Helvetica", 24))
title.grid(row=0, column=0, sticky="N", padx=20, pady=10)

credit_label = tk.Label(window, text="Authors: Domenico Palmisano and Francesca Pollicelli")
credit_label.grid(row=1, column=0, stick="N", padx=0, pady=0)

chooses = tk.Label(window, text="Cosa vuoi fare?", font=("Helvetica", 12))
chooses.grid(row=2, column=0, sticky="W", padx=10, pady=20)

choose_1 = tk.Button(text="Caricare Lista Contatti")
choose_1.grid(row=3, column=0, sticky="W", padx=10, pady=10)

choose_2 = tk.Button(text="Scraping Contatti", command=getChatLabels)
choose_2.grid(row=3, column=0, sticky="W", padx=160, pady=10)


if __name__ == '__main__':
    window.mainloop()
    '''
    choise = input ("Cosa vuoi fare?\n"
                    "1)Caricare la lista dei contatti: premi 1\n"
                    "Fare scraping di ogni contatto: premi 2")

    if choise == '2':
        # mettere in una lista tutti i label delle varie chat per scorrerli successivamente
    if choise == '1':
        file = input("Inserisci il percorso del file csv")
        chatLabels = getChatFromCSV(file, driver) vedere da dove prendere driver
'''


    # TODO: spostare tutti i gile in un'unica cartella
    # TODO: VELOCIZZARE PROCESSO DI CHAT DA FILE
    # TODO: LEGGERE CHAT ARCHIVIATE
    # TODO: CHECK DEGLI ERRORI DI CHIUSURA, CHIUDERE DRIVER NEGLI EXCEPT DEI TRY CATCH
    # TODO: IMPLEMENTARE SUPPORTO AD ALTRI BROWSER
    # TODO: cancellare feedback quando lo scraping è terminato (cliccando uno dei due pulsanti)
    # TODO: sistemare problema download doc multipli
    # TODO: ridurre tempo attesa caricamento media
    # TODO: cambiare cartella di download di default


