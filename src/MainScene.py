import pygame
from pyghelpers import Scene

import random
import time

from widgets.widgets import SpriteSheetAnimation
from constants import BASEPATH, TEXT_LIGHT, WINDOW_WIDTH, WINDOW_HEIGHT, \
    PLAYING_HEIGHT


class MainScene(Scene):

    def __init__(self, window):
        # World
        self.sceneKey = self.__class__.__name__
        self.window = window
        self.gravity = 2
        self.init_bat_speed = 1
        self.agnes_speed = 3
        self.background_speed = 1
        self.score = 0

        # Text
        self.retro_font = pygame.font.Font(BASEPATH / "media" /
                                           "Retrograde-Regular.otf", 14)
        self.score_text = self.retro_font.render(str(self.score), 1,
                                                 TEXT_LIGHT)

        # Sounds / Music
        self.blip = pygame.mixer.Sound(BASEPATH / "media" / "blip.wav")
        self.scream = pygame.mixer.Sound(BASEPATH / "media" / "scream.mp3")
        self.background_music = pygame.mixer.music.load(
            BASEPATH / "media" / "ES_HAUNTED Playhouse - Stationary Sign.mp3"
        )
        pygame.mixer.music.play(-1)

        # Background
        # Load the near and far background scenes
        self.scene_far1 = pygame.image.load(
            BASEPATH / "media" / "background_far.gif"
        ).convert()
        self.scene_near1 = pygame.image.load(
            BASEPATH / "media" / "background_near.png"
        ).convert_alpha()
        self.scene_far2 = pygame.image.load(
            BASEPATH / "media" / "background_far.gif"
        ).convert()
        self.scene_near2 = pygame.image.load(
            BASEPATH / "media" / "background_near.png"
        ).convert_alpha()

        # Size of background images
        self.background_size = self.scene_far1.get_size()

        # Get the rects for the background images
        self.scene_far1_rect = self.scene_far1.get_rect()
        self.scene_near1_rect = self.scene_near1.get_rect()
        self.scene_far2_rect = self.scene_far2.get_rect()
        self.scene_near2_rect = self.scene_near2.get_rect()

        # Position the background scenes next to eachother
        self.scene_far1_rect.topleft = (0, 0)
        self.scene_near1_rect.topleft = (0, 0)
        self.scene_far2_rect.topleft = (-self.background_size[0], 0)
        self.scene_near2_rect.topleft = (-self.background_size[0], 0)

        # Boundaries
        self.bat_boundary = pygame.Rect(
            -33, 0, WINDOW_WIDTH + 32, PLAYING_HEIGHT
        )
        self.game_boundary = pygame.Rect(0, 0, WINDOW_WIDTH, PLAYING_HEIGHT)

        # Witch characters
        self.agnes = pygame.image.load(
            BASEPATH / "media" / "agnes_no_shadow.png"
        )
        subsurface_rect = pygame.Rect(96, 192, 48, 64)
        self.agnes = self.agnes.subsurface(subsurface_rect)
        self.agnes_rect = self.agnes.get_rect()
        self.agnes_rect.center = (
            3*WINDOW_WIDTH//4, PLAYING_HEIGHT//2
        )

        self.glinda = pygame.image.load(
            BASEPATH / "media" / "glinda_no_shadow.png"
        )
        self.glinda = self.glinda.subsurface(subsurface_rect)
        self.glinda_rect = self.glinda.get_rect()
        self.glinda_rect.center = (3*WINDOW_WIDTH//4, PLAYING_HEIGHT//2)

        # User defined events
        self.FIRST_BATS = pygame.USEREVENT + 0
        self.first_bats = pygame.event.Event(self.FIRST_BATS)
        pygame.time.set_timer(self.first_bats, 3000, 3)
        self.NEW_BAT = pygame.USEREVENT + 1
        self.new_bat = pygame.event.Event(self.NEW_BAT)
        pygame.time.set_timer(self.new_bat, 15000)
        self.MOVE_BATS = pygame.USEREVENT + 2
        self.move_bats = pygame.event.Event(self.MOVE_BATS)
        self.move_bats_time = 14
        pygame.time.set_timer(self.move_bats, self.move_bats_time)
        self.SPEED_UP = pygame.USEREVENT + 3
        self.speed_up = pygame.event.Event(self.SPEED_UP)
        self.speed_up_time = 22000
        pygame.time.set_timer(self.speed_up, self.speed_up_time)
        self.MOVE_BACK = pygame.USEREVENT + 4
        self.move_back = pygame.event.Event(self.MOVE_BACK)
        self.move_back_time = 70
        pygame.time.set_timer(self.move_back, self.move_back_time)

        # Enemies
        self.bat_animation = SpriteSheetAnimation(
                        self.window,
                        (-32, random.randrange(0, PLAYING_HEIGHT, 32)),
                        BASEPATH / "media" / "bat.32x32.gif",
                        5, 32, 32, .1, bak_color=(255, 0, 255),
                        flip=(1, 0), loop=True, auto_start=True
        )
        self.bats = pygame.sprite.Group()
        self.bats.add(self.bat_animation)

    def enter(self, data):
        """Set the witch to be the character that was selected in the
        start scene
        """

        if data["name"] == "Glinda":
            self.witch = self.glinda
            self.witch_rect = self.glinda_rect
        elif data["name"] == "Agnes":
            self.witch = self.agnes
            self.witch_rect = self.agnes_rect

    def getSceneKey(self):
        """Return the scene key"""
        return self.sceneKey

    def handleInputs(self, events, keyPressedList):
        """Create any new bats, move the witch,
        and see if the witch has colided with a bat"""

        for event in events:

            if event.type == self.FIRST_BATS:
                bat_animation = SpriteSheetAnimation(
                        self.window,
                        (-32, random.randrange(0, PLAYING_HEIGHT-32, 32)),
                        BASEPATH / "media" / "bat.32x32.gif",
                        5, 32, 32, .1, bak_color=(255, 0, 255),
                        flip=(1, 0), loop=True, auto_start=True
                )
                self.bats.add(bat_animation)

            # Move the bats along & check for collision with the witch
            if event.type == self.MOVE_BATS:
                bat_sprites = pygame.sprite.Group.sprites(self.bats)
                for bat_sprite in bat_sprites:
                    if bat_sprite.overlaps_rect(self.bat_boundary):
                        bat_sprite.move_x(self.init_bat_speed)
                        if bat_sprite.rect.bottom < PLAYING_HEIGHT and \
                           bat_sprite.rect.top > 0:
                            bat_sprite.move_y(random.choice((-1, 0, 1)))
                    else:
                        bat_sprite.loc = (
                            -32, random.randrange(0, PLAYING_HEIGHT-32, 32)
                        )
                        self.score += 1
                        self.score_text = self.retro_font.render(
                                                str(self.score), 1, TEXT_LIGHT
                                          )
                    if self.witch_rect.collidepoint(bat_sprite.rect.center):
                        self.scream.play()
                        pygame.mixer.music.fadeout(50)
                        time.sleep(1)
                        self.goToScene("ScoresScene")

            # Add another bat to make the game harder
            if event.type == self.NEW_BAT:
                if len(pygame.sprite.Group.sprites(self.bats)) < 7:
                    bat_animation = SpriteSheetAnimation(
                            self.window,
                            (-32, random.randrange(0, PLAYING_HEIGHT-32, 32)),
                            BASEPATH / "media" / "bat.32x32.gif",
                            5, 32, 32, .1, bak_color=(255, 0, 255),
                            flip=(1, 0), loop=True, auto_start=True
                    )
                    self.bats.add(bat_animation)

            # Speed Up Bats
            if event.type == self.SPEED_UP:
                if self.move_bats_time > 5:
                    self.move_bats_time += -2
                    pygame.time.set_timer(self.move_bats, self.move_bats_time)
                    self.agnes_speed += 1

            # Witch sound effects
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.blip.play()
                if event.key == pygame.K_LEFT:
                    self.blip.play()
                if event.key == pygame.K_RIGHT:
                    self.blip.play()

            # Scroll the background
            if event.type == self.MOVE_BACK:
                if self.scene_far1_rect.left < WINDOW_WIDTH:
                    self.scene_far1_rect.left = self.scene_far1_rect.left + \
                        self.background_speed
                else:
                    self.scene_far1_rect.topleft = \
                        (-self.background_size[0], 0)

                if self.scene_far2_rect.left < WINDOW_WIDTH:
                    self.scene_far2_rect.left = self.scene_far2_rect.left + \
                        self.background_speed
                else:
                    self.scene_far2_rect.topleft = \
                        (-self.background_size[0], 0)

                if self.scene_near1_rect.left < WINDOW_WIDTH:
                    self.scene_near1_rect.left = self.scene_near1_rect.left + \
                        self.background_speed*2
                else:
                    self.scene_near1_rect.topleft = \
                        (-self.background_size[0]+2, 0)

                if self.scene_near2_rect.left < WINDOW_WIDTH:
                    self.scene_near2_rect.left = self.scene_near2_rect.left + \
                        self.background_speed*2
                else:
                    self.scene_near2_rect.topleft = \
                        (-self.background_size[0]+2, 0)

        # Move the character
        if keyPressedList[pygame.K_UP]:
            if self.witch_rect.top > 0:
                self.witch_rect.top += -self.agnes_speed
        else:
            if self.witch_rect.bottom < PLAYING_HEIGHT:
                self.witch_rect.top += self.gravity
        if keyPressedList[pygame.K_RIGHT]:
            if self.witch_rect.right < WINDOW_WIDTH:
                self.witch_rect.left += self.agnes_speed
        elif keyPressedList[pygame.K_LEFT]:
            if self.witch_rect.left > 2*WINDOW_WIDTH//3:
                self.witch_rect.left += -self.agnes_speed

    def draw(self):
        """Draw the window elements"""
        self.window.blit(self.scene_far1, self.scene_far1_rect)
        self.window.blit(self.scene_far2, self.scene_far2_rect)
        self.window.blit(self.scene_near1, self.scene_near1_rect)
        self.window.blit(self.scene_near2, self.scene_near2_rect)

        self.window.blit(
            self.score_text,
            (WINDOW_WIDTH-40, WINDOW_HEIGHT-20)
        )
        self.bats.draw(self.window)
        self.window.blit(self.witch, self.witch_rect)

    def update(self):
        """Update the bats"""
        self.bats.update()
