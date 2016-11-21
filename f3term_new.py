# -*- coding: utf-8 -*-
import pygame, sys, time, random, string, sqlite3
from datetime import datetime
from datetime import timedelta
from pygame.locals import * 
import pygame.mixer

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
screen = pygame.display.set_mode((800,600),0,32) 
pygame.display.set_caption("ROBCO RIT-300 TERMINAL")
background = pygame.image.load('f3term.png')
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

myTime = 30
dY = 0
dX = 0 
numTries = 4
wordLen = 8
wordNum = 10
deltaY = 23
deltaX = 12
wordBase = ''
wordDisp = ''
garbStr = ''
secretWord = ''
statX = 0
statY = 0
powerStatus = 0
termLockStatus = 0
changeParmStatus = 0
termHackStatus = 0
menuStatus = 0
menuScrNum = 0
fieldArea = []
textArea = []
statWord = []
wordChoice = []
servAreaTxt = ' ' * 192
servArea = []
posWords = []
idAst = [67, 65, 63, 61]
leftBrakes = ['[', '(', '{', '<']
rightBrakes = [']', ')', '}', '>']
lasHlPos = 0
lastHlLen = 0
lastMenuHlPos = 0
lastMenuHlEnd = 0
activeWords = 0

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

def getDBparms():
    global numTries
    global wordLen
    global wordNum
    global powerStatus
    global termLockStatus
    global termHackStatus
    conn = sqlite3.connect('ft.db')
    req = conn.cursor()
    req.execute('SELECT value FROM params WHERE name == "attempts"')
    S = str(req.fetchone())
    numTries = int(S[3:-3])
    req.execute('SELECT value FROM params WHERE name == "difficulty"')
    S = str(req.fetchone())
    wordLen = int(S[3:-3])
    req.execute('SELECT value FROM params WHERE name == "count"')
    S = str(req.fetchone())
    wordNum = int(S[3:-3])
    req.execute('SELECT value FROM params WHERE name == "is_power_all"')
    S = str(req.fetchone())
    if S[3:-3] == 'YES':
        powerStatus = 1
    else:
        powerStatus = 0
    req.execute('SELECT value FROM params WHERE name == "is_terminal_locked"')
    S = str(req.fetchone())
    if S[3:-3] == 'YES':
        termLockStatus = 1
    else:
        termLockStatus = 0
    req.execute('SELECT value FROM params WHERE name == "is_terminal_hacked"')
    S = str(req.fetchone())
    if S[3:-3] == 'YES':
        termHackStatus = 1
    else:
        termHackStatus = 0
    conn.close()

def updateDBparms():
    global numTries
    global wordLen
    global wordNum
    global powerStatus
    global termLockStatus
    global termHackStatus
    global changeParmStatus
    if changeParmStatus == 1:
        print "Update parms"
        conn = sqlite3.connect('ft.db')
        req = conn.cursor()
        if termLockStatus == 1:
            req.execute("UPDATE params SET value = 'YES' WHERE name='is_terminal_locked'")
        else:
            req.execute("UPDATE params SET value = 'NO' WHERE name='is_terminal_locked'")
        conn.commit()
        if termHackStatus == 1:
            req.execute("UPDATE params SET value = 'YES' WHERE name='is_terminal_hacked'")
        else:
            req.execute("UPDATE params SET value = 'NO' WHERE name='is_terminal_hacked'")
        conn.commit()
        conn.close()
    return()

out_flag = 'bg'
print_flag = 0
bg_flag = 0

def millis():
   dt = datetime.now() - start_time
   ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
   return ms

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
                    print "Enter"
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
                    prtSnd.play(loops = 0, maxtime = myTime)
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
    servClear()
    servAreaTxt = 192 * ' '
    statWordClear()
    killAllText(fieldArea)
    killAllText(textArea)
    background = pygame.image.load('f3term.png')
    screen.blit(background, (0, 0))
    pygame.display.flip()

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
            background = pygame.image.load('f3term.png')
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
    
