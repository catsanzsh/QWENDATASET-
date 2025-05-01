import pygame
import sys
import random

# Constants from SMB3 physics [[2]]
GRAVITY = 0.3
MAX_FALL_SPEED = 4.0
JUMP_POWER = -5.5
MOVE_SPEED = 2.0

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

class Player:
    def __init__(self):
        self.x = 100
        self.y = 300
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.size = 30
        self.score = 0
        self.lives = 3
        self.powered_up = False

    def update(self, keys):
        # Horizontal movement [[2]]
        if keys[pygame.K_LEFT]:
            self.vel_x = max(-MOVE_SPEED, self.vel_x - 0.2)
        elif keys[pygame.K_RIGHT]:
            self.vel_x = min(MOVE_SPEED, self.vel_x + 0.2)
        else:
            self.vel_x *= 0.8  # Friction

        # Jumping with variable height [[3]]
        if keys[pygame.K_SPACE]:
            if not self.on_ground:
                self.vel_y = min(MAX_FALL_SPEED, self.vel_y + 0.1)  # Short jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = JUMP_POWER
            self.on_ground = False

        # Apply gravity [[4]]
        self.vel_y = min(MAX_FALL_SPEED, self.vel_y + GRAVITY)
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y

        # Ground/platform collision
        self.on_ground = False
        if self.y > 500:
            self.y = 500
            self.vel_y = 0
            self.on_ground = True

        # Screen boundaries
        self.x = max(0, min(770, self.x))

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = -1
        self.active = True

    def update(self):
        self.x += self.vel_x
        if random.random() < 0.01:
            self.vel_x *= -1
            
        # Simple platform collision
        if self.y > 500:
            self.y = 500
            self.vel_x *= 1.1  # Speed up when hitting ground

class Platform:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = random.randint(100, 200)
        self.active = True

class Collectible:
    def __init__(self, x, y, type='coin'):
        self.x = x
        self.y = y
        self.type = type
        self.bounce = 0
        self.active = True

player = Player()
enemies = [Enemy(600, 470) for _ in range(3)]
platforms = [Platform(100, 400), Platform(400, 300), Platform(600, 200)]
coins = [Collectible(p.x + p.width//2, p.y-20) for p in platforms]
powerups = [Collectible(400, 470, 'mushroom')]

def check_collision(a, b, size=30):
    return (a.x < b.x + 30 and a.x + size > b.x and 
            a.y < b.y + 30 and a.y + size > b.y)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    player.update(keys)
    
    screen.fill((135, 206, 235))  # Sky blue background
    
    # Update and draw platforms
    for platform in platforms:
        pygame.draw.rect(screen, (165, 42, 42), (platform.x, platform.y, platform.width, 20))
        # Platform collision
        if (player.y + 30 >= platform.y and player.y + 30 <= platform.y + 10 and 
            player.x + 15 > platform.x and player.x + 15 < platform.x + platform.width):
            player.y = platform.y - 30
            player.vel_y = 0
            player.on_ground = True

    # Update and draw enemies
    for enemy in enemies:
        if enemy.active:
            enemy.update()
            pygame.draw.circle(screen, (0, 0, 0), (int(enemy.x), int(enemy.y)), 15)
            pygame.draw.circle(screen, (255, 0, 0), (int(enemy.x), int(enemy.y)), 15, 1)
            
            # Enemy collision
            if check_collision(player, enemy):
                if player.y + 30 < enemy.y + 15:
                    enemy.active = False
                    player.score += 100
                else:
                    player.lives -= 1
                    player.x, player.y = 100, 300
                    player.vel_x = player.vel_y = 0

    # Update and draw collectibles
    for item in coins + powerups:
        if item.active:
            item.y += item.bounce
            item.bounce += 0.1
            if item.y > 500:
                item.y = 500
                item.bounce = -abs(item.bounce) * 0.5
                
            if item.type == 'coin':
                pygame.draw.circle(screen, (255, 255, 0), (int(item.x), int(item.y)), 8)
            else:
                pygame.draw.rect(screen, (255, 0, 0), (int(item.x)-10, int(item.y)-10, 20, 20))
                
            if check_collision(player, item):
                item.active = False
                if item.type == 'coin':
                    player.score += 10
                else:
                    player.powered_up = True

    # Draw ground
    pygame.draw.rect(screen, (34, 139, 34), (0, 520, 800, 80))
    
    # Draw Mario as a colored rectangle [[1]]
    color = (255, 0, 0) if not player.powered_up else (0, 0, 255)
    size = 30 if not player.powered_up else 40
    pygame.draw.rect(screen, color, (int(player.x), int(player.y), size, size))
    
    # Draw score and lives
    score_text = font.render(f"Score: {player.score}", True, (0, 0, 0))
    lives_text = font.render(f"Lives: {player.lives}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (650, 10))
    
    pygame.display.flip()
    clock.tick(60)
