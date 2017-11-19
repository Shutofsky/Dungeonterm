import pygame, sys, time, random, string, sqlite3
from datetime import datetime
from datetime import timedelta
from pygame.locals import *
import pygame.mixer
import paho.mqtt.client as mqtt
import socket
import asyncio
import threading #Tupitsyn
import time #

mqtt_broker_ip = '10.23.192.193'
mqtt_broker_port = 1883
mqttFlag = 0
my_ip = ''

wordBase = []
wordListSelected = []
wordListZero = []
wordListMax = []
wordListOther = []
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
#posWords = []
idAst = [67, 65, 63, 61]
leftBrakes = ['[', '(', '{', '<']
rightBrakes = [']', ')', '}', '>']
lasHlPos = 0
lastHlLen = 0
lastMenuHlPos = 0
lastMenuHlEnd = 0
activeWords = 0
#numTries = 4

start_time = datetime.now()
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
screen = pygame.display.set_mode((800,600),0,32)#TODO pygame.FULLSCREEN
pygame.display.toggle_fullscreen()
pygame.display.set_caption("ROBCO RIT-300 TERMINAL")
background = pygame.image.load('f3term.png').convert() #Один раз загружаем картинку в начале.
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
clock=pygame.time.Clock()
cursor, mask = pygame.cursors.compile(inverseBar_strings,'x','.','o')
pygame.mouse.set_cursor((16,16),(7,5),cursor,mask)
screen.blit(background, (0, 0))
pygame.display.flip()

#Tupitsyn
db_parameters = {} #Игровые параметры
is_db_updating = False #Флаг, обновляется ли состояние в данный момент. Флаг выставляется процессом обновления БД.
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
   dt = datetime.now() - start_time
   ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
   return ms

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
        req.execute("UPDATE params SET value = 'NO' WHERE name='is_terminal_locked'")
        req.execute("UPDATE params SET value = 'NO' WHERE name='is_terminal_hacked'")
        req.execute("UPDATE params SET value = 'NO' WHERE name='is_power_all'")
        req.execute("UPDATE params SET value = 'NO' WHERE name='is_lock_open'")
        req.execute("UPDATE params SET value = 'NO' WHERE name='is_level_down'")
        req.execute("UPDATE params SET value = 'NO' WHERE name='do_lock_open'")
        req.execute("UPDATE params SET value = 'NO' WHERE name='do_level_down'")
        req.execute("UPDATE params SET value = 8 WHERE name='difficulty'")
        req.execute("UPDATE params SET value = 4 WHERE name='attempts'")
        req.execute("UPDATE params SET value = 10 WHERE name='count'")
    elif commList[1] == 'POWER':
        req.execute("UPDATE params SET value = ? WHERE name='is_power_all'", [commList[2]])
    elif commList[1] == 'LOCK':
        req.execute("UPDATE params SET value = ? WHERE name='is_terminal_locked'", [commList[2]])
    elif commList[1] == 'HACK':
        req.execute("UPDATE params SET value = ? WHERE name='is_terminal_hacked'", [commList[2]])
    elif commList[1] == 'ISLOCK':
        req.execute("UPDATE params SET value = ? WHERE name='is_lock_open'", [commList[2]])
    elif commList[1] == 'DOLOCK':
        req.execute("UPDATE params SET value = ? WHERE name='do_lock_open'", [commList[2]])
    elif commList[1] == 'ISLEVEL':
        req.execute("UPDATE params SET value = ? WHERE name='is_level_down'", [commList[2]])
    elif commList[1] == 'DOLEVEL':
        req.execute("UPDATE params SET value = ? WHERE name='do_level_down'", [commList[2]])
    elif commList[1] == 'ATTEMPTS':
        req.execute("UPDATE params SET value = ? WHERE name='attempts'", [commList[2]])
    elif commList[1] == 'DIFFICULTY':
        req.execute("UPDATE params SET value = ? WHERE name='difficulty'", [commList[2]])
    elif commList[1] == 'WORDSNUM':
        req.execute("UPDATE params SET value = ? WHERE name='count'", [commList[2]])
    elif commList[1] == 'MENULIST':
        req.execute("UPDATE params SET value = ? WHERE name='menu'", [commList[2]])
    elif commList[1] == 'MAILHEAD':
        req.execute("UPDATE params SET value = ? WHERE name='letter_head'", [commList[2].decode('utf-8','ignore')])
    elif commList[1] == 'MAILBODY':
        req.execute("UPDATE params SET value = ? WHERE name='letter'", [commList[2].decode('utf-8','ignore')])
    elif commList[1] == 'PING':
        client.publish("TERMASK",my_ip+'/PONG')
    elif commList[1] == 'GETDB':
        req.execute("SELECT value FROM params WHERE name='is_terminal_locked'")
        S = req.fetchone()
        client.publish("TERMASK",my_ip+'/Lock_status/'+S[0])
        req.execute("SELECT value FROM params WHERE name='is_terminal_hacked'")
        S = req.fetchone()
        client.publish("TERMASK",my_ip+'/Hack_status/'+S[0])
	# print "TERMASK",my_ip+'/Hack_status/'+S[0]
        req.execute("SELECT value FROM params WHERE name='menu'")
        S = req.fetchone()
        client.publish("TERMASK",my_ip+'/Menulist/'+S[0])
        req.execute("SELECT value FROM params WHERE name='menu'")
        S = req.fetchone()
        client.publish("TERMASK",my_ip+'/Menulist/'+S[0])
        req.execute("SELECT value FROM params WHERE name='letter_head'")
        S = req.fetchone()
        client.publish("TERMASK",my_ip+'/Msg_head/'+S[0])
        req.execute("SELECT value FROM params WHERE name='letter'")
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
                pygame.quit()
                quit()
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

