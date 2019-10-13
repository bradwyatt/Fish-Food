"""
Created by Brad Wyatt
Created with Python version 3.7.3

Future improvements:
1) Better handling of sound (two sounds can't play at once)
2) Better menu to click rather than press enter?
3) Rainbow fish size sometimes shrinks over time which is a bit odd
"""
import sys
import random
import warnings
import pygame
import os
from genmenu import *

# GLOBAL CONSTANT VARIABLES
(SCREEN_WIDTH, SCREEN_HEIGHT) = 928, 544
PLAY_SCREEN, START_SCREEN, GAMEOVER_SCREEN, PAUSE_SCREEN, INFO_SCREEN = 0, 1, 2, 3, 4
IMAGES = {}
SOUNDS = {}

def adjust_to_correct_appdir():
    try:
        appdir = sys.argv[0] #feel free to use __file__
        if not appdir:
            raise ValueError
        appdir = os.path.abspath(os.path.dirname(sys.argv[0]))
        os.chdir(appdir)
        if not appdir in sys.path:
            sys.path.insert(0, appdir)
    except:
        #placeholder for feedback, adjust to your app.
        #remember to use only python and python standard libraries
        #not any resource or module into the appdir 
        #a window in Tkinter can be adequate for apps without console
        #a simple print with a timeout can be enough for console apps
        print('Please run from an OS console.')
        import time
        time.sleep(10)
        sys.exit(1)

def load_sound(file, name):
    sound = pygame.mixer.Sound(file)
    SOUNDS[name] = sound
    
def load_image(file, name, transparent, alpha):
    new_image = pygame.image.load(file)
    if alpha:
        new_image = new_image.convert_alpha()
    else:
        new_image = new_image.convert()
    if transparent:
        colorkey = new_image.get_at((0, 0))
        new_image.set_colorkey(colorkey, RLEACCEL)
    IMAGES[name] = new_image
    
def display_caption():
    pygame.display.set_caption("Fish Food")

def quit_game():
    print('Thanks for playing')
    warnings.filterwarnings("ignore")
    pygame.quit()
    sys.exit()

def startplaceholder():
    global menu_selection
    menu_selection = PLAY_SCREEN

def infoplaceholder():
    global menu_selection
    menu_selection = INFO_SCREEN

class Menu():
    def __init__(self, screen, start_menu, ocean_font_main):
        """
        Main menu that begins when starting the game.
        Use arrow keys to move up and down, enter to select
        """
        self.screen = screen
        self.title = start_menu
        self.menu = genmenu(['START', lambda: startplaceholder()],
                            ['INFO', lambda: infoplaceholder()],
                            ['QUIT', lambda: quit_game()])
        self.menu.changeFont('oceanfont.ttf', 28)
        self.menu.position(430, 190)
        self.menu.defaultColor((0, 0, 0))
        self.menu.choiceColor((255, 255, 255))
        self.clock = pygame.time.Clock()
        event = pygame.event.get()
        self.menu.create(self.screen)
        self.menu.choose(event)
        self.main_loop(ocean_font_main)

    def main_loop(self, ocean_font_main):
        global menu_selection
        while menu_selection == START_SCREEN:
            self.clock.tick(60)
            events = pygame.event.get()
            self.menu.choose(events)
            self.screen.blit(self.title, (0, 0))
            press_enter_text = ocean_font_main.render("Press Enter", 1, (150, 189, 0))
            self.screen.blit(press_enter_text, (570, 280))
            high_score_text = ocean_font_main.render("High Score: " + str(get_high_score()),
                                                     1, (243, 189, 0))
            self.screen.blit(high_score_text, (530, 190))
            self.menu.create(self.screen)
            pygame.display.flip()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

class InfoScreen():
    def __init__(self, screen, info_screen):
        """
        Menu for how to play the game, avoiding enemies and special powerups
        """
        self.screen = screen
        self.title = info_screen
        self.clock = pygame.time.Clock()
        self.main_loop()

    def main_loop(self):
        global menu_selection
        while menu_selection == INFO_SCREEN:
            self.clock.tick(60)
            self.screen.blit(self.title, (0, 0))
            events = pygame.event.get()
            pygame.display.flip()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        menu_selection = START_SCREEN

class GameOver():
    def __init__(self, screen, game_over, font_arial, font_ocean_gameover, score):
        """
        If a predator eats you, you'll get this screen
        Contains the high score in the menu
        """
        self.screen = screen
        self.title = game_over
        self.clock = pygame.time.Clock()
        self.main_loop(font_arial, font_ocean_gameover, score)

    def main_loop(self, font_arial, font_ocean_gameover, score):
        global menu_selection
        while menu_selection == GAMEOVER_SCREEN:
            self.clock.tick(60)
            events = pygame.event.get()
            self.screen.blit(self.title, (0, 0))
            score_gameover_text = font_arial.render("Score: " + str(score), 1, (0, 0, 0))
            self.screen.blit(score_gameover_text, (50, 175))
            if score == get_high_score():
                high_score_text = font_ocean_gameover.render("High Score!", 1, (0, 0, 0))
                self.screen.blit(high_score_text, (50, 260))
            else:
                high_score_text = font_ocean_gameover.render("Try Again!", 1, (0, 0, 0))
                self.screen.blit(high_score_text, (50, 270))
            high_score_text = font_arial.render("Personal Best: " + str(get_high_score()),
                                                1, (0, 0, 0))
            self.screen.blit(high_score_text, (50, 220))
            pygame.display.flip()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        menu_selection = START_SCREEN

def resumeplaceholder():
    global menu_selection
    menu_selection = PLAY_SCREEN

def mainmenuplaceholder():
    global menu_selection
    menu_selection = START_SCREEN

class PauseScreen():
    def __init__(self, screen, bgwater):
        """
        Screen to resume playing or quit in mid-game
        """
        self.screen = screen
        self.title = bgwater
        self.menu = genmenu(['Resume', lambda: resumeplaceholder()],
                            ['End Game', lambda: mainmenuplaceholder()])
        self.menu.changeFont('oceanfont.ttf', 28)
        self.menu.position(430, 190)
        self.menu.defaultColor((0, 0, 0))
        self.menu.choiceColor((255, 255, 255))
        self.clock = pygame.time.Clock()
        event = pygame.event.get()
        self.menu.create(self.screen)
        self.menu.choose(event)
        self.main_loop()

    def main_loop(self):
        global menu_selection
        while menu_selection == PAUSE_SCREEN:
            self.clock.tick(60)
            events = pygame.event.get()
            self.menu.choose(events)
            self.screen.blit(self.title, (0, 0))
            self.menu.create(self.screen)
            pygame.display.flip()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

