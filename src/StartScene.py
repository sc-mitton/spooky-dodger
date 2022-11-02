import pygame
from pyghelpers import Scene
from pygame.locals import MOUSEBUTTONDOWN

import sys

from widgets.widgets import SpriteSheetAnimation
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, BASEPATH, PLAYING_HEIGHT, \
    TEXT_DARK, PINK_SKY


class StartScene(Scene):
    def __init__(self, window):

        # World
        self.window = window
        self.sceneKey = self.__class__.__name__
        self.fadein = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.fadein.fill(PINK_SKY)
        self.opacity = 255

        # Setup the backgruond
        self.background_far = pygame.image.load(
            BASEPATH / "media" / "background_far.gif"
        )
        self.background_near = pygame.image.load(
            BASEPATH / "media" / "background_near.png"
        )

        # Initiate the witch characters and sprite group
        self.agnes = SpriteSheetAnimation(
            self.window, ((WINDOW_WIDTH//2)-96, (PLAYING_HEIGHT//2)-64),
            BASEPATH / "media" / "agnes.png", 12, 48, 64, .2, [11, 10, 9, 10],
            loop=True, auto_start=True
        )
        self.glinda = SpriteSheetAnimation(
            self.window, ((WINDOW_WIDTH//2)+48, (PLAYING_HEIGHT//2)-64),
            BASEPATH / "media" / "glinda.png", 12, 48, 64, .2, [11, 10, 9, 10],
            loop=True, auto_start=True
        )
        self.witches = pygame.sprite.Group([self.agnes, self.glinda])

        # Text
        self.retro_font = pygame.font.Font(
            BASEPATH / "media" / "Retrograde-Regular.otf", 16
        )
        self.pick_message = self.retro_font.render(
            "CHOOSE YOUR CHARACTER", 1, TEXT_DARK
        )
        self.pick_message_rect = self.pick_message.get_rect()
        self.pick_message_rect.center = (
            WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 20
        )

    def getSceneKey(self):
        return self.sceneKey

    def handleInputs(self, events, keyPressedList):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                mouse_loc = pygame.mouse.get_pos()
                if self.glinda.rect.collidepoint(mouse_loc):
                    self.character = "Glinda"
                    self.goToScene("MainScene", {"name": "Glinda"})
                elif self.agnes.rect.collidepoint(mouse_loc):
                    self.character = "Agnes"
                    self.goToScene("MainScene", {"name": "Agnes"})

        # Fade in first screen
        self.opacity += -5
        self.fadein.set_alpha(self.opacity)

    def update(self):
        self.witches.update()

    def draw(self):
        self.window.blit(self.background_far, (0, 0))
        self.window.blit(self.background_near, (0, 0))
        self.witches.draw(self.window)
        self.window.blit(self.pick_message, self.pick_message_rect)
        self.window.blit(self.fadein, (0, 0))
