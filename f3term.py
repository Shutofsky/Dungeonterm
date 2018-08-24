import pygame, sys, time, random, string, sqlite3
import json
#from datetime import timedelta
#from pygame.locals import *
import pygame.mixer
import paho.mqtt.client as mqtt
import socket
#import asyncio
import threading #Tupitsyn
import time #

mqtt_broker_ip = "localhost"
mqtt_broker_port = 1883
mqttFlag = 0
my_ip = ""

wordBase = []
wordPass = ''
garbLen = 408 # Длина общеего массива 12*17 дважды
garbStr = ''
posWords = []

powerStatus = 1
termHackStatus = 0
termLockStatus = 0
wordNum = 12
wordLen = 8
numTries = 4
wordCount = 0


myTime = 30
dY = 0 # Уйдет внутрь функции перерисовки, если не используется вне её.
dX = 0 #
deltaY = 23 #
deltaX = 12 #
statX = 0 #
statY = 0 #
changeParmStatus = 0
menuStatus = 0
menuScrNum = 0
fieldArea = []
textArea = []
statWord = []
wordChoice = []
servAreaTxt = ' ' * 192
servArea = []
idAst = [67, 65, 63, 61]

lasHlPos = 0
lastHlLen = 0
lastMenuHlPos = 0
lastMenuHlEnd = 0
activeWords = 0


start_time = time.time()
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()
(x,y,fontSize) = (10,40,20)
sX = 10
sY = 20
fontColor = (0xAA,0xFF,0xC3)
fontHlColor = (0x00,0x08,0x00)
bgHlColor = (0xAA,0xFF,0xC3)
myFont = pygame.font.SysFont("DejaVu Sans Mono", fontSize)
bgColor = (0,8,0)
screen = pygame.display.set_mode((1222,653),0,32)#TODO pygame.FULLSCREEN
pygame.display.toggle_fullscreen()
pygame.display.set_caption("ROBCO RIT-300 TERMINAL")
background = pygame.image.load('f3term_alt.png').convert() #Один раз загружаем картинку в начале.
background_offline = pygame.image.load('load_off.png').convert()
inverseBar_strings = (
    "                ",
    " oooooooooooooo ",
    " oooooooooooooo ",
    " oooooooooooooo ",
    " oooooooooooooo ",
    " oooooooooooooo ",
    " oooooooooooooo ",
    " oooooooooooooo ",
    " oooooooooooooo ",
    " oooooooooooooo ",
    " oooooooooooooo ",
    " oooooooooooooo ",
    " oooooooooooooo ",
    " oooooooooooooo ",
    " oooooooooooooo ",
    "                ")
clock = pygame.time.Clock()
clock.tick(15)
cursor, mask = pygame.cursors.compile(inverseBar_strings,'x','.','o')
pygame.mouse.set_cursor((16,16),(7,5),cursor,mask)
screen.blit(background_offline, (0, 0))
pygame.display.flip()

#Tupitsyn
db_parameters = {} #Игровые параметры
is_db_updating = False #Флаг, обновляется ли состояние в данный момент. Флаг выставляется процессом обновления БД.
forceClose = False # Флаг, который смотрят все потоки, означающий закрытие игры.
lineY = -200
lineTime = 0
dbCheckInterval = 2# Интервал проверки БД в секундах

#END

class outSym(object):
    def __init__(self,x,y,width,height,char):
        self.data = [x,y,width,height,char]
        self.r = pygame.Rect(self.data[0]-self.data[2]/2, self.data[1]-self.data[3]/2, self.data[2], self.data[3])
        self.bg = background.subsurface(self.r)
    def __getitem__(self,item):
        return self.data[item]
    def __setitem__(self, idx, value):
        self.data[idx] = value
    @property
    def x(self):
        return self.data[0]
    @property
    def y(self):
        return self.data[1]
    @property
    def width(self):
        return self.data[2]
    @property
    def height(self):
        return self.data[3]
    @property
    def char(self):
        return self.data[4]
    def output(self):
        textImage = myFont.render(self.data[4],True,fontColor)
        textRect = textImage.get_rect()
        textRect.center = (self.data[0], self.data[1])
        screen.blit(textImage, textRect)
        pygame.display.update(self.r)
    def clear(self):
        screen.blit(self.bg, (self.data[0]-self.data[2]/2, self.data[1]-self.data[3]/2))
        pygame.display.update(self.r)
    def highlight(self):
        textImage = myFont.render(self.data[4],True,fontHlColor,bgHlColor)
        textRect = textImage.get_rect()
        textRect.center = (self.data[0], self.data[1])
        screen.blit(textImage, textRect)
        pygame.display.update(self.r)
    def bgreturn(self):
        textImage = myFont.render(self.data[4],True,fontColor)
        textRect = textImage.get_rect()
        textRect.center = (self.data[0], self.data[1])
        screen.blit(self.bg, (self.data[0]-self.data[2]/2, self.data[1]-self.data[3]/2))
        screen.blit(textImage, textRect)
        pygame.display.update(self.r)

def millis():
    return (time.time() - start_time) * 1000.0

def on_connect(client, userdata, flags, rc):
    client.subscribe("TERM/#")