class Wall(pygame.sprite.Sprite):
    def __init__(self, allsprites):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["spr_wall"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
    def remove_sprite(self):
        self.kill()

class Seaweed(pygame.sprite.Sprite):
    taco = []
    def __init__(self, allsprites, x_pos, y_pos):
        """
        Animated seaweed
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["spr_seaweed"]
        self.rect = self.image.get_rect()
        self.rect.topleft = x_pos, y_pos
        allsprites.add(self)
        self.seaweed_animate_timer = random.randint(0, 30)
        Seaweed.taco.append(str("Seaweed"))
    def update(self):
        print(len(Seaweed.taco))
        self.seaweed_animate_timer += 1
        seaweed_images = [IMAGES["spr_seaweed"], IMAGES["spr_seaweed_left"], IMAGES["spr_seaweed_right"]]
        if self.seaweed_animate_timer > 15 and self.seaweed_animate_timer < 30:
            self.image = seaweed_images[1]
        if self.seaweed_animate_timer >= 30:
            self.image = seaweed_images[2]
        if self.seaweed_animate_timer > 45:
            self.seaweed_animate_timer = 0
            self.image = seaweed_images[0]
    def remove_sprite(self):
        self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self, allsprites):
        """
        Main fish that player controls in the game
        Ability to grow to eat smaller fish (prey)
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["player_left"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.player_width, self.player_height = (41, 19)
        self.sizescore = 0
        self.speedpower = 0
        self.speed_x, self.speed_y = 6, 6
        self.powerup_time_left, self.speed_time_left = 500, 500
        self.starpower, self.playeranimatetimer = 0, 0
        self.pos = [SCREEN_WIDTH/2, SCREEN_HEIGHT/2+100]
        self.rect.topleft = (self.pos[0], self.pos[1])
    def update(self):
        self.rect = self.image.get_rect()
        newpos = (self.pos[0], self.pos[1])
        self.rect.topleft = newpos
        # GROW
        if self.sizescore < 0:
            self.sizescore = 0
        if self.sizescore > 40:
            self.sizescore = 40
        self.image = pygame.transform.smoothscale(self.image, (self.player_width+self.sizescore, self.player_height+self.sizescore))
        self.rect.inflate_ip(self.sizescore, self.sizescore)
        # STAR POWERUPS
        if self.starpower == 0: #no star power
            self.powerup_time_left = 500 #restart to 5 seconds
        elif self.starpower == 1: #star powerup
            self.playeranimatetimer += 1
            if self.playeranimatetimer > 6:
                self.playeranimatetimer = 0
            self.powerup_time_left -= 1
        elif self.starpower == 2: #mini sharks
            self.powerup_time_left -= 1
        # SPEED POWERUPS/DEFECTS
        if self.speedpower == 0:
            self.speed_x, self.speed_y = 6, 6
            self.speed_time_left = 500
        elif (self.speedpower == 1 or self.speedpower == 2): # Seahorse & jellyfish
            self.speed_time_left -= 1
        # RESET TIMERS
        if self.powerup_time_left < 0: # Powerup is over on the player
            self.starpower = 0
            self.powerup_time_left = 500
        if self.speed_time_left < 0:
            self.speedpower = 0
            self.speed_time_left = 500
    def move_up(self):
        self.player_width, self.player_height = (21, 42)
        self.image = pygame.transform.flip(IMAGES["player_down"], 1, 1)
        if self.pos[1] > 50: # Boundary, 32 is block, added a few extra pixels to make it look nicer
            self.pos[1] -= self.speed_y
        if self.starpower == 1:
            if self.playeranimatetimer > 2:
                self.image = pygame.transform.flip(IMAGES["player_down_gold"], 1, 1)
            if self.playeranimatetimer > 4:
                self.image = pygame.transform.flip(IMAGES["player_down"], 1, 1)
    def move_down(self):
        self.player_width, self.player_height = (21, 42)
        self.image = IMAGES["player_down"]
        if self.pos[1] < SCREEN_HEIGHT-75:
            self.pos[1] += self.speed_y
        if self.starpower == 1:
            if self.playeranimatetimer > 2:
                self.image = IMAGES["player_down_gold"]
            if self.playeranimatetimer > 4:
                self.image = IMAGES["player_down"]
    def move_left(self):
        self.player_width, self.player_height = (41, 19)
        self.image = IMAGES["player_left"]
        if self.pos[0] > 32:
            self.pos[0] -= self.speed_x
        if self.starpower == 1:
            if self.playeranimatetimer > 2:
                self.image = IMAGES["player_left_gold"]
            if self.playeranimatetimer > 4:
                self.image = IMAGES["player_left"]
    def move_right(self):
        self.player_width, self.player_height = (41, 19)
        self.image = pygame.transform.rotate(IMAGES["player_left"], 180)
        self.image = pygame.transform.flip(self.image, 0, 1)
        if self.pos[0] < SCREEN_WIDTH-75:
            self.pos[0] += self.speed_x
        if self.starpower == 1:
            if self.playeranimatetimer > 2:
                self.image = pygame.transform.rotate(IMAGES["player_left_gold"], 180)
                self.image = pygame.transform.flip(self.image, 0, 1)
            if self.playeranimatetimer > 4:
                self.image = pygame.transform.rotate(IMAGES["player_left"], 180)
                self.image = pygame.transform.flip(self.image, 0, 1)
    def move_upleft(self):
        self.player_width, self.player_height = (34, 34)
        self.image = pygame.transform.flip(IMAGES["player_downright"], 0, 1)
        self.image = pygame.transform.rotate(self.image, 90)
        if self.starpower == 1:
            if self.playeranimatetimer > 2:
                self.image = pygame.transform.flip(IMAGES["player_downright"], 0, 1)
                self.image = pygame.transform.rotate(self.image, 90)
            if self.playeranimatetimer > 4:
                self.image = pygame.transform.flip(IMAGES["player_downright_gold"], 0, 1)
                self.image = pygame.transform.rotate(self.image, 90)
    def move_upright(self):
        self.player_width, self.player_height = (34, 34)
        self.image = pygame.transform.rotate(IMAGES["player_downright"], 90)
        if self.starpower == 1:
            if self.playeranimatetimer > 2:
                self.image = pygame.transform.rotate(IMAGES["player_downright"], 90)
            if self.playeranimatetimer > 4:
                self.image = pygame.transform.rotate(IMAGES["player_downright_gold"], 90)
    def move_downleft(self):
        self.player_width, self.player_height = (34, 34)
        self.image = pygame.transform.flip(IMAGES["player_downright"], 1, 0)
        if self.starpower == 1:
            if self.playeranimatetimer > 2:
                self.image = pygame.transform.flip(IMAGES["player_downright_gold"], 1, 0)
            if self.playeranimatetimer > 4:
                self.image = pygame.transform.flip(IMAGES["player_downright"], 1, 0)
    def move_downright(self):
        self.player_width, self.player_height = (34, 34)
        self.image = IMAGES["player_downright"]
        if self.starpower == 1:
            if self.playeranimatetimer > 2:
                self.image = IMAGES["player_downright_gold"]
            if self.playeranimatetimer > 4:
                self.image = IMAGES["player_downright"]
    def collide_with_redfish(self, score, score_blit):
        score_blit = 1
        score += 1
        self.sizescore += 1
        return score, score_blit
    def collide_with_greenfish(self, score, score_blit):
        score_blit = 2
        score += 2
        self.sizescore += 2
        return score, score_blit
    def collide_with_silverfish(self, score, score_blit):
        score_blit = 3
        score += 3
        self.sizescore += 3
        return score, score_blit
    def collide_with_shark(self, score, score_blit):
        if self.starpower == 2:
            score_blit = 1
            score += 1
            self.sizescore += 1
            return score, score_blit
        elif self.starpower == 0: # Player die
            self.game_over()
            return score, score_blit
        else:
            return score, score_blit
    def collide_with_seahorse(self):
        self.speedpower = 1
        self.speed_x, self.speed_y = 9, 9
        self.speed_time_left = 500
    def collide_with_jellyfish(self):
        self.speedpower = 2
        self.sizescore = 0
        self.speed_x, self.speed_y = 2, 2
        self.speed_time_left = 500
    def collide_with_snake(self):
        self.sizescore = 0
    def collide_with_star(self):
        self.starpower = random.choice([0, 1])+1
    def game_over(self):
        global menu_selection
        menu_selection = GAMEOVER_SCREEN
    def get_powerup_timer_text(self, ocean_font):
        if self.starpower != 0:
            return ocean_font.render("Powerup Timer: " + str((self.powerup_time_left//100)+1), 1, (255, 255, 255))
        return ocean_font.render("", 1, (0, 0, 0))
    def get_speed_timer_text(self, ocean_font):
        if self.speedpower == 1:
            return ocean_font.render("Speed Timer: " + str((self.speed_time_left//100)+1), 1, (255, 255, 255))
        elif self.speedpower == 2:
            return ocean_font.render("Sting Timer: " + str((self.speed_time_left//100)+1), 1, (255, 255, 255))
        else:
            return ocean_font.render("", 1, (0, 0, 0))
    def remove_sprite(self):
        self.kill()

class RedFish(pygame.sprite.Sprite):
    def __init__(self, allsprites):
        """
        Weakest prey in the game
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["spr_redfish"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.direction = (random.choice([-2, 2]), random.choice([-2, 0, 2]))
        self.change_dir_timer = 0
        self.rect.topleft = (random.randrange(100, SCREEN_WIDTH-100), random.randrange(100, SCREEN_HEIGHT-100))
    def update(self):
        newpos = (self.rect.topleft[0] + self.direction[0],
                  self.rect.topleft[1] + self.direction[1])
        self.rect.topleft = newpos
        self.change_dir_timer += 1
        if self.direction[0] == -2:
            self.image = pygame.transform.flip(IMAGES["spr_redfish"], 1, 0)
        elif self.direction[0] == 2:
            self.image = IMAGES["spr_redfish"]
        if self.change_dir_timer > random.randrange(100, 600):
            self.direction = random.choice([(self.direction[0]*-1, self.direction[1]),
                                            (self.direction[0], self.direction[1]*-1),
                                            (self.direction[0]*-1, self.direction[1]*-1)])
            self.change_dir_timer = 0
    def collision_with_wall(self, rect):
        if self.rect.colliderect(rect):
            self.change_dir_timer = 0
            if self.rect.left < 32: # Left walls
                self.direction = (2, random.choice([-2, 0, 2]))
            elif self.rect.top > SCREEN_HEIGHT-64: # Bottom walls
                self.direction = (random.choice([-2, 0, 2]), -2)
            elif self.rect.right > SCREEN_WIDTH-32: # Right walls
                self.direction = (-2, random.choice([-2, 0, 2]))
            elif self.rect.top < 32: # Top walls
                self.direction = (random.choice([-2, 0, 2]), 2)
    def collide_with_player(self):
        self.rect.topleft = (random.randrange(100, SCREEN_WIDTH-100), random.randrange(100, SCREEN_HEIGHT-100))
    def collide_with_brightbluefish(self):
        self.rect.topleft = (random.randrange(100, SCREEN_WIDTH-100), random.randrange(100, SCREEN_HEIGHT-100))
    def collide_with_greenfish(self):
        self.rect.topleft = (random.randrange(100, SCREEN_WIDTH-100), random.randrange(100, SCREEN_HEIGHT-100))
    def remove_sprite(self):
        self.kill()

class GreenFish(pygame.sprite.Sprite):
    def __init__(self, allsprites):
        """
        Prey until it eats several red fish, and becomes a big green fish that
        can eat the player (unless the player is bigger)
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["spr_greenfish"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.direction = (random.choice([-4, 4]), random.choice([-4, 0, 4]))
        self.change_dir_timer = 0
        self.big_green_fish_score = 0
        self.rect.topleft = (random.randrange(100, SCREEN_WIDTH-100), random.randrange(100, SCREEN_HEIGHT-100))
    def update(self):
        newpos = (self.rect.topleft[0] + self.direction[0],
                  self.rect.topleft[1] + self.direction[1])
        self.rect.topleft = newpos
        self.change_dir_timer += 1
        if self.big_green_fish_score < 70:
            if self.direction[0] == -4:
                self.image = IMAGES["spr_greenfish_left"]
            elif self.direction[0] == 4:
                self.image = IMAGES["spr_greenfish"]
        if self.change_dir_timer > random.randrange(50, 300):
            self.direction = random.choice([(self.direction[0]*-1, self.direction[1]),
                                            (self.direction[0], self.direction[1]*-1),
                                            (self.direction[0]*-1, self.direction[1]*-1)])
            self.change_dir_timer = 0
    def collision_with_wall(self, rect):
        self.change_dir_timer = 0
        if self.rect.colliderect(rect):
            if self.rect.left < 32: # Left walls
                self.direction = (4, random.choice([-4, 4]))
            elif self.rect.top > SCREEN_HEIGHT-64: # Bottom walls
                self.direction = (random.choice([-4, 4]), -4)
            elif self.rect.right > SCREEN_WIDTH-32: # Right walls
                self.direction = (-4, random.choice([-4, 4]))
            elif self.rect.top < 32: # Top walls
                self.direction = (random.choice([-4, 4]), 4)
    def collision_with_redfish(self):
        self.big_green_fish_score += 10
        if self.big_green_fish_score == 70:
            self.image = pygame.transform.smoothscale(IMAGES["spr_biggreenfish"], (103, 58))
    def small_collision_with_player(self):
        self.image = IMAGES["spr_greenfish"]
        self.rect.topleft = (random.randrange(100, SCREEN_WIDTH-100), random.randrange(100, SCREEN_HEIGHT-100))
    def remove_sprite(self):
        self.kill()

class SilverFish(pygame.sprite.Sprite):
    def __init__(self, allsprites):
        """
        Whem eaten, higher amount of points, but shows up infrequently
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["spr_silverfish"]
        self.rect = self.image.get_rect()
        self.rect.topleft = (random.choice([-50, SCREEN_WIDTH]), random.randrange(50, 150))
        self.restarttimer = 0
        self.direction = random.choice([0, 1]) #right or left
        allsprites.add(self)
    def update(self):
        self.restarttimer += 1
        if self.restarttimer > 250:
            if self.rect.topleft[0] == -50:
                self.direction = 1 # right
            elif self.rect.topleft[0] == SCREEN_WIDTH:
                self.direction = 0 # left
            if self.direction == 1: # right movements
                self.rect.topleft = self.rect.topleft[0]+3, self.rect.topleft[1]
                self.image = IMAGES["spr_silverfish"]
            elif self.direction == 0: # left movements
                self.rect.topleft = self.rect.topleft[0]-3, self.rect.topleft[1]
                self.image = pygame.transform.flip(IMAGES["spr_silverfish"], 1, 0)
            if(self.rect.topleft[0] < -40 and self.direction == 0): #restarts position
                self.rect.topleft = (random.choice([-50, SCREEN_WIDTH]), random.randrange(50, 150))
                self.rect.topleft = self.rect.topleft[0], self.rect.topleft[1]
                self.restarttimer = 0
            elif(self.rect.topleft[0] > SCREEN_WIDTH-10 and self.direction == 1): #restarts position
                self.rect.topleft = (random.choice([-50, SCREEN_WIDTH]), random.randrange(50, 150))
                self.rect.topleft = self.rect.topleft[0], self.rect.topleft[1]
                self.restarttimer = 0
    def collide_with_player(self):
        self.rect.topleft = (random.choice([-50, SCREEN_WIDTH]), random.randrange(50, 150))
        self.restarttimer = 0
    def collide_with_brightbluefish(self):
        self.rect.topleft = (random.choice([-50, SCREEN_WIDTH]), random.randrange(50, 150))
        self.restarttimer = 0
    def remove_sprite(self):
        self.kill()

class Shark(pygame.sprite.Sprite):
    def __init__(self, allsprites):
        """
        Most frequently-seen predator in the game.
        Starts coming from above and then bounces around the room
        Only time player can avoid:
        When player has a star powerup, shark respawns
        When player has mini shark powerup, they can eat sharks
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["spr_shark"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.direction = (random.choice([-3, 3]), random.choice([-3, 3]))
        self.mini_shark = 0
        self.activate = 0
        self.rect.topleft = (random.randrange(100, SCREEN_WIDTH-100), -400)
        self.arrow_warning = 0
    def update(self):
        if self.rect.topleft[1] < 0:
            if self.activate == 1:
                self.rect.topleft = (self.rect.topleft[0], self.rect.topleft[1]+3)
                self.arrow_warning = 1
        else:
            self.arrow_warning = 0
            newpos = (self.rect.topleft[0] + self.direction[0],
                      self.rect.topleft[1] + self.direction[1])
            self.rect.topleft = newpos
        if self.mini_shark == 1:
            self.image = pygame.transform.smoothscale(self.image, (60, 30))
        else:
            self.image = IMAGES["spr_shark"]
    def collision_with_wall(self, rect):
        if self.rect.colliderect(rect):
            if self.rect.left < 32: #left walls
                self.direction = (3, random.choice([-3, 3]))
            elif self.rect.top > SCREEN_HEIGHT-64: #bottom walls
                self.direction = (random.choice([-3, 3]), -3)
            elif self.rect.right > SCREEN_WIDTH-32: #right walls
                self.direction = (-3, random.choice([-3, 3]))
            elif self.rect.top < 32: #top walls
                self.direction = (random.choice([-3, 3]), 3)
    def collide_with_brightbluefish(self):
        self.rect.topleft = (random.randrange(100, SCREEN_WIDTH-100), -100)
    def collide_with_player(self):
        self.rect.topleft = (random.randrange(100, SCREEN_WIDTH-100), -100)
    def remove_sprite(self):
        self.kill()

class BrightBlueFish(pygame.sprite.Sprite):
    def __init__(self, allsprites):
        """
        Biggest predator in the game, eats everything that comes in contact
        Player can avoid if they have a star powerup
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["spr_brightbluefish"]
        self.direction = random.choice([0, 1]) #move left: 0, move right: 1
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.activate = 0
        self.rect.topleft = (random.choice([-1000, SCREEN_WIDTH+1000]),
                             random.randrange(50, SCREEN_HEIGHT-200))
        self.arrow_warning = 0
    def update(self):
        if self.activate == 1:
            self.arrow_warning = 1
            if self.direction == 1:
                self.image = IMAGES["bigBrightBlueFish"]
            elif self.direction == 0:
                self.image = IMAGES["bigBrightBlueFishLeft"]
            if self.direction == 1 and self.activate == 1: #right movements
                self.rect.topleft = self.rect.topleft[0]+4, self.rect.topleft[1]
                if self.rect.right > -200: # Remove arrow
                    self.arrow_warning = 0
                if self.rect.left > SCREEN_WIDTH: # Past right side of screen
                    self.activate = 0
            elif self.direction == 0 and self.activate == 1: #left movements
                self.rect.topleft = self.rect.topleft[0]-4, self.rect.topleft[1]
                if self.rect.left <= SCREEN_WIDTH:
                    self.arrow_warning = 0
                if self.rect.right < -300: # Past left side of screen
                    self.activate = 0

        else:
            self.image = IMAGES["spr_brightbluefish"]
    def remove_sprite(self):
        self.kill()

class RainbowFish(pygame.sprite.Sprite):
    def __init__(self, allsprites):
        """
        Starts from above, then begins to chase player if player is smaller
        Will run away if player is bigger
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["spr_rainbowfish"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.score_exit = 0
        self.rainbowtimer = 0
        self.size = [55, 35]
        self.pos = (random.randrange(100, SCREEN_WIDTH-100), -400)
        self.rect.topleft = self.pos
        self.arrow_warning = 0
        self.activate = 0
        self.chase = 0
    def update(self):
        self.rect.topleft = (self.pos[0], self.pos[1])
        self.rainbowtimer += 1
        if self.activate == 1:
            if self.rainbowtimer >= 2000 or self.score_exit == 1: #return; go off screen
                self.chase = 0
                # RETURN TO TOP OF SCREEN
                if self.pos[1] > -100:
                    self.score_exit = 1
                    self.pos = (self.pos[0], self.pos[1]-3) # slightly faster running away
                else:
                    # RESET EVERYTHING
                    self.activate = 0
                    self.pos = (random.randrange(100, SCREEN_WIDTH-100), -100)
                    self.rainbowtimer, self.score_exit = 0, 0
                    if self.size[0]-20 <= 55: #one check on [0], so 85 width is max size
                        self.size[0] += 10
                        self.size[1] += 10
                    self.image = IMAGES["spr_rainbowfish"]
            # Move down at start
            elif self.rainbowtimer >= 300 and self.pos[1] < 200 and self.chase == 0 and self.score_exit == 0: 
                self.arrow_warning = 1
                if self.size[0]-30 == 55: #so it doesn't get more blurry each time at max size
                    self.pos = (self.pos[0], self.pos[1]+2)
                else:
                    self.image = pygame.transform.smoothscale(self.image, (self.size[0], self.size[1]))
                    self.pos = (self.pos[0], self.pos[1]+2)
            if self.pos[1] >= 100:
                self.arrow_warning = 0
            if self.pos[1] >= 200 and self.score_exit == 0:
                self.chase = 1
                
    def chase_player(self, player_sizescore, player_starpower, player_pos):
        if self.score_exit == 0 and self.chase == 1:
            if(self.size[0]-45 <= player_sizescore or player_starpower == 1):
                #Avoid Player
                if self.pos[0] > player_pos[0]:
                    self.pos = (self.pos[0]+2, self.pos[1])
                elif self.pos[0] < player_pos[0]:
                    self.pos = (self.pos[0]-2, self.pos[1])
                if self.pos[1] < player_pos[1]:
                    self.pos = (self.pos[0], self.pos[1]-2)
                elif self.pos[1] > player_pos[1]:
                    self.pos = (self.pos[0], self.pos[1]+2)
                # Rainbow fish can't go past walls, must go up if stuck
                if(self.pos[0] < 0 or self.pos[0] > SCREEN_WIDTH-32):
                    self.score_exit = 1
                    self.chase = 0
                elif(self.pos[1] < 32 or self.pos[1] > SCREEN_HEIGHT-32):
                    self.score_exit = 1
                    self.chase = 0
            else:
                #Chase Player
                if self.pos[0] > player_pos[0]:
                    self.pos = (self.pos[0]-1, self.pos[1])
                elif self.pos[0] < player_pos[0]:
                    self.pos = (self.pos[0]+1, self.pos[1])
                if self.pos[1] < player_pos[1]:
                    self.pos = (self.pos[0], self.pos[1]+1)
                elif self.pos[1] > player_pos[1]:
                    self.pos = (self.pos[0], self.pos[1]-1)
    def collide_with_player(self):
        self.rainbowtimer = 0
        self.activate = 0
        self.pos = (random.randrange(100, SCREEN_WIDTH-100), -100)
        if self.size[0]-20 <= 55: #increases till max size
            self.size[0] += 10
            self.size[1] += 10
    def collide_with_brightbluefish(self):
        self.pos = (random.randrange(100, SCREEN_WIDTH-100), -100)
        self.rainbowtimer = 0
    def remove_sprite(self):
        self.kill()

class Snake(pygame.sprite.Sprite):
    def __init__(self, allsprites):
        """
        Snake bite causes player to downsize to the original size
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["spr_snake"]
        self.restarttimer = 0
        self.direction = random.choice([0, 1]) #move left: 0, move right: 1
        self.rect = self.image.get_rect()
        self.snakeplayeranimatetimer = 0
        self.randomspawn = random.randrange(200, 400)
        allsprites.add(self)
        self.rect.topleft = (random.choice([-70, SCREEN_WIDTH]), random.randrange(SCREEN_HEIGHT-110, SCREEN_HEIGHT-50))
    def update(self):
        self.snakeplayeranimatetimer += 1
        if self.direction == 0: #go left
            if self.snakeplayeranimatetimer > 5:
                self.image = IMAGES["spr_snake2"]
            if self.snakeplayeranimatetimer > 10:
                self.image = IMAGES["spr_snake3"]
            if self.snakeplayeranimatetimer > 15:
                self.image = IMAGES["spr_snake4"]
            if self.snakeplayeranimatetimer > 20:
                self.image = IMAGES["spr_snake"]
                self.snakeplayeranimatetimer = 0
        elif self.direction == 1: #go right
            if self.snakeplayeranimatetimer > 5:
                self.image = pygame.transform.flip(IMAGES["spr_snake2"], 1, 0)
            if self.snakeplayeranimatetimer > 10:
                self.image = pygame.transform.flip(IMAGES["spr_snake3"], 1, 0)
            if self.snakeplayeranimatetimer > 15:
                self.image = pygame.transform.flip(IMAGES["spr_snake4"], 1, 0)
            if self.snakeplayeranimatetimer > 20:
                self.image = pygame.transform.flip(IMAGES["spr_snake"], 1, 0)
                self.snakeplayeranimatetimer = 0
        self.restarttimer += 1
        if self.restarttimer > self.randomspawn:
            if self.rect.topleft[0] == -70:
                self.direction = 1 #right
            elif self.rect.topleft[0] == SCREEN_WIDTH:
                self.direction = 0 #left
            if self.direction == 1: #right movements
                self.rect.topleft = self.rect.topleft[0]+2, self.rect.topleft[1]
            elif self.direction == 0: #left movements
                self.rect.topleft = self.rect.topleft[0]-2, self.rect.topleft[1]
            if(self.rect.topleft[0] < -60 and self.direction == 0): #restarts position
                self.rect.topleft = (random.choice([-70, SCREEN_WIDTH]),
                                     random.randrange(SCREEN_HEIGHT-110, SCREEN_HEIGHT-50))
                self.rect.topleft = self.rect.topleft[0], self.rect.topleft[1]
                self.restarttimer = 0
            elif(self.rect.topleft[0] > SCREEN_WIDTH-10 and self.direction == 1): #restarts position
                self.rect.topleft = (random.choice([-70, SCREEN_WIDTH]),
                                     random.randrange(SCREEN_HEIGHT-110, SCREEN_HEIGHT-50))
                self.rect.topleft = self.rect.topleft[0], self.rect.topleft[1]
                self.restarttimer = 0
    def collide_with_brightbluefish(self):
        self.rect.topleft = (random.choice([-70, SCREEN_WIDTH]), random.randrange(SCREEN_HEIGHT-110, SCREEN_HEIGHT-50))
        self.restarttimer = 0
    def collide_with_player(self):
        self.rect.topleft = (random.choice([-70, SCREEN_WIDTH]),
                             random.randrange(SCREEN_HEIGHT-110, SCREEN_HEIGHT-50))
        self.restarttimer = 0
    def remove_sprite(self):
        self.kill()

class SeaHorse(pygame.sprite.Sprite):
    def __init__(self, allsprites):
        """
        Speed powerup for player
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["spr_seahorse"]
        self.restarttimer = 0
        self.direction = random.choice([0, 1]) #move left: 0, move right: 1
        self.randomspawn = random.randrange(200, 500) #timer
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.rect.topleft = (random.choice([-70, SCREEN_WIDTH]), random.randrange(50, SCREEN_HEIGHT-200))
    def update(self):
        self.restarttimer += 1
        if self.direction == 1:
            self.image = pygame.transform.flip(IMAGES["spr_seahorse"], 1, 0)
        else:
            self.image = IMAGES["spr_seahorse"]
        if self.restarttimer > self.randomspawn:
            if self.rect.topleft[0] == -70:
                self.direction = 1 #right
            elif self.rect.topleft[0] == SCREEN_WIDTH:
                self.direction = 0 #left
            if self.direction == 1: #right movements
                self.rect.topleft = self.rect.topleft[0]+3, self.rect.topleft[1]
            elif self.direction == 0: #left movements
                self.rect.topleft = self.rect.topleft[0]-3, self.rect.topleft[1]
            if(self.rect.topleft[0] < -60 and self.direction == 0): #restarts position
                self.rect.topleft = (random.choice([-70, SCREEN_WIDTH]),
                                     random.randrange(50, SCREEN_HEIGHT-200))
                self.rect.topleft = self.rect.topleft[0], self.rect.topleft[1]
                self.restarttimer = 0
                self.randomspawn = random.randrange(1500, 2000)
            elif(self.rect.topleft[0] > SCREEN_WIDTH-10 and self.direction == 1): #restarts position
                self.rect.topleft = (random.choice([-70, SCREEN_WIDTH]),
                                     random.randrange(50, SCREEN_HEIGHT-200))
                self.rect.topleft = self.rect.topleft[0], self.rect.topleft[1]
                self.restarttimer = 0
                self.randomspawn = random.randrange(1500, 2000)
    def collide_with_player(self):
        self.rect.topleft = (random.choice([-70, SCREEN_WIDTH]), random.randrange(50, SCREEN_HEIGHT-200))
        self.restarttimer = 0
    def remove_sprite(self):
        self.kill()

class JellyFish(pygame.sprite.Sprite):
    def __init__(self, allsprites):
        """
        Slows down player temporarily for 5 seconds
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["spr_jellyfish"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.returnback = 0
        self.jellyfishtimer = 0
        self.jellyfishanimatetimer = 0
        self.jellyfishrandomspawn = random.randrange(700, 900)
        self.newpos = self.rect.topleft[0], self.rect.topleft[1]
        self.jfstring = []
        self.activate = 0
        self.rect.topleft = (random.randrange(100, SCREEN_WIDTH-100), -50)
    def update(self):
        self.jellyfishanimatetimer += 1
        self.jfstring = [IMAGES["spr_jellyfish"], IMAGES["spr_jellyfish2"], IMAGES["spr_jellyfish3"],
                         IMAGES["spr_jellyfish4"], IMAGES["spr_jellyfish5"], IMAGES["spr_jellyfish6"],
                         IMAGES["spr_jellyfish7"]]
        for i in range(2, 16, 2): #cycle through first 13 sprite animations
            if self.jellyfishanimatetimer >= i:
                self.image = self.jfstring[(i//2)-1]
        for i in range(18, 28, 2): #cycle through 13 sprite animations backwards
            if self.jellyfishanimatetimer > i:
                self.image = self.jfstring[((28-i)//2)+1]
        if self.jellyfishanimatetimer > 28:
            self.jellyfishanimatetimer = 1
        self.jellyfishtimer += 1
        if self.rect.topleft[1] == -50:
            self.returnback = 0
        if self.rect.topleft[1] > SCREEN_HEIGHT-80:
            #collide with BOTTOM wall
            self.returnback = 1
        if self.returnback == 0 and self.jellyfishtimer > self.jellyfishrandomspawn:
            if self.activate:
                self.newpos = (self.rect.topleft[0], self.rect.topleft[1]+3)
                self.rect.topleft = self.newpos
        elif self.returnback == 1:
            self.newpos = (self.rect.topleft[0], self.rect.topleft[1]-3)
            self.rect.topleft = self.newpos
            if self.rect.topleft[1] < -32:
                self.jellyfishtimer = 0
                self.jellyfishrandomspawn = random.randrange(500, 1200)
                self.rect.topleft = random.randrange(100, SCREEN_WIDTH-100), -50
    def collide_with_player(self):
        self.rect.topleft = (random.randrange(100, SCREEN_WIDTH-100), -50)
        self.jellyfishtimer = 0
    def collide_with_brightbluefish(self):
        self.rect.topleft = (random.randrange(100, SCREEN_WIDTH-100), -50)
        self.jellyfishtimer = 0
    def remove_sprite(self):
        self.kill()

class StarPowerup(pygame.sprite.Sprite):
    def __init__(self, allsprites):
        """
        Player becomes invincible for period of time
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["spr_star"]
        self.rect = self.image.get_rect()
        allsprites.add(self)
        self.staranimator = 0
        self.spawntimer = 0
        self.pos = (SCREEN_WIDTH, SCREEN_HEIGHT-80) # Out of screen
        self.rect.topleft = self.pos
    def update(self):
        self.spawntimer += 1
        self.staranimator += 1
        self.rect.topleft = (self.pos[0], self.pos[1])
        if self.spawntimer == 2600: # Reset position, timer to 0
            self.pos = (SCREEN_WIDTH, SCREEN_HEIGHT-80)
            self.spawntimer = 0
        elif self.spawntimer > 1500: # Respawn
            self.pos = (self.pos[0]-5, SCREEN_HEIGHT-80)
            if self.staranimator > 0:
                self.image = IMAGES["spr_star"]
            if self.staranimator > 10:
                self.image = IMAGES["spr_star2"]
            if self.staranimator > 20:
                self.image = IMAGES["spr_star3"]
            if self.staranimator > 30:
                self.image = IMAGES["spr_star2"]
            if self.staranimator > 40:
                self.staranimator = 0
    def collide_with_player(self):
        self.pos = (SCREEN_WIDTH, SCREEN_HEIGHT-80)
        self.spawntimer = 0
    def remove_sprite(self):
        self.kill()

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

def main():
    global menu_selection
    KEYS = [False, False, False, False] #up, left, down, right
    menu_selection = START_SCREEN # Initialize on START_SCREEN
    RUNNING, RESTART, DEBUG = 0, 1, 2
    state = RESTART
    debug_message = 0
    SCORE, SCORE_BLIT, ONEPOWERUPSOUND, SCORE_DISAPPEAR_TIMER = 0, 0, 0, 0
    screen = None
    last_pressed = 0
    (x_first, y_first) = (0, 0)
    (x_second, y_second) = (0, -SCREEN_HEIGHT)
    clock = pygame.time.Clock()
    adjust_to_correct_appdir()

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Fish Food")

    load_image("sprites/wall.bmp", "spr_wall", True, False)
    load_image("sprites/Player_left.png", "player_left", True, True)
    load_image("sprites/Player_downright.png", "player_downright", True, True)
    load_image("sprites/Player_down.png", "player_down", True, True)
    load_image("sprites/Player_left_gold.png", "player_left_gold", True, True)
    load_image("sprites/Player_downright_gold.png", "player_downright_gold", True, True)
    load_image("sprites/Player_down_gold.png", "player_down_gold", True, True)
    load_image("sprites/redfish.png", "spr_redfish", True, True)
    load_image("sprites/greenfish.png", "spr_greenfish", True, True)
    IMAGES["spr_greenfish_left"] = pygame.transform.flip(IMAGES["spr_greenfish"], 1, 0)
    load_image("sprites/biggreenfish.png", "spr_biggreenfish", True, True)
    load_image("sprites/silverfish.png", "spr_silverfish", True, True)
    load_image("sprites/snake1.png", "spr_snake", True, True)
    load_image("sprites/snake2.png", "spr_snake2", True, True)
    load_image("sprites/snake3.png", "spr_snake3", True, True)
    load_image("sprites/snake4.png", "spr_snake4", True, True)
    load_image("sprites/seahorse.png", "spr_seahorse", True, True)
    load_image("sprites/jellyfish1.png", "spr_jellyfish", True, True)
    load_image("sprites/jellyfish2.png", "spr_jellyfish2", True, True)
    load_image("sprites/jellyfish3.png", "spr_jellyfish3", True, True)
    load_image("sprites/jellyfish4.png", "spr_jellyfish4", True, True)
    load_image("sprites/jellyfish5.png", "spr_jellyfish5", True, True)
    load_image("sprites/jellyfish6.png", "spr_jellyfish6", True, True)
    load_image("sprites/jellyfish7.png", "spr_jellyfish7", True, True)
    load_image("sprites/shark.png", "spr_shark", True, True)
    load_image("sprites/brightbluefish.png", "spr_brightbluefish", True, True)
    IMAGES["bigBrightBlueFish"] = pygame.transform.smoothscale(IMAGES["spr_brightbluefish"], (300, 200))
    IMAGES["bigBrightBlueFishLeft"] = pygame.transform.flip(IMAGES["bigBrightBlueFish"], 1, 0)
    load_image("sprites/starfish1.png", "spr_star", True, True)
    load_image("sprites/starfish2.png", "spr_star2", True, True)
    load_image("sprites/starfish3.png", "spr_star3", True, True)
    load_image("sprites/arrowwarningred.png", "arrow_warning_red", True, True)
    load_image("sprites/arrowwarningsilver.png", "arrow_warning_silver", True, True)
    load_image("sprites/arrowwarningblue.png", "arrow_warning_blue", True, True)
    load_image("sprites/SeaweedMiddle.png", "spr_seaweed", True, True)
    load_image("sprites/SeaweedLeft.png", "spr_seaweed_left", True, True)
    load_image("sprites/SeaweedRight.png", "spr_seaweed_right", True, True)
    load_image("sprites/rainbowfish.png", "spr_rainbowfish", True, True)
    #font and texts
    ocean_font = pygame.font.Font("fonts/oceanfont.ttf", 16)
    ocean_font_main = pygame.font.Font("fonts/oceanfont.ttf", 48)
    font_ocean_gameover = pygame.font.Font("fonts/oceanfont.ttf", 76)
    font_arial = pygame.font.SysFont('Arial', 32)
    #backgrounds
    start_menu = pygame.image.load("sprites/startmenu.png").convert()
    start_menu = pygame.transform.scale(start_menu, (SCREEN_WIDTH, SCREEN_HEIGHT))
    info_screen = pygame.image.load("sprites/infoscreen.bmp").convert()
    info_screen = pygame.transform.scale(info_screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
    game_over = pygame.image.load("sprites/gameover.png").convert()
    game_over = pygame.transform.scale(game_over, (SCREEN_WIDTH, SCREEN_HEIGHT))
    ground = pygame.image.load("sprites/ground.bmp").convert()
    ground = pygame.transform.scale(ground, (SCREEN_WIDTH, 100))
    bgwater = pygame.image.load("sprites/background.bmp").convert()
    bgwater = pygame.transform.scale(bgwater, (SCREEN_WIDTH, SCREEN_HEIGHT))
    blackbg = pygame.image.load("sprites/blackbg.jpg").convert()
    blackbg = pygame.transform.scale(blackbg, (SCREEN_WIDTH, 30))
    gameicon = pygame.image.load("sprites/redfishico.png")
    pygame.display.set_icon(gameicon)
    pygame.display.set_caption('Fish Food')
    pygame.mouse.set_visible(0)
    load_sound("sounds/snd_eat.wav", "snd_eat")
    SOUNDS["snd_eat"].set_volume(.2)
    load_sound("sounds/eatshark.wav", "snd_eatshark")
    SOUNDS["snd_eatshark"].set_volume(.2)
    load_sound("sounds/sizedown.wav", "snd_sizedown")
    load_sound("sounds/playerdie.wav", "snd_playerdie")
    SOUNDS["snd_playerdie"].set_volume(.3)
    load_sound("sounds/poweruptimer.wav", "snd_poweruptimer")
    SOUNDS["snd_poweruptimer"].set_volume(.3)
    load_sound("sounds/siren.wav", "snd_siren")
    SOUNDS["snd_siren"].set_volume(.05)
    load_sound("sounds/sharkincoming.wav", "snd_sharkincoming")
    SOUNDS["snd_sharkincoming"].set_volume(.03)
    # Music loop
    pygame.mixer.music.load("sounds/gamemusic.mp3")
    pygame.mixer.music.set_volume(.1)
    pygame.mixer.music.play(-1)
    
    while True:
        clock.tick(80)
        display_caption()
        
        ##################
        # MENUS
        ##################
        if state == RESTART and menu_selection == 0: 
            # Play screen
            # Create object instances
            allsprites = pygame.sprite.Group()
            walls = []
            seaweeds = []
            for x_top in range(29):
                wall = Wall(allsprites)
                wall.rect.topleft = (x_top*32, 0) #top walls
                walls.append(wall)
            for x_bottom in range(29):
                wall = Wall(allsprites)
                wall.rect.topleft = (x_bottom*32, SCREEN_HEIGHT-32) #bottom walls
                walls.append(wall)
            for y_left in range(17):
                wall = Wall(allsprites)
                wall.rect.topleft = (0, (y_left*32)+32) #left walls
                walls.append(wall)
            for y_right in range(17):
                wall = Wall(allsprites)
                wall.rect.topleft = (SCREEN_WIDTH-32, (y_right*32)+32) #right walls
                walls.append(wall)
            for x_pos in range(5, SCREEN_WIDTH-15, 60):
                seaweed = Seaweed(allsprites, x_pos, SCREEN_HEIGHT-120)
                seaweeds.append(seaweed)
            player = Player(allsprites)
            red_fishes = [RedFish(allsprites) for i in range(6)]
            green_fishes = [GreenFish(allsprites) for i in range(3)]
            silverfish = SilverFish(allsprites)
            snake = Snake(allsprites)
            seahorse = SeaHorse(allsprites)
            jellyfishes = [JellyFish(allsprites) for i in range(3)]
            sharks = [Shark(allsprites) for i in range(4)]
            brightbluefish = BrightBlueFish(allsprites)
            star = StarPowerup(allsprites)
            rainbow_fish = RainbowFish(allsprites)

            SCORE = 0
            SCORE_BLIT = 0
            SCORE_DISAPPEAR_TIMER = 0
            ONEPOWERUPSOUND = 0

            state = RUNNING
        if menu_selection == START_SCREEN: # Menu Screen
            Menu(screen, start_menu, ocean_font_main)
            SCORE = 0     
            state = RESTART
        elif menu_selection == GAMEOVER_SCREEN: # Gameover Screen
            KEYS = [False, False, False, False]
            high_score = get_high_score()
            if SCORE > high_score:
                save_high_score(SCORE)
            SOUNDS["snd_playerdie"].play()
            SOUNDS["snd_poweruptimer"].stop()
            GameOver(screen, game_over, font_arial, font_ocean_gameover, SCORE)
            state = RESTART
            for spr in allsprites:
                spr.remove_sprite()
        elif menu_selection == PAUSE_SCREEN:
            KEYS = [False, False, False, False]
            PauseScreen(screen, bgwater)
        elif menu_selection == INFO_SCREEN:
            InfoScreen(screen, info_screen)
        elif state == RUNNING and menu_selection != START_SCREEN:
            ##################
            # EVENTS AND KEYBOARD PRESSES (INCLUDING PLAYER MOVEMENT)
            ##################
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        for i in range(0, len(SOUNDS)):
                            soundslist = list(SOUNDS.keys()) # Returns list of keys in sounds
                            SOUNDS[soundslist[i]].stop() # Stops all sounds when go to menu
                        menu_selection = PAUSE_SCREEN
                    elif event.key == pygame.K_UP:
                        KEYS[0] = True
                    elif event.key == pygame.K_LEFT:
                        KEYS[1] = True
                    elif event.key == pygame.K_DOWN:
                        KEYS[2] = True
                    elif event.key == pygame.K_RIGHT:
                        KEYS[3] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        KEYS[0] = False
                    elif event.key == pygame.K_LEFT:
                        last_pressed = 0
                        KEYS[1] = False
                    elif event.key == pygame.K_DOWN:
                        KEYS[2] = False
                    elif event.key == pygame.K_RIGHT:
                        last_pressed = 1
                        KEYS[3] = False
                    elif event.key == pygame.K_SPACE:
                        debug_message = 1
                        state = DEBUG
            if KEYS[0]:
                player.move_up()
            if KEYS[2]:
                player.move_down()
            if KEYS[1]:
                player.move_left()
            if KEYS[3]:
                player.move_right()
            if KEYS[0] and KEYS[1]:
                player.move_upleft()
            if KEYS[0] and KEYS[3]:
                player.move_upright()
            if KEYS[2] and KEYS[1]:
                player.move_downleft()
            if KEYS[2] and KEYS[3]:
                player.move_downright()
            if KEYS == [False, False, False, False]:
                player.player_width, player.player_height = (41, 19)
                if last_pressed == 0:
                    if player.starpower == 1:
                        if player.playeranimatetimer > 2:
                            player.image = IMAGES["player_left_gold"]
                        if player.playeranimatetimer > 4:
                            player.image = IMAGES["player_left"]
                    else:
                        player.image = IMAGES["player_left"]
                else:
                    if player.starpower == 1:
                        if player.playeranimatetimer > 2:
                            player.image = pygame.transform.rotate(IMAGES["player_left_gold"], 180)
                            player.image = pygame.transform.flip(player.image, 0, 1)
                        if player.playeranimatetimer > 4:
                            player.image = pygame.transform.rotate(IMAGES["player_left"], 180)
                            player.image = pygame.transform.flip(player.image, 0, 1)
                    else:
                        player.image = pygame.transform.rotate(IMAGES["player_left"], 180)
                        player.image = pygame.transform.flip(player.image, 0, 1)

            ##################
            # Call update function for each object
            ##################
            allsprites.update()

            ##################
            # Draw menus for in-game
            ##################
            # Water background movement
            y_first += 10
            y_second += 10
            screen.blit(bgwater, (x_first, y_first))
            screen.blit(bgwater, (x_second, y_second))
            if y_second > SCREEN_HEIGHT:
                y_second = -SCREEN_HEIGHT
            if y_first > SCREEN_HEIGHT:
                y_first = -SCREEN_HEIGHT
            screen.blit(ground, (0, SCREEN_HEIGHT-100))
            allsprites.draw(screen)

            # Menu Design
            screen.blit(blackbg, (0, 0))
            menu_text = ocean_font.render("Menu:", 1, (255, 255, 255))
            screen.blit(menu_text, (10, 5))
            screen.blit(IMAGES["spr_redfish"], (65, 11))
            screen.blit(IMAGES["spr_greenfish"], (90, 11))
            screen.blit(IMAGES["spr_silverfish"], (120, 9))
            if rainbow_fish.size[0]-45 <= player.sizescore: #55 is orig size
                blitted_rainbow_fish = pygame.transform.smoothscale(IMAGES["spr_rainbowfish"], (24, 17))
                screen.blit(blitted_rainbow_fish, (158, 6))
            else:
                screen.blit(ocean_font.render("", 1, (0, 0, 0)), (158, 6))
            if player.sizescore >= 40:
                blitted_Big_Green_Fish = pygame.transform.smoothscale(IMAGES["spr_biggreenfish"], (24, 15))
                screen.blit(blitted_Big_Green_Fish, (189, 7))
            else:
                screen.blit(ocean_font.render("", 1, (0, 0, 0)), (189, 7))
            if player.starpower == 2:
                blittedshark = pygame.transform.smoothscale(IMAGES["spr_shark"], (24, 15))
                screen.blit(blittedshark, (220, 7))
            else:
                screen.blit(ocean_font.render("", 1, (0, 0, 0)), (220, 7))

            # Font On Top of Playing Screen
            score_text = ocean_font.render("Score: " + str(SCORE), 1, (255, 255, 255))
            screen.blit(score_text, ((SCREEN_WIDTH/2)-32, 5))
            player.get_powerup_timer_text(ocean_font)
            player.get_speed_timer_text(ocean_font)
            screen.blit(player.get_powerup_timer_text(ocean_font), (732, 5))
            screen.blit(player.get_speed_timer_text(ocean_font), (550, 5))
            if SCORE_BLIT == 0:
                SCORE_BLIT_TEXT = ocean_font.render("", 1, (255, 255, 255))
            else:
                SCORE_BLIT_TEXT = ocean_font.render("+" + str(SCORE_BLIT), 1, (255, 255, 255))
                if SCORE_DISAPPEAR_TIMER > 10:
                    SCORE_BLIT = 0
                    SCORE_DISAPPEAR_TIMER = 0
            screen.blit(SCORE_BLIT_TEXT, (player.pos[0]+13, player.pos[1]-25-(player.sizescore/2)))

            ##################
            # ENEMY MOVEMENTS & ARROW WARNINGS
            ##################
            # Rainbow Fish
            if rainbow_fish.rainbowtimer >= 200:
                rainbow_fish.activate = 1
            if rainbow_fish.activate == 1 and rainbow_fish.score_exit == 0:
                if rainbow_fish.arrow_warning == 1 and rainbow_fish.rect.top < 0:
                    screen.blit(IMAGES["arrow_warning_red"], (rainbow_fish.rect.topleft[0], 40))
                    SOUNDS["snd_sharkincoming"].play()
                rainbow_fish.chase_player(player.sizescore, player.starpower, player.pos)
            # Sharks
            if SCORE >= 5:
                sharks[0].activate = 1
                if sharks[0].arrow_warning == 1:
                    screen.blit(IMAGES["arrow_warning_silver"], (sharks[0].rect.topleft[0], 40))
                    SOUNDS["snd_sharkincoming"].play()
            if SCORE >= 20:
                sharks[1].activate = 1
                if sharks[1].arrow_warning == 1:
                    screen.blit(IMAGES["arrow_warning_silver"], (sharks[1].rect.topleft[0], 40))
                    SOUNDS["snd_sharkincoming"].play()
            if SCORE >= 45:
                sharks[2].activate = 1
                if sharks[2].arrow_warning == 1:
                    screen.blit(IMAGES["arrow_warning_silver"], (sharks[2].rect.topleft[0], 40))
                    SOUNDS["snd_sharkincoming"].play()
            if SCORE >= 75:
                sharks[3].activate = 1
                if sharks[3].arrow_warning == 1:
                    screen.blit(IMAGES["arrow_warning_silver"], (sharks[3].rect.topleft[0], 40))
                    SOUNDS["snd_sharkincoming"].play()
            # Bright Blue Fish
            # Starts moving when you have a certain score
            if(brightbluefish.activate == 0 and (SCORE % 50 >= 0 and SCORE % 50 <= 2) and SCORE >= 50):
                brightbluefish.direction = random.choice([0, 1])
                brightbluefish.activate = 1
                if brightbluefish.direction == 1: # MOVING RIGHT
                    brightbluefish.rect.topright = (-500, random.randrange(50, SCREEN_HEIGHT-200))
                elif brightbluefish.direction == 0: # MOVING LEFT
                    brightbluefish.rect.topleft = (SCREEN_WIDTH+500, random.randrange(50, SCREEN_HEIGHT-200))
            # Arrow Warning for Bright Blue Fish
            if brightbluefish.arrow_warning == 1:
                if brightbluefish.direction == 1 and brightbluefish.rect.topleft[0] < 0: # MOVING RIGHT
                    screen.blit(IMAGES["arrow_warning_blue"], (20, brightbluefish.rect.midright[1]+40))
                    SOUNDS["snd_siren"].play()
                elif brightbluefish.direction == 0 and brightbluefish.rect.topleft[0] > SCREEN_WIDTH: # MOVING LEFT
                    screen.blit(pygame.transform.flip(IMAGES["arrow_warning_blue"], 1, 0),
                                (SCREEN_WIDTH-70, brightbluefish.rect.midright[1]+40))
                    SOUNDS["snd_sharkincoming"].stop()
                    SOUNDS["snd_siren"].play()

            # Jellyfish
            if SCORE >= 0:
                jellyfishes[0].activate = 1
            if SCORE >= 30:
                jellyfishes[1].activate = 1    
            if SCORE == 60:
                jellyfishes[2].activate = 1

            ##################
            # COLLISIONS
            ##################
            for red_fish in red_fishes:
                if pygame.sprite.collide_mask(red_fish, player):
                    red_fish.collide_with_player()
                    SCORE, SCORE_BLIT = player.collide_with_redfish(SCORE, SCORE_BLIT)
                    SOUNDS["snd_eat"].play()
                for greenfish in green_fishes:
                    if red_fish.rect.colliderect(greenfish):
                        greenfish.collision_with_redfish()
                        if greenfish.image != IMAGES["spr_biggreenfish"]:
                            red_fish.collide_with_greenfish()
                if pygame.sprite.collide_mask(red_fish, brightbluefish):
                    red_fish.collide_with_brightbluefish()
                for wall in walls:
                    if red_fish.rect.colliderect(wall.rect):
                        red_fish.collision_with_wall(wall.rect)
            for greenfish in green_fishes:
                if pygame.sprite.collide_mask(greenfish, player):
                    if(greenfish.image == IMAGES["spr_greenfish"] or 
                       greenfish.image == IMAGES["spr_greenfish_left"] or 
                       player.sizescore >= 40 or 
                       player.starpower == 1):
                        SOUNDS["snd_eat"].play()
                        SCORE, SCORE_BLIT = player.collide_with_greenfish(SCORE, SCORE_BLIT)
                        greenfish.small_collision_with_player()
                        greenfish.big_green_fish_score = 0
                    else: # When it transforms to big green fish, player dies
                        menu_selection = GAMEOVER_SCREEN
                if pygame.sprite.collide_mask(greenfish, brightbluefish):
                    greenfish.big_green_fish_score = 0
                    greenfish.image = IMAGES["spr_greenfish"]
                    greenfish.rect.topleft = (random.randrange(100, SCREEN_WIDTH-100), random.randrange(100, SCREEN_HEIGHT-100))
                for wall in walls:
                    if greenfish.rect.colliderect(wall.rect):
                        greenfish.collision_with_wall(wall.rect)
            if pygame.sprite.collide_mask(silverfish, player):
                SOUNDS["snd_eat"].play()
                SCORE, SCORE_BLIT = player.collide_with_silverfish(SCORE, SCORE_BLIT)
                silverfish.collide_with_player()
            if pygame.sprite.collide_mask(silverfish, brightbluefish):
                SOUNDS["snd_eat"].play()
                silverfish.collide_with_brightbluefish()
            for shark in sharks:
                if pygame.sprite.collide_mask(shark, player):
                    SCORE, SCORE_BLIT = player.collide_with_shark(SCORE, SCORE_BLIT)
                    shark.collide_with_player()
                    if player.starpower != 0:
                        SOUNDS["snd_eatshark"].play()
                if pygame.sprite.collide_mask(shark, brightbluefish):
                    shark.collide_with_brightbluefish()
                    SOUNDS["snd_eat"].play()
                for wall in walls:
                    if shark.rect.colliderect(wall.rect):
                        shark.collision_with_wall(wall.rect)
                if player.starpower == 2:
                    shark.mini_shark = 1
                else:
                    shark.mini_shark = 0
            if pygame.sprite.collide_mask(rainbow_fish, player):
                # Player eats rainbow_fish only when appears bigger (arbitrary)
                if (rainbow_fish.size[0]-45 <= player.sizescore) or (player.starpower == 1):
                    SOUNDS["snd_eat"].play()
                    SCORE_BLIT = 2
                    SCORE += 2
                    player.sizescore += 2
                    rainbow_fish.collide_with_player()
                else:
                    if player.starpower != 1:
                        menu_selection = GAMEOVER_SCREEN
            if pygame.sprite.collide_mask(rainbow_fish, brightbluefish):
                SOUNDS["snd_eat"].play()
                rainbow_fish.collide_with_brightbluefish()
            if pygame.sprite.collide_mask(snake, player):
                snake.collide_with_player()
                if player.starpower != 1:
                    player.collide_with_snake()
                    SOUNDS["snd_sizedown"].play()
                else:
                    SOUNDS["snd_eat"].play()
            if pygame.sprite.collide_mask(snake, brightbluefish):
                snake.collide_with_brightbluefish()
            if pygame.sprite.collide_mask(seahorse, player):
                player.collide_with_seahorse()
                seahorse.collide_with_player()
                SOUNDS["snd_eat"].play()
                ONEPOWERUPSOUND += 1
                if ONEPOWERUPSOUND > 1:
                    SOUNDS["snd_poweruptimer"].stop()
                for i in range(0, len(SOUNDS)):
                    soundslist = list(SOUNDS.keys()) #returns list of keys in sounds
                    SOUNDS[soundslist[i]].stop() #stops all sounds
                SOUNDS["snd_poweruptimer"].play()
            for jellyfish in jellyfishes:
                if pygame.sprite.collide_mask(jellyfish, player):
                    jellyfish.collide_with_player()
                    if player.starpower == 1:
                        SOUNDS["snd_eat"].play()
                    else:
                        player.collide_with_jellyfish()
                        SOUNDS["snd_sizedown"].play()
                        ONEPOWERUPSOUND += 1
                        if ONEPOWERUPSOUND > 1:
                            SOUNDS["snd_poweruptimer"].stop()
                        for i in range(0, len(SOUNDS)):
                            soundslist = list(SOUNDS.keys()) # Returns list of keys in sounds
                            SOUNDS[soundslist[i]].stop() # Stops all sounds
                        SOUNDS["snd_poweruptimer"].play()
                if pygame.sprite.collide_mask(jellyfish, brightbluefish):
                    jellyfish.collide_with_brightbluefish()
                    SOUNDS["snd_eat"].play()
            if player.rect.colliderect(star):
                player.collide_with_star()
                star.collide_with_player()
                SOUNDS["snd_eat"].play()
                ONEPOWERUPSOUND += 1
                if ONEPOWERUPSOUND > 1:
                    SOUNDS["snd_poweruptimer"].stop()
                for i in range(0, len(SOUNDS)):
                    soundslist = list(SOUNDS.keys()) # Returns list of keys in sounds
                    SOUNDS[soundslist[i]].stop() # Stops all sounds
                SOUNDS["snd_poweruptimer"].play()
            if pygame.sprite.collide_mask(brightbluefish, player):
                if player.starpower != 1:
                    menu_selection = GAMEOVER_SCREEN
            if SCORE_BLIT > 0: # Score Timer above player sprite
                SCORE_DISAPPEAR_TIMER += 1
            ##################
            # Sound Checks
            ##################
            if player.starpower == 0: # Powerup is over on the player
                ONEPOWERUPSOUND -= 1
                SOUNDS["snd_poweruptimer"].stop()
            if player.speed_time_left < 0:
                ONEPOWERUPSOUND -= 1
                SOUNDS["snd_poweruptimer"].stop()

            ##################
            # Update screen display
            ##################
            pygame.display.flip()

        ##################
        # DEBUGGING PURPOSES
        ##################
        elif state == DEBUG and menu_selection == PLAY_SCREEN:
            if debug_message == 1:
                debug_message = 0
                # USE BREAKPOINT HERE
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        state = RUNNING
            
if __name__ == '__main__':
    main()
