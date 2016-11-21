import pygame, sys, time, random, string    
from datetime import datetime
from datetime import timedelta
from pygame.locals import * 

start_time = datetime.now()
def millis():
   dt = datetime.now() - start_time
   ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
   return ms

pygame.init() 
(x,y,fontSize) = (10,40,20) 
myFont = pygame.font.SysFont("DejaVu Sans Mono", fontSize) 
bgColor = (0,8,0) 
screen = pygame.display.set_mode((800,600),0,32) 
pygame.display.set_caption("My First PyGame Windows")
background = pygame.image.load('f3term.png')
fontColor = (0xAA,0xFF,0xC3) 
screen.blit(background, (0, 0))
pygame.display.flip()

done=False

clock=pygame.time.Clock()
s_time=millis()

out_flag = 'bg'
print_flag = 0
bg_flag = 0


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
    def width(self):
        return self.data[3]
    @property
    def height(self):
        return self.data[4]

    def output(self):
        textImage = myFont.render(self.data[4],True,fontColor)
        textRect = textImage.get_rect()
        textRect.center = (self.data[0], self.data[1])
	pygame.display.update(self.r)
	screen.blit(textImage, textRect)
    def clear(self):
        pygame.display.update(self.r)
        screen.blit(self.bg, (self.data[0]-self.data[2]/2, self.data[1]-self.data[3]/2))

helloText = 'Hello, world!'

t = []

def typeWriter(x,y,typeStr,interval):
    i = 0
    for char in typeStr:
        t.append(outSym(100+10*i,100,10,20,char))
        t[i].output()
        time.sleep(interval/1000.0)
        t[i].output()
        i+=1

typeWriter(100,200,helloText,50)

s = outSym(400,400,10,20,'A')

while done==False:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done=True

    c_time=millis()

    if(c_time >= (s_time+1000)):
        if(out_flag == 'bg'):
           out_flag = 'fg'
        else:
           out_flag = 'bg'
        s_time = c_time
           
    if(out_flag == 'bg'):
        if(print_flag == 0):
	    s.output()
            print_flag = 1
	    bg_flag = 0
    else:
	if(bg_flag == 0):
            s.clear()
            bg_flag = 1
            print_flag = 0

    
    clock.tick(30)

pygame.quit()


