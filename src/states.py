import time

import pygame

from src import common, tiles, utils, powerup
from src.interrupt import *


class BaseState:
    def __init__(self):
        self.next_state = self.__class__

    def change_state(self, other_state):
        self.next_state = other_state


class MainGameState(BaseState):
    def __init__(self):
        super().__init__()

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL and common.DEBUG:
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
                    with open(common.PATH / "maps" / common.maps[common.active_map_id][2], "w") as f:
                        f.write(common.active_map.save())
                # Toggles freezing the world
                elif event.key == pygame.K_F3:
                    common.DEBUG_FREEZE = not common.DEBUG_FREEZE
                elif event.key == pygame.K_F9:
                    self.change_state(TestState)

    @staticmethod
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

    def run(self):
        common.fps = 1000 / common.clock.tick(60)

        self.gameplay_map()

        if common.DEBUG:
            mx, my = pygame.mouse.get_pos()
            x, y = utils.to_world_space(mx, my)

            common.window.blit(common.font.render(
                f"FPS: {int(common.fps)}; "
                f"X: {int(x)}; Y: {int(y)}; "
                f"Block: {tiles.TILE_DICT[common.player.debug_tile]}",
                False, (255, 255, 255), (0, 0, 0)
            ).convert_alpha(), (0, 0))


class ShopState(BaseState):
    def __init__(self):
        super().__init__()

        self.time_entered = time.perf_counter()
        self.store_items = [
            {
                "name": "Medkit",
                "summary": "Heal yes by 1",
                "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin risus in nisi gravida tincidunt in eu nisi. Vivamus in ligula ac massa congue blandit facilisis vel urna. Donec efficitur augue justo, in sollicitudin tortor auctor non. Phasellus id turpis auctor, lacinia orci ac, auctor justo.",
                "price": 15,
                "image": pygame.transform.scale(pygame.image.load(common.PATH / "assets/ghost.png"), (100, 100))
            }
            # {
            #     "name": "E",
            #     "summary": "E",
            #     "description": "E",
            #     "price": 69,
            #     "image": pygame.transform.scale(pygame.image.load(common.PATH / "assets/ghost.png"), (50, 50))
            # }
        ] * 9

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F9:
                exit_time = time.perf_counter()

                self.change_state(MainGameState)

                common.player.moved_after_shop_exit = False
                reconstructed_powerups = {}
                for power, data in powerup.powerups.items():
                    new_data = data[:]
                    if powerup.is_powerup_on(power):
                        new_data[1] = new_data[1] + exit_time - self.time_entered
                    reconstructed_powerups[power] = new_data
                powerup.powerups = reconstructed_powerups

    def run(self):
        common.window.fill((255, 255, 128))

        for i, item in enumerate(self.store_items):
            location_of_item = divmod(i, 4)
            w = common.window.get_width()
            h = common.window.get_height()
            common.window.blit(item['image'], (location_of_item[1] * w / 4 + 10/620*w, location_of_item[0] * (2/3*h) / 2 + 40/620*h))


class TestState(BaseState):
    def __init__(self):
        super().__init__()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F9:
                self.change_state(MainGameState)

    def run(self):
        common.window.fill((0, 0, 0))