def fillWordBase():
    global wordBase
    global wordLen
    global wordCount
    i = 0
    f = open ('words'+str(wordLen)+'.txt','r')
    for line in f:
        wordBase += line.strip()
        i += 1
    f.close()
    wordCount = i

def selectPassWord():
    global wordBase
    global wordLen
    global wordCount
    global wordPass
    passNum = random.randint(0, wordCount-1)
    wordPass = ''.join(wordBase[passNum*wordLen:passNum*wordLen+wordLen])

def wordsParse():
    global wordBase
    global wordLen
    global wordCount
    global wordPass
    global wordListMax
    global wordListZero
    global wordListOther
    i = 0
    while i < wordCount:
        wordNew = ''.join(wordBase[i * wordLen:i * wordLen + wordLen])
        if wordNew != wordPass:
            t = compareWords(wordNew, wordPass)
            if t == 0:
                wordListZero.append(wordNew)
            elif t == (wordLen - 1):
                wordListMax.append(wordNew)
            else:
                wordListOther.append(wordNew)
        i += 1
    wordDelta = 2
    while len(wordListMax) == 0:
        i = 0
        while i < wordCount:
            wordNew = ''.join(wordBase[i * wordLen:i * wordLen + wordLen])
            if wordNew != wordPass:
                t = compareWords(wordNew, wordPass)
                if t == 0:
                    wordListZero.append(wordNew)
                elif t == (wordLen - 1):
                    wordListMax.append(wordNew)
                elif t == (wordLen - wordDelta):
                    wordListMax.append(wordNew)
                else:
                    wordListOther.append(wordNew)
            i += 1
        wordDelta += 1
    print(wordPass,wordListMax)

def selectWordsOther():
    global wordBase
    global wordLen
    global wordNum
    global wordCount
    global wordPass
    global wordListMax
    global wordListZero
    global wordListOther
    global wordListSelected
    wordListSelected.append(wordPass)
    wordPos = random.randint(0, len(wordListZero) - 1)
    wordListSelected.append(wordListZero[wordPos])
    wordPos = random.randint(0, len(wordListMax) - 1)
    wordListSelected.append(wordListMax[wordPos])
    wordListSelected.append(wordListOther[random.randint(0, len(wordListOther) - 1)])
    i = 0
    while i < wordNum - 4:
        wordSel = wordListOther[random.randint(0, len(wordListOther) - 1)]
        if wordSel not in wordListSelected:
            wordListSelected.append(wordSel)
            i += 1
    i = 0
    while i < wordNum:
        t = random.randint(0, wordNum - 1)
        tWord = wordListSelected[t]
        wordListSelected[t] = wordListSelected[i]
        wordListSelected[i] = tWord
        i += 1

def formOutString():
    global wordLen
    global wordNum
    global wordListSelected
    global garbLen
    global garbStr
    global posWords
    lenArea = int(garbLen / wordNum)
    i = 0
    while i < wordNum:
        startPos = random.randint(i * lenArea, i * lenArea + (lenArea - wordLen - 1) )
        j = i * lenArea
        print(startPos, lenArea)
        while j < startPos:
            garbStr += random.choice(string.punctuation)
            print(garbStr)
            j += 1
        posWords.append(j)
        garbStr += wordListSelected[i]
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

