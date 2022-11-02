# Standard
from pyghelpers import SceneMgr
import pygame

from constants import WINDOW_WIDTH, WINDOW_HEIGHT, FRAME_RATE
from MainScene import MainScene
from ScoresScene import ScoresScene
from StartScene import StartScene


def run():

    # Establish World
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Spooky Dodger")

    # Build scene manager
    main_scene = MainScene(window)
    scores_scene = ScoresScene(window)
    start_scene = StartScene(window)

    scenes_list = [start_scene, main_scene, scores_scene]
    scene_manager = SceneMgr(scenes_list, FRAME_RATE)

    scene_manager.run()


if __name__ == '__main__':
    run()
