from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time ; import tkinter.ttk as ttk ; from tkinter import filedialog
import os ; import hashlib ; import tkinter as tk ; import threading

message_dic = {}
user = os.environ["USERNAME"]
window = tk.Tk()
window.geometry("900x650")
window.title("Whatapp Scraper")
window.grid_columnconfigure(0, weight=1)
window.resizable(False, False)
pyExePath = os.path.dirname(os.path.abspath(__file__))

tree = ttk.Treeview(window, columns=("Data", "Ora", "Mittente",'Messaggio'), height = 18)

tree.heading('Data', text="Data",anchor = tk.W)
tree.heading('Ora', text="Ora",anchor = tk.W)
tree.heading('Mittente', text="Mittente",anchor = tk.W)
tree.heading('Messaggio', text="Messaggio",anchor = tk.W)
tree.column('#0', minwidth=0,stretch=tk.NO, width=0)
tree.column('#1', minwidth=90,stretch=tk.NO, width= 90)
tree.column('#2',minwidth=70,stretch=tk.NO, width= 70)
tree.column('#3',minwidth=150,stretch=tk.NO,width= 150)
tree.column('#4',minwidth=150,stretch=tk.NO,width= 566)
style = ttk.Style(window)
tree.grid(row=5, column=0, padx=10, pady=10, stick='NEWS')


vsbar = tk.Scrollbar(window, orient=tk.VERTICAL, command=tree.yview)
vsbar.place(x=870, y=231, height=360)
tree.configure(yscrollcommand=vsbar.set)

style.theme_use("clam")
style.configure("Treeview", background="white",
                fieldbackground="white", foreground="white")

def findChromeDriver():
    for root, dirs, files in os.walk(pyExePath):
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
    #CREAZIONE PROFILO SOLO PER DEBUG
    options.add_argument(
       "user-data-dir=C:\\Users\\" + user + "\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1")  # crea un nuovo profilo utente in chrome per scansionare il qw
    driver = webdriver.Chrome(options=options, executable_path=findChromeDriver())

    # apre whatsapp nel browser
    driver.get('http://web.whatsapp.com')
    try:
        element = WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="side"]/header/div[1]/div/img'))
        )
    except:
        output_label_2.configure(text='impossibile connettersi a WhatsApp Web')
        window.update()
        driver.close()
    return driver


def readMessages(name, driver):
    output_label_2.configure(text="scraping dei messaggi in corso...")
    window.update()
    message_dic[name] = []
    dir = pyExePath+'/Scraped/Chat/'
    if not os.path.exists(dir):
        os.makedirs(dir)
    f = open(dir+name+'.csv', 'w', encoding='utf-8')
    f.write('Data,Ora,Mittente,Messaggio\n')
    trovato = False
    while trovato == False:
        try:
            element = driver.find_element_by_xpath("//*[@id='main']/div[3]/div/div/div[2]/div[2]/div/div/div/span/span")
            trovato = True
        except:
            driver.find_element_by_xpath("//*[@id='main']/div[3]/div/div").send_keys(Keys.CONTROL + Keys.HOME)
            trovato = False

    messageContainer = driver.find_elements_by_xpath("//div[contains(@class,'message-')]")
    for messages in messageContainer:
        if (save_media.get() == 1):
            output_label_2.configure(text="salvataggio degli audio in corso...")
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
                            EC.presence_of_element_located((By.XPATH, ".//span[contains(@data-testid,'audio-play')]"))
                        )
                    except:
                        output_label_2.configure(text="Impossibile scaricare l'audio")
                        window.update()
                except: pass
                downContext = messages.find_element_by_xpath(".//span[contains(@data-testid,'down-context')]")
                downContext.click()
                button = WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located(
                    (By.XPATH, ".//div[contains(@title,'Scarica')]")))
                button.click()
            except:pass
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
            ora = oraData[oraData.find('[') + 1: oraData.find(',')]
            data = oraData[oraData.find(' ') + 1: oraData.find(']')]
            mittente = info.split(']')[1].strip()
            mittente = mittente.split(':')[0].strip()
            tree.insert("", 0, values=(data, ora, mittente, message))
            finalMessage = data + "," + ora + "," + mittente + "," + message

            window.update()
            f.write(finalMessage)
            f.write('\n')
            message_dic[name].append(finalMessage)

        except NoSuchElementException:  # solo emoji nel messaggio
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
                    tree.insert("", 0, values=(data, ora, mittente, message))
                    finalMessage = data + "," + ora + "," + mittente + "," + message
                    window.update()
                    f.write(finalMessage)
                    f.write('\n')
                    message_dic[name].append(finalMessage)
            except NoSuchElementException:
                pass
    f.close()
    output_label_2.configure(text="generazione del doppio hash della chat in corso...")
    window.update()
    hashing(pyExePath+'/Scraped/Chat/'+name,'.csv')   #Creazione del doppio hash del file contenente le chat
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
    dir = pyExePath+'/Scraped/Hash/'
    if not os.path.exists(dir):
        os.makedirs(dir)
    f_hash = open(dir + 'hashing.txt', 'a', encoding='utf-8')
    f_hash.write(name+extension+","+sha512_digest)
    f_hash.write('\n')
    return