def lockScreen():
    global termLockStatus
    lssTime = millis()
    done = True
    statOutput = 0
    if powerStatus == 0:
        return()
    allscrReset()
    while done:
        if termLockStatus == 1:
            hello1Text = "WELCOME TO ROBCO INDUSTRIES (TM) TERMLINK\n\n" + \
            ">SET TERMINAL INQUIRE\n\n" + \
            "RIT-V300\n\n" + \
            "TERMINAL LOCKED!!! TERMINAL LOCKED!!! TERMINAL LOCKED!!! \n\n" + \
            "CALL SYSTEM ADMINISTRATOR!!!"
            if statOutput == 0:
                killAllText(fieldArea)
                typeWriter(10,10,hello1Text,30,fieldArea)
                statOutput = 1
        else:
            done = False
            killAllText(fieldArea)
            #background = pygame.image.load('f3term_alt.png')
            screen.blit(background, (0, 0))
            pygame.display.flip()
        lscTime =  millis()
        if lscTime >= (lssTime + 3000):
            conn = sqlite3.connect('ft.db')
            req = conn.cursor()
            req.execute('SELECT value FROM params WHERE name == "is_terminal_locked"')
            S = str(req.fetchone())
            if S[3:-3] == 'YES':
                termLockStatus = 1
            else:
                termLockStatus = 0
            conn.close()
            lssTime = lscTime
    return()

def powerScreen():
    global powerStatus
    done = True
    statOutput = 0
    # Стартовый экран:
    allscrReset()
    fssTime = millis()
    while done:
        if powerStatus == 1:
            done = False
            break
        else:
            hello1Text = "WELCOME TO ROBCO INDUSTRIES (TM) TERMLINK\n\n" + \
            ">SET TERMINAL INQUIRE\n\n" + \
            "RIT-V300\n\n" + \
            "POWER DOWN. CHECK POWER SUPPLY!"
            if statOutput == 0:
                killAllText(fieldArea)
                typeWriter(10,10,hello1Text,30,fieldArea)
                statOutput = 1
        fscTime =  millis()
        if fscTime >= (fssTime + 3000):
            conn = sqlite3.connect('ft.db')
            req = conn.cursor()
            req.execute('SELECT value FROM params WHERE name == "is_power_all"')
            S = str(req.fetchone())
            if S[3:-3] == 'YES':
                powerStatus = 1
                statOutput = 0
            else:
                powerStatus = 0
            conn.close()
            fssTime = fscTime
    return()

