import pygame
import sys

# Constants from SMB3 physics [[2]]
GRAVITY = 0.3
MAX_FALL_SPEED = 4.0
JUMP_POWER = -5.5
MOVE_SPEED = 2.0

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

class Player:
    def __init__(self):
        self.x = 100
        self.y = 300
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

    def update(self, keys):
        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.vel_x = max(-MOVE_SPEED, self.vel_x - 0.2)
        elif keys[pygame.K_RIGHT]:
            self.vel_x = min(MOVE_SPEED, self.vel_x + 0.2)
        else:
            self.vel_x *= 0.8  # Friction

        # Jumping
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = JUMP_POWER
            self.on_ground = False

        # Apply gravity
        self.vel_y = min(MAX_FALL_SPEED, self.vel_y + GRAVITY)
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y

        # Ground collision
        if self.y > 500:
            self.y = 500
            self.vel_y = 0
            self.on_ground = True

player = Player()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    player.update(keys)
    
    screen.fill((135, 206, 235))  # Sky blue background
    
    # Draw ground
    pygame.draw.rect(screen, (34, 139, 34), (0, 520, 800, 80))  # Forest green ground
    
    # Draw Mario as a red rectangle
    pygame.draw.rect(screen, (255, 0, 0), 
                    (int(player.x), int(player.y), 30, 30))  # Red block for Mario
    
    pygame.display.flip()
    clock.tick(60)  # Maintain 60 FPS