def on_message(client, userdata, msg):
    global my_ip
    # print str(msg.payload)
    commList = str(msg.payload).split('/')
    if commList[0] != my_ip and commList[0] != '*':
        return()
    conn = sqlite3.connect('ft.db')
    req = conn.cursor()
    if commList[1] == 'RESETDB':
        req.execute("UPDATE params SET value = 'NO' WHERE name='isLocked'")
        req.execute("UPDATE params SET value = 'NO' WHERE name='isHacked'")
        req.execute("UPDATE params SET value = 'NO' WHERE name='isPowerOn'")
        req.execute("UPDATE params SET value = 'NO' WHERE name='isLockOpen'")
        req.execute("UPDATE params SET value = 'NO' WHERE name='isLevelDown'")
        req.execute("UPDATE params SET value = 'NO' WHERE name='isLockOpen'")
        req.execute("UPDATE params SET value = 'NO' WHERE name='isLevelDown'")
        req.execute("UPDATE params SET value = 8 WHERE name='wordLength'")
        req.execute("UPDATE params SET value = 4 WHERE name='attempts'")
        req.execute("UPDATE params SET value = 10 WHERE name='wordsPrinted'")
    elif commList[1] == 'POWER':
        req.execute("UPDATE params SET value = ? WHERE name='isPowerOn'", [commList[2]])
    elif commList[1] == 'LOCK':
        req.execute("UPDATE params SET value = ? WHERE name='isLocked'", [commList[2]])
    elif commList[1] == 'HACK':
        req.execute("UPDATE params SET value = ? WHERE name='isHacked'", [commList[2]])
    elif commList[1] == 'ISLOCK':
        req.execute("UPDATE params SET value = ? WHERE name='isLockOpen'", [commList[2]])
    elif commList[1] == 'DOLOCK':
        req.execute("UPDATE params SET value = ? WHERE name='isLockOpen'", [commList[2]])
    elif commList[1] == 'ISLEVEL':
        req.execute("UPDATE params SET value = ? WHERE name='isLevelDown'", [commList[2]])
    elif commList[1] == 'DOLEVEL':
        req.execute("UPDATE params SET value = ? WHERE name='isLevelDown'", [commList[2]])
    elif commList[1] == 'ATTEMPTS':
        req.execute("UPDATE params SET value = ? WHERE name='attempts'", [commList[2]])
    elif commList[1] == 'DIFFICULTY':
        req.execute("UPDATE params SET value = ? WHERE name='wordLength'", [commList[2]])
    elif commList[1] == 'WORDSNUM':
        req.execute("UPDATE params SET value = ? WHERE name='wordsPrinted'", [commList[2]])
    elif commList[1] == 'MENULIST':
        req.execute("UPDATE params SET value = ? WHERE name='menuList'", [commList[2]])
    elif commList[1] == 'MAILHEAD':
        req.execute("UPDATE params SET value = ? WHERE name='msgHead'", [commList[2].decode('utf-8','ignore')])
    elif commList[1] == 'MAILBODY':
        req.execute("UPDATE params SET value = ? WHERE name='msgBody'", [commList[2].decode('utf-8','ignore')])
    elif commList[1] == 'PING':
        client.publish("TERMASK",my_ip+'/PONG')
    elif commList[1] == 'GETDB':
        req.execute("SELECT value FROM params WHERE name='isLocked'")
        S = req.fetchone()
        client.publish("TERMASK",my_ip+'/Lock_status/'+S[0])
        req.execute("SELECT value FROM params WHERE name='isHacked'")
        S = req.fetchone()
        client.publish("TERMASK",my_ip+'/Hack_status/'+S[0])
	# print "TERMASK",my_ip+'/Hack_status/'+S[0]
        req.execute("SELECT value FROM params WHERE name='menuList'")
        S = req.fetchone()
        client.publish("TERMASK",my_ip+'/Menulist/'+S[0])
        req.execute("SELECT value FROM params WHERE name='menuList'")
        S = req.fetchone()
        client.publish("TERMASK",my_ip+'/Menulist/'+S[0])
        req.execute("SELECT value FROM params WHERE name='msgHead'")
        S = req.fetchone()
        client.publish("TERMASK",my_ip+'/Msg_head/'+S[0])
        req.execute("SELECT value FROM params WHERE name='msgBody'")
        S = req.fetchone()
        client.publish("TERMASK",my_ip+'/Msg_body/'+S[0])
    conn.commit()
    conn.close()

def wordHl(wordPos,wordSize):
    global lastHlPos
    global lastHlLen
    i = 0
    while i < wordSize:
        textArea[i + wordPos].highlight()
        i += 1
    lastHlPos = wordPos
    lastHlLen = wordSize
    return

def wordBg():
    global lastHlPos
    global lastHlLen
    i = 0
    while i < lastHlLen:
        textArea[i + lastHlPos].bgreturn()
        i += 1
    lastHlPos = 0
    lastHlLen = 0
    return

def menuHl(wordStartPos,wordEndPos):
    global lastMenuHlPos
    global lastMenuHlEnd
    i = wordStartPos
    while i < wordEndPos:
        servArea[i].highlight()
        i += 1
    lastMenuHlPos = wordStartPos
    lastMenuHlEnd = wordEndPos
    return

def menuBg():

    def moveLine():
        global lineY
        global lineTime
        line = pygame.image.load('line.png')
        while True:
            screen.blit(line,(x,lineY))
            lineTime += 1
            if lineTime > 5:
                lineY = lineY + 8 if lineY <= 800 else -200
                lineTime = 0
            pygame.display.update()


    global lastMenuHlPos
    global lastMenuHlEnd
    i = lastMenuHlPos
    while i < lastMenuHlEnd:
        servArea[i].bgreturn()
        i += 1

    return

def statWordWrite(myX, myY, typeStr):
    global deltaX
    global deltaY
    global dX
    global dY
    i = 0
    for char in typeStr:
        statWord.append(outSym(568 + deltaX * dX, myY + dY, sX, sY, char))
        statWord[i].output()
        i += 1
        dX += 1
    dY = 0
    dX = 0

def statWordClear():
    i = 0
    l = len(statWord)
    while i < l:
        statWord[i].clear()
        i += 1
    i = l - 1
    while i >= 0:
        del statWord[i]
        i -= 1
    return