def getChatLabels():
    output_label_2.configure(text="apertura di WhatsApp Web in corso...")
    window.update()
    tree.delete(*tree.get_children())
    driver = openChrome()
    chatLabels = []
    if (archiviate.get() == 1):
        output_label_2.configure(text="spostamento delle chat archiviate in generali in corso...")
        window.update()
        chatLabelsDeArch = moveArchiviate(driver)
    recentList = driver.find_elements_by_xpath('//*[@id="pane-side"]/div[1]/div/div/div')
    for label in recentList:
        chatLabels.append(label)
    chatLabels.sort(key=lambda x: int(x.get_attribute('style').split("translateY(")[1].split('px')[0]), reverse=False)
    iterChatList(chatLabels, driver)
    if (archiviate.get() == 1):
        output_label_2.configure(text="spostamento delle chat de-archiviate in archivio in corso...")
        window.update()
        archiviaChat(chatLabelsDeArch,driver)
    output_label_2.configure(text="scraping terminato con successo!")
    window.update()
    driver.close()
    path = pyExePath+'/Scraped'
    path = os.path.realpath(path)
    os.startfile(path)
    return

def archiviaChat(chatLabelsDeArch,driver):
    for chat in chatLabelsDeArch:
        chatElement = driver.find_element_by_xpath("//span[contains(@title,'" + chat + "')]")
        actionChains = ActionChains(driver)
        actionChains.context_click(chatElement).perform()
        archivia = driver.find_element_by_xpath('//*[@id="app"]/div/span[4]/div/ul/li[1]/div')
        archivia.click()
        time.sleep(10)
    return

def iterChatList(chatLabels, driver):
    output_label_2.configure(text="caricamento delle chat in corso...")
    window.update()
    for chat in chatLabels:
        chat.click()
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/header/div[2]/div[1]/div/span'))
            )
            label = chat.find_elements_by_xpath('//*[@id="main"]/header/div[2]/div[1]/div/span')
        except:
            output_label_2.configure(text="Impossibile caricare le chat")
            window.update()

        chatName = label[0].get_attribute('title')
        if len(chatName) == 0:
            label = chat.find_elements_by_xpath('//*[@id="main"]/header/div[2]/div[1]/div/span/span') # se il nome contiene un'emoji, va nello span di sotto
            chatName = label[0].get_attribute('title')
        readMessages(chatName, driver)
        if (save_media.get() == 1):
            saveMedia(chatName, driver)
            output_label_2.configure(text="generazione del doppio hash dei media in corso...")
            window.update()
            hashingMedia()
    return


