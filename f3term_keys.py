import pygame, sys, time, random, string
from pygame.locals import * 

pygame.init() 
screen = pygame.display.set_mode((800,600),0,32) 
pygame.display.set_caption("My First PyGame Windows")
helloText = ["WELCOME TO ROBCO INDUSTRIES (TM) TERMLINK\n\n\
>SET TERMINAL INQUIRE\n\n\
RIT-V300\n\n\
>SET FILE/PROTECTION OWNER:RWED ACCOUNTS.F\n\
>SET HALT RESTART/MAINT\n\n\
Initializing Robco Industries(TM) MF Boot Agent v2.3.0\n\
RETROS BIOS\n\
RBIOS-4.02.08.00 52EE5.E7.E8\n\
Copyright 2201-2203 Robco Ind.\n\
Uppermem 64 KB\n\
Root (5A8)\n\
Maintenance Mode\n\n\
>RUN DEBUG/ACCOUNTS.F",
""]


textCount = 2

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
"                "   )

cursor, mask = pygame.cursors.compile(inverseBar_strings,'x','.','o')
pygame.mouse.set_cursor((16,16),(7,5),cursor,mask)

(cX,cY,fontSize) = (106,165,20) 
myFont = pygame.font.SysFont("DejaVu Sans Mono", fontSize) 
fontColor = (0xAA,0xFF,0xC3) 
bgColor = (0,8,0) 
bgImage = pygame.image.load("f3term.png")
mainLoop = True 

i = 0
numScreens = 0
firstTime = 0
startTime = 0
myTime = 30
dY = 0
dX = 0 
numText = 0
numTries = 4
wordLen = 8
wordNum = 10
deltaY = 23
deltaX = 12
wordBase = ""
wordDisp = ""
garbStr = ""

WIDTH = 12
HEIGHT = 6
COLOR = (0xAA,0xFF,0xC3) 


screen.fill(bgColor) 
screen.blit(bgImage,(0,0)) 

def typeWriter(myText, myX, myY):
	global i
	global firstTime
	global startTime
	global deltaY
	global deltaX
	global dY
	global dX
	global myTime
	global numScreens
	if firstTime == 0:
		startTime = int(round(time.time() * 1000))
		firstTime = 1
		dX = 0
	flag = 0
	if (int(round(time.time() * 1000)) - startTime) >= myTime:
		myChar = myText[i]
		if myChar == '\n':
			dY += deltaY
			dX = 0
		else:
			if myChar == '\r':
				dx = 0
			else:
				fontImage = myFont.render(myChar,True,fontColor)
				screen.blit(fontImage,(myX + dX * deltaX,myY + dY)) 
	        		startTime = int(round(time.time() * 1000))
				dX += 1
		i += 1
	if i >= len(myText):
		i = 0
		flag = 0
		firstTime = 0
		myTime = 30
		dY = 0
		numScreens += 1
		return

def fieldFull():
	global wordBase
	global wordDisp
	global wordNum
	global wordLen
	global garbStr

	i = 0
	triesAst= ''
	while i < numTries:
		triesAst += '* '
		i += 1
	helloText[1]="ROBCO INDUSTRIES (TM) TERMLINK PROTOCOL\n\
ENTER PASSWORD\n\n\
{0} TRIES {1}\n\n".format(numTries,triesAst)
	i = 0
	f = open ('words8.txt','r')
	for line in f:
		wordBase += line.strip()
		i += 1
	f.close
	
	wordCnt = i

	i = 0
	n = 0
	
	step = int(wordCnt/wordNum)

	while i < wordNum:
		n = random.randint(i*step,i*step+step)
		wordDisp += wordBase[n*wordLen:n*wordLen+wordLen]
		i += 1

	i = 0
	j = 0

	step = int(408/wordNum)
	print step

	while i < wordNum: 
		cPos = random.randint(0,step-wordLen)
		print cPos
		j = 0
		while j < cPos:
			garbStr += random.choice(string.punctuation)
			j += 1
		
		garbStr += wordDisp[i*wordLen:i*wordLen+wordLen]
		
		j += wordLen
	
		while j < step:
			garbStr += random.choice(string.punctuation)
			j += 1
		i += 1

	j = len(garbStr)

	while j<408:
		garbStr += random.choice(string.punctuation)
		j += 1
	
	print len(garbStr)
	
	i = 0

	startHex = random.randint(0x1A00,0xFA00)

	while i < 17:
		hexLeft = '{0:#4X}  '.format(startHex + i*12)
		hexRight = '    {0:#4X}  '.format(startHex + (i+17)*12)
		helloText[1] = helloText[1] + "\n" + hexLeft + garbStr[i*12:i*12+12] 
		helloText[1] = helloText[1] + hexRight + garbStr[(i+17)*12:(i+17)*12+12]
		i += 1
	
	helloText[1] = helloText[1] + "  >"

fieldFull()

while True: 
	pygame.display.update()
	if(numScreens == 0):
		typeWriter(helloText[0],10,10)
	if(numScreens == 1):
		if(firstTime == 0):
			pygame.time.delay(1000)
			screen.fill(bgColor) 
			screen.blit(bgImage,(0,0)) 
			pygame.display.update()			
		typeWriter(helloText[1],10,10)
	
	for ev in pygame.event.get():
		 if ev.type==QUIT:
			 exit()

 	press=pygame.key.get_pressed()
	if(press[pygame.K_RETURN] != 0 ):
		myTime = 10
	if(press[pygame.K_SPACE] != 0 ):
		myTime = 10
	if(press[pygame.K_ESCAPE] != 0 ):
		exit()

	(curX,curY) = pygame.mouse.get_pos()
	(b1,b2,b3) = pygame.mouse.get_pressed()
	if(b1 == True):
		numstr = curY / deltaY
		numchr = curX / deltaX - 1
		splText = helloText[1].split('\n',600/deltaY)
		if(numstr >= 6):
			txtstr = "".join([splText[numstr-1],splText[numstr],splText[numstr+1]])
			if(numchr>=9):
				pos = len(splText[numstr-1])+numchr
				if(txtstr[pos].isalpha):
					crchar = txtstr[pos]
					selword = ""
					i = 0
					while (crchar.isalpha()):
						crchar = txtstr[pos+i]
						i-=1
					i+=2
					crchar = splText[numstr][numchr+i]
					while (crchar.isalpha()):
						selword += crchar
						crchar = txtstr[pos+i]
						if(crchar == ' ' or crchar == '\n'):
							pos+=(len(splText[numstr]) - 11)
							print len(splText[numstr]) - 11
							crchar = txtstr[pos]						
							i = 0
						i+=1
        				print selword
		
	

pygame.quit() 