def servWrite(typeStr):
    global deltaX
    global deltaY
    i = 0
    j = 0
    while i < 16:
        while j < 12:
            servArea.append(outSym(568 + deltaX * j, 125 + deltaY * i, sX, sY, typeStr[i*12+j]))
            servArea[i*12+j].output()
            j += 1
        i += 1
        j = 0
    return

def servClear():
    i = 0
    l = len(servArea)
    while i < l:
        servArea[i].clear()
        i += 1
    i = l - 1
    while i >= 0:
        del servArea[i]
        i -= 1
    return

def typeWriter(myX, myY, typeStr, interval, t):
    myTime = interval
    global deltaX
    global deltaY
    global dX
    global dY
    global statX
    global statY
    global forceClose

    done = True
    startTime = millis()
    myLen = len(t)
    i = 0
    j = 0
    flag = 0
    prtSnd = pygame.mixer.Sound('f3termprint.wav')
    while done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                forceClose = True
                return
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    forceClose = True
                    return
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # print "Enter"
                    myTime = interval / 4
        if flag == 0:
            char = typeStr[i]
            flag = 1
            if char == '\n':
                dY += deltaY
                dX = 0
            else:
                if char == '\r':
                    dX = 0
                else:
                    prtSnd.play(loops = 0, maxtime = int(myTime))
                    t.append(outSym(3+myX + deltaX * dX, myY + dY, sX, sY, char))
                    t[j + myLen].output()
                    j += 1
                    dX += 1
        curTime = millis()
        if curTime >= (startTime + myTime):
            i += 1
            if i >= len(typeStr):
                done = False
            flag = 0
            startTime = curTime
    statX = myX + deltaX * dX
    statY = myY + dY
    dX = 0
    dY = 0
    return

def killAllText(t):
    global dX
    global dY
    i = 0
    l = len(t)
    while i < l:
        t[i].clear()
        i += 1
    i = l - 1
    while i >= 0:
        del t[i]
        i -= 1
    dX = 0
    dY = 0
    return

def allscrReset():
    global servAreaTxt
    global lastHlPos
    global lastHlLen
    servClear()
    servAreaTxt = 192 * ' '
    statWordClear()
    lastHlPos = 0
    lastHlLen = 0
    killAllText(fieldArea)
    killAllText(textArea)
    #background = pygame.image.load('f3term_alt.png')
    screen.blit(background, (0, 0))
    pygame.display.flip()

def compareWords(word_1, word_2):
    i = 0
    count = 0
    for char in word_1:
        if char == word_2[i]:
            count += 1
        i += 1
    return count

#Tupitsyn

def Ton_message(client, userdata, msg):
    global my_ip
    try:
        print(msg.payload.decode("UTF-8",errors="ignore"))
        commList = msg.payload.decode("UTF-8",errors="ignore").split('/')
        print(commList[0],my_ip)
        if commList[0] != my_ip and commList[0] != '*':
            return
        if commList[1] == 'RESETDB':#TODO Reset
            print("TODO Reset")
        elif commList[1] == 'PING':
            client.publish("TERMASK",my_ip+'/PONG')
        elif commList[1] == 'GETDB':
            if len(commList) > 2:
                if commList[2] == "ALL" or commList[2] == "*" or commList[2] == "GETDB":
                    client.publish("TERMASK", my_ip+'/DB_INFO/'+json.dumps(db_parameters))
            else:
                client.publish("TERMASK", my_ip+'/DB_INFO/'+json.dumps(db_parameters))
        elif commList[1] == "UPDATEDB":
            try:
                pars = json.loads(commList[2])
                updateDBParameters(pars)
                client.publish("TERMASK",my_ip+'/UPDATE_OK')
            except:
                client.publish("TERMASK",my_ip+'/UPDATE_FAILED')
    except Exception as err:
        client.publish("TERMASK", my_ip+"/COMMAND_FAILED/"+str(err))

def readDBParameters(checkInterval=2):
    #Tupitsyn
    global db_parameters
    global is_db_updating
    global forceClose
    while True:
        if forceClose:
            break
        if not is_db_updating:
            print("Reading DB.")
            is_db_updating = True
            conn = sqlite3.connect(r'ft.db')
            req = conn.cursor()
            req.execute('SELECT name,value FROM params')
            params = req.fetchall()
            conn.close()
            for data in params:
                if data[0] == "msgBody":
                    val = data[1].split("\n")
                else:
                    if data[1].isdigit():
                        val = int(data[1])
                    else:
                        if data[1].upper() == "YES":
                            val = True
                        elif data[1].upper() == "NO":
                            val = False
                        else:
                            val = data[1]
                db_parameters.update({data[0]:val})
            is_db_updating = False
        time.sleep(checkInterval)

def updateDBParameters(parameters):
    """Принимает словарь, где ключ - поле в базе, значение ключа - значение, которое нужно записать в базу."""
    global is_db_updating
    while is_db_updating:
        pass
    try:
        is_db_updating = True
        conn = sqlite3.connect('ft.db')
        req = conn.cursor()
        print(parameters)
        for par in parameters.keys():
            req.execute("UPDATE params SET value = '{1}' WHERE name='{0}'".format(par,parameters[par]))
        conn.commit()
        conn.close()
    except Exception as err:
        print(err)
    finally:
        is_db_updating = False

def loadWordsAndSelectPassword():
    words = []
    with open('words'+str(wordLen)+'.txt','r') as f:
        for word in f:
            words.append(word.strip("\n\t "))
    count = len(words)
    pwd = words[random.randint(0, count-1)]
    return words,count,pwd

