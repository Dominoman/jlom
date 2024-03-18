import sys

import pygame

from game import Midnight
from screens import SplashScreen, Font, Color, ShieldSet, Entity


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("pLom")
        self.surface = pygame.display.set_mode((512, 425))
        self.clock = pygame.time.Clock()
        self.game = Midnight.get_instance()
        self.current_screen = SplashScreen(self, self.game)
        with open("data\\fontData","rb") as fo:
            self.font=Font.make_font(fo)
        with open("data\\shieldFontData","rb") as fo:
            self.shields=ShieldSet.make_shields(fo)
        with open("data\\entityFontData","rb") as fo:
            pass

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.current_screen.update()
            self.current_screen.draw(self.surface)
            for i in range(10):
                self.shields[i].draw(self.surface,i*5,0)
            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    game = Game()
    game.run()
