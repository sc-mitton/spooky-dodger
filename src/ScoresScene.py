import pygame
from pyghelpers import Scene

import sys

from constants import BASEPATH


class ScoresScene(Scene):

    def __init__(self, window):
        self.sceneKey = self.__class__.__name__
        self.window = window

        self.background_far = pygame.image.load(
            BASEPATH / "media" / "background_far.gif"
        )
        self.background_near = pygame.image.load(
            BASEPATH / "media" / "background_near.png"
        )

    def getSceneKey(self):
        return self.sceneKey

    def handleInputs(self, events, keyPressedList):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def update(self):
        return

    def draw(self):
        self.window.blit(self.background_far, (0, 0))
        self.window.blit(self.background_near, (0, 0))