def TwordsParse(words,wordLen,pwd,count=12):
    wordListMax = [] #Слова, максимально похожие по расположению букв на слово-пароль.
    wordListZero = [] #Слова, совершенно не имеющие одинаково расположенных букв с паролем.
    wordListOther = [] #
    wordDelta = 2 #Начинаем перебор слов. Ищем слова, максимально близкие по расположению букв к слову-паролю.
    while len(wordListMax) == 0:
        i = 0
        for word in words:
            if word != pwd:
                c = TcompareWords(word, pwd)
                if c == 0:
                    wordListZero.append(word)
                elif c == (wordLen - 1):
                    wordListMax.append(word)
                elif c == (wordLen - wordDelta):
                        wordListMax.append(word)
                else:
                    wordListOther.append(word)
        wordDelta += 1

    #selectWordsOther
    wordListSelected = []#Слова, которые будут использоваться непосредственно в игре.
    wordListSelected.append(pwd) #Пароль.
    wordListSelected.append(wordListMax[random.randint(0,len(wordListMax)-1)]) #Одно слово, максимально близкое к паролю.
    wordPos = random.randint(0, len(wordListZero) - 1) #Одно слово, которое совершенно не похоже на пароль.
    wordListSelected.append(wordListZero[wordPos])
    i = 0
    while i < count - 3: # Добавляем ещё слов из общего списка.
        word = wordListOther[random.randint(0, len(wordListOther) - 1)]
        if word not in wordListSelected:
            wordListSelected.append(word)
            i += 1
    random.shuffle(wordListSelected) #Перемешиваем.
    #end
    print(wordListSelected)
    print(pwd)
    return wordListSelected, pwd

def TcompareWords(fWord, sWord):
    i = 0
    count = 0
    for char in fWord:
        if char == sWord[i]:
            count += 1
        i += 1
    return count

def TformOutString(wordLen,wordNum,wordList,garbLen):
    #Функция формирует строку для вывода в терминал. Строка представляет собой 'мусорные' символы,
    #  между которыми вставлены слова для подбора пароля.
    #Заменил глобальные переменные на локальные, в остальном без изменений.
    posWords = []
    garbStr = ""
    lenArea = int(garbLen / wordNum)
    i = 0
    while i < wordNum:
        startPos = random.randint(i * lenArea, i * lenArea + (lenArea - wordLen - 1) )
        j = i * lenArea
        while j < startPos:
            garbStr += random.choice(string.punctuation)
            j += 1
        posWords.append(j)
        garbStr += wordList[i]
        garbStr += random.choice(string.punctuation)
        j += wordLen + 1
        while j < (i + 1) * lenArea:
            garbStr += random.choice(string.punctuation)
            j += 1
        i += 1
    i = len(garbStr)
    while i < garbLen:
        garbStr += random.choice(string.punctuation)
        i += 1
    return garbStr, posWords

def drawScreen():
    #Пока нигде не используется.
    global forceClose
    def TtypeWriter(myX, myY, typeStr, interval, t):
        myTime = interval
        dY = 0
        dX = 0
        deltaY = 23
        deltaX = 12
        statX = 0
        statY = 0
        done = True
        startTime = millis()
        myLen = len(t)
        i = 0
        j = 0
        flag = 0
        prtSnd = pygame.mixer.Sound('f3termprint.wav')
        while done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    forceClose = True
                    return
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        quit()
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # print "Enter"
                        myTime = interval / 4
            if flag == 0:
                char = typeStr[i]
                flag = 1
                if char == '\n':
                    dY += deltaY
                    dX = 0
                else:
                    if char == '\r':
                        dX = 0
                    else:
                        prtSnd.play(loops = 0, maxtime = int(myTime))
                        t.append(outSym(myX + deltaX * dX, myY + dY, sX, sY, char))
                        t[j + myLen].output()
                        j += 1
                        dX += 1
            curTime = millis()
            if curTime >= (startTime + myTime):
                i += 1
                if i >= len(typeStr):
                    done = False
                flag = 0
                startTime = curTime
        statX = myX + deltaX * dX
        statY = myY + dY
        dX = 0
        dY = 0
        return

    def TkillAllText(t):
        global dX
        global dY
        i = 0
        l = len(t)
        while i < l:
            t[i].clear()
            i += 1
        i = l - 1
        while i >= 0:
            del t[i]
            i -= 1
        dX = 0
        dY = 0
        return

