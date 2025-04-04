try:
    import sys
    import random
    import math
    import os
    import getopt
    import pygame
    from socket import *
    from pygame.locals import *
except ImportError as err:
    print(f"couldn't load module. {err}")
    sys.exit(2)

    class Ball(pygame.sprite.Sprite):
        """A ball that will move across the screen
    Returns: ball object
    Functions: update, calcnewpos
    Entree: frequence contraction des muscle du mollet + mouvement (acceleration)
    Attributes: area, vector"""

    class Person(pygame.sprite.Sprite):
        """A personn that move horizontally and protect the goal
    Returns: person object,
    Functions: update, calcnewpos
    entree: frequence rythme cardiaque et respiration 
    Attributes: area, vector"""


    class Goal(pygame.sprite.Sprite):
            """Object fix qui doit indiquer si l'utilisateur à marqué 
    Returns:  goal object,
    Functions: update, calcnewpos
    entree: entreeBallon??
    Attributes: area, vector"""
    #essayer de la faire avec un true false /r colision goal ballon


    def __init__(self, vector):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('ball.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.vector = vector

    def update(self):
        newpos = self.calcnewpos(self.rect,self.vector)
        self.rect = newpos

    def calcnewpos(self,rect,vector):
        (angle,z) = vector
        (dx,dy) = (z*math.cos(angle),z*math.sin(angle))
        return rect.move(dx,dy)

def main():
    # Initialise screen
    pygame.init()
    screen = pygame.display.set_mode((150, 50))#change size
    pygame.display.set_caption('Basic Pygame program')

    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    # ajouter pygame.Color.g au background

    # Display some text
    font = pygame.font.Font(None, 36)
    text = font.render("Début de la séance ", 1, (10, 10, 10))
    # à mod
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    background.blit(text, textpos)

    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # Event loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return

        screen.blit(background, (0, 0))
        pygame.display.flip()


if __name__ == '__main__': main()