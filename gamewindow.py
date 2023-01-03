import pygame
import sys

from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from game import Game

class GameWindow:
    def __init__(self):
        self.display = pygame.display.set_mode((SCREEN_WIDTH/2, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.game = Game(self.display, self.clock)
        
    def load(self):
        while self.game.state != 'end':
            self.game.play()
                
        pygame.quit()
        sys.exit()