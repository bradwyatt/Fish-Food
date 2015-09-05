"""
custom icon, author name, more info on the COMPILED file
taskbar icon
difficulty levels (hard, sharks faster)
red fish respawn by big red fish eggs?
fix game over screen to not cut through shit
fish collision
levels instead of score
"""
import pygame, random, sys
from pygame.locals import *
from genmenu import *
running = True #Flags game as on
menuOn = 1
firstMessage = 1
Rooms = []
(screenWidth, screenHeight) = 928, 544
SCORE, scoreBlit, onePowerupSound, scoreDisappearTimer = 0, 0, 0, 0
player = None
screen = None
keys = [False, False, False, False]
walls = []
images = {}
sounds = {}
lastPressed = 0
(x1, y1) = (0, 0)
(x2, y2) = (0, -screenHeight)
allsprites = pygame.sprite.Group()
clock = pygame.time.Clock()

def load_sound(file, name):
    sound = pygame.mixer.Sound(file)
    sounds[name] = sound
    
def load_image(file, name, transparent, alpha):
    new_image = pygame.image.load(file)
    if alpha == True:
        new_image = new_image.convert_alpha()
    else:
        new_image = new_image.convert()
    if transparent:
        colorkey = new_image.get_at((0,0))
        new_image.set_colorkey(colorkey, RLEACCEL)
    images[name] = new_image
    
def displayCaption():
    pygame.display.set_caption("Fish Food")

def quit():
    print 'Thanks for playing'
    sys.exit()

def startplaceholder(screen):
    global menuOn, keys
    Rooms = []
    Rooms.append(Room())
    SCORE = 0
    menuOn = 0
    keys = [False, False, False, False]
    pass

def infoplaceholder(screen):
    global menuOn
    menuOn = 4
    pass

class Menu(object):
    def __init__(self,screen):
        self.screen = screen
        self.title = startMenu
        self.menu = genmenu(['START', lambda: startplaceholder(screen)],['INFO', lambda: infoplaceholder(screen)], ['QUIT', lambda: quit()])
        self.menu.changeFont('oceanfont.ttf',28)
        self.menu.position(430,190)
        self.menu.defaultColor((0,0,0))
        self.menu.choiceColor((255,255,255))
        self.clock = pygame.time.Clock()
        event = pygame.event.get()
        self.menu.create(self.screen)
        self.menu.choose(event)
        self.main_loop()

    def main_loop(self):
        global menuOn
        while menuOn == 1:
            self.clock.tick(60)
            events = pygame.event.get()
            self.menu.choose(events)
            self.screen.blit(self.title, (0, 0))
            highScoreText = oceanFontMain.render("High Score: "+str(get_high_score()), 1, (243,189,0))
            self.screen.blit(highScoreText, (550, 240))
            self.menu.create(self.screen)
            pygame.display.flip()
            for event in events:
                if event.type == QUIT:
                    sys.exit()
                    
class InfoScreen(object):
    def __init__(self,screen):
        self.screen = screen
        self.title = infoScreen
        self.clock = pygame.time.Clock()
        event = pygame.event.get()
        self.main_loop()

    def main_loop(self):
        global menuOn
        while menuOn == 4:
            self.clock.tick(60)
            self.screen.blit(self.title, (0, 0))
            events = pygame.event.get()
            pygame.display.flip()
            for event in events:
                if event.type == QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        menuOn = 1

class GameOver(object):
    def __init__(self,screen):
        self.screen = screen
        self.title = gameOver
        self.clock = pygame.time.Clock()
        event = pygame.event.get()
        self.main_loop()

    def main_loop(self):
        global menuOn
        while menuOn == 2:
            self.clock.tick(60)
            events = pygame.event.get()
            self.screen.blit(self.title, (0, 0))
            scoreGameOverText = arialFont.render("Score: "+str(SCORE), 1, (0,0,0))
            self.screen.blit(scoreGameOverText, (50, 175))
            if(SCORE == get_high_score()):
                highScoreText = oceanFontGameOver.render("High Score!", 1, (0,0,0))
                self.screen.blit(highScoreText, (50, 260))
            else:
                highScoreText = oceanFontGameOver.render("Try Again!", 1, (0,0,0))
                self.screen.blit(highScoreText, (50, 270))
            highScoreText = arialFont.render("Personal Best: "+str(get_high_score()), 1, (0,0,0))
            self.screen.blit(highScoreText, (50, 220))
            pygame.display.flip()
            for event in events:
                if event.type == QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        reset()
                        menuOn = 1

def resumeplaceholder(screen):
    global menuOn, keys
    menuOn = 0
    keys = [False, False, False, False]
    if(player.starpower != 0):
        sounds["snd_poweruptimer"].play()
    pass

def mainmenuplaceholder(screen):
    global menuOn
    menuOn = 1
    pass

class PauseScreen(object):
    def __init__(self,screen):
        self.screen = screen
        self.title = bgwater
        self.menu = genmenu(['Resume', lambda: resumeplaceholder(screen)],['End Game', lambda: mainmenuplaceholder(screen)])
        self.menu.changeFont('oceanfont.ttf',28)
        self.menu.position(430,190)
        self.menu.defaultColor((0,0,0))
        self.menu.choiceColor((255,255,255))
        self.clock = pygame.time.Clock()
        event = pygame.event.get()
        self.menu.create(self.screen)
        self.menu.choose(event)
        self.main_loop()

    def main_loop(self):
        global menuOn
        while menuOn == 3:
            self.clock.tick(60)
            events = pygame.event.get()
            self.menu.choose(events)
            self.screen.blit(self.title, (0, 0))
            self.menu.create(self.screen)
            pygame.display.flip()
            for event in events:
                if event.type == QUIT:
                    sys.exit()

