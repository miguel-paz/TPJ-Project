import pygame

from random import randint

class Enemy():
    def __init__(self):
        self.speed = randint(2,8)
        self.damage = 1/4
        
    def reverse(self):
        self.speed *= -1