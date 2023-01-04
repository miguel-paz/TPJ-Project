import pygame

from settings import GAME_NAME
from button import Button
from sprites import TitleSprite, ButtonSprite

# Classe tem como objetivo criar um conjunto de botões, utilizando a classe Button e ButtonSprite,
# associando a cada um deles uma transição de estado ao carregar nestes.
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
            
    # Método responsável por atualizar o debaunce do clique
    def click(self, click_val):
        self.clicked = click_val
        
    # Método responsável por verificar a colisão entre o ponto do clique e o botão
    def check_click_collision(self):
        if self.clicked:
            pos = pygame.mouse.get_pos()
            for sprite in self.buttons:
                if sprite.rect.collidepoint(pos):
                    button = sprite.button
                    button.callback_funct(button.args)
        
    # Método principal de atualização de sprites e verificação de sprites
    def run(self):
        self.title.update()
        self.buttons.update()
        self.check_click_collision()
        
        