class Wall(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_wall"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["player_left"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.playerWidth, self.playerHeight = (41, 19)
        self.speedpower, self.speedpowertimer, self.sizescore = 0, 0, 0
        self.speedX, self.speedY = 6, 6
        self.puTimeLeft, self.speedTimeLeft = 5, 5
        self.starpower, self.starpowertimer, self.playeranimatetimer = 0, 0, 0
        self.pos = [screenWidth/2, screenHeight/2]
    def update(self):
        global onePowerupSound
        self.rect = self.image.get_rect()
        newpos = (self.pos[0], self.pos[1])
        self.rect.topleft = newpos
        if(self.sizescore < 0):
            self.sizescore = 0
        if(self.sizescore > 40):
            self.sizescore = 40
        self.image = pygame.transform.smoothscale(self.image, (self.playerWidth+self.sizescore, self.playerHeight+self.sizescore))
        self.rect.inflate_ip(self.sizescore, self.sizescore)
        if(self.starpower == 0): #no star power
            self.starpowertimer = 0
            self.puTimeLeft = 5
        elif(self.starpower == 1): #star powerup
            self.playeranimatetimer += 1
            if(self.playeranimatetimer > 6):
                self.playeranimatetimer = 0
            for i in range(5,0,-1):
                if self.starpowertimer == i*100:
                    self.puTimeLeft -= 1
        elif(self.starpower == 2): #mini sharks
            for i in range(5,0,-1):
                if self.starpowertimer == i*100:
                    self.puTimeLeft -= 1
        if(self.speedpower != 0):
            self.speedpowertimer += 1
        else:
            self.speedpowertimer = 0
        if(self.speedpower == 0):
            self.speedX, self.speedY = 6, 6
            self.speedTimeLeft = 5
        elif(self.speedpower == 1): #seahorse
            for i in range(5,0,-1):
                if self.speedpowertimer == i*100:
                    self.speedTimeLeft -= 1
        elif(self.speedpower == 2): #jellyfish
            for i in range(5,0,-1):
                if self.speedpowertimer == i*100:
                    self.speedTimeLeft -= 1
        if(self.starpowertimer > 500): #powerup is over on the player
            self.starpower, self.starpowertimer = 0, 0
            onePowerupSound -= 1
            sounds["snd_poweruptimer"].stop()
            self.puTimeLeft = 5
        if(self.speedpowertimer > 500):
            self.speedpower, self.speedpowertimer = 0, 0
            onePowerupSound -= 1
            sounds["snd_poweruptimer"].stop()
            self.speedTimeLeft = 5

class RedFish(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_redfish"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.direction = (random.choice([-2,2]),random.choice([-2,0,2]))
        self.change_dir_timer = 0
    def update(self):
        newpos = (self.rect.topleft[0]+self.direction[0],self.rect.topleft[1]+self.direction[1])
        self.rect.topleft = newpos
        self.change_dir_timer += 1
        if(self.direction[0] == -2):
            self.image = pygame.transform.flip(images["spr_redfish"], 1, 0)
        elif(self.direction[0] == 2):
            self.image = images["spr_redfish"]
        if(self.change_dir_timer > random.randrange(100,600)):
            self.direction = random.choice([(self.direction[0]*-1,self.direction[1]),(self.direction[0],self.direction[1]*-1),
                                           (self.direction[0]*-1,self.direction[1]*-1)])
            self.change_dir_timer = 0
    def collision_with_wall(self, wall):
        if self.rect.colliderect(wall.rect):
            self.change_dir_timer = 0
            if self.rect.left < 32: #left walls
                self.direction = (2, random.choice([-2,0,2]))
            elif self.rect.top > screenHeight-64: #bottom walls, 
                self.direction = (random.choice([-2,0,2]), -2)
            elif self.rect.right > screenWidth-32: #right walls
                self.direction = (-2, random.choice([-2,0,2]))
            elif self.rect.top < 32: #top walls
                self.direction = (random.choice([-2,0,2]), 2)
class GreenFish(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_greenfish"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.direction = (random.choice([-4,4]),random.choice([-4,0,4]))
        self.change_dir_timer = 0
        global greenScoreList
        greenScoreList = [0, 0, 0] #3 spots for 3 greenfish
    def update(self):
        newpos = (self.rect.topleft[0]+self.direction[0],self.rect.topleft[1]+self.direction[1])
        self.rect.topleft = newpos
        self.change_dir_timer += 1
        if(self.direction[0] == -4):
            for i in range(3):
                if(self == greenFishes[i]):
                    if(greenScoreList[i] < 70):
                        self.image = images["spr_greenfish_left"]
        elif(self.direction[0] == 4):
            for i in range(3):
                if(self == greenFishes[i]):
                    if(greenScoreList[i] < 70):
                        self.image = images["spr_greenfish"]
        if(self.change_dir_timer > random.randrange(50,300)):
            self.direction = random.choice([(self.direction[0]*-1,self.direction[1]),(self.direction[0],self.direction[1]*-1),
                                           (self.direction[0]*-1,self.direction[1]*-1)])
            self.change_dir_timer = 0
    def collision_with_wall(self, wall):
        self.change_dir_timer = 0
        if self.rect.colliderect(wall.rect):
            if self.rect.left < 32: #left walls
                self.direction = (4, random.choice([-4,4]))
            elif self.rect.top > screenHeight-64: #bottom walls, 
                self.direction = (random.choice([-4,4]), -4)
            elif self.rect.right > screenWidth-32: #right walls
                self.direction = (-4, random.choice([-4,4]))
            elif self.rect.top < 32: #top walls
                self.direction = (random.choice([-4,4]), 4)
    def collision_with_redFish(self, thisGreenFish):
        for i in range(3):
            if i == thisGreenFish:
                greenScoreList[i] += 10
                if(greenScoreList[i] == 70):
                    self.image = pygame.transform.smoothscale(images["spr_biggreenfish"], (103, 58))
                break
    def small_collision_with_player(self):
        self.image = images["spr_greenfish"]
        self.rect.topleft = (random.randrange(100, screenWidth-100), random.randrange(100, screenHeight-100))
class SilverFish(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_silverfish"]
        self.rect = self.image.get_rect()
        self.rect.topleft = (random.choice([-50,screenWidth]), random.randrange(50, 150))
        self.restarttimer = 0
        self.direction = random.choice([0,1]) #right or left?
        allsprites.add(self)
    def update(self):
        self.restarttimer += 1
        if (self.restarttimer > 250):
            if(self.rect.topleft[0] == -50):
                self.direction = 1 #right
            elif(self.rect.topleft[0] == screenWidth):
                self.direction = 0 #left
            if(self.direction == 1): #right movements
                self.rect.topleft = self.rect.topleft[0]+3, self.rect.topleft[1]
                self.image = images["spr_silverfish"]
            elif(self.direction == 0): #left movements
                self.rect.topleft = self.rect.topleft[0]-3, self.rect.topleft[1]
                self.image = pygame.transform.flip(images["spr_silverfish"], 1, 0)
            if(self.rect.topleft[0] < -40 and self.direction == 0): #restarts position
                self.rect.topleft = (random.choice([-50,screenWidth]), random.randrange(50, 150))
                self.rect.topleft = self.rect.topleft[0], self.rect.topleft[1]
                self.restarttimer = 0
            elif(self.rect.topleft[0] > screenWidth-10 and self.direction == 1): #restarts position
                self.rect.topleft = (random.choice([-50,screenWidth]), random.randrange(50, 150))
                self.rect.topleft = self.rect.topleft[0], self.rect.topleft[1]
                self.restarttimer = 0
class Shark(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_shark"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.direction = (random.choice([-3,3]),random.choice([-3,3]))
    def update(self):
        if(player.starpower == 2):
            self.image = pygame.transform.smoothscale(self.image, (60, 30))
        else:
            self.image = images["spr_shark"]
        if(self.rect.topleft[1] < 0):
            if(SCORE >= 5):
                if(self == sharks[0]):
                    self.rect.topleft = (self.rect.topleft[0], self.rect.topleft[1]+3)
                    if(player.starpower != 2 and SCORE <= 10):
                        sounds["snd_sharkincoming"].play()
            if(SCORE >= 25):
                if(self == sharks[1]):
                    self.rect.topleft = (self.rect.topleft[0], self.rect.topleft[1]+3)
                    if(player.starpower != 2 and SCORE <= 30):
                        sounds["snd_sharkincoming"].play()
            if(SCORE >= 50):
                if(self == sharks[2]):
                    self.rect.topleft = (self.rect.topleft[0], self.rect.topleft[1]+3)
                    if(player.starpower != 2 and SCORE <= 55):
                        sounds["snd_sharkincoming"].play()
            if(SCORE >= 75):
                if(self == sharks[3]):
                    self.rect.topleft = (self.rect.topleft[0], self.rect.topleft[1]+3)
                    if(player.starpower != 2 and SCORE <= 80):
                        sounds["snd_sharkincoming"].play()
        else:
            newpos = (self.rect.topleft[0]+self.direction[0],self.rect.topleft[1]+self.direction[1])
            self.rect.topleft = newpos
    def collision_with_wall(self, wall):
        if self.rect.colliderect(wall.rect):
            if self.rect.left < 32: #left walls
                self.direction = (3, random.choice([-3,3]))
            elif self.rect.top > screenHeight-64: #bottom walls, 
                self.direction = (random.choice([-3,3]), -3)
            elif self.rect.right > screenWidth-32: #right walls
                self.direction = (-3, random.choice([-3,3]))
            elif self.rect.top < 32: #top walls
                self.direction = (random.choice([-3,3]), 3)
class BrightBlueFish(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_brightbluefish"]
        self.direction = random.choice([0,1]) #move left: 0, move right: 1
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.movingVar = 0
    def update(self):
        if (self.movingVar == 1):
            if(self.rect.topleft[0] == -1000):
                self.direction = 1 #right
                self.image = images["bigBrightBlueFish"]
            elif(self.rect.topleft[0] == screenWidth+1000):
                self.direction = 0 #left
                self.image = images["bigBrightBlueFishLeft"]
            if(self.direction == 1): #right movements
                self.rect.topleft = self.rect.topleft[0]+4, self.rect.topleft[1]
            elif(self.direction == 0): #left movements
                self.rect.topleft = self.rect.topleft[0]-4, self.rect.topleft[1]
            if(self.rect.topleft[0] < -990 and self.direction == 0): #restarts position
                self.image = images["spr_brightbluefish"]
                if(SCORE%50 <= 2):
                    self.rect.topleft = self.rect.topleft[0]-20, self.rect.topleft[1]
                elif(SCORE%50 > 2):
                    self.rect.topleft = (random.choice([-1000,screenWidth+1000]), random.randrange(50, screenHeight-200))
                    self.movingVar = 0
            elif(self.rect.topleft[0] > screenWidth+990 and self.direction == 1): #restarts position
                self.image = images["spr_brightbluefish"]
                if(SCORE%50 <= 2):
                    self.rect.topleft = self.rect.topleft[0]+20, self.rect.topleft[1]
                elif(SCORE%50 > 2):
                    self.rect.topleft = (random.choice([-1000,screenWidth+1000]), random.randrange(50, screenHeight-200))
                    self.movingVar = 0
        else:
            self.image = images["spr_brightbluefish"]

class RainbowFish(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_rainbowfish"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.scoreExit = 0
        self.rainbowtimer = 0
        self.size = [55, 35]
        self.pos = (random.randrange(100, screenWidth-100), -100)
    def update(self): # chase movement
        self.rect.topleft = (self.pos[0], self.pos[1])
        self.rainbowtimer += 1
        if self.rainbowtimer >= 2000: #return; go off screen
            if(self.pos[1] > -100):
                self.scoreExit = 1
                self.pos = (self.pos[0], self.pos[1]-2)
            else:
                self.pos = (random.randrange(100, screenWidth-100), -100)
                self.rainbowtimer, self.scoreExit = 0, 0
                if(self.size[0]-20 <= 55): #one check on [0], so 85 width is max size
                    self.size[0] += 10
                    self.size[1] += 10
                self.image = images["spr_rainbowfish"]
        elif self.rainbowtimer >= 1250: #chase player
            if self.scoreExit == 0:
                if(self.rainbowtimer >= 1500 and ((self.size[0]-45 <= player.sizescore) or (player.starpower == 1))):
                    #Avoid Player (fish realizes it at rainbowtimer=1500)
                    if self.pos[0] > player.pos[0]:
                        self.pos = (self.pos[0]+2, self.pos[1])
                    elif self.pos[0] < player.pos[0]:
                        self.pos = (self.pos[0]-2, self.pos[1])
                    if self.pos[1] < player.pos[1]:
                        self.pos = (self.pos[0], self.pos[1]-2)
                    elif self.pos[1] > player.pos[1]:
                        self.pos = (self.pos[0], self.pos[1]+2)
                    if(self.pos[0] < -32 or self.pos[0] > screenWidth):
                        self.rainbowtimer = 2000
                        self.pos = (-50, -50)
                    elif(self.pos[1] < 32 or self.pos[1] > screenHeight):
                        self.rainbowtimer = 2000
                        self.pos = (-50, -50)
                else:
                    #Chase Player
                    if self.pos[0] > player.pos[0]:
                        self.pos = (self.pos[0]-1, self.pos[1])
                    elif self.pos[0] < player.pos[0]:
                        self.pos = (self.pos[0]+1, self.pos[1])
                    if self.pos[1] < player.pos[1]:
                        self.pos = (self.pos[0], self.pos[1]+1)
                    elif self.pos[1] > player.pos[1]:
                        self.pos = (self.pos[0], self.pos[1]-1)
        elif self.rainbowtimer >= 1150: #move down at start
            if self.scoreExit == 0:
                if(self.size[0]-30 == 55): #so it doesn't get more blurry each time at max size
                    self.pos = (self.pos[0], self.pos[1]+2)
                else:
                    self.image = pygame.transform.smoothscale(self.image, (self.size[0], self.size[1]))
                    self.pos = (self.pos[0], self.pos[1]+2)
class Snake(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_snake"]
        self.restarttimer = 0
        self.direction = random.choice([0,1]) #move left: 0, move right: 1
        self.rect = self.image.get_rect()
        self.snakeplayeranimatetimer = 0
        self.randomspawn = random.randrange(200, 400)
        allsprites.add(self)
    def update(self):
        self.snakeplayeranimatetimer += 1
        if(self.direction == 0): #go left
            if(self.snakeplayeranimatetimer > 5):
                self.image = images["spr_snake2"]
            if(self.snakeplayeranimatetimer > 10):
                self.image = images["spr_snake3"]
            if(self.snakeplayeranimatetimer > 15):
                self.image = images["spr_snake4"]
            if(self.snakeplayeranimatetimer > 20):
                self.image = images["spr_snake"]
                self.snakeplayeranimatetimer = 0
        elif(self.direction == 1): #go right
            if(self.snakeplayeranimatetimer > 5):
                self.image = pygame.transform.flip(images["spr_snake2"], 1, 0)
            if(self.snakeplayeranimatetimer > 10):
                self.image = pygame.transform.flip(images["spr_snake3"], 1, 0)
            if(self.snakeplayeranimatetimer > 15):
                self.image = pygame.transform.flip(images["spr_snake4"], 1, 0)
            if(self.snakeplayeranimatetimer > 20):
                self.image = pygame.transform.flip(images["spr_snake"], 1, 0)
                self.snakeplayeranimatetimer = 0
        self.restarttimer += 1
        if (self.restarttimer > self.randomspawn):
            if(self.rect.topleft[0] == -70):
                self.direction = 1 #right
            elif(self.rect.topleft[0] == screenWidth):
                self.direction = 0 #left
            if(self.direction == 1): #right movements
                self.rect.topleft = self.rect.topleft[0]+2, self.rect.topleft[1]
            elif(self.direction == 0): #left movements
                self.rect.topleft = self.rect.topleft[0]-2, self.rect.topleft[1]
            if(self.rect.topleft[0] < -60 and self.direction == 0): #restarts position
                self.rect.topleft = (random.choice([-70,screenWidth]), random.randrange(screenHeight-110, screenHeight-50))
                self.rect.topleft = self.rect.topleft[0], self.rect.topleft[1]
                self.restarttimer = 0
            elif(self.rect.topleft[0] > screenWidth-10 and self.direction == 1): #restarts position
                self.rect.topleft = (random.choice([-70,screenWidth]), random.randrange(screenHeight-110, screenHeight-50))
                self.rect.topleft = self.rect.topleft[0], self.rect.topleft[1]
                self.restarttimer = 0
class SeaHorse(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_seahorse"]
        self.restarttimer = 0
        self.direction = random.choice([0,1]) #move left: 0, move right: 1
        self.randomspawn = random.randrange(1500, 2000)
        self.rect = self.image.get_rect()
        allsprites.add(self)
    def update(self):
        self.restarttimer += 1
        if(self.direction == 1):
            self.image = pygame.transform.flip(images["spr_seahorse"], 1, 0)
        else:
            self.image = images["spr_seahorse"]
        if (self.restarttimer > self.randomspawn):
            if(self.rect.topleft[0] == -70):
                self.direction = 1 #right
            elif(self.rect.topleft[0] == screenWidth):
                self.direction = 0 #left
            if(self.direction == 1): #right movements
                self.rect.topleft = self.rect.topleft[0]+3, self.rect.topleft[1]
            elif(self.direction == 0): #left movements
                self.rect.topleft = self.rect.topleft[0]-3, self.rect.topleft[1]
            if(self.rect.topleft[0] < -60 and self.direction == 0): #restarts position
                self.rect.topleft = (random.choice([-70,screenWidth]), random.randrange(50, screenHeight-200))
                self.rect.topleft = self.rect.topleft[0], self.rect.topleft[1]
                self.restarttimer = 0
                self.randomspawn = random.randrange(1500, 2000)
            elif(self.rect.topleft[0] > screenWidth-10 and self.direction == 1): #restarts position
                self.rect.topleft = (random.choice([-70,screenWidth]), random.randrange(50, screenHeight-200))
                self.rect.topleft = self.rect.topleft[0], self.rect.topleft[1]
                self.restarttimer = 0
                self.randomspawn = random.randrange(1500, 2000)
class JellyFish(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_jellyfish"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.returnback = 0
        self.jellyfishtimer = 0
        self.jellyfishanimatetimer = 0
        self.jellyfishrandomspawn = random.randrange(700, 900)
        self.newpos = self.rect.topleft[0], self.rect.topleft[1]
    def update(self):
        self.jellyfishanimatetimer += 1
        self.jfstring = [images["spr_jellyfish"], images["spr_jellyfish2"], images["spr_jellyfish3"], images["spr_jellyfish4"],
                    images["spr_jellyfish5"], images["spr_jellyfish6"], images["spr_jellyfish7"]]
        for i in range(2, 16, 2): #cycle through first 13 sprite animations
            if(self.jellyfishanimatetimer >= i):
                self.image = self.jfstring[(i/2)-1]
        for i in range(18, 28, 2): #cycle through 13 sprite animations backwards
            if(self.jellyfishanimatetimer > i):
                self.image = self.jfstring[((28-i)/2)+1]
        if(self.jellyfishanimatetimer > 28):
            self.jellyfishanimatetimer = 1
        self.jellyfishtimer += 1
        if(self.rect.topleft[1] == -50):
            self.returnback = 0
        if self.rect.topleft[1] > screenHeight-80:
            #collide with BOTTOM wall
            self.returnback = 1
        if self.returnback == 0 and self.jellyfishtimer > self.jellyfishrandomspawn:
            if(SCORE >= 0):
                if(self == jellyFishes[0]):
                    self.newpos = (self.rect.topleft[0], self.rect.topleft[1]+3)
                    self.rect.topleft = self.newpos
            if(SCORE >= 30):
                if(self == jellyFishes[1]):
                    self.newpos = (self.rect.topleft[0], self.rect.topleft[1]+3)
                    self.rect.topleft = self.newpos
            if(SCORE >= 60):
                if(self == jellyFishes[2]):
                    self.newpos = (self.rect.topleft[0], self.rect.topleft[1]+3)
                    self.rect.topleft = self.newpos
        elif self.returnback == 1:
            if(SCORE >= 0):
                if(self == jellyFishes[0]):
                    self.newpos = (self.rect.topleft[0], self.rect.topleft[1]-3)
                    self.rect.topleft = self.newpos
                    if(self.rect.topleft[1] < -32):
                        self.jellyfishtimer = 0
                        self.jellyfishrandomspawn = random.randrange(500, 1200)
                        self.rect.topleft = random.randrange(100, screenWidth-100), -50
            if(SCORE >= 10):
                if(self == jellyFishes[1]):
                    self.newpos = (self.rect.topleft[0], self.rect.topleft[1]-3)
                    self.rect.topleft = self.newpos
                    if(self.rect.topleft[1] < -32):
                        self.jellyfishtimer = 0
                        self.jellyfishrandomspawn = random.randrange(700, 1200)
                        self.rect.topleft = random.randrange(100, screenWidth-100), -50
            if(SCORE >= 20):
                if(self == jellyFishes[2]):
                    self.newpos = (self.rect.topleft[0], self.rect.topleft[1]-3)
                    self.rect.topleft = self.newpos
                    if(self.rect.topleft[1] < -32):
                        self.jellyfishtimer = 0
                        self.jellyfishrandomspawn = random.randrange(700, 1200)
                        self.rect.topleft = random.randrange(100, screenWidth-100), -50

class StarPowerup(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_star"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.staranimator = 0
        self.spawntimer = 0
        self.pos = (screenWidth, screenHeight-80) #out of screen made up numbers
    def update(self):
        self.spawntimer += 1
        self.staranimator += 1
        self.rect.topleft = (self.pos[0], self.pos[1])
        if self.spawntimer == 2600:
            self.pos = (screenWidth, screenHeight-80)
            self.spawntimer = 0
        elif self.spawntimer > 2400:
            if(player.starpower == 0):
                self.pos = (self.pos[0]-5,screenHeight-80)
                if self.staranimator > 0:
                    self.image = images["spr_star"]
                if self.staranimator > 10:
                    self.image = images["spr_star2"]
                if self.staranimator > 20:
                    self.image = images["spr_star3"]
                if self.staranimator > 30:
                    self.image = images["spr_star2"]
                if self.staranimator > 40:
                    self.staranimator = 0
            else:
                self.pos = (screenWidth, screenHeight-80)
        elif self.spawntimer == 0:
            self.pos = (screenWidth, screenHeight-80)
        if(player.starpower != 0):
            player.starpowertimer += 1
        else:
            player.starpowertimer = 0

class Room():
    def __init__(self):
        for x in range(29):
            wall = Wall()
            wall.rect.topleft = (x*32,0) #top walls
            walls.append(wall)
        for x in range(29):
            wall = Wall()
            wall.rect.topleft = (x*32,screenHeight-32) #bottom walls
            walls.append(wall)
        for y in range(17):
            wall = Wall()
            wall.rect.topleft = (0, (y*32)+32) #left walls
            walls.append(wall)
        for y in range(17):
            wall = Wall()
            wall.rect.topleft = (screenWidth-32, (y*32)+32) #right walls
            walls.append(wall)
        reset()
        powerUpReset()

def powerUpReset():
    global SCORE
    SCORE = 0
    star.spawntimer = 0
    player.starpower, player.starpowertimer = 0, 0
    player.puTimeLeft = 5
    player.speedpower, player.speedpowertimer = 0, 0
    player.speedTimeLeft = 5

def reset():
    global SCORE, scoreBlit, onePowerupSound, scoreDisappearTimer
    SCORE, player.sizescore, scoreBlit, scoreDisappearTimer = 0, 0, 0, 0
    player.pos = [screenWidth/2, (screenHeight/2)+100]
    player.rect.topleft = (player.pos[0], player.pos[1])
    player.image = images["player_left"]
    keys = [False, False, False, False]
    for greenFish in greenFishes:
        greenFish.image = images["spr_greenfish"]
        greenScoreList[greenFishes.index(greenFish)] = 0
        greenFish.rect.topleft = (random.randrange(100, screenWidth-100), random.randrange(100, screenHeight-100))
    for redFish in redfishes:
        redFish.rect.topleft = (random.randrange(100, screenWidth-100), random.randrange(100, screenHeight-100))
    silverfish.rect.topleft = (random.choice([-50,screenWidth]), random.randrange(50, 150))
    silverfish.restarttimer = 0
    sharks[0].rect.topleft = (random.randrange(100, screenWidth-100), -400)
    sharks[1].rect.topleft = (random.randrange(100, screenWidth-100), -400)
    sharks[2].rect.topleft = (random.randrange(100, screenWidth-100), -400)
    sharks[3].rect.topleft = (random.randrange(100, screenWidth-100), -400)
    snake.rect.topleft = (random.choice([-70,screenWidth]), random.randrange(screenHeight-110, screenHeight-50))
    seahorse.rect.topleft = (random.choice([-70,screenWidth]), random.randrange(50, screenHeight-200))
    jellyFishes[0].rect.topleft = (random.randrange(100, screenWidth-100), -50)
    jellyFishes[1].rect.topleft = (random.randrange(100, screenWidth-100), -50)
    jellyFishes[2].rect.topleft = (random.randrange(100, screenWidth-100), -50)
    rainbowFish.pos = (random.randrange(100, screenWidth-100), -100)
    rainbowFish.rect.topleft = rainbowFish.pos
    rainbowFish.size = [55, 35]
    rainbowFish.image = images["spr_rainbowfish"]
    star.pos = (screenWidth, screenHeight-80)
    (rainbowFish.scoreExit, brightbluefish.movingVar, rainbowFish.rainbowtimer, snake.restarttimer, seahorse.restarttimer) = 0, 0, 0, 0, 0
    seahorse.randomspawn = random.randrange(1500, 2000)
    seahorse.direction = random.choice([0,1])
    snake.randomspawn = random.randrange(200, 400)
    brightbluefish.rect.topleft = (random.choice([-1000,screenWidth+1000]), random.randrange(50, screenHeight-200))
    brightbluefish.direction = random.choice([0,1])
    for jellyfish in jellyFishes:
        if(jellyfish == jellyFishes[0]):
            jellyfish.jellyfishtimer = 0
            jellyfish.jellyfishanimatetimer = 0
        if(jellyfish == jellyFishes[1]):
            jellyfish.jellyfishtimer = 0
            jellyfish.jellyfishanimatetimer = 8
        if(jellyfish == jellyFishes[2]):
            jellyfish.jellyfishtimer = 0
            jellyfish.jellyfishanimatetimer = 16
    onePowerupSound = 0
    
def get_high_score():
    #Default high score
    high_score = 0
    #Try to read the high score from a file
    try:
        high_score_file = open("high_score.txt", "r")
        high_score = int(high_score_file.read())
        high_score_file.close()
    except IOError:
        #Error reading file, no high score
        pass
    except ValueError:
        #There's a file there, but we don't understand the number.
        print("Error Reading High Score. Please delete high_score.txt in the game folder.")
    return high_score
    
def save_high_score(new_high_score):
    try:
        # Write the file to disk
        high_score_file = open("high_score.txt", "w")
        high_score_file.write(str(new_high_score))
        high_score_file.close()
    except IOError:
        pass
    #Try to read the high score from a file
    try:
        high_score_file = open("high_score.txt", "r")
        high_score = int(high_score_file.read())
        high_score_file.close()
    except IOError:
        #No high score yet
        print("There is no high score yet.")
    except ValueError:
        #Bad number formatting in file
        print("Error Reading High Score. Please delete high_score.txt in the game folder.")
    return high_score

#Init
pygame.init()
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Fish Food")
spr_wall = load_image("sprites/wall.bmp", "spr_wall", True, False)
#player sprites
player_left = load_image("sprites/Player_left.png", "player_left", True, True)
player_downright = load_image("sprites/Player_downright.png", "player_downright", True, True)
player_down = load_image("sprites/Player_down.png", "player_down", True, True)
player_left_gold = load_image("sprites/Player_left_gold.png", "player_left_gold", True, True)
player_downright_gold = load_image("sprites/Player_downright_gold.png", "player_downright_gold", True, True)
player_down_gold = load_image("sprites/Player_down_gold.png", "player_down_gold", True, True)
player = Player()
#other fish sprites
spr_redfish = load_image("sprites/redfish.png", "spr_redfish", True, True)
redfishes = [ RedFish() for i in range(6)]
spr_greenfish = load_image("sprites/greenfish.png", "spr_greenfish", True, True)
images["spr_greenfish_left"] = pygame.transform.flip(images["spr_greenfish"], 1, 0)
greenFishes = [ GreenFish() for i in range(3)]
spr_biggreenfish = load_image("sprites/biggreenfish.png", "spr_biggreenfish", True, True)
spr_silverfish = load_image("sprites/silverfish.png", "spr_silverfish", True, True)
silverfish = SilverFish()
spr_snake = load_image("sprites/snake1.png", "spr_snake", True, True)
spr_snake2 = load_image("sprites/snake2.png", "spr_snake2", True, True)
spr_snake3 = load_image("sprites/snake3.png", "spr_snake3", True, True)
spr_snake4 = load_image("sprites/snake4.png", "spr_snake4", True, True)
snake = Snake()
spr_seahorse = load_image("sprites/seahorse.png", "spr_seahorse", True, True)
seahorse = SeaHorse()
spr_jellyfish = load_image("sprites/jellyfish1.png", "spr_jellyfish", True, True)
spr_jellyfish2 = load_image("sprites/jellyfish2.png", "spr_jellyfish2", True, True)
spr_jellyfish3 = load_image("sprites/jellyfish3.png", "spr_jellyfish3", True, True)
spr_jellyfish4 = load_image("sprites/jellyfish4.png", "spr_jellyfish4", True, True)
spr_jellyfish5 = load_image("sprites/jellyfish5.png", "spr_jellyfish5", True, True)
spr_jellyfish6 = load_image("sprites/jellyfish6.png", "spr_jellyfish6", True, True)
spr_jellyfish7 = load_image("sprites/jellyfish7.png", "spr_jellyfish7", True, True)
jellyFishes = [JellyFish() for i in range(3)]
spr_shark = load_image("sprites/shark.png", "spr_shark", True, True)
sharks = [ Shark() for i in range(4)]
spr_brightbluefish = load_image("sprites/brightbluefish.png", "spr_brightbluefish", True, True)
brightbluefish = BrightBlueFish()
images["bigBrightBlueFish"] = pygame.transform.smoothscale(brightbluefish.image, (300, 200))
images["bigBrightBlueFishLeft"] = pygame.transform.flip(images["bigBrightBlueFish"], 1, 0)
spr_star = load_image("sprites/starfish1.png", "spr_star", True, True)
spr_star2 = load_image("sprites/starfish2.png", "spr_star2", True, True)
spr_star3 = load_image("sprites/starfish3.png", "spr_star3", True, True)
star = StarPowerup()
arrow_warning_red = load_image("sprites/arrowwarningred.png", "arrow_warning_red", True, True)
arrow_warning_silver = load_image("sprites/arrowwarningsilver.png", "arrow_warning_silver", True, True)
arrow_warning_blue = load_image("sprites/arrowwarningblue.png", "arrow_warning_blue", True, True)
spr_seaweed = load_image("sprites/seaweed.png", "spr_seaweed", True, True)
spr_rainbowfish = load_image("sprites/rainbowfish.png", "spr_rainbowfish", True, True)
rainbowFish = RainbowFish()
#font and texts
oceanFont = pygame.font.Font("fonts/oceanfont.ttf", 16)
oceanFontMain = pygame.font.Font("fonts/oceanfont.ttf", 48)
oceanFontGameOver = pygame.font.Font("fonts/oceanfont.ttf", 76)
arialFont = pygame.font.SysFont('Arial', 32)
#backgrounds
startMenu = pygame.image.load("sprites/startmenu.png").convert()
startMenu = pygame.transform.scale(startMenu, (screenWidth, screenHeight))
infoScreen = pygame.image.load("sprites/infoscreen.bmp").convert()
infoScreen = pygame.transform.scale(infoScreen, (screenWidth, screenHeight))
gameOver = pygame.image.load("sprites/gameover.png").convert()
gameOver = pygame.transform.scale(gameOver, (screenWidth, screenHeight))
ground = pygame.image.load("sprites/ground.bmp").convert()
ground = pygame.transform.scale(ground, (screenWidth, 100))
bgwater = pygame.image.load("sprites/background.bmp").convert()
bgwater = pygame.transform.scale(bgwater, (screenWidth, screenHeight))
blackbg = pygame.image.load("sprites/blackbg.jpg").convert()
blackbg = pygame.transform.scale(blackbg, (screenWidth, 30))
#window
gameicon = pygame.image.load("sprites/redfishico.png")
pygame.display.set_icon(gameicon)
pygame.display.set_caption('Fish Food')
pygame.mouse.set_visible(0)
#sounds
snd_eat = load_sound("sounds/snd_eat.wav", "snd_eat")
sounds["snd_eat"].set_volume(.2)
snd_eatshark = load_sound("sounds/eatshark.wav", "snd_eatshark")
sounds["snd_eatshark"].set_volume(.2)
snd_sizedown = load_sound("sounds/sizedown.wav", "snd_sizedown")
snd_playerdie = load_sound("sounds/playerdie.wav", "snd_playerdie")
sounds["snd_playerdie"].set_volume(.3)
snd_poweruptimer = load_sound("sounds/poweruptimer.wav", "snd_poweruptimer")
sounds["snd_poweruptimer"].set_volume(.3)
snd_siren = load_sound("sounds/siren.wav", "snd_siren")
sounds["snd_siren"].set_volume(.15)
snd_sharkincoming = load_sound("sounds/sharkincoming.wav", "snd_sharkincoming")
sounds["snd_sharkincoming"].set_volume(.05)
#music loop
pygame.mixer.music.load("sounds/gamemusic.mp3")
pygame.mixer.music.set_volume(.2)
pygame.mixer.music.play(-1)
#Main
while running:
    if(firstMessage == 1):
        print "Please ignore the errors."
        firstMessage = 0
    clock.tick(60)
    displayCaption()
    if menuOn == 1: #Menu Screen
        Menu(screen)
        SCORE = 0     
    elif menuOn == 2: #Gameover Screen
        high_score = get_high_score()
        if SCORE > high_score:
            save_high_score(SCORE)
        sounds["snd_playerdie"].play()
        sounds["snd_poweruptimer"].stop()
        GameOver(screen)
    elif menuOn == 3:
        PauseScreen(screen)
    elif menuOn == 4:
        InfoScreen(screen)
    if(scoreBlit > 0): #Score Timer above player sprite
        scoreDisappearTimer += 1
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                for i in range(0, len(sounds)):
                    soundslist = sounds.keys() #returns list of keys in sounds
                    sounds[soundslist[i]].stop() #stops all sounds when go to menu
                menuOn = 3
            elif event.key==K_UP:
                keys[0]=True
            elif event.key==K_LEFT:
                keys[1]=True
            elif event.key==K_DOWN:
                keys[2]=True
            elif event.key==K_RIGHT:
                keys[3]=True
        if event.type == pygame.KEYUP:
            if event.key==pygame.K_UP:
                keys[0]=False
            elif event.key==pygame.K_LEFT:
                lastPressed = 0
                keys[1]=False
            elif event.key==pygame.K_DOWN:
                keys[2]=False
            elif event.key==pygame.K_RIGHT:
                lastPressed = 1
                keys[3]=False
    if keys[0]:#up
        player.playerWidth, player.playerHeight = (21, 42)
        player.image = pygame.transform.flip(images["player_down"], 1, 1)
        if player.pos[1] > 50: #boundary, 32 is block, added a few extra pixels to make it look nicer
            player.pos[1] -= player.speedY
        if(player.starpower == 1):
            if(player.playeranimatetimer > 2):
                player.image = pygame.transform.flip(images["player_down_gold"], 1, 1)
            if(player.playeranimatetimer > 4):
                player.image = pygame.transform.flip(images["player_down"], 1, 1)
    if keys[2]:#down
        player.playerWidth, player.playerHeight = (21, 42)
        player.image = images["player_down"]
        if player.pos[1] < screenHeight-75: 
            player.pos[1] += player.speedY
        if(player.starpower == 1):
            if(player.playeranimatetimer > 2):
                player.image = images["player_down_gold"]
            if(player.playeranimatetimer > 4):
                player.image = images["player_down"]
    if keys[1]:#left
        player.playerWidth, player.playerHeight = (41, 19)
        player.image = images["player_left"]
        if player.pos[0] > 32:
            player.pos[0] -= player.speedX
        if(player.starpower == 1):
            if(player.playeranimatetimer > 2):
                player.image = images["player_left_gold"]
            if(player.playeranimatetimer > 4):
                player.image = images["player_left"]
    if keys[3]:#right
        player.playerWidth, player.playerHeight = (41, 19)
        player.image = pygame.transform.rotate(images["player_left"], 180)
        player.image = pygame.transform.flip(player.image, 0, 1)
        if player.pos[0] < screenWidth-75:
            player.pos[0] += player.speedX
        if(player.starpower == 1):
            if(player.playeranimatetimer > 2):
                player.image = pygame.transform.rotate(images["player_left_gold"], 180)
                player.image = pygame.transform.flip(player.image, 0, 1)
            if(player.playeranimatetimer > 4):
                player.image = pygame.transform.rotate(images["player_left"], 180)
                player.image = pygame.transform.flip(player.image, 0, 1)
    if keys[0] and keys[1]:#upleft
        player.playerWidth, player.playerHeight = (34, 34)
        player.image = pygame.transform.flip(images["player_downright"], 0, 1)
        player.image = pygame.transform.rotate(player.image, 90)
        if(player.starpower == 1):
            if(player.playeranimatetimer > 2):
                player.image = pygame.transform.flip(images["player_downright"], 0, 1)
                player.image = pygame.transform.rotate(player.image, 90)
            if(player.playeranimatetimer > 4):
                player.image = pygame.transform.flip(images["player_downright_gold"], 0, 1)
                player.image = pygame.transform.rotate(player.image, 90)
    if keys[0] and keys[3]:#upright
        player.playerWidth, player.playerHeight = (34, 34)
        player.image = pygame.transform.rotate(images["player_downright"], 90)
        if(player.starpower == 1):
            if(player.playeranimatetimer > 2):
                player.image = pygame.transform.rotate(images["player_downright"], 90)
            if(player.playeranimatetimer > 4):
                player.image = pygame.transform.rotate(images["player_downright_gold"], 90)
    if keys[2] and keys[1]:#downleft
        player.playerWidth, player.playerHeight = (34, 34)
        player.image = pygame.transform.flip(images["player_downright"], 1, 0)
        if(player.starpower == 1):
            if(player.playeranimatetimer > 2):
                player.image = pygame.transform.flip(images["player_downright_gold"], 1, 0)
            if(player.playeranimatetimer > 4):
                player.image = pygame.transform.flip(images["player_downright"], 1, 0)
    if keys[2] and keys[3]:#downright
        player.playerWidth, player.playerHeight = (34, 34)
        player.image = images["player_downright"]
        if(player.starpower == 1):
            if(player.playeranimatetimer > 2):
                player.image = images["player_downright_gold"]
            if(player.playeranimatetimer > 4):
                player.image = images["player_downright"]
    if keys == [False, False, False, False]:
        player.playerWidth, player.playerHeight = (41, 19)
        if lastPressed == 0:
            if(player.starpower == 1):
                if(player.playeranimatetimer > 2):
                    player.image = images["player_left_gold"]
                if(player.playeranimatetimer > 4):
                    player.image = images["player_left"]
            else:
                player.image = images["player_left"]
        else:
            if(player.starpower == 1):
                if(player.playeranimatetimer > 2):
                    player.image = pygame.transform.rotate(images["player_left_gold"], 180)
                    player.image = pygame.transform.flip(player.image, 0, 1)
                if(player.playeranimatetimer > 4):
                    player.image = pygame.transform.rotate(images["player_left"], 180)
                    player.image = pygame.transform.flip(player.image, 0, 1)
            else:
                player.image = pygame.transform.rotate(images["player_left"], 180)
                player.image = pygame.transform.flip(player.image, 0, 1)
    allsprites.update()
    #water background movement
    y1 += 10
    y2 += 10
    screen.blit(bgwater, (x1,y1))
    screen.blit(bgwater, (x2,y2))
    if y2 > screenHeight:
        y2 = -screenHeight
    if y1 > screenHeight:
        y1 = -screenHeight
    screen.blit(ground, (0,screenHeight-100))
    #Arrow Warnings
    if rainbowFish.rainbowtimer >= 1000 and rainbowFish.rainbowtimer <= 1150: #Rainbow Fish Warning
        if rainbowFish.scoreExit == 0:
            screen.blit(images["arrow_warning_red"], (rainbowFish.rect.topleft[0], 40))
            if rainbowFish.rainbowtimer == 1000: #play only once
                sounds["snd_siren"].play()
    if (SCORE >= 0 and SCORE < 5) or (SCORE >= 5 and sharks[0].rect.topleft[1] < 0):
        screen.blit(images["arrow_warning_silver"], (sharks[0].rect.topleft[0], 40))
    if (SCORE >= 20 and SCORE < 25) or (SCORE >= 25 and sharks[1].rect.topleft[1] < 0):
        screen.blit(images["arrow_warning_silver"], (sharks[1].rect.topleft[0], 40))
    if (SCORE >= 45 and SCORE < 50) or (SCORE >= 50 and sharks[2].rect.topleft[1] < 0):
        screen.blit(images["arrow_warning_silver"], (sharks[2].rect.topleft[0], 40))
    if (SCORE >= 70 and SCORE < 75) or (SCORE >= 75 and sharks[3].rect.topleft[1] < 0):
        screen.blit(images["arrow_warning_silver"], (sharks[3].rect.topleft[0], 40))
    if(menuOn == 2):
        sounds["snd_poweruptimer"].stop()
        brightbluefish.image = images["spr_brightbluefish"]
    allsprites.draw(screen)
    screen.blit(blackbg, (0,0))
    #Seaweed
    for i in range(5,screenWidth-15,60):
        screen.blit(images["spr_seaweed"], (i, screenHeight-130)) #top seaweed
    for i in range(5,screenWidth-15,60):
        screen.blit(images["spr_seaweed"], (i, screenHeight-80))
        if(brightbluefish.movingVar == 1 and (brightbluefish.rect.topright[0] < 0)):
            if(brightbluefish.rect.topleft == -1000):
                sounds["snd_siren"].play() #only plays once
            rightHeightVar = brightbluefish.rect.midright[1]+40 #Y coordinate is in middle of bluefish
            if brightbluefish.direction == 1 and brightbluefish.rect.topright[0] < 0:
                screen.blit(images["arrow_warning_blue"], (40, rightHeightVar))
        elif(brightbluefish.movingVar == 1 and brightbluefish.rect.topleft[0] > screenWidth):
            if(brightbluefish.rect.topleft == screenWidth+1000):
                sounds["snd_siren"].play() #only plays once
            leftHeightVar = brightbluefish.rect.midleft[1]+40
            if brightbluefish.direction == 0 and brightbluefish.rect.topleft[0] > screenWidth:
                arrow_warning_blue_flip = pygame.transform.flip(images["arrow_warning_blue"],1,0)
                screen.blit(arrow_warning_blue_flip, (screenWidth-95, leftHeightVar))
    #Menu Design
    menuText = oceanFont.render("Menu:", 1, (255,255,255))
    screen.blit(menuText, (10, 5))
    screen.blit(images["spr_redfish"], (65, 11))
    screen.blit(images["spr_greenfish"], (90, 11))
    screen.blit(images["spr_silverfish"], (120, 9))
    if(rainbowFish.size[0]-45 <= player.sizescore): #55 is orig size
        blittedRainbowFish = pygame.transform.smoothscale(images["spr_rainbowfish"], (24, 17))
        screen.blit(blittedRainbowFish, (158, 6))
    else:
        screen.blit(oceanFont.render("", 1, (0,0,0)), (158,6))
    if(player.sizescore >= 40):
        blittedBigGreenFish = pygame.transform.smoothscale(images["spr_biggreenfish"], (24, 15))
        screen.blit(blittedBigGreenFish, (189, 7))
    else:
        screen.blit(oceanFont.render("", 1, (0,0,0)), (189,7))
    if(player.starpower == 2):
        blittedshark = pygame.transform.smoothscale(images["spr_shark"], (24, 15))
        screen.blit(blittedshark, (220, 7))
    else:
        screen.blit(oceanFont.render("", 1, (0,0,0)), (220,7))
    #Font On Top
    scoreText = oceanFont.render("Score: "+str(SCORE), 1, (255,255,255))
    screen.blit(scoreText, ((screenWidth/2)-32, 5))
    #powerup timer
    if(player.starpower != 0):
        powerUpTimerText = oceanFont.render("Powerup Timer: "+str(player.puTimeLeft), 1, (255,255,255))
    else:
        powerUpTimerText = oceanFont.render("", 1, (0,0,0))
    #speed timer
    if(player.speedpower == 1):
        speedTimerText = oceanFont.render("Speed Timer: "+str(player.speedTimeLeft), 1, (255,255,255))
    elif(player.speedpower == 2):
        speedTimerText = oceanFont.render("Sting Timer: "+str(player.speedTimeLeft), 1, (255,255,255))
    else:
        speedTimerText = oceanFont.render("", 1, (0,0,0))
    for redFish in redfishes:
        if pygame.sprite.collide_mask(redFish, player):
            redFish.rect.topleft = (random.randrange(100, screenWidth-100), random.randrange(100, screenHeight-100))
            sounds["snd_eat"].play()
            scoreBlit = 1
            SCORE += 1
            player.sizescore += 1
        for greenFish in greenFishes:
            if redFish.rect.colliderect(greenFish):
                thisGreenFish = greenFishes.index(greenFish)
                greenFish.collision_with_redFish(thisGreenFish)
                if greenFish.image != images["spr_biggreenfish"]:
                    redFish.rect.topleft = (random.randrange(100, screenWidth-100), random.randrange(100, screenHeight-100))
        if pygame.sprite.collide_mask(redFish, brightbluefish):
            redFish.rect.topleft = (random.randrange(100, screenWidth-100), random.randrange(100, screenHeight-100))
        for wall in walls:
            if redFish.rect.colliderect(wall.rect):
                redFish.collision_with_wall(wall)
    for greenFish in greenFishes:
        if pygame.sprite.collide_mask(greenFish, player):
            if greenFish.image == images["spr_greenfish"] or greenFish.image == images["spr_greenfish_left"] or player.sizescore >= 40 or player.starpower == 1:
                sounds["snd_eat"].play()
                scoreBlit = 2
                SCORE += 2
                player.sizescore += 2
                greenFish.small_collision_with_player()
                greenScoreList[greenFishes.index(greenFish)] = 0
                greenFish.image = images["spr_greenfish"]
                greenFish.rect.topleft = (random.randrange(100, screenWidth-100), random.randrange(100, screenHeight-100))
            else: #when bigGreenFish, player dies
                menuOn = 2
        if pygame.sprite.collide_mask(greenFish, brightbluefish):
                greenScoreList[greenFishes.index(greenFish)] = 0
                greenFish.image = images["spr_greenfish"]
                greenFish.rect.topleft = (random.randrange(100, screenWidth-100), random.randrange(100, screenHeight-100))
        for wall in walls:
            if greenFish.rect.colliderect(wall.rect):
                greenFish.collision_with_wall(wall)
                break
    if pygame.sprite.collide_mask(silverfish, player):
        sounds["snd_eat"].play()
        scoreBlit = 3
        SCORE += 3
        player.sizescore += 3
        silverfish.rect.topleft = (random.choice([-50,screenWidth]), random.randrange(50, 150))
        silverfish.restarttimer = 0
    if pygame.sprite.collide_mask(silverfish, brightbluefish):
        sounds["snd_eat"].play()
        silverfish.rect.topleft = (random.choice([-50,screenWidth]), random.randrange(50, 150))
        silverfish.restarttimer = 0
    for shark in sharks:
        if pygame.sprite.collide_mask(shark, player):
            if(player.starpower == 2):
                shark.rect.topleft = (random.randrange(100, screenWidth-100), -100)
                sounds["snd_eatshark"].play()
                scoreBlit = 1
                SCORE += 1
                player.sizescore += 1
            elif(player.starpower == 0): #player die
                menuOn = 2
        if pygame.sprite.collide_mask(shark, brightbluefish):
            shark.rect.topleft = (random.randrange(100, screenWidth-100), -100)
            sounds["snd_eat"].play()
        for wall in walls:
            if shark.rect.colliderect(wall.rect):
                shark.collision_with_wall(wall)
                break
    if pygame.sprite.collide_mask(rainbowFish, player):
        #player eats rainbowFish only when appears bigger (arbitrary)
        if (rainbowFish.size[0]-45 <= player.sizescore) or (player.starpower == 1):
            sounds["snd_eat"].play()
            scoreBlit = 2
            SCORE += 2
            player.sizescore += 2
            rainbowFish.rainbowtimer = 0
            rainbowFish.pos = (random.randrange(100, screenWidth-100), -100)
            if(rainbowFish.size[0]-20 <= 55): #increases till max size
                rainbowFish.size[0] += 10
                rainbowFish.size[1] += 10
        else: #Gameover
            if(player.starpower != 1):
                menuOn = 2
    if pygame.sprite.collide_mask(rainbowFish, brightbluefish):
        sounds["snd_eat"].play()
        rainbowFish.pos = (random.randrange(100, screenWidth-100), -100)
        rainbowFish.rainbowtimer = 0
    if pygame.sprite.collide_mask(snake, player):
        snake.rect.topleft = (random.choice([-70,screenWidth]), random.randrange(screenHeight-110, screenHeight-50))
        snake.restarttimer = 0
        if(player.starpower != 1):
            sounds["snd_sizedown"].play()
            player.sizescore = 0
        else:
            sounds["snd_eat"].play()
    if pygame.sprite.collide_mask(snake, brightbluefish):
        snake.rect.topleft = (random.choice([-70,screenWidth]), random.randrange(screenHeight-110, screenHeight-50))
        snake.restarttimer = 0
    if pygame.sprite.collide_mask(seahorse, player):
        player.speedpower = 1
        player.speedpowertimer = 0 #restarts timer
        player.speedTimeLeft = 5 #restarts timer
        seahorse.rect.topleft = (random.choice([-70,screenWidth]), random.randrange(50, screenHeight-200))
        sounds["snd_eat"].play()
        onePowerupSound += 1
        if(onePowerupSound > 1):
            sounds["snd_poweruptimer"].stop()
        for i in range(0, len(sounds)):
            soundslist = sounds.keys() #returns list of keys in sounds
            sounds[soundslist[i]].stop() #stops all sounds
        sounds["snd_poweruptimer"].play()
        seahorse.restarttimer = 0
        player.speedX, player.speedY = 9, 9
    for jellyfish in jellyFishes:
        if pygame.sprite.collide_mask(jellyfish, player):
            jellyfish.rect.topleft = (random.randrange(100, screenWidth-100), -50)
            jellyfish.jellyfishtimer = 0
            if(player.starpower == 1):
                sounds["snd_eat"].play()
            else:
                player.speedpower = 2
                player.speedTimeLeft = 5 #restarts timer
                player.speedpowertimer = 0 #restarts timer
                sounds["snd_sizedown"].play()
                onePowerupSound += 1
                if(onePowerupSound > 1):
                    sounds["snd_poweruptimer"].stop()
                for i in range(0, len(sounds)):
                    soundslist = sounds.keys() #returns list of keys in sounds
                    sounds[soundslist[i]].stop() #stops all sounds
                sounds["snd_poweruptimer"].play()
                player.sizescore = 0
                player.speedX, player.speedY = 2, 2
        if pygame.sprite.collide_mask(jellyfish, brightbluefish):
            jellyfish.rect.topleft = (random.randrange(100, screenWidth-100), -50)
            jellyfish.jellyfishtimer = 0
            sounds["snd_eat"].play()
    if player.rect.colliderect(star):
        player.starpower = random.choice([0,1])+1
        star.pos = (screenWidth, screenHeight-80)
        sounds["snd_eat"].play()
        onePowerupSound += 1
        if(onePowerupSound > 1):
            sounds["snd_poweruptimer"].stop()
        for i in range(0, len(sounds)):
            soundslist = sounds.keys() #returns list of keys in sounds
            sounds[soundslist[i]].stop() #stops all sounds
        sounds["snd_poweruptimer"].play()
    if pygame.sprite.collide_mask(brightbluefish, player):
        if(player.starpower != 1): #GameOver
            menuOn = 2
    if(brightbluefish.movingVar == 0):
        if((SCORE%50 == 0 or SCORE%50 == 1 or SCORE%50 == 2) and SCORE != 0 and SCORE != 1 and SCORE != 2):
            brightbluefish.movingVar = 1
    #Test Print Code: FOR DEBUGGING PURPOSES BELOW:
    
    #Top Screen Design
    screen.blit(powerUpTimerText, (732, 5))
    screen.blit(speedTimerText, (550, 5))
    if(scoreBlit == 0):
        scoreBlitText = oceanFont.render("", 1, (255,255,255))
    else:
        scoreBlitText = oceanFont.render("+" + str(scoreBlit), 1, (255,255,255))
        if(scoreDisappearTimer > 10):
            scoreBlit = 0
            scoreDisappearTimer = 0
    screen.blit(scoreBlitText, (player.pos[0]+13, player.pos[1]-25-(player.sizescore/2)))
    pygame.display.flip()
    pygame.display.update()