def mainScreen():
    global wordBase
    global wordDisp
    global wordNum
    global wordLen
    global numTries
    global garbStr
    global helloText
    global wordChoice
    global wordPass
    global statX
    global statY
    global deltaX
    global deltaY
    global activeWords
    global termLockStatus
    global termHackStatus
    global powerStatus

    startWord = 0
    hlPos = 0
    hlLen = 0

    if powerStatus == 0 or termLockStatus == 1 or termHackStatus == 1:
        return()

    hello1Text = "WELCOME TO ROBCO INDUSTRIES (TM) TERMLINK\n\n" + \
    ">SET TERMINAL INQUIRE\n\n" + \
    "RIT-V300\n\n" + \
    ">SET FILE/PROTECTION OWNER:RWED ACCOUNTS.F\n" + \
    ">SET HALT RESTART/MAINT\n\n" + \
    "Initializing Robco Industries(TM) MF Boot Agent v2.3.0\n" + \
    "RETROS BIOS\n" + \
    "RBIOS-4.02.08.00 52EE5.E7.E8\n" + \
    "Copyright 2201-2203 Robco Ind.\n" + \
    "Uppermem 64 KB\n" + \
    "Root (5A8)\n" + \
    "Maintenance Mode\n\n" + \
    ">RUN DEBUG/ACCOUNTS.F"

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
               "ROBCO INDUSTRIES (TM) TERMLINK PROTOCOL\nENTER PASSWORD\n\n{0} TRIES {1}\n\n".format(numTries,
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
            conn = sqlite3.connect('ft.db')
            req = conn.cursor()
            req.execute('SELECT value FROM params WHERE name == "is_power_all"')
            S = str(req.fetchone())
            if S[3:-3] == 'NO' and powerStatus == 1:
                # Отключилось питание
                powerStatus = 0
                conn.close()
                return()
                # Добавить функцию по апдейту параметров. Вызывать из ЛокСкрина и ПоверСкрина
                # В любом случае перегенерировать весь экран
            req.execute('SELECT value FROM params WHERE name == "is_terminal_locked"')
            S = str(req.fetchone())
            if S[3:-3] == 'YES' and termLockStatus == 0:
                termLockStatus = 1
                # Терминал залочился
                conn.close()
                return ()
                # Добавить функцию по апдейту параметров. Вызывать из ЛокСкрина и ПоверСкрина
                # В любом случае перегенерировать весь экран
            # req.execute('SELECT value FROM params WHERE name == "attempts"')
            # S = str(req.fetchone())
            # numTriesNew = int(S[3:-3])
            # req.execute('SELECT value FROM params WHERE name == "difficulty"')
            # S = str(req.fetchone())
            # wordLenNew = int(S[3:-3])
            # req.execute('SELECT value FROM params WHERE name == "count"')
            # S = str(req.fetchone())
            # wordNumNew = int(S[3:-3])
            # if (wordLen != wordLenNew  or wordNum != wordNumNew):
            #     # Сменилось число попыток
            #     numTries = numTriesNew
            #     wordLen = wordLenNew
            #     wordNum = wordNumNew
            #     return()
                # В любом случае перегенерировать весь экран

        for event in pygame.event.get():
            # Пока оставим выход
            if event.type == pygame.QUIT:
                exit()
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
                prtLet = str(rightLet) + ' of ' + str(wordLen)
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
                    # conn = sqlite3.connect('ft.db')
                    # req = conn.cursor()
                    # req.execute("UPDATE params SET value = ? WHERE name='attempts'",[numTries])
                    # conn.commit()
                    # conn.close()
                    if numTries == 0:
                        # Залочились
                        termLockStatus = 1
                        conn = sqlite3.connect('ft.db')
                        req = conn.cursor()
                        req.execute("UPDATE params SET value = 'YES' WHERE name='is_terminal_locked'")
                        conn.commit()
                        conn.close()
                        if mqttFlag:
                            client.publish('TERMASK', my_ip + '/Lock_status/YES')
                        # print my_ip + '/Lock_status/YES'
                        return()
                else:
                    # Угадали слово
                    termHackStatus = 1
                    conn = sqlite3.connect('ft.db')
                    req = conn.cursor()
                    req.execute("UPDATE params SET value = 'YES' WHERE name='is_terminal_hacked'")
                    conn.commit()
                    conn.close()
                    if mqttFlag:
                        client.publish('TERMASK', my_ip + '/Hack_status/YES')
                    # print my_ip + '/Hack_status/YES'
                    return()
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
    clock.tick(30)

def hackScreen():
    global powerStatus
    global termHackStatus
    global termLockStatus
    global menuStatus
    global statX
    global statY
    if powerStatus == 0 or termLockStatus == 1 or termHackStatus == 0 or menuStatus == 1:
        return()
    helloText = "WELCOME TO ROBCO INDUSTRIES (TM) TERMLINK\n\n" + \
                "LOCAL SYSTEM ADMINISTRSATOR ACCESS GRANTED\n\n" + \
                "SELECT MENU ITEM\n\n\n"

    conn = sqlite3.connect('ft.db')
    req = conn.cursor()
    req.execute('SELECT value FROM params WHERE name == "menu"')
    S = str(req.fetchone())
    menuItems = S[3:-3]
    menuText = ' ' * 12
    menuCount = 0
    menuList = []
    menuPos = []
    numItems = menuItems.split(",")
    for mChar in numItems:
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
            menuList.append(8 + menuCount * 2)
            menuPos.append(len(menuText) - menuCount*2)
            req.execute('SELECT value FROM params WHERE name == "letter_head"')
            S = req.fetchone()
            R = ''.join(S)
            menuText += R.upper() + '\n\n' + ' ' * 12
            menuCount += 1
    conn.close()
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
            # Читаем базу
            conn = sqlite3.connect('ft.db')
            req = conn.cursor()
            req.execute('SELECT value FROM params WHERE name == "is_power_all"')
            S = str(req.fetchone())
            if S[3:-3] == 'NO' and powerStatus == 1:
                # Отключилось питание
                powerStatus = 0
                conn.close()
                return()
            req.execute('SELECT value FROM params WHERE name == "is_terminal_locked"')
            S = str(req.fetchone())
            if S[3:-3] == 'YES' and termLockStatus == 0:
                termLockStatus = 1
                # Терминал залочился
                conn.close()
                return ()
            req.execute('SELECT value FROM params WHERE name == "is_terminal_hacked"')
            S = str(req.fetchone())
            if S[3:-3] == 'NO':
                termHackStatus = 0
                conn.close()
                return ()
        for event in pygame.event.get():
            # Пока оставим выход
            if event.type == pygame.QUIT:
                exit()
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
                    if numItems[i] != selItem:
                        wordBg()
                        selItem = numItems[i]
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
                menuStatus = 1
                return()
            if selItem == '1':
                # Выбрано открыть замок
                conn = sqlite3.connect('ft.db')
                req = conn.cursor()
                req.execute('SELECT value FROM params WHERE name == "is_lock_open"')
                S = req.fetchone()
                if S[0] == 'NO':
                    req.execute('UPDATE params SET value = "YES" WHERE name == "do_lock_open"')
                    if mqttFlag:
                        client.publish('TERMASK', my_ip + '/DOLOCKOPEN/YES')
                    conn.commit()
                conn.close()
            if selItem == '2':
                # Выбрано оснизить уровень тревоги
                conn = sqlite3.connect('ft.db')
                req = conn.cursor()
                req.execute('SELECT value FROM params WHERE name == "is_level_down"')
                S = req.fetchone()
                if S[0] == 'NO':
                    req.execute('UPDATE params SET value = "YES" WHERE name == "do_level_down"')
                    if mqttFlag:
                        client.publish('TERMASK', my_ip + '/DOLEVELDOWN/YES')
                    conn.commit()
                conn.close()

def menuScreen():
    global powerStatus
    global termHackStatus
    global termLockStatus
    global statX
    global statY
    global menuStatus
    global menuScrNum
    if menuStatus == 0:
        return()
    conn = sqlite3.connect('ft.db')
    req = conn.cursor()
    req.execute('SELECT value FROM params WHERE name == "letter_head"')
    S = req.fetchone()
    RHead = ''.join(S)
    req.execute('SELECT value FROM params WHERE name == "letter"')
    S = req.fetchone()
    R = ''.join(S)
    conn.close()
    tmpLet = R.split(' ')
    curStr = 0
    curScreen = 0
    tmpStr = ''
    tmpScr = ''
    tmpOutData = ''
    tmpOutList = []
    allScreens = []
    for word in tmpLet:
        if len(word) + len(tmpStr) >= 64:
            tmpOutData += tmpStr + '\n'
            tmpStr = word + ' '
        else:
            tmpStr += word + ' '
    tmpOutList = tmpOutData.split('\n')
    numStr = len(tmpOutList)
    # print numStr
    tmpScr = ''
    i = 0
    j = 0
    for strData in tmpOutList:
        tmpScr += strData + '\n'
        j += 1
        if j == 13:
            allScreens.append(tmpScr)
            tmpScr = ''
            i += 1
            j = 0
    curScreen = i - 1
    numScr = menuScrNum
    helloText = "WELCOME TO ROBCO INDUSTRIES (TM) TERMLINK\n\n" + \
                "LOCAL SYSTEM ADMINISTRSATOR ACCESS GRANTED\n\n" + \
                "DATA BLOCK FOR HEADER \'" + RHead.upper() + '\' ' + \
                str(numScr + 1) + '/' + str(curScreen + 1) + "\n\n\n"
    allscrReset()
    typeWriter(10, 10, helloText, 30, fieldArea)
    txtY = statY
    charStartPos = [5, 29, 53]
    charEndPos = [10, 35, 59]
    menuStr = ' '*5
    if numScr == 0:
        menuStr += ' '*12
        startMenu = 1
    else:
        menuStr += u'НАЗАД' + ' '*7
        startMenu = 0
    menuStr += ' '*12 + u'НАВЕРХ' + ' '*6 + ' '*12
    if numScr == curScreen:
        menuStr += ' '*12
        endMenu = 1
    else:
        menuStr += u'ВПЕРЕД'
        endMenu = 2

    typeWriter(10, txtY, allScreens[numScr], 30, textArea)
    typeWriter(10, statY + deltaY, menuStr, 10, servArea)

    done = True
    selItem = -1
    pSound = 0
    wrdSnd = pygame.mixer.Sound('f3termword.wav')
    mssTime = millis()
    while done:
        mscTime = millis()
        if (mscTime >= (mssTime + 3000)):
            mssTime =  mscTime
            # Читаем базу
            conn = sqlite3.connect('ft.db')
            req = conn.cursor()
            req.execute('SELECT value FROM params WHERE name == "is_power_all"')
            S = str(req.fetchone())
            if S[3:-3] == 'NO' and powerStatus == 1:
                # Отключилось питание
                powerStatus = 0
                menuStatus = 0
                conn.close()
                return()
            req.execute('SELECT value FROM params WHERE name == "is_terminal_locked"')
            S = str(req.fetchone())
            if S[3:-3] == 'YES' and termLockStatus == 0:
                termLockStatus = 1
                # Терминал залочился
                menuStatus = 0
                conn.close()
                return ()
            req.execute('SELECT value FROM params WHERE name == "is_terminal_hacked"')
            S = str(req.fetchone())
            if S[3:-3] == 'NO':
                termHackStatus = 0
                menuStatus = 0
                conn.close()
                return ()
        for event in pygame.event.get():
            # Пока оставим выход
            if event.type == pygame.QUIT:
                exit()
        (curX, curY) = pygame.mouse.get_pos()
        (b1, b2, b3) = pygame.mouse.get_pressed()
        numStr = int(curY / deltaY) + 1
        numChr = int(curX / deltaX)
        selItem = -1

        if numStr >= 22 and numStr <= 23:
            i = startMenu
            while i <= endMenu:
                if numChr >= charStartPos[i] and numChr <= charEndPos[i]:
                    selItem = i
                    menuHl(charStartPos[i], charEndPos[i])
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
            pSound = 0
        if b1 == True and selItem != -1:
            if selItem == 0:
                numScr -= 1
            if selItem == 1:
                menuStatus = 0
            if selItem == 2:
                numScr += 1
            menuScrNum = numScr
            # print numScr
            return ()


#Tupitsyn
def readDBParameters():
    #Tupitsyn
    #current_parameters = {}
    global db_parameters
    global is_db_updating
    while True:
        if not is_db_updating:
            print("Reading DB.")
            is_db_updating = True
            conn = sqlite3.connect(r'ft.db')
            req = conn.cursor()
            req.execute('SELECT name,value FROM params')
            params = req.fetchall()
            conn.close()
            for data in params:
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
        time.sleep(3)


    #return current_parameters

def updateDBParameters(parameters):
    """Принимает словарь, где ключ - поле в базе, значение ключа - значение, которое нужно записать в базу."""
    global is_db_updating
    while is_db_updating:
        pass
    try:
        is_db_updating = True
        conn = sqlite3.connect('ft.db')
        req = conn.cursor()
        for par in parameters.keys():
            req.execute("UPDATE params SET value = '{1}' WHERE name='{0}'".format(par,parameters[par]))
        conn.commit()
        conn.close()
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
    wordsListSelected = []#Слова, которые будут использоваться непосредственно в игре.
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
    return wordListZero,wordListMax,wordListOther,wordsListSelected

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
                    pygame.quit()
                    quit()
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
    wordLen = db_parameters["difficulty"]
    numTries = db_parameters['attempts']
    startWord = 0
    hlPos = 0
    hlLen = 0


    #Выбор нового пароля непосредственно перед игрой.
    wordBase, wordCount, wordPass = loadWordsAndSelectPassword()
    TwordsParse(wordBase,wordLen,wordPass)
    garbStr, posWords = TformOutString(wordLen, wordNum, wordListSelected, garbLen)


    hello1Text = "WELCOME TO ROBCO INDUSTRIES (TM) TERMLINK\n\n" + \
    ">SET TERMINAL INQUIRE\n\n" + \
    "RIT-V300\n\n" + \
    ">SET FILE/PROTECTION OWNER:RWED ACCOUNTS.F\n" + \
    ">SET HALT RESTART/MAINT\n\n" + \
    "Initializing Robco Industries(TM) MF Boot Agent v2.3.0\n" + \
    "RETROS BIOS\n" + \
    "RBIOS-4.02.08.00 52EE5.E7.E8\n" + \
    "Copyright 2201-2203 Robco Ind.\n" + \
    "Uppermem 64 KB\n" + \
    "Root (5A8)\n" + \
    "Maintenance Mode\n\n" + \
    ">RUN DEBUG/ACCOUNTS.F"

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
               "ROBCO INDUSTRIES (TM) TERMLINK PROTOCOL\nENTER PASSWORD\n\n{0} TRIES {1}\n\n".format(numTries,
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
            while is_db_updating:#Ожидаем, пока обновится состояние из БД.
                pass
            if not db_parameters["is_power_all"] or db_parameters["is_terminal_locked"] or db_parameters["is_terminal_hacked"]:
                return

        for event in pygame.event.get():
            # Пока оставим выход
            if event.type == pygame.QUIT:
                exit()
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
                    prtLet = "Exact match!"
                else:
                    prtLet = 'Match '+str(rightLet) + ' of ' + str(wordLen)
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
                        updateDBParameters({"is_terminal_locked":"YES"})
                        db_parameters["is_terminal_locked"] = True
                        pygame.time.wait(1000)
                        #if mqttFlag:
                        #    client.publish('TERMASK', my_ip + '/Lock_status/YES')
                        return
                else:
                    # Угадали слово
                    updateDBParameters({"is_terminal_hacked":"YES"})
                    db_parameters["is_terminal_hacked"] = True
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

    if menuStatus == 1:
        return
    helloText = "WELCOME TO ROBCO INDUSTRIES (TM) TERMLINK\n\n" + \
                "LOCAL SYSTEM ADMINISTRSATOR ACCESS GRANTED\n\n" + \
                "SELECT MENU ITEM\n\n\n"

    menuItems = db_parameters["menu"].split(",")
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

            if not db_parameters["is_power_all"] or db_parameters["is_terminal_locked"] or not db_parameters["is_terminal_hacked"]:
                return

        for event in pygame.event.get():
            # Пока оставим выход
            if event.type == pygame.QUIT:
                exit()
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
                if not db_parameters["is_lock_open"]:
                    updateDBParameters({"do_lock_open":"YES"})
                    # if mqttFlag:
                    #     client.publish('TERMASK', my_ip + '/DOLEVELDOWN/YES')
            if selItem == '2':
                # Выбрано снизить уровень тревоги
                if not db_parameters["is_level_down"]:
                    updateDBParameters({"do_level_down":"YES"})
                    # if mqttFlag:
                    #     client.publish('TERMASK', my_ip + '/DOLEVELDOWN/YES')

def TletterScreen():
    global statX
    global statY
    global menuScrNum

    RHead = db_parameters["letter_head"]
    R = db_parameters["letter"]
    tmpLet = R.split(' ')
    curStr = 0
    curScreen = 0
    tmpStr = ''
    tmpScr = ''
    tmpOutData = ''
    tmpOutList = []
    allScreens = []
    for word in tmpLet:
        if len(word) + len(tmpStr) >= 64:
            tmpOutData += tmpStr + '\n'
            tmpStr = word + ' '
        else:
            tmpStr += word + ' '
    tmpOutList = tmpOutData.split('\n')
    numStr = len(tmpOutList)
    # print numStr
    tmpScr = ''
    i = 0
    j = 0
    for strData in tmpOutList:
        tmpScr += strData + '\n'
        j += 1
        if j == 13:
            allScreens.append(tmpScr)
            tmpScr = ''
            i += 1
            j = 0
    curScreen = i - 1
    numScr = menuScrNum
    helloText = "WELCOME TO ROBCO INDUSTRIES (TM) TERMLINK\n\n" + \
                "LOCAL SYSTEM ADMINISTRSATOR ACCESS GRANTED\n\n" + \
                "DATA BLOCK FOR HEADER \'" + RHead.upper() + '\' ' + \
                str(numScr + 1) + '/' + str(curScreen + 1) + "\n\n\n"
    allscrReset()
    typeWriter(10, 10, helloText, 30, fieldArea)
    txtY = statY
    charStartPos = [5, 29, 53]
    charEndPos = [10, 35, 59]
    menuStr = ' '*5
    if numScr == 0:
        menuStr += ' '*12
        startMenu = 1
    else:
        menuStr += u'ПРЕД. СТРАНИЦА' + ' '*9
        startMenu = 0
    menuStr += ' '*9 + u'НАЗАД В МЕНЮ' + ' '*9
    if numScr == curScreen:
        menuStr += ' '*12
        endMenu = 1
    else:
        menuStr += u'СЛЕД. СТРАНИЦА'
        endMenu = 2
    typeWriter(10, txtY, allScreens[numScr], 30, textArea)
    typeWriter(10, statY + deltaY, menuStr, 10, servArea)

    done = True
    selItem = -1
    pSound = 0
    wrdSnd = pygame.mixer.Sound('f3termword.wav')
    mssTime = millis()
    while done:
        mscTime = millis()
        if (mscTime >= (mssTime + 3000)):
            mssTime =  mscTime
            # Читаем базу
            if not db_parameters["is_power_all"] or db_parameters["is_terminal_locked"] or not db_parameters["is_terminal_hacked"]:
                return
        for event in pygame.event.get():
            # Пока оставим выход
            if event.type == pygame.QUIT:
                exit()
        (curX, curY) = pygame.mouse.get_pos()
        (b1, b2, b3) = pygame.mouse.get_pressed()
        numStr = int(curY / deltaY) + 1
        numChr = int(curX / deltaX)
        selItem = -1

        if numStr >= 22 and numStr <= 23:
            i = startMenu
            while i <= endMenu:
                if numChr >= charStartPos[i] and numChr <= charEndPos[i]:
                    selItem = i
                    menuHl(charStartPos[i], charEndPos[i])
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
            pSound = 0
        if b1 == True and selItem != -1:
            if selItem == 0:
                numScr -= 1
            if selItem == 1:
                menuStatus = 0
                return
            if selItem == 2:
                numScr += 1
            menuScrNum = numScr
            # print numScr


def TstartTerminal():
    #Основной игровой цикл.
    global db_parameters
    previous_state = "" #Предыдущее состояние терминала. Если не совпадает с текущим - будет выполнена очистка и перерисовка экрана. # Unpowerd - нет питания. Locked  - заблокирован. Hacked - взломан. Normal - запитан, ждет взлома.
    allscrReset()
    #fssTime = millis()
    while True:
        while is_db_updating:#Ожидаем, пока обновится состояние из БД.
            pass
        # Проверяем: 1. Есть ли питание. 2. Не заблокирован ли терминал. Если все в порядке, показываем игру. После взлома показываем меню.
        if not db_parameters["is_power_all"]:
            if previous_state != "Unpowered":
                allscrReset()
                termText = "WELCOME TO ROBCO INDUSTRIES (TM) TERMLINK\n\n" + \
                ">SET TERMINAL INQUIRE\n\n" + \
                "RIT-V300\n\n" + \
                "POWER DOWN. CHECK POWER SUPPLY!"
                killAllText(fieldArea)
                typeWriter(10,10,termText,30,fieldArea)
                previous_state = "Unpowered"
        elif db_parameters["is_terminal_locked"]:
            if previous_state != "Locked":
                allscrReset()
                termText = "WELCOME TO ROBCO INDUSTRIES (TM) TERMLINK\n\n" + \
                ">SET TERMINAL INQUIRE\n\n" + \
                "RIT-V300\n\n" + \
                "TERMINAL LOCKED!!! TERMINAL LOCKED!!! TERMINAL LOCKED!!! \n\n" + \
                "CALL SYSTEM ADMINISTRATOR!!!"
                killAllText(fieldArea)
                typeWriter(10,10,termText,30,fieldArea)
                previous_state = "Locked"
        elif db_parameters["is_terminal_hacked"]:
            #Чтение письма ушло внутрь меню.
            TmenuScreen()
        else:
            #Взлом.
            TgameScreen()


#END T
if __name__ == "__main__":
    # client = mqtt.Client()
    # client.on_connect = on_connect
    # client.on_message = on_message
    #
    # try:
    #     client.connect(mqtt_broker_ip, mqtt_broker_port, 5)
    # except BaseException:
    #     mqttFlag = 0
    # else:
    #     mqttFlag = 1
    #     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     s.connect((mqtt_broker_ip,mqtt_broker_port))
    #     my_ip = s.getsockname()[0]
    #     s.close()
    #     client.loop_start()
    #while True:
    #readDBParameters()
    dbThread = threading.Thread(target=readDBParameters)
    dbThread.start()
    time.sleep(1)
    while is_db_updating:
        #Ожидаем, пока обновится состояние из БД.
        pass
    print(db_parameters)
    TstartTerminal()
    pygame.quit()
