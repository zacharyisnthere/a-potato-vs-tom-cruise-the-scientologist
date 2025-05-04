#!/home/zachary/Documents/Repos/apotatovstomcruisethescientologist/venv/bin/python

import pygame
pygame.init()


class TextSprite(pygame.sprite.Sprite):
    def __init__(self, text, pos, groups, text_size=30, text_col='black', bg_col=None):
        super().__init__(groups)
        
        self.text = text

        self.font = pygame.font.Font('./assets/fonts/Pixeland.ttf', text_size)
        self.text_col = text_col
        self.bg_col = bg_col

        self.pos = pygame.math.Vector2(pos[0], pos[1])
        self.image = self.font.render(self.text, True, self.text_col, self.bg_col)
        
        self.rect = self.image.get_frect(center = self.pos)
    
    def change_color(self, text_col, bg_col=None):
        self.text_col = text_col
        self.bg_col = bg_col
        self.image = self.font.render(self.text, True, self.text_col, self.bg_col)