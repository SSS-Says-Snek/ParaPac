import pygame
import os
import sys

from src import common, tiles, utils
from src.world import World
from src.interrupt import *
from src.player import Player
from src.ghost import Ghost
from src.gui import Dashboard


def setup():
    pygame.display.set_caption("ParaPac - Pygame Community Summer Team Jam")

    common.maps = [
        (World(os.path.join("maps", "map_a.txt")), (0, 32, 64), "map_a.txt"),
        (World(os.path.join("maps", "map_b.txt")), (64, 0, 0), "map_b.txt")
    ]

    common.player = Player(19, 29)
    common.active_map_id = 0
    common.active_map = common.maps[common.active_map_id][0]
    common.dashboard = Dashboard()
    for dimension, _bg, _file in common.maps:
        dimension.entities.append(common.player)


def gameplay_events():
    pygame.display.flip()
    common.fps = 1000 / common.clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise GameExit
        elif event.type == pygame.MOUSEWHEEL and common.DEBUG:
            common.player.debug_tile -= event.y
            common.player.debug_tile %= len(tiles.TILE_DICT)
        elif event.type == pygame.KEYDOWN:
            # Toggles debug mode
            if event.key == pygame.K_F1:
                common.DEBUG = not common.DEBUG
            # Changes the map dimension
            elif event.key == pygame.K_p:
                common.transitioning_mode = common.Transition.FADING
                common.alpha = 255

            elif common.DEBUG:
                # Saves the map
                if event.key == pygame.K_F2:
                    with open(os.path.join("maps",
                                           common.maps[common.active_map_id][2]), "w") as f:
                        f.write(common.active_map.save())
                # Toggles freezing the world
                elif event.key == pygame.K_F3:
                    common.DEBUG_FREEZE = not common.DEBUG_FREEZE


def gameplay_map():
    common.active_map.update()
    game_surf = world = common.active_map.render()

    if not common.DEBUG:
        dashboard = common.dashboard.render(world.get_width())
        game_surf = pygame.Surface((world.get_width(), world.get_height() + dashboard.get_height()))
        game_surf.fill(common.maps[common.active_map_id][1])
        game_surf.blit(dashboard, (0, 0))
        game_surf.blit(world, (0, dashboard.get_height()))

    common.window.fill(common.maps[common.active_map_id][1])
    ratio = game_surf.get_width() / game_surf.get_height()
    if common.window.get_width() > ratio * common.window.get_height():
        common.map_area_width = int(ratio * common.window.get_height())
        common.map_area_height = int(common.window.get_height())
        common.map_area_x = (common.window.get_width() - common.map_area_width) // 2
        common.map_area_y = 0
    else:
        common.map_area_width = int(common.window.get_width())
        common.map_area_height = int(common.window.get_width() / ratio)
        common.map_area_x = 0
        common.map_area_y = (common.window.get_height() - common.map_area_height) // 2

    world = pygame.transform.scale(game_surf, (common.map_area_width, common.map_area_height))

    if common.transitioning_mode != common.Transition.NOT_TRANSITIONING:
        world.set_alpha(common.alpha)
        if common.transitioning_mode == common.Transition.FADING:
            common.alpha -= 5
        elif common.transitioning_mode == common.Transition.REAPPEARING:
            common.alpha += 5

        if common.alpha < 0:
            common.transitioning_mode = common.Transition.REAPPEARING
            common.active_map_id = (common.active_map_id + 1) % len(common.maps)
            common.active_map = common.maps[common.active_map_id][0]

        if common.alpha == 255:
            common.transitioning_mode = common.Transition.NOT_TRANSITIONING

    common.window.blit(world, (common.map_area_x, common.map_area_y))


def gameplay_loop():
    gameplay_events()
    gameplay_map()

    if common.DEBUG:
        mx, my = pygame.mouse.get_pos()
        x, y = utils.to_world_space(mx, my)

        common.window.blit(common.font.render(
            f"FPS: {int(common.fps)}; "
            f"X: {int(x)}; Y: {int(y)}; "
            f"Block: {tiles.TILE_DICT[common.player.debug_tile]}",
            False, (255, 255, 255), (0, 0, 0)
        ).convert_alpha(), (0, 0))


def main():
    while True:
        try:
            gameplay_loop()
        except GameExit:
            sys.exit(0)
        except GamePaused:
            pass
        except GameRetry:
            pass
        except GameOver:
            pass


if __name__ == "__main__":
    setup()
    main()
