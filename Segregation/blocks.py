
import pygame
# See https://github.com/pygame/pygame/blob/master/src_py/colordict.py for THECOLORS names.
from pygame.colordict import THECOLORS
from pygame.rect import Rect
from pygame.sprite import collide_rect, Sprite
from pygame.surface import Surface
from pygame.time import Clock

from random import randint


class Block(Sprite):

    block_size = 20

    def __init__(self, screen_rect, color=(255, 255, 255, 255)):
        super().__init__()
        self.idle_color = color  # white - if not colliding
        self.hit_color = (0, 255, 0, 255)  # green - if colliding

        block_x = randint(0, screen_rect.w - Block.block_size)
        block_y = randint(0, screen_rect.h - Block.block_size)
        block_rect = Rect(block_x, block_y, Block.block_size, Block.block_size)

        self.image = Surface((block_rect.w, block_rect.h))
        self.color = self.idle_color  # default
        # Do NOT set color here, decided by collision status!
        self.rect = block_rect


class Player(Block):

    def __init__(self, screen_rect):
        super().__init__(screen_rect, color=(255, 0, 0, 255))
        self.image.fill(self.color)


class World(object):

    def __init__(self, screen_rect, num_blocks=50):

        self.player = Player(screen_rect)
        self.blocks = [Block(screen_rect) for _ in range(num_blocks)]
        self.elements = self.blocks + [self.player]
        self.screen_rect = screen_rect

        # hard-coded player x and y speed for bouncing around
        self.player_speed_x = 1
        self.player_speed_y = 1

    # Bounces player off the screen edges
    # Simply dummy method - no collisions here!
    def move_player(self):
        p_rect = self.player.rect
        if p_rect.right >= self.screen_rect.right or p_rect.left <= self.screen_rect.left:
            self.player_speed_x *= -1
        if p_rect.top <= self.screen_rect.top or p_rect.bottom >= self.screen_rect.bottom:
            self.player_speed_y *= -1
        # move_ip is move in place.
        p_rect.move_ip(self.player_speed_x, self.player_speed_y)  # modifies IN PLACE!

    def update(self):
        self.move_player()
        for block in self.blocks:
            block.color = block.hit_color if collide_rect(block, self.player) else block.idle_color


class Game:

    def __init__(self):
        pygame.init()

        self.width = 800
        self.height = 800
        self.fps = 60
        self.color = THECOLORS['black']  # (0, 120, 120, 255)  # gray background

        self.screen = pygame.display.set_mode((self.width, self.height))
        title = "Collision Test"
        pygame.display.set_caption(title)
        self.world = World(self.screen.get_rect())

        self.clock = Clock( )


    # Clear screen with background color, then draw blocks, then draw player on top. Then update the actual display.
    def draw(self, blocks):
        self.screen.fill(self.color)
        for block in blocks:
            # update fill to color decided by handle_collisions function...
            block.image.fill(block.color)
            self.screen.blit(block.image, block.rect)

        pygame.display.update()

    def run_game(self):
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return

            self.world.update()
            self.draw(self.world.elements)
            self.clock.tick(self.fps)


if __name__ == "__main__":
    Game().run_game()