def TgameScreen():
    #Бывш. mainScreen
    global wordNum
    global statX
    global statY
    global deltaX
    global deltaY
    global db_parameters
    global forceClose
    global wordLen
    global numTries
    leftBrakes = ('[', '(', '{', '<')
    rightBrakes = (']', ')', '}', '>')
    wordLen = db_parameters['wordLength']
    wordNum = db_parameters['wordsPrinted']
    numTries = db_parameters['attempts']
    hlPos = 0
    hlLen = 0
    selectedWords = []
    selectedPass = ""

    #Выбор нового пароля непосредственно перед игрой.
    wordBase, wordCount, wordPass = loadWordsAndSelectPassword()
    selectedWords, selectedPass = TwordsParse(wordBase, wordLen, wordPass)
    garbStr, posWords = TformOutString(wordLen, wordNum, selectedWords, garbLen)


    hello1Text = "МИНИСТЕРСТВО ОБОРОНЫ СССР\n\n" + \
    "ЗАГРУЗКА ДИАЛОГОВОЙ СРЕДЫ ПРИМУС\n\n" + \
    "ТЕРМИНАЛ ИСКРА-9876\n\n" + \
    "....... УСТАНОВКА ПРАВ ДОСТУПА К ФАЙЛАМ ....... ОК\n" + \
    "........НАСТРОЙКА ТОЧКИ ВХОДА....... ОК\n\n" + \
    "НАЧАЛЬНЫЙ ЗАГРУЗЧИК НС-1056\n" + \
    "СТАРТУЮ ОС СИНТЕЗ\n" + \
    "СИНТЕЗ-ОС ВЕРСИИ 3.46 (С) ФИНТЕХ\n" + \
    ".......... ЗАГРУЗКА ......... ОК\n" + \
    "ПАМЯТЬ 64 КБ - ОК\n" + \
    "ЯДРО СИНТЕЗ-ОС ......... ЗАГРУЖЕНО\n" + \
    "СЕНТЕЗ-ОС СЛУЖЕБНЫЙ РЕЖИМ ...... ЗАГРУЖЕН\n\n" + \
    "КОРРЕКТИРОВКА ПОЛЬЗОВАТЕЛЕЙ ....... ЗАПУЩЕНА"
    killAllText(fieldArea)
    #background = pygame.image.load('f3term_alt.png')
    screen.blit(background, (0, 0))
    pygame.display.flip()
    typeWriter(10, 10, hello1Text, 20, fieldArea)
    time.sleep(0.5)
    killAllText(fieldArea)

    activeWords = wordNum - 1

    i = 0
    triesAst = ''
    helloText = ''
    allscrReset()
    while i < numTries:
        triesAst += '* '
        i += 1
    typeWriter(10, 10,
               "ОС СИНТЕЗ ДС ПРИМУС (TM) ФИНТЕХ \nВВЕДИТЕ ПАРОЛЬ\n\n{0} ПОПЫТОК {1}\n\n".format(numTries,
                                                                                                     triesAst),
               10, fieldArea)
    i = 0
    startHex = random.randint(0x1A00, 0xFA00)
    workY = statY
    while i < 17:
        hexLeft = '{0:#4X}  '.format(startHex + i * 12)
        statX = 10
        typeWriter(statX, statY, hexLeft, 10, fieldArea)
        typeWriter(statX, statY, garbStr[i * 12:i * 12 + 12] + "\n", 10, textArea)
        i += 1
    statY = workY
    i = 0
    while i < 17:
        statX = 248
        hexRight = '    {0:#4X}  '.format(startHex + (i + 17) * 12)
        typeWriter(statX, statY, hexRight, 10, fieldArea)
        typeWriter(statX, statY, garbStr[(i + 17) * 12:(i + 17) * 12 + 12] + "\n", 10, textArea)
        i += 1
    typeWriter(538, 493, " >", 10, fieldArea)
    i = 0

    prevWord = ''
    selWord = ''
    servAreaTxt = ' ' * 12 * 16
    done = False
    tmpLet = []

    wrdSnd = pygame.mixer.Sound('f3termprint.wav')

    bMouse = 0
    firstpos = 0

    servWrite(servAreaTxt)

    mssTime = millis()

    while done == False:
        mscTime = millis()
        if (mscTime >= (mssTime + 3000)):
            mssTime =  mscTime
            # Читаем базу
            if not db_parameters["isPowerOn"] or db_parameters["isLocked"] or db_parameters["isHacked"]:
                return
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    forceClose = True
                    return
        (curX,curY) = pygame.mouse.get_pos()
        (b1,b2,b3) = pygame.mouse.get_pressed()
        numstr = int(curY / deltaY)
        numchr = int(curX / deltaX)
        splText = helloText.split('\n',int(600/deltaY))
        curpos = -1
        selWord=''
        if(numstr >= 5 and numstr <= 21 and numchr >=8 and numchr <= 43):
            if(numchr >= 8 and numchr <= 19):
                curpos = (numstr - 5) * 12 + numchr - 8
            else:
                if(numchr >= 32 and numchr <= 43):
                    curpos = 12 * 17 + (numstr - 5) * 12 + numchr - 32
            if(garbStr[curpos].isalpha()):
                i=0
                curchr=garbStr[curpos]
                while(curchr.isalpha() and (curpos+i) >= 0):
                    i -= 1
                    curchr = garbStr[curpos+i]
                i += 1
                firstpos = curpos + i
                hlPos = firstpos
                hlLen = wordLen
                startWord = firstpos
                i = 0
                curchr = garbStr[firstpos]
                while(curchr.isalpha() and (firstpos+i) <= 407):
                    selWord += curchr
                    i += 1
                    curchr = garbStr[firstpos + i]
                if prevWord != selWord:
                    wrdSnd.play()
                    bMouse = 1
                    wordBg()
                    wordHl(hlPos,hlLen)
                    statWordClear()
                    statWordWrite(statX,statY,selWord)
                    prevWord = selWord
            else:
                if garbStr[curpos] in leftBrakes:
                    selWord = 'brakes'
                    leftBorder = curpos
                    rightBorder = int((curpos)/12+1)*12 - 1
                    idxBrake = curpos
                    numBrake = leftBrakes.index(garbStr[curpos])
                    while idxBrake <= rightBorder:
                        if garbStr[idxBrake] == rightBrakes[numBrake]:
                            hlPos = curpos
                            hlLen = idxBrake + 1 - curpos
                            selWord = garbStr[leftBorder:idxBrake + 1]
                            break
                        if garbStr[idxBrake].isalpha():
                            break
                        idxBrake += 1
                else:
                    if garbStr[curpos] in rightBrakes:
                        selWord = 'brakes'
                        rightBorder = curpos
                        leftBorder = int((curpos)/12)*12
                        idxBrake = curpos
                        numBrake = rightBrakes.index(garbStr[curpos])
                        while idxBrake >= leftBorder:
                            if garbStr[idxBrake] == leftBrakes[numBrake]:
                                hlPos = idxBrake
                                hlLen = rightBorder+1-idxBrake
                                selWord = garbStr[idxBrake:rightBorder+1]
                                break
                            if garbStr[idxBrake].isalpha():
                                break
                            idxBrake -= 1
                if ((selWord != prevWord and selWord != 'brakes') or (selWord != prevWord and prevWord != '')):
                    if selWord == '' or selWord == 'brakes':
                        wordBg()
                        statWordClear()
                        selWord = ''
                    else:
                        wrdSnd.play()
                        bMouse = 1
                        wordBg()
                        statWordClear()
                        statWordWrite(statX, statY, selWord)
                        wordHl(hlPos,hlLen)
                    prevWord = selWord
        else:
            statWordClear()
            wordBg()
            prevWord = ''
            selWord = ''
        if (b1 == True and bMouse == 1 and selWord != '' and selWord != 'brakes'):
        # Обрабатываем выбор слова
            # print selWord
            # print secretWord
            if selWord[0].isalpha():
                # выбрано слово
                i = 0
                rightLet = compareWords(selWord, wordPass)
                if rightLet == wordLen:
                    prtLet = "СОВПАЛ"
                else:
                    prtLet = 'БУКВ '+str(rightLet) + ' ИЗ ' + str(wordLen)
                servAreaTxt = servAreaTxt[24:] + (selWord + ' ' * (12 - len(selWord)) + prtLet + ' ' * (12 - len(prtLet)))
                servClear()
                servWrite(servAreaTxt)
                selWord = ''
                bMouse = 0
                i = 0
                if rightLet != wordLen:
                    # Списываем попытку
                    numTries -= 1
                    ntX = fieldArea[53].x
                    ntY = fieldArea[53].y
                    fieldArea[53].clear()
                    fieldArea[53] = outSym(ntX, ntY, sX, sY, str(numTries))
                    fieldArea[53].output()
                    fieldArea[idAst[numTries]].clear()
                    if numTries == 0:
                        # Залочились
                        updateDBParameters({"isLocked":"YES"})
                        db_parameters["isLocked"] = True
                        pygame.time.wait(1000)
                        #if mqttFlag:
                        #    client.publish('TERMASK', my_ip + '/Lock_status/YES')
                        return
                else:
                    # Угадали слово
                    updateDBParameters({"isHacked":"YES"})
                    db_parameters["isHacked"] = True
                    pygame.time.wait(1000)
                    #if mqttFlag:
                    #    client.publish('TERMASK', my_ip + '/Hack_status/YES')
                    return
            else:
                # выбрана последовательность знаков в скобках
                # заменяем спецзнаки точками, не трогая правую скобку
                i = 0
                while i < lastHlLen - 1:
                    garbStr = garbStr[:lastHlPos+i] + '.' + garbStr[lastHlPos + i + 1:]
                    textArea[lastHlPos + i].clear()
                    ntX = textArea[lastHlPos + i].x
                    ntY = textArea[lastHlPos + i].y
                    textArea[lastHlPos + i] = outSym(ntX, ntY, sX, sY, '.')
                    textArea[lastHlPos + i].output()
                    i += 1
                resBrakes = random.randint(1,4) # Вероятность сброса попыток - 1/4
                if resBrakes == 1:
                    # Восстанавливаем число попыток
                    tmpWord = 'RESET TRIES '
                    bMouse = 0
                    servAreaTxt = servAreaTxt[12:] + tmpWord
                    servClear()
                    servWrite(servAreaTxt)
                    numTries = 4
                    ntX = fieldArea[53].x
                    ntY = fieldArea[53].y
                    fieldArea[53].clear()
                    fieldArea[53] = outSym(ntX, ntY, sX, sY, str(numTries))
                    fieldArea[53].output()
                    i = 0
                    while i < 4:
                        fieldArea[idAst[i]].output()
                        i += 1
                else:
                    # Убираем "заглушку"
                    tmpWord = 'REMOVE DUMMY'
                    bMouse = 0
                    servAreaTxt = servAreaTxt[12:] + tmpWord
                    servClear()
                    servWrite(servAreaTxt)
                    if activeWords > 0:
                        # Не только пароль на экране
                        resBrakes = random.randint(0,activeWords - 1)
                        activeWords -= 1
                        i = 0
                        while i < wordLen:
                            txt = garbStr[:posWords[resBrakes]+i]
                            txt1 = garbStr[posWords[resBrakes] + i + 1:]
                            garbStr = garbStr[:posWords[resBrakes]+i] + '.' + garbStr[posWords[resBrakes] + i + 1:]
                            textArea[posWords[resBrakes]+i].clear()
                            ntX = textArea[posWords[resBrakes]+i].x
                            ntY = textArea[posWords[resBrakes]+i].y
                            textArea[posWords[resBrakes]+i] = outSym(ntX, ntY, sX, sY, '.')
                            textArea[posWords[resBrakes]+i].output()
                            i += 1
                        del posWords[resBrakes]
                    else:
                        # Восстанавливаем число попыток
                        # print "Reset Tries"
                        tmpWord = 'RESET TRIES '
                        bMouse = 0
                        servAreaTxt = servAreaTxt[12:] + tmpWord
                        servClear()
                        servWrite(servAreaTxt)
                        numTries = 4
                        ntX = fieldArea[53].x
                        ntY = fieldArea[53].y
                        fieldArea[53].clear()
                        fieldArea[53] = outSym(ntX, ntY, sX, sY, str(numTries))
                        fieldArea[53].output()
                        i = 0
                        while i < 4:
                            fieldArea[idAst[i]].output()
                            i += 1

