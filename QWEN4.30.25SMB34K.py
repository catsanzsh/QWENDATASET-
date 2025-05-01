import pygame
import sys
import random

# SMB3 GBA Palette [[3]]
PALETTE = {
    'sky_blue': (135, 206, 235),
    'grass_green': (34, 139, 34),
    'brick_brown': (139, 69, 19),
    'mountain_gray': (192, 192, 192),
    'mario_red': (205, 0, 0),
    'coin_gold': (255, 215, 0),
    'pipe_green': (152, 209, 89),
    'cloud_white': (245, 245, 220),
    'powerup_red': (255, 0, 0),
    'powerup_white': (255, 255, 255)
}

# Game constants
TILE_SIZE = 40
MAP_WIDTH = 20
MAP_HEIGHT = 20
GRAVITY = 0.15
MOVE_SPEED = 3.0

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Enhanced Tile Types [[3]][[6]]
TILE_TYPES = {
    0: ('Grass', PALETTE['grass_green']),
    1: ('Path', PALETTE['brick_brown']),
    2: ('Mountain', PALETTE['mountain_gray']),
    3: ('Entrance', PALETTE['powerup_red']),
    4: ('Brick', PALETTE['brick_brown']),
    5: ('Pipe', PALETTE['pipe_green']),
    6: ('CoinBlock', PALETTE['coin_gold']),
    7: ('Empty', (0,0,0))
}

class Map:
    def __init__(self):
        self.tiles = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        self.clouds = []
        self.generate_gb_tiles()
        
    def generate_gb_tiles(self):
        # Create SMB3-style environment
        for row in range(MAP_HEIGHT):
            for col in range(MAP_WIDTH):
                if row == MAP_HEIGHT-1 or col in (0, MAP_WIDTH-1):
                    self.tiles[row][col] = 2  # Mountains
                if row == 10:
                    self.tiles[row][col] = 1  # Path
                # Add bricks and pipes
                if row == 9 and col % 4 == 0:
                    self.tiles[row][col] = 4  # Bricks
                if random.random() < 0.05:
                    self.tiles[random.randint(0,18)][random.randint(0,19)] = 5  # Pipes
                if row == 8 and col % 6 == 0:
                    self.tiles[row][col] = 6  # Coin blocks

        # Pre-generate cloud positions [[3]]
        self.clouds = [(random.randint(0, 800), random.randint(50, 200)) for _ in range(5)]

    def get_tile(self, x, y):
        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)
        if 0 <= tile_x < MAP_WIDTH and 0 <= tile_y < MAP_HEIGHT:
            return self.tiles[tile_y][tile_x]
        return 7  # Treat out of bounds as empty