def fieldFull():
    global wordBase
    global wordDisp
    global wordNum
    global wordLen
    global garbStr
    global helloText
    global wordChoice
    global secretWord
    global statX
    global statY
    global deltaX
    global deltaY
    global activeWords
    activeWords = wordNum - 1
    i = 0
    triesAst= ''
    helloText = ''
    while i < numTries:
        triesAst += '* '
        i += 1
    typeWriter(10, 10,
               "ROBCO INDUSTRIES (TM) TERMLINK PROTOCOL\nENTER PASSWORD\n\n{0} TRIES {1}\n\n".format(numTries,triesAst),
               10, fieldArea)
    i = 0
    f = open ('words8.txt','r')
    for line in f:
        wordBase += line.strip()
        i += 1
    f.close()
    wordCnt = i
    i = 0
    n = 0
    step = int(wordCnt/wordNum)
    while i < wordNum:
        n = random.randint(i*step, i*step+step)
        wordChoice.append(wordBase[n*wordLen:n*wordLen+wordLen])
        wordDisp += wordBase[n*wordLen:n*wordLen+wordLen]
        i += 1
    secretWord = wordChoice[random.randint(0, wordNum - 1)]
    print secretWord
    i = 0
    j = 0
    wCnt = 0
    step = int(408/wordNum)
    while i < wordNum: 
        cPos = random.randint(0,step-wordLen)
        j = 0
        while j < cPos:
            garbStr += random.choice(string.punctuation)
            j += 1
        garbStr += wordDisp[i*wordLen:i*wordLen+wordLen]
        posWords.append((len(garbStr)-wordLen))
        wCnt += 1
        j += wordLen
        while j < step:
            garbStr += random.choice(string.punctuation)
            j += 1
        i += 1
    j = len(garbStr)
    while j<408:
        garbStr += random.choice(string.punctuation)
        j += 1
    i = 0
    startHex = random.randint(0x1A00,0xFA00)
    workY = statY
    while i < 17:
        hexLeft = '{0:#4X}  '.format(startHex + i*12)
        statX = 10
        typeWriter(statX, statY, hexLeft, 10, fieldArea)
        typeWriter(statX, statY, garbStr[i*12:i*12+12] + "\n", 10, textArea)
        i += 1
    statY = workY
    i = 0
    while i < 17:
        statX = 248
        hexRight = '    {0:#4X}  '.format(startHex + (i+17)*12)
        typeWriter(statX, statY, hexRight, 10, fieldArea)
        typeWriter(statX, statY, garbStr[(i+17)*12:(i+17)*12+12]+"\n", 10, textArea)
        i += 1
    typeWriter(538,493," >",10, fieldArea)
    i = 0
    while i < wordNum:
        selWord = garbStr[posWords[i]:posWords[i]+wordLen]
        if selWord == secretWord:
            print "Password detected"
            del(posWords[i])
            break
        i += 1

def mainScreen():
    global startWord
    global hlPos
    global hlLen
    global powerStatus
    global termLockStatus
    global changeParmStatus
    global termHackStatus
    global servAreaTxt
    global garbStr
    global wordNum
    global wordLen
    global activeWords
    global secretWord
    global numTries

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
    background = pygame.image.load('f3term.png')
    screen.blit(background, (0, 0))
    pygame.display.flip()

    typeWriter(10, 10, hello1Text, 20, fieldArea)
    time.sleep(0.5)
    killAllText(fieldArea)
    fieldFull()
    prevWord = ''
    selWord = ''
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
            req.execute('SELECT value FROM params WHERE name == "attempts"')
            S = str(req.fetchone())
            numTriesNew = int(S[3:-3])
            req.execute('SELECT value FROM params WHERE name == "difficulty"')
            S = str(req.fetchone())
            wordLenNew = int(S[3:-3])
            req.execute('SELECT value FROM params WHERE name == "count"')
            S = str(req.fetchone())
            wordNumNew = int(S[3:-3])
            if (wordLen != wordLenNew  or wordNum != wordNumNew):
                # Сменилось число попыток
                numTries = numTriesNew
                wordLen = wordLenNew
                wordNum = wordNumNew
                return()
                # В любом случае перегенерировать весь экран

        for event in pygame.event.get():
            # Пока оставим выход
            if event.type == pygame.QUIT:
                exit()
        (curX,curY) = pygame.mouse.get_pos()
        (b1,b2,b3) = pygame.mouse.get_pressed()
        numstr = int(curY / deltaY) + 1
        numchr = int(curX / deltaX)
        splText = helloText.split('\n',600/deltaY)
        curpos = -1
        selWord=''
        if(numstr >= 6 and numstr <= 22 and numchr >=8 and numchr <= 43):
            if(numchr >= 8 and numchr <= 20):
                curpos = (numstr - 6) * 12 + numchr - 8
            else:
                if(numchr >= 32 and numchr <= 43):
                    curpos = 12 * 17 + (numstr - 6) * 12 + numchr - 32
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
                rightLet = 0
                while i < wordLen:
                    if selWord[i] == secretWord[i]:
                        rightLet += 1
                    i += 1
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
                    conn = sqlite3.connect('ft.db')
                    req = conn.cursor()
                    req.execute("UPDATE params SET value = ? WHERE name='is_terminal_locked'",[numTries])
                    conn.commit()
                    conn.close()
                    if numTries == 0:
                        # Залочились
                        termLockStatus = 1
                        changeParmStatus = 1
                        return()
                else:
                    # Угадали слово
                    termHackStatus = 1
                    changeParmStatus = 1
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
                resBrakes = random.randint(0,wordLen)
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
                        print "Reset Tries"
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
    helloText = "WELOCOME TO ROBCO INDUSTRIES (TM) TERMLINK\n\n" + \
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
    while done:
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
                req.execute('UPDATE params SET value = "YES" WHERE name == "do_lock_open"')
                conn.commit()
                conn.close()
            if selItem == '2':
                # Выбрано оснизить уровень тревоги
                conn = sqlite3.connect('ft.db')
                req = conn.cursor()
                req.execute('UPDATE params SET value = "YES" WHERE name == "do_level_down"')
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
    print numStr
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
    while done:
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
            print "Str = " + str(numStr) + " Chr = " + str(numChr) + " Select = " + str(selItem)
            if selItem == 0:
                numScr -= 1
            if selItem == 1:
                menuStatus = 0
            if selItem == 2:
                numScr += 1
            menuScrNum = numScr
            print numScr
            return ()


while True:
    getDBparms()
    powerScreen()
    lockScreen()
    mainScreen()
    updateDBparms()
    hackScreen()
    menuScreen()
pygame.quit()