def TmenuScreen():
    global powerStatus
    global termHackStatus
    global termLockStatus
    global menuStatus
    global statX
    global statY
    global db_parameters
    global forceClose

    if menuStatus == 1:
        return
    helloText = "ПОДТВЕРЖДАЮ ДОСТУП .... ДОСТУП АДМИНИСТРАТОРА ПОДТВЕРЖДЁН\n\n" + \
                "ДОБРО ПОЖАЛОВАТЬ, АДМИНИСТРАТОР\n\n" + \
                "ВЫБЕРИТЕ ДЕЙСТВИЕ:\n\n\n"

    menuItems = db_parameters["menuList"].split(",")
    menuText = ' ' * 12
    menuCount = 0
    menuList = []
    menuPos = []
    for mChar in menuItems:
        if int(mChar) == 1:
            menuItem = u'ОТКРЫТЬ ЗАМОК'
            menuList.append(8 + menuCount * 2)
            menuPos.append(len(menuText) - menuCount*2)
            menuText += menuItem + '\n\n' + ' ' * 12
            menuCount += 1
        if int(mChar) == 2:
            menuItem = u'ПОНИЗИТЬ СТАТУС ТРЕВОГИ'
            menuList.append(8 + menuCount * 2)
            menuPos.append(len(menuText) - menuCount*2)
            menuText += menuItem + '\n\n' + ' ' * 12
            menuCount += 1
        if int(mChar) == 3:
            menuItem = u'ПРОСМОТРЕТЬ СООБЩЕНИЯ'
            menuList.append(8 + menuCount * 2)
            menuPos.append(len(menuText) - menuCount*2)
            menuText += menuItem + '\n\n' + ' ' * 12
            menuCount += 1
    allscrReset()
    typeWriter(10, 10, helloText, 30, fieldArea)
    txtY = statY
    typeWriter(10, txtY, menuText, 30, textArea)
    selItem = -1
    hlStatus = 0
    bPressed = 0
    wrdSnd = pygame.mixer.Sound('f3termword.wav')
    done = True
    mssTime = millis()
    while done:
        mscTime = millis()
        if (mscTime >= (mssTime + 3000)):
            mssTime =  mscTime

            if not db_parameters["isPowerOn"] or db_parameters["isLocked"] or not db_parameters["isHacked"]:
                return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                forceClose = True
                return
        (curX,curY) = pygame.mouse.get_pos()
        (b1,b2,b3) = pygame.mouse.get_pressed()
        numStr = int(curY / deltaY) + 1
        numChr = int(curX / deltaX)
        splMenu = menuText.split('\n\n')
        curpos = -1
        if((numStr >=8 and numStr <= 8+(menuCount-1)*2) and  (numChr >= 12 and numChr <= 54)):
            i = 0
            for menuStr in menuList:
                if(numStr == menuStr):
                    if menuItems[i] != selItem:
                        wordBg()
                        selItem = menuItems[i]
                        hlStatus = 0
                    if hlStatus == 0:
                        wordHl(menuPos[i], len(splMenu[i]) - 12)
                        wrdSnd.play()
                        hlStatus = 1
                i += 1
        else:
            wordBg()
            hlStatus = 0
        if (b1 == True and bPressed == 0):
            if selItem == '3':
                # Выбрано прочтение послания
                #menuStatus = 1
                TletterScreen()
                return
            if selItem == '1':
                # Выбрано открыть замок
                if not db_parameters["isLockOpen"]:
                    updateDBParameters({"isLockOpen":"YES"})
                    pygame.time.wait(100)
                    if mqttFlag:
                         client.publish('TERMASK', my_ip + '/DOLOCKOPEN/YES')
            if selItem == '2':
                # Выбрано снизить уровень тревоги
                if not db_parameters["isLevelDown"]:
                    updateDBParameters({"isLevelDown":"YES"})
                    pygame.time.wait(100)
                    if mqttFlag:
                         client.publish('TERMASK', my_ip + '/DOLEVELDOWN/YES')

