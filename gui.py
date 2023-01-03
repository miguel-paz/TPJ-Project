import pygame

from subject import EVENT_PLAYER_INJURED, EVENT_COIN_ACQUIRED

class GUI:
    def __init__(self, player, level):
        self.player_max_health = player.max_health
        self.player_current_health = self.player_max_health
        self.player_coins = 0
        self.level = level
        
        player.register(EVENT_PLAYER_INJURED, self.decrease_health)
        player.register(EVENT_COIN_ACQUIRED, self.add_coin)
        
    def decrease_health(self, context):
        damage = context.damage_taken 
        self.player_current_health -= damage
        if self.player_current_health <= 0:
            context.kill()
            self.level.lost()
    
    def add_coin(self, context):
        value = context.acquired_coin_value
        self.player_coins += value
        if self.player_coins == self.level.level_coins:
            context.kill()
            self.level.won()