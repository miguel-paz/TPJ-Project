import pygame
import copy
import os
import time

from menu import Menu
from level import Level
from level_data import level_0, default_map
from subject import GAME_EVENT, EVENT_PLAYER_INJURED, EVENT_ENEMY_KILLED, EVENT_COIN_ACQUIRED 

class Game:
    def __init__(self, display, clock):
        self.display = display
        self.display_def_width = self.display.get_width()
        self.display_def_height = self.display.get_height()
        self.clock = clock
        self.state = 'menu'
        self.prev_state = None  
        self.screen = None
        self.click = False
            
    def play(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = 'end'
            elif event.type == pygame.MOUSEBUTTONUP:
                self.click = True
                            
        self.display.fill('grey')
        
        self.run()

        pygame.display.update()
        self.clock.tick(60)
        
    def run(self):
        if self.state == 'menu':
            if self.prev_state != self.state:
                if self.display.get_width() != self.display_def_width:
                    pygame.display.quit()
                    self.display = pygame.display.set_mode((self.display_def_width, self.display_def_height))
                
                button_dict = {'Play': (self.change_to_state,'submenu'), 'Quit': (self.change_to_state,'end')}
                self.screen = Menu(button_dict, self.display)
                self.prev_state = self.state
            self.screen.click(self.click)
            self.click = False
            
        elif self.state == 'submenu':
            if self.prev_state != self.state:
                if self.display.get_width() != self.display_def_width:
                    pygame.display.quit()
                    self.display = pygame.display.set_mode((self.display_def_width, self.display_def_height))
                
                button_dict = {'Normal Mode': (self.change_to_state,'play_normal'), 'Survival Mode': (self.change_to_state,'play_survival'), 'Back': (self.change_to_state,'menu')}
                self.screen = Menu(button_dict, self.display)
                self.prev_state = self.state
            self.screen.click(self.click)
            self.click = False
                        
        elif self.state == 'play_normal' or self.state == 'play_survival':
            if self.prev_state != self.state:
                pygame.display.quit()
                self.display = pygame.display.set_mode((self.display_def_width*2, self.display_def_height))
                if self.state == 'play_normal':
                    self.screen = Level(level_0, 'normal', self.display)
                elif self.state == 'play_survival':
                    self.screen = Level(default_map, 'survival', self.display)
                self.prev_state = self.state
            
            if self.screen.win is None:
                pressed = pygame.key.get_pressed()
                if any(pressed):
                    cmd = self.screen.player.command(pressed)
                else:
                    cmd = self.screen.player.command("Stop")
            else:
                self.screen.run()
                pygame.display.update()
                time.sleep(2)
                self.change_to_state('menu')           
        
        self.screen.run()
        
    def change_to_state(self, state):
        self.state = state