def saveMedia(name, driver):
    menu = driver.find_element_by_xpath("(//div[@title='Menu'])[2]")
    menu.click()
    info = driver.find_element_by_xpath('//*[@id="main"]')
    try:
        element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@title,'Info gruppo')]"))
        )
        info = driver.find_element_by_xpath("//div[contains(@title,'Info gruppo')]")
        info.click()
    except:
        try:
            element = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@title,'Info contatto')]"))
            )
            info = driver.find_element_by_xpath("//div[contains(@title,'Info contatto')]")
            info.click()
        except:
            try:
                element = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@title,'Info lista broadcast')]"))
                )
                info = driver.find_element_by_xpath("//div[contains(@title,'Info lista broadcast')]")
                info.click()
            except:
                output_label_2.configure(text="non riesco a cliccare su info")
                window.update()

    try:
        element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Media, link e documenti']"))
        )
        media = driver.find_element_by_xpath("//span[text()='Media, link e documenti']")
        media.click()
        saveImgVidAud(name, driver)
        saveDoc(name, driver)
    except:
        output_label_2.configure(text="non riesco a cliccare su media")
        window.update()
    return

def saveDoc(name, driver):
    output_label_2.configure(text="salvataggio dei documenti in corso...")
    window.update()
    time.sleep(3)
    docs_xpath = '//button[text()="Documenti"]'
    docs = driver.find_element_by_xpath(docs_xpath)
    docs.click()
    dir = pyExePath+'/Scraped/Media/'
    if not os.path.exists(dir):
        os.makedirs(dir)
    try:
        noMedia_xpath ="//span[text()='Nessun documento']"
        time.sleep(5)
        WebDriverWait(driver, 5).until(lambda driver: driver.find_element_by_xpath(noMedia_xpath))
        noMedia = True
    except:
        noMedia = False

    if noMedia == False:
        try:
            doc_list= driver.find_elements_by_xpath("//*[@id='app']/div/div/div[2]/div[3]/span/div/span/div/div[2]/span/div/div/div/div/div/div/div/div")
        except:
            doc_list = driver.find_element_by_xpath("//*[@id='app']/div/div/div[2]/div[3]/span/div/span/div/div[2]/span/div/div/div/div/div/div/div/div")
        for document in doc_list:
            a_tag = document.find_element_by_xpath('.//button') #prende il tag <a> superiore che contiene il nome del file
            fileName = a_tag.get_attribute("Title")
            fileName = fileName[9:-1] #il tag <a> contiene la parola Scarica, la rimuovo per ottenere solo il noe del file
            document.click()
    return

def saveImgVidAud(name, driver):
    output_label_2.configure(text="apertura dei media in corso...")
    window.update()
    dir = pyExePath+'/Scraped/Media/'
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
            image_xpath = "//div[contains(@style,'background-image')]" #1 media
            image = WebDriverWait(driver, 5).until(lambda driver: driver.find_element_by_xpath(image_xpath))
        except:noMedia= True
        lastimg = 'false'
        driver.execute_script("arguments[0].click();", image)
        while (lastimg == 'false'):
            try:
                downloadXpath = "//div[@title='Scarica']"
                download = driver.find_element_by_xpath(downloadXpath)
                download.click()
            except:pass
            if noMedia == False:
                try:
                    element = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/span[3]/div/div/div[2]/div[2]/div[1]/div'))
                    )
                    nextButton = driver.find_element_by_xpath('//*[@id="app"]/div/span[3]/div/div/div[2]/div[2]/div[1]/div')
                    lastimg = nextButton.get_attribute("aria-disabled")
                    nextButton.click()
                except:
                    lastimg = True
            else:
                lastimg = True
        #time.sleep(3)
        #close_image_button = driver.find_element_by_xpath('//div[@title="Chiudi"]')
        #close_image_button.click()
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

