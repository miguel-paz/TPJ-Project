import pygame

GAME_EVENT = pygame.event.custom_type()

EVENT_PLAYER_INJURED = "event_player_injured"
EVENT_ENEMY_KILLED = "event_enemy_killed"
EVENT_COIN_ACQUIRED = "event_coin_acquired"

class Subject:
    def __init__(self):
        self.events = {}

    def register(self, event, event_handler):
        if event not in self.events:
            self.events[event] = []
        self.events[event].append(event_handler)

    def notify(self, event, arg = None):
        for event_handler in self.events[event]:
            event_handler(self)

        ev = pygame.event.Event(GAME_EVENT, {'name': event, 'obj': self})
        pygame.event.post(ev)