import pygame, sys, time, random, string
from pygame.locals import * 
from time import * 
from pygame.sprite import Group

pygame.init() 
screen = pygame.display.set_mode((800,600),0,32) 

(cX,cY,fontSize) = (106,165,20) 
myFont = pygame.font.SysFont("DejaVu Sans Mono", fontSize) 
fontColor = (0xAA,0xFF,0xC3) 
bgColor = (0,8,0) 
bgImage = pygame.image.load("f3term.png")
mainLoop = True 

class Text(object):

    def __init__(self, value, size, color,
                 left_orientation=False,
                 font=None,
                 x=0, y=0,
                 top=None, bottom=None, left=None, right=None,
                 centerx=None, centery=None):

        self._size = size
        self._color = color
        self._value = value
        self._font = pygame.font.Font(font, self._size)
        self.width, self.height = self._font.size(self._value)
        self.left_orientation = left_orientation

        self.image = self._create_surface()
        self.rect = self.image.get_rect()
        if x: self.rect.x = x
        if y: self.rect.y = y
        if top: self.rect.top = top
        if bottom: self.rect.bottom = bottom
        if left: self.rect.left = left
        if right: self.rect.right = right
        if centerx: self.rect.centerx = centerx
        if centery: self.rect.centery = centery

    def _create_surface(self):
        return self._font.render(self._value, True, self._color)

    def set_value(self, new_value):
        if new_value != self._value:
            self._value = new_value
            self.image = self._create_surface()

            new_rect = self.image.get_rect(x = self.rect.x, y = self.rect.y)
            if self.left_orientation:
                width_diff = new_rect.width - self.rect.width
                new_rect.x = self.rect.x - width_diff
            self.rect = new_rect

    def set_position(self, x_or_x_and_y, y=None):
        if y != None:
            self.rect.x = x_or_x_and_y
            self.rect.y = y
        else:
            self.rect.x = x_or_x_and_y[0]
            self.rect.y = x_or_x_and_y[1]

t = Text("T",fontSize,fontColor,True,myFont,12,24)
 
while True:
	t.Surf.blit(screen(10,10))
	screen.blit(0,0)
	flip()
	sys.exit()

