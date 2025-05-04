#!/home/zachary/Documents/Repos/apotatovstomcruisethescientologist/venv/bin/python

import pygame
pygame.init()

class SliderBar(pygame.sprite.Sprite):
    def __init__(self, rect, color, groups):
        super().__init__(groups)

        self.image = pygame.Surface((rect.width, rect.height))
        self.rect = self.image.get_frect(topleft=rect.topleft)
        self.image.fill(color)
    
    def change_color(self, color):
        self.image.fill(color)
        

class Nob(pygame.sprite.Sprite):
    def __init__(self, rect, color, groups):
        super().__init__(groups)

        self.image = pygame.Surface((rect.width, rect.height))
        self.rect = self.image.get_frect(center=rect.center)
        self.image.fill(color)

    def change_color(self, color):
        self.image.fill(color)

        
#nob_pos is a range from 0-100, where 0 is all the way to the left and 100 is all the way to the right
class Slider(pygame.sprite.Sprite):
    def __init__(self, text, pos, groups, nob_pos, nob_width=10, nob_height=15, nob_color='black', slider_width=100, slider_height=5, slider_color='black', text_size=30, text_col='black', bg_col=None, buf=10):
        super().__init__(groups)

        self.text = text
        self.font = pygame.font.Font('./assets/fonts/Pixeland.ttf', text_size)
        self.text_col = text_col
        self.bg_col = bg_col

        self.pos = pygame.math.Vector2(pos[0], pos[1])
        self.image = self.font.render(self.text, True, self.text_col, self.bg_col)
        self.rect = self.image.get_frect(center = self.pos)


        self.slider_rect = pygame.FRect(self.rect.right+buf, self.rect.top + (self.rect.height/2) - (slider_height/2), slider_width, slider_height)
        self.slider = SliderBar(self.slider_rect, slider_color, groups)

        #abpos is the actual position of the nob
        self.nob_abpos = (nob_pos*self.slider_rect.width)/100 + self.slider_rect.left
        self.nob_rect = pygame.FRect(self.nob_abpos - nob_width/2, self.rect.centery-(nob_height/2), nob_width, nob_height)
        self.nob = Nob(self.nob_rect, nob_color, groups)


    def change_color(self, text_col, bg_col=None):
        self.text_col = text_col
        self.bg_col = bg_col
        self.image = self.font.render(self.text, True, self.text_col, self.bg_col)

    #TODO add a function here to handle variable changes, also create a new file to hold settings and handle setting changes.
    #Note, an easier way to do what I'm specifically wanting to do is to just create some sort of functionality that calls the input system on key hold down rather than just keydown which is what it's at currently.
    #idk it's just really annoying having to push the sliders individually.

    #note: my workaround right now is to just increase the amount the sliders slide by to 10 instead of 1. I still should implement a better menu system, but eh.