def TletterScreen():

    global forceClose

    def showLetterPage(pageNumber):

        pageHeader = "ОС СИНТЕЗ ДС ПРИМУС (С) ФИНТЕХ\n\n" + \
                    "ДОБРО ПОЖАЛОВАТЬ, АДМИНИСТРАТОР\n\n" + \
                    "БЛОК ДАННЫХ ПОД ЗАГОЛОВКОМ \'"

        pageText = pageHeader + db_parameters["msgHead"].upper() + '\' ' + \
                str(pageNumber+1) + '/' + str(pageCount) + "\n\n\n"
        allscrReset()
        typeWriter(10, 10, pageText, 30, fieldArea)
        txtY = statY
        menuStr = ' '*5
        if pageNumber == 0:
            menuStr += ' '*14
            startMenu = 1
        else:
            menuStr += u'ПРЕД. СТРАНИЦА'
            startMenu = 0
        menuStr += ' '*7 + u'НАЗАД В МЕНЮ' + ' '*9
        if pageNumber+1 == pageCount:
            menuStr += ' '*20
            endMenu = 1
        else:
            menuStr += u'СЛЕД. СТРАНИЦА'
            endMenu = 2
        typeWriter(10, txtY, pages[pageNumber], 30, textArea)
        typeWriter(10, statY + deltaY, menuStr, 10, servArea)
        menuPos = pages[pageNumber].count("\n") + 9 # N строки, на которой будут располагаться кнопки меню. Нужно для корреткной подсветки при наведении курсора.
        return startMenu, endMenu, menuPos

    menuButtonsStartPos = [5, 26, 47] #Начальные и конечные позиции кнопок меню.
    menuButtonsEndPos = [19, 38, 61]


    lineLength = 80
    pages = [] #В списке храниться текст каждой страницы.
    lineCountOnPage = 0
    pageData = ""

    for line in db_parameters["msgBody"]: # В цикле последовательно все слова собираются в текст страницы

        if len(line) > lineLength:
            lineParts = int(len(line) / lineLength)
            lineCount = 0
            for part in range(0, lineParts):
                text = line[lineLength*part:lineLength*(part+1)]
                if not text.endswith(" ") and not text.endswith("\t"):
                    text += "-"
                pageData += text + "\n"
                lineCountOnPage += 1
                lineCount += 1
                if lineCountOnPage == 13:
                    pages.append(pageData+"\n")
                    pageData = ""
                    lineCountOnPage = 0
            if len(line) > lineLength*(lineCount):
                pageData += line[lineLength*lineCount:] + "\n"
        else:
            pageData += line + "\n"
        lineCountOnPage += 1
        if lineCountOnPage == 13:
            pages.append(pageData+"\n")
            pageData = ""
            lineCountOnPage = 0

    pages.append(pageData + "\n")
    pageCount = len(pages)
    currentPage = 0
    startMenu, endMenu, menuPos = showLetterPage(0)

    mssTime = millis()
    done = True
    while done:
        pSound = 0
        wrdSnd = pygame.mixer.Sound('f3termword.wav')
        mscTime = millis()
        if (mscTime >= (mssTime + 3000)):
            mssTime =  mscTime
            # Читаем базу
            if not db_parameters["isPowerOn"] or db_parameters["isLocked"] or not db_parameters["isHacked"]:
                return
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                forceClose = True
                return
        (curX, curY) = pygame.mouse.get_pos()
        (b1, b2, b3) = pygame.mouse.get_pressed()
        numStr = int(curY / deltaY) + 1
        numChr = int(curX / deltaX)
        selItem = -1
        if numStr >= menuPos - 1 and numStr <= menuPos + 1:
            i = startMenu
            while i <= endMenu:
                if numChr >= menuButtonsStartPos[i] and numChr <= menuButtonsEndPos[i]:
                    selItem = i
                    menuHl(menuButtonsStartPos[i], menuButtonsEndPos[i])
                    if pSound == 0:
                        pSound = 1
                        wrdSnd.play()
                    break
                i += 1
            if selItem == -1:
                menuBg()
                pSound = 0
        else:
            menuBg()
        if b1 == True and selItem != -1:
            if selItem == 0:
                currentPage -= 1
                startMenu, endMenu, menuPos = showLetterPage(currentPage)
            if selItem == 1:
                return
            if selItem == 2:
                currentPage += 1
                startMenu, endMenu, menuPos = showLetterPage(currentPage)

