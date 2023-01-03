import pygame

from settings import GAME_NAME
from button import Button
from sprites import TitleSprite, ButtonSprite

class Menu:
    def __init__(self, button_dict, surface):
        self.clicked = False
        self.display_surface = surface
        
        self.title = pygame.sprite.GroupSingle()
        title_sprite = TitleSprite(GAME_NAME, self.display_surface) 
        self.title.add(title_sprite)
        
        self.buttons = pygame.sprite.Group()
        offset_value = 50
        for button_idx,key in enumerate(button_dict):
            button = Button(button_dict[key])
            offset = (button_idx, offset_value)
            sprite = ButtonSprite(button, key, offset, self.display_surface)
            self.buttons.add(sprite)
            
    def click(self, click_val):
        self.clicked = click_val
        
    def check_click_collision(self):
        if self.clicked:
            pos = pygame.mouse.get_pos()
            for sprite in self.buttons:
                if sprite.rect.collidepoint(pos):
                    button = sprite.button
                    button.callback_funct(button.args)
        
    def run(self):
        self.title.update()
        self.buttons.update()
        self.check_click_collision()
        
        