def getChatFromCSV():
    output_label_2.configure(text="ricerca delle chat selezionate in corso...")
    tree.delete(*tree.get_children())
    filename = filedialog.askopenfilename(initialdir="/",title="Seleziona un file",filetypes=(("CSV files","*.csv*"),("all files","*.*")))
    nomeFile = os.path.basename(filename)
    if nomeFile != "":
        choose_label.configure(text=nomeFile)
        choose_label.configure(fg="black")
        driver = openChrome()
        chatLabels = []
        f = open(filename, 'r')
        line = f.read()
        names = line.split(",")
        for i in range(0, len(names)):
            if 'str' in names[i]:
                break
            try:
                found = driver.find_element_by_xpath(".//span[contains(@title,'"+names[i]+"')]")
                chatLabels.append(found)
            except: #se non lo trovo nelle principali cerco in archivio
                menuDots = driver.find_element_by_xpath("//*[@id='side']/header/div[2]/div/span/div[3]/div/span")
                menuDots.click()
                archiv = driver.find_element_by_xpath("//*[@id='side']/header/div[2]/div/span/div[3]/span/div/ul/li[4]/div")
                archiv.click()
                try:
                    found = driver.find_element_by_xpath(".//span[contains(@title,'" + names[i] + "')]")
                    actionChains = ActionChains(driver)
                    actionChains.context_click(found).perform()
                    estrai = driver.find_element_by_xpath('//*[@id="app"]/div/span[4]/div/ul/li[1]/div')
                    estrai.click()
                    time.sleep(10)
                    goBack = driver.find_element_by_xpath(
                    '//*[@id="app"]/div/div/div[2]/div[1]/span/div/span/div/header/div/div[1]/button/span')
                    goBack.click()
                    found = driver.find_element_by_xpath(".//span[contains(@title,'" + names[i] + "')]")
                    chatLabels.append(found)
                except:
                    output_label_2.configure(text="Errore: non risultano presenti chat con uno o più dei contatti caricati")

        iterChatList(chatLabels, driver)
        output_label_2.configure(text="scraping terminato con successo.")
        window.update()
        driver.close()
    return


def moveArchiviate(driver):
    menuDots = driver.find_element_by_xpath("//*[@id='side']/header/div[2]/div/span/div[3]/div/span")
    menuDots.click()
    archiv = driver.find_element_by_xpath("//*[@id='side']/header/div[2]/div/span/div[3]/span/div/ul/li[4]/div")
    archiv.click()
    chatLabels = []
    recentList = driver.find_elements_by_xpath('//*[@id="app"]/div/div/div[2]/div[1]/span/div/span/div/div/div[1]/div/div/div')
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
        time.sleep(10)
    goBack = driver.find_element_by_xpath('//*[@id="app"]/div/div/div[2]/div[1]/span/div/span/div/header/div/div[1]/button/span')
    goBack.click()
    return chatNames

def hashingMedia():
    directory = pyExePath+'/Scraped/Media/'
    for filename in os.listdir(directory):
        file = os.path.splitext(filename)
        hashing(directory + file[0], file[1])
    return
title = tk.Label(window, text="Whatapp Scraper", font=("Helvetica", 24))
title.grid(row=0, column=0, sticky="N", padx=20, pady=10)

credit_label = tk.Label(window, text="Autori: Domenico Palmisano e Francesca Pollicelli")
credit_label.grid(row=6, column=0, stick="E", padx=10, pady=0)

choose_1 = tk.Button(text="Caricare Lista Contatti",command=lambda:threading.Thread(target=getChatFromCSV).start())
choose_1.grid(row=2, column=0, sticky="E", padx=250, pady=10)

choose_label = tk.Label(text="____________________________________", bg="white", fg="white")
choose_label.grid(row=2, column=0, sticky="E", padx=50, pady=10)

choose_2 = tk.Button(text="Scraping di tutti i contatti", command=lambda:threading.Thread(target=getChatLabels).start())
choose_2.grid(row=2, column=0, sticky="W", padx=50, pady=10)

output_label = tk.Label(text="Log: ")
output_label.grid(row=3, column=0, sticky="W", padx=50, pady=10)

output_label_2 = tk.Label(text="scraper pronto")
output_label_2.grid(row=3, column=0, sticky="W", padx=100, pady=10)

save_media = tk.IntVar()
c1 = tk.Checkbutton(window, text='Scraping media',variable=save_media, onvalue=1, offvalue=0)
c1.grid(row=1, column=0, stick="W", padx=50, pady=10)

archiviate = tk.IntVar()
c2 = tk.Checkbutton(window, text='Scraping chat archiviate',variable=archiviate, onvalue=1, offvalue=0)
c2.grid(row=1, column=0, stick="W", padx=200, pady=10)


if __name__ == '__main__':
    window.mainloop()
    #todo: scrollbar
    #todo: riorganizzare interfaccia
    #todo: test programma su diversi pc
    #todo: velocizzare download immagini
    #todo: rimuovere profilo 1, commentare per renderlo più generale
    #todo: rimuovere console di debug da applicativo