def TstartTerminal():
    #Основной игровой цикл.
    global db_parameters
    previous_state = "" #Предыдущее состояние терминала. Если не совпадает с текущим - будет выполнена очистка и перерисовка экрана. # Unpowerd - нет питания. Locked  - заблокирован. Hacked - взломан. Normal - запитан, ждет взлома.
    allscrReset()
    while True:
        print("Menu")
        if forceClose:
            break
        while is_db_updating:#Ожидаем, пока обновится состояние из БД.
            pass
        # Проверяем: 1. Есть ли питание. 2. Не заблокирован ли терминал. Если все в порядке, показываем игру. После взлома показываем меню.
        if not db_parameters["isPowerOn"]:
            if previous_state != "Unpowered":
                allscrReset()
                termText = "МИНИСТЕРСТВО ОБОРОНЫ СССР\n\n" + \
                "ТЕРМИНАЛ ИСКРА-9876\n\n" + \
                "ДИАЛОГОВАЯ СРЕДА ПРИМУС\n\n" + \
                "НЕДОСТАТОЧНО ЭНЕРГИИ ДЛЯ РАБОТЫ. ПРОВЕРЬТЕ ЭЛЕКТРОПИТАНИЕ!"
                killAllText(fieldArea)
                typeWriter(10,10,termText,30,fieldArea)
                previous_state = "Unpowered"
            pygame.time.wait(dbCheckInterval*1000)
        elif db_parameters["isLocked"]:
            if previous_state != "Locked":
                allscrReset()
                termText = "МИНИСТЕРСТВО ОБОРОНЫ СССР\n\n" + \
                "ТЕРМИНАЛ ИСКРА-9876\n\n" + \
                "ДИАЛОГОВАЯ СРЕДА ПРИМУС\n\n" + \
                "АВАРИЙНАЯ БЛОКИРОВКА ТЕРМИНАЛА!!!\n\n" + \
                "ОБРАТИТЕСЬ К СИСТЕМНОМУ АДМИНИСТРАТОРУ!!!"
                killAllText(fieldArea)
                typeWriter(10,10,termText,30,fieldArea)
                previous_state = "Locked"
        elif db_parameters["isHacked"]:
            previous_state = "Hacked"
            TmenuScreen()
        else:
            #Взлом.
            previous_state = "Normal"
            TgameScreen()


#
#
# def moveLine():
#     #Разобраться, будет ли работать при текущем варианте кода.
#     lineY = -200
#     lineTime = 0
#     line = pygame.image.load('line.png')
#     while True:
#         screen.blit(line,(x,lineY))
#         lineTime += 1
#         if lineTime > 5:
#             lineY = lineY + 8 if lineY <= 800 else -200
#             lineTime = 0


if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = Ton_message

    try:
        client.connect(mqtt_broker_ip, mqtt_broker_port, 5)
    except BaseException:
        mqttFlag = 0
    else:
        mqttFlag = 1
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((mqtt_broker_ip,mqtt_broker_port))
        my_ip = s.getsockname()[0]
        s.close()
        client.loop_start()
    dbThread = threading.Thread(target=readDBParameters, args=(dbCheckInterval,))
    dbThread.start()
    time.sleep(1)
    while is_db_updating:
        #Ожидаем, пока обновится состояние из БД.
        pass
    print(db_parameters)
    TstartTerminal()
    print("Forced terminal close.")
    pygame.quit()
   # except:
   #     forceClose = True
    #     sys.exit()
