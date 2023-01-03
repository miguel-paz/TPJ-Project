
class Button:
    def __init__(self, callback):
        self.callback_funct = callback[0]
        self.args = callback[1]