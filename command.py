import pygame

from settings import *
from datetime import datetime

class Actor:
    def __init__(self):
        self.name = "Unknown"

    def move(self, movement):
        raise NotImplemented
    
    
class Command:
    def __init__(self):
        self.actor = None
        self.dt = datetime.now()

    def execute(self, actor):
        raise NotImplemented

    def __str__(self):
        return f"[{self.dt}] {self.actor.name}: {self.__class__.__name__}"


class Left(Command):
    def execute(self, actor):
        self.actor = actor
        actor.move("Left")

class Right(Command):
    def execute(self, actor):
        self.actor = actor
        actor.move("Right")
        
class Jump(Command):
    def execute(self, actor):
        self.actor = actor
        actor.move("Jump")
        
class Attack(Command):
    def execute(self, actor):
        self.actor = actor
        actor.move("Attack")
        
class Dash(Command):
    def execute(self, actor):
        self.actor = actor
        actor.move("Dash")
        
class Stop(Command):
    def execute(self, actor):
        self.actor = actor
        actor.move("Stop")