class Player:
    def __init__(self):
        self.x = 200
        self.y = 200
        self.vel_x = 0
        self.vel_y = 0
        self.size = 30
        self.powerup = False
        self.blink_counter = 0
        self.score = 0

    def draw(self, camera_x, camera_y):
        # SMB3 Mario rendering [[6]]
        mario_color = PALETTE['powerup_red'] if self.powerup else PALETTE['mario_red']
        pygame.draw.rect(screen, mario_color, 
                        (self.x - camera_x, self.y - camera_y, self.size, self.size))
        
        # Add hat and details
        pygame.draw.rect(screen, PALETTE['powerup_white'], 
                        (self.x - camera_x + 5, self.y - camera_y - 10, 
                         self.size-10, 5))  # Hat
        
        # Blinking effect [[3]]
        if self.blink_counter > 0:
            self.blink_counter -= 1
            return
        pygame.draw.circle(screen, PALETTE['powerup_white'], 
                          (int(self.x + self.size/2 - camera_x), 
                           int(self.y + self.size/2 - camera_y)), 3)  # Highlight

    def update(self, keys, map):
        # Movement [[2]]
        acceleration = 0.1
        friction = 0.8
        if keys[pygame.K_LEFT]:
            self.vel_x = max(-MOVE_SPEED, self.vel_x - acceleration)
        elif keys[pygame.K_RIGHT]:
            self.vel_x = min(MOVE_SPEED, self.vel_x + acceleration)
        else:
            self.vel_x *= friction

        # Jumping [[6]]
        self.vel_y += GRAVITY
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -6 if self.powerup else -5.5

        prev_x, prev_y = self.x, self.y
        self.x += self.vel_x
        self.y += self.vel_y

        # Collision detection with all tiles [[3]]
        self.on_ground = False
        for dx in (0, self.size):
            for dy in (0, self.size):
                x = self.x + dx
                y = self.y + dy
                tile = map.get_tile(x, y)
                if tile in [2,4,5,6]:  # Solid tiles
                    self.x, self.y = prev_x, prev_y
                    break
                if tile != 0 and dy > 0:  # Check for ground
                    self.on_ground = True

        # Powerup activation [[6]]
        tile_under = map.get_tile(self.x + self.size//2, self.y + self.size)
        if tile_under == 3 and not self.powerup:
            self.powerup = True
            self.size = 40
            self.score += 100
            # Mark entrance as used
            row = int((self.y + self.size//2) // TILE_SIZE)
            col = int((self.x + self.size//2) // TILE_SIZE)
            map.tiles[row][col] = 7  # Remove entrance

        # Coin block interaction [[6]]
        if map.get_tile(self.x + self.size//2, self.y + self.size//2) == 6:
            self.score += 50
            # Mark as broken
            row = int((self.y + self.size//2) // TILE_SIZE)
            col = int((self.x + self.size//2) // TILE_SIZE)
            map.tiles[row][col] = 7

        # Boundary clamping
        self.x = max(0, min(MAP_WIDTH*TILE_SIZE - self.size, self.x))
        self.y = max(0, min(MAP_HEIGHT*TILE_SIZE - self.size, self.y))

def draw_smb3_elements(map, camera_x, camera_y):
    # Clouds [[3]]
    for cx, cy in map.clouds:
        pygame.draw.circle(screen, PALETTE['cloud_white'], (cx - camera_x, cy - camera_y), 20)
        pygame.draw.circle(screen, PALETTE['cloud_white'], (cx+20 - camera_x, cy-10 - camera_y), 20)
        
    # Pipes [[5]]
    for row in range(MAP_HEIGHT):
        for col in range(MAP_WIDTH):
            if map.tiles[row][col] == 5:
                pipe_x = col*TILE_SIZE
                pipe_y = row*TILE_SIZE
                # Draw pipe shape
                pygame.draw.rect(screen, PALETTE['pipe_green'], 
                                (pipe_x - camera_x, pipe_y - camera_y, 
                                 TILE_SIZE, TILE_SIZE*2))
                pygame.draw.circle(screen, PALETTE['pipe_green'], 
                                  (pipe_x + TILE_SIZE/2 - camera_x, 
                                   pipe_y - camera_y), 
                                  TILE_SIZE, 0)

    # Coin blocks [[6]]
    for row in range(MAP_HEIGHT):
        for col in range(MAP_WIDTH):
            if map.tiles[row][col] == 6:
                block_x = col*TILE_SIZE
                block_y = row*TILE_SIZE
                pygame.draw.rect(screen, PALETTE['coin_gold'], 
                                (block_x - camera_x, block_y - camera_y, 
                                 TILE_SIZE, TILE_SIZE))
                coin_x = block_x + TILE_SIZE/2
                coin_y = block_y + TILE_SIZE/2
                pygame.draw.circle(screen, PALETTE['coin_gold'], 
                                  (int(coin_x - camera_x), 
                                   int(coin_y - camera_y)), 8)
                pygame.draw.circle(screen, PALETTE['powerup_white'], 
                                  (int(coin_x - camera_x), 
                                   int(coin_y - camera_y)), 3)

def main():
    map = Map()
    player = Player()
    camera_x = 0
    camera_y = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        player.update(keys, map)
        
        # Camera system [[3]]
        camera_x = player.x - 400  
        camera_y = player.y - 300  
        camera_x = max(0, min(camera_x, (MAP_WIDTH*TILE_SIZE) - 800))
        camera_y = max(0, min(camera_y, (MAP_HEIGHT*TILE_SIZE) - 600))

        screen.fill(PALETTE['sky_blue'])  # [[3]]
        
        # Draw core tiles
        for row in range(MAP_HEIGHT):
            for col in range(MAP_WIDTH):
                tile_type = map.tiles[row][col]
                if tile_type ==7: continue  # Skip empty tiles
                color = TILE_TYPES[tile_type][1]
                x = col*TILE_SIZE - camera_x
                y = row*TILE_SIZE - camera_y
                if (x < 800 and y < 600 and 
                    x + TILE_SIZE > 0 and y + TILE_SIZE > 0):
                    pygame.draw.rect(screen, color, 
                                    (x, y, TILE_SIZE, TILE_SIZE))

        # Draw SMB3 elements
        draw_smb3_elements(map, camera_x, camera_y)
        
        # Draw player with enhanced rendering
        player.draw(camera_x, camera_y)  
        
        # Draw UI
        score_text = font.render(f"Score: {player.score}", True, (0,0,0))
        screen.blit(score_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
