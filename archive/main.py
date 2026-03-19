import asyncio
import pygame
import sys
import random

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Complex Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Load image function
def load_image(file, name, images):
    image = pygame.image.load("sprites/" + file).convert_alpha()
    images[name] = image

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, images):
        super().__init__()
        self.image = images["player"]
        self.rect = self.image.get_rect(center=(x, y))
        self.score = 0

    def update(self, key_states, enemies):
        speed = 5
        if key_states[pygame.K_LEFT]:
            self.rect.x -= speed
        if key_states[pygame.K_RIGHT]:
            self.rect.x += speed
        if key_states[pygame.K_UP]:
            self.rect.y -= speed
        if key_states[pygame.K_DOWN]:
            self.rect.y += speed

        # Collision with enemies
        for enemy in enemies:
            if pygame.sprite.collide_rect(self, enemy):
                self.handle_collision(enemy)

    def handle_collision(self, enemy):
        # Define collision behavior based on enemy type
        if isinstance(enemy, SilverFish):
            enemy.eaten()  # Assume SilverFish has an 'eaten' method
            self.score += 10
            self.grow()
        elif isinstance(enemy, Shark):
            self.score -= 10  # Example behavior with a shark
        # Add more elif blocks for other enemy types

    def grow(self):
        # Increase the size of the player when eating a fish
        self.image = pygame.transform.scale(self.image, (self.rect.width + 5, self.rect.height + 5))
        self.rect = self.image.get_rect(center=self.rect.center)


# Fish class (generic for different fish types)
class Fish(pygame.sprite.Sprite):
    def __init__(self, image, speed, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.speed[0] = -self.speed[0]
        if self.rect.bottom >= SCREEN_HEIGHT or self.rect.top <= 0:
            self.speed[1] = -self.speed[1]
            
class Seaweed(pygame.sprite.Sprite):
    def __init__(self, x, y, images):
        super().__init__()
        self.image = images["seaweed"]
        self.rect = self.image.get_rect(topleft=(x, y))

class SilverFish(pygame.sprite.Sprite):
    def __init__(self, images):
        super().__init__()
        self.image = images["silver_fish"]
        self.rect = self.image.get_rect(center=(random.randint(20, SCREEN_WIDTH-20), random.randint(20, SCREEN_HEIGHT-20)))
        self.speed = random.choice([-3, 3])

    def update(self):
        self.rect.x += self.speed
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.speed = -self.speed
    def eaten(self):
        # Reset position when eaten
        self.rect.center = (random.randint(20, SCREEN_WIDTH-20), random.randint(20, SCREEN_HEIGHT-20))


# Shark class
class Shark(pygame.sprite.Sprite):
    def __init__(self, images):
        super().__init__()
        self.image = images["shark"]
        self.rect = self.image.get_rect(center=(random.randint(20, SCREEN_WIDTH-20), random.randint(20, SCREEN_HEIGHT-20)))
        self.speed = [random.choice([-4, 4]), random.choice([-4, 4])]

    def update(self):
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.speed[0] = -self.speed[0]
        if self.rect.bottom >= SCREEN_HEIGHT or self.rect.top <= 0:
            self.speed[1] = -self.speed[1]

# Main game loop
def main():
    images = {}
    load_image("player_left.png", "player", images)
    load_image("red_fish.png", "red_fish", images)
    load_image("green_fish.png", "green_fish", images)
    load_image("shark.png", "shark", images)
    load_image("silver_fish.png", "silver_fish", images)
    load_image("seaweed.png", "seaweed", images)

    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, images)

    # Create different fish and a shark
    red_fishes = pygame.sprite.Group(Fish(images["red_fish"], [2, 2], random.randint(20, SCREEN_WIDTH-20), random.randint(20, SCREEN_HEIGHT-20)) for _ in range(5))
    green_fishes = pygame.sprite.Group(Fish(images["green_fish"], [3, 3], random.randint(20, SCREEN_WIDTH-20), random.randint(20, SCREEN_HEIGHT-20)) for _ in range(3))
    sharks = pygame.sprite.Group(Fish(images["shark"], [4, 4], random.randint(20, SCREEN_WIDTH-20), random.randint(20, SCREEN_HEIGHT-20)) for _ in range(2))
    seaweeds = pygame.sprite.Group(Seaweed(random.randint(50, SCREEN_WIDTH-50), SCREEN_HEIGHT-120, images) for _ in range(5))
    silver_fishes = pygame.sprite.Group(SilverFish(images) for _ in range(3))
    sharks = pygame.sprite.Group(Shark(images) for _ in range(2))

    allsprites = pygame.sprite.Group(player, *red_fishes, *green_fishes, *seaweeds, *silver_fishes, *sharks)


    running = True
    while running:
        key_states = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update player with key states and enemies
        player.update(key_states, sharks)
        # Update all other sprites
        for sprite in allsprites:
            sprite.update()

            # Check if the player eats a SilverFish
            if isinstance(sprite, SilverFish) and pygame.sprite.collide_rect(player, sprite):
                sprite.eaten()
                player.score += 10
                player.grow()

        screen.fill((0, 0, 0))  # Clear screen
        allsprites.draw(screen)

        # Display score
        score_text = font.render("Score: " + str(player.score), True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()  # Update the display
        clock.tick(FPS)
        # await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

# Run the game
# asyncio.run(main())
main()
