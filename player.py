import pygame

from command import Actor, Left, Right, Jump, Attack, Dash, Stop
from subject import Subject, EVENT_COIN_ACQUIRED, EVENT_PLAYER_INJURED

# A classe “Player” identifica e caracteriza o jogador, sendo este capaz de seguir em frente, trás, 
# saltar, atacar e “dashing”, gerando o seu próprio conjunto de estados associados.
class Player(Actor, Subject):
    def __init__(self):
        Subject.__init__(self)
                
        #player movement
        self.control_keys = dict()
        self.gravity = 0.8
        self.gravity_wall = self.gravity/2.5
        self.direction = pygame.math.Vector2(0,0)
        self.x_vel = 3
        self.y_vel = -16
        self.y_inc = self.y_vel/1000
        self.y_inc_temp = self.y_inc
        
        self.right_disable = False
        self.left_disable = False
        
        #player sounds
        self.jump_sound = pygame.mixer.Sound('Sound/jump.wav')
        self.jump_sound.set_volume(0.7)
        
        #player status
        self.max_health = 100
        self.status = 'idle'
        self.jumping = False
        self.to_right = True
        self.on_ground = False
        self.on_ceiling = False
        self.on_left = False
        self.on_right = False
        self.attacking = False
        self.dead = False
        
        #abilities
        self.dash_speed = self.x_vel*2
        self.dash_cooldown = 1    
        self.dash_input = 0
        self.attack_cooldown = 1
        self.attack_input = 0
        
        self.abilities = {'attack': [self.attack_input,self.attack_cooldown], 'dash': [self.dash_input,self.dash_cooldown]}
        
    # Método de associação de teclas (controlos) às ações do jogador
    def controls(self, left, right, jump, attack, dash):
        self.control_keys = {left: Left, right: Right, jump: Jump, attack: Attack, dash: Dash}        
    
    # Lógica de receção, validação e envio do comando
    def command(self, control):
        if control == "Stop":
            cmd = Stop()
            cmd.execute(self)
            return cmd
        else:
            for key in self.control_keys.keys():
                if control[key]:
                    if self.control_keys[key].__name__ == "Jump" and self.jumping:
                        return
                    else:
                        #print("Sending " + self.control_keys[key].__name__ )
                        cmd = self.control_keys[key]()
                        cmd.execute(self)
            return
        print("Invalid key")
        
    # Consoante o comando recebido, é executada uma ação representante do mesmo
    def move(self, movement):
    
        if movement == "Right":
            self.direction.x = 1
            self.to_right = True
        elif movement == "Left":
            self.direction.x = -1
            self.to_right = False
        
        if movement == "Stop":
            self.direction.x = 0
        
        if movement == "Jump": 
            if self.on_ground:
                self.jump()
                
        if movement == "Attack":
            self.attack()
                
        if movement == "Dash":
            self.dash()
        
    # Método de salto do jogador
    def jump(self):
        #self.direction.y = max(self.direction.y+self.y_inc_temp,self.y_vel)
        self.direction.y = self.y_vel
        self.jump_sound.play()
        
    def attack(self):
        current_time = pygame.time.get_ticks()/1000
        if self.check_cooldown('attack', current_time) and not self.attacking:
            self.attacking = True
            self.abilities['attack'][0] = current_time
        else: 
            print('attack on cooldown')
    
    # Método de dashing do jogador, fazendo com que este percorre uma grande distancia num curto perio de tempo
    def dash(self):
        current_time = pygame.time.get_ticks()/1000
        if self.check_cooldown('dash', current_time):
            if self.to_right:
                self.direction.x = self.dash_speed
            else:
                self.direction.x = -self.dash_speed
            
            self.abilities['dash'][0] = current_time
        else: 
            print('dash on cooldown')
            if self.on_ground:
                self.direction.x = 0
                
    # Verifica os cooldowns das habilidades consoante a ultima vez que foram usadas
    def check_cooldown(self,ability,current_time):
        input_time = self.abilities[ability][0]
        cooldown = self.abilities[ability][1]
        if (current_time - input_time) >= cooldown:
            return True
        return False
         
    # Logica de transição de estados do jogador
    def get_status(self):
        if self.attacking:
            self.status = "attack"
        elif self.direction.y < 0:    
            self.status = 'jump'
        elif self.direction.y > self.gravity:
            self.status = 'fall'
        else:
            if self.direction.x != 0:
                self.status = 'run'
            else:
                self.status = 'idle'
        
    # Método de notificação de perda de vida
    def get_hit(self, damage):
        self.damage_taken = self.max_health*damage
        self.notify(EVENT_PLAYER_INJURED)
    
    # Método de notificação de moeda colecionada 
    def get_coin(self, value):
        self.acquired_coin_value = value
        self.notify(EVENT_COIN_ACQUIRED)
    
    # Método para forçar a morte do jogador
    def kill(self):
        if not self.dead: print("Player has died")
        self.dead = True
            