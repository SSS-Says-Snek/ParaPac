import time

import pygame
import copy

from src import common, tiles, utils, powerup, notification, items, entity
from src.ghost import Ghost
from src.interrupt import GameExit
from src.tiles import Tile


class BaseState:
    def __init__(self):
        self.next_state = self.__class__

        self.enter_state = time.perf_counter()

    def change_state(self, other_state):
        if other_state == MainGameState:
            common.transition_timer = time.perf_counter() - self.enter_state + common.transition_timer
        self.next_state = other_state


class MainGameState(BaseState):
    def __init__(self):
        super().__init__()

        powerup.add_powerup(powerup.PowerUp.IMMUNITY, 12)
        common.player.immune = True
        common.player.immunity_duration = powerup.powerups[powerup.PowerUp.IMMUNITY][1]
        common.player.immunity_timer = time.perf_counter()

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL and common.DEBUG:
            common.player.debug_tile -= event.y
            common.player.debug_tile %= len(tiles.TILE_DICT)
        elif event.type == pygame.KEYDOWN:
            # Toggles debug mode
            if event.key == pygame.K_F1:
                common.DEBUG = not common.DEBUG
                notification.new_notif(f"{'Enabled' if common.DEBUG else 'Disabled'} debug mode", 3, (255, 255, 0))
                for dimension, _bg, _file in common.maps:
                    dimension.render_world()
            # Changes the map dimension
            elif event.key == pygame.K_p:
                if common.DEBUG or time.perf_counter() - common.transition_timer > 25:
                    common.transitioning_mode = common.Transition.FADING
                    common.alpha = 255
                else:
                    notification.new_notif("Dimension travelling not ready!", 3)
            # Pause Game
            elif event.key == pygame.K_ESCAPE:
                powerup.pause()
                self.change_state(PauseState)

            # Saves the map
            if event.key == pygame.K_F2:
                if common.DEBUG:
                    with open(common.PATH / "maps" / common.maps[common.active_map_id][2], "w") as f:
                        f.write(common.active_map.save())
                    notification.new_notif(f"Saved {common.maps[common.active_map_id][2]}", 3, (255, 255, 0))
                else:
                    notification.new_notif("You must be on debug mode to save the map!", 3)
            # Toggles freezing the world
            elif event.key == pygame.K_F3:
                common.DEBUG_FREEZE = not common.DEBUG_FREEZE
                notification.new_notif(f"{'Froze' if common.DEBUG_FREEZE else 'Unfrozen'} the game", 3, (255, 255, 0))
            # Teleports behind a dimension
            elif event.key == pygame.K_F4:
                common.active_map_id = (common.active_map_id - 1) % len(common.maps)
                common.active_map = common.maps[common.active_map_id][0]
                notification.new_notif(f"Teleported to {common.maps[common.active_map_id][2]}", 3, (255, 255, 0))
            # Teleports ahead a dimension
            elif event.key == pygame.K_F5:
                common.active_map_id = (common.active_map_id + 1) % len(common.maps)
                common.active_map = common.maps[common.active_map_id][0]
                notification.new_notif(f"Teleported to {common.maps[common.active_map_id][2]}", 3, (255, 255, 0))

    @staticmethod
    def gameplay_map():
        common.active_map.update()
        game_surf = world = common.active_map.render()

        if common.transitioning_mode != common.Transition.NOT_TRANSITIONING:
            world.set_alpha(common.alpha)
            if common.transitioning_mode == common.Transition.FADING:
                common.alpha -= 10
            elif common.transitioning_mode == common.Transition.REAPPEARING:
                common.alpha += 10

            if common.alpha < 0:
                if common.player.direction in [entity.Direction.UP, entity.Direction.RIGHT]:
                    if common.active_map_id + 1 > len(common.maps):
                        notification.new_notif("There are no dimensions ahead!", 3)
                    else:
                        common.transitioning_mode = common.Transition.REAPPEARING
                        common.transition_timer = time.perf_counter()

                        common.active_map_id = (common.active_map_id + 1) % len(common.maps)
                        if common.active_map_id != len(common.maps) - 1:
                            notification.new_notif("Teleported ahead a dimension!", 3, (0, 255, 0))
                        else:
                            notification.new_notif("Teleported to boss dimension!", 3, (252, 157, 3))
                elif common.player.direction in [entity.Direction.DOWN, entity.Direction.LEFT]:
                    if common.active_map_id - 1 >= 0:
                        common.transitioning_mode = common.Transition.REAPPEARING
                        common.transition_timer = time.perf_counter()

                        common.active_map_id -= 1
                        notification.new_notif("Teleported behind a dimension!", 3, (0, 255, 0))
                    else:
                        common.transitioning_mode = common.Transition.REAPPEARING
                        notification.new_notif("There are no dimensions behind!", 3)
                common.active_map = common.maps[common.active_map_id][0]

            if common.alpha == 255:
                common.transitioning_mode = common.Transition.NOT_TRANSITIONING

                if not common.player.nudge(common.active_map, 0, 0) and \
                        not powerup.is_powerup_on(powerup.PowerUp.WALL_HAX) and not common.DEBUG:
                    common.player.task = common.player.die
                    common.transitioning_mode = common.Transition.NOT_TRANSITIONING

                    notification.new_notif("Can't teleport to that spot!", 3)

                    if common.player.direction in [entity.Direction.UP, entity.Direction.RIGHT]:
                        common.active_map_id = (common.active_map_id - 1) % len(common.maps)
                    elif common.player.direction in [entity.Direction.DOWN, entity.Direction.LEFT]:
                        common.active_map_id = (common.active_map_id + 1) % len(common.maps)
                    common.active_map = common.maps[common.active_map_id][0]

        if not common.DEBUG:
            dashboard = common.dashboard.render(world.get_width())
            game_surf = pygame.Surface((world.get_width(), world.get_height() + dashboard.get_height()))
            game_surf.fill(common.maps[common.active_map_id][1])
            game_surf.blit(dashboard, (0, 0))
            game_surf.blit(world, (0, dashboard.get_height()))

        common.window.fill(common.maps[common.active_map_id][1])

        game_surf, chords = utils.fit_to_screen(game_surf)
        common.map_area_x, common.map_area_y = chords
        common.map_area_width, common.map_area_height = game_surf.get_width(), game_surf.get_height()
        common.map_area_ratio = game_surf.get_width() / game_surf.get_height()
        common.window.blit(game_surf, chords)

    def run(self):
        common.fps = 1000 / common.clock.tick(60)

        self.gameplay_map()

        if common.DEBUG:
            mx, my = pygame.mouse.get_pos()
            x, y = utils.to_world_space(mx, my)

            common.window.blit(common.font.render(
                f"FPS: {int(common.fps)}; "
                f"Map: {common.maps[common.active_map_id][2]}; "
                f"X: {int(x)}; Y: {int(y)}; "
                f"Block: {tiles.TILE_DICT[common.player.debug_tile]}",
                False, (255, 255, 255), (0, 0, 0)
            ).convert_alpha(), (0, 0))
        pygame.display.update()


class ShopState(BaseState):
    def __init__(self):
        super().__init__()

        self.show_buy_screen = False
        self.normal_shop_alpha = 0
        self.focused_item = None

        self.screen_to_blit_surf = None
        self.buy_screen_surf = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F9:
                self.exit_shop()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = list(event.pos)
            mouse_pos[0] -= (common.window.get_width() - 620) // 2
            if not self.show_buy_screen:
                for i, item in enumerate(items.store_items):
                    try:
                        if item['rect'].collidepoint(mouse_pos):
                            print(f"CLICKED INDEX {i}")
                            self.normal_shop_alpha = 128
                            self.show_buy_screen = True
                            self.focused_item = item
                    except KeyError:
                        # Index 8 and above is not included because it is not on the same page (literally)
                        pass
            else:
                try:
                    if not self.buy_screen_rect.collidepoint(event.pos):
                        self.remove_buy_popup()
                    self.handle_buypopup_buttons(
                        (event.pos[0] - self.buy_screen_rect.x, event.pos[1] - self.buy_screen_rect.y))
                except AttributeError:
                    pass

            self.exit_shop_button.handle_event(event, mouse_pos=mouse_pos)

    def run(self):
        surf_to_blit = pygame.Surface(common.window.get_size())
        common.window.fill((12, 25, 145))
        surf_to_blit.fill((12, 25, 145))
        mouse_pos = list(pygame.mouse.get_pos())
        mouse_pos[0] -= (common.window.get_width() - 620) // 2
        w = surf_to_blit.get_width()
        h = surf_to_blit.get_height()
        w = min(w, h)

        self.exit_shop_button = utils.Button(
            surf_to_blit, (425 / 620 * w, 550 / 620 * h, 150 / 620 * w, 50 / 620 * h), self.exit_shop,
            rect_color=(128, 128, 128), text="Exit Shop", font_size=20,
            border_color=(100, 100, 100), border_width=5,
            hover_color=(150, 150, 150)
        )

        self.exit_shop_button.draw(mouse_pos=mouse_pos)

        for i, item in enumerate(items.store_items):
            location_of_item = divmod(i, 4)
            if location_of_item[0] * (2 / 3 * h) / 1.9 + 40 / 620 * h < 2 / 3 * h:
                coords = (
                    int(location_of_item[1] * w / 4 + 10 / 620 * w),
                    int(location_of_item[0] * (2 / 3 * h) / 1.9 + 40 / 620 * h)
                )
                txt_coords = (
                    int(location_of_item[1] * w / 4 + 10 / 620 * w),
                    int(location_of_item[0] * (2 / 3 * h) / 1.9)
                )

                surf = pygame.transform.scale(item['image'], (int(60 / 620 * w), int(70 / 620 * h)))
                surf_to_blit.blit(
                    surf,
                    coords
                )

                txt = utils.load_font(30).render(item['name'], True, (0, 0, 0))
                surf_to_blit.blit(
                    txt,
                    txt_coords
                )

                t = utils.TextMessage((coords[0], coords[1] + surf.get_height() + 20 / 620 * h),
                                      surf.get_width() * 1.5, surf.get_height(), (128, 128, 128), item['summary'],
                                      utils.load_font(18), (0, 0, 0), (100, 100, 100), 5, screen=surf_to_blit)
                t.draw()

                mod_store_items = items.store_items[:]
                overall_rect = pygame.Rect(coords[0] - 5 / 620 * w, coords[1] - 5 / 620 * h, t.width + 10 / 620 * w,
                                           surf.get_height() + t.height - (
                                                   coords[1] + surf.get_height() - t.text_rect.top) + 10 / 620 * h)
                mod_store_items[i]['rect'] = overall_rect
                items.store_items = mod_store_items[:]
                if self.focused_item is not None:
                    item = self.focused_item
                    overall_rect = item['rect']
                if overall_rect.collidepoint(mouse_pos) or self.focused_item:
                    pygame.draw.rect(surf_to_blit, (133, 0, 0), overall_rect, int(5 / 620 * w))
                    truncated_text = item['description']
                    if len(truncated_text) > 250:
                        truncated_text = item['description'][:247] + '...'
                    t_moreinfo = utils.TextMessage((10 / 620 * w, 450 / 620 * h), 600 / 620 * w, 150 / 620 * h,
                                                   (128, 128, 128),
                                                   f"\n{truncated_text}", common.font, border_color=(100, 100, 100),
                                                   border_width=5,
                                                   text_width=550 / 620 * w, screen=surf_to_blit)
                    t_moreinfo.draw()

                    custom_price_font = utils.load_font(24)
                    custom_price_font.bold = True

                    price_txt = custom_price_font.render(f"{item['price']} coins", True, (0, 0, 0))
                    price_txt_pos = t_moreinfo.text_rect.topright
                    price_txt_pos = price_txt.get_rect(topright=price_txt_pos)
                    surf_to_blit.blit(price_txt, price_txt_pos)

                    name_txt = custom_price_font.render(item['name'], True, (0, 0, 0))
                    name_txt_pos = (t_moreinfo.text_rect.topleft[0] + 5 / 620 * w, t_moreinfo.text_rect.topleft[1])
                    name_txt_pos = name_txt.get_rect(topleft=name_txt_pos)
                    surf_to_blit.blit(name_txt, name_txt_pos)

        pos_to_blit = surf_to_blit.get_rect()
        pos_to_blit.topleft = ((common.window.get_width() - 620) // 2, 0)
        common.window.blit(surf_to_blit, pos_to_blit)

        darken_surf = pygame.Surface(common.window.get_size()).convert_alpha()
        darken_surf.fill((0, 0, 0, self.normal_shop_alpha))
        common.window.blit(darken_surf, (0, 0))

        if self.show_buy_screen:
            buy_screen_surf = pygame.Surface((450 / 620 * w, 450 / 620 * h))
            buy_screen_pos = buy_screen_surf.get_rect(
                center=(common.window.get_width() // 2, common.window.get_height() // 2))
            self.buy_screen_rect = buy_screen_pos

            buy_screen_surf.fill((128, 128, 128))
            bw = buy_screen_surf.get_width()
            bh = buy_screen_surf.get_height()

            transaction_txt = utils.load_font(int(40 / 620 * bh)).render(
                f"Transaction for {self.focused_item['name']}:", True, (0, 0, 0))
            transaction_txt_pos = transaction_txt.get_rect(center=(bw // 2, 30 / 450 * bh))
            buy_screen_surf.blit(transaction_txt, transaction_txt_pos)

            confirmation_txt_font = utils.load_font(int(28 / 450 * bh))

            confirmation_txt = utils.TextMessage.wrap_text(
                f"Are you sure you want to buy a {self.focused_item['name']} for {self.focused_item['price']} coins?\n\n"
                f"You have: {common.coins} coins\n"
                f"Cost: {self.focused_item['price']} coins\n",
                bw, confirmation_txt_font
            )

            for i, text in enumerate(confirmation_txt):
                buy_screen_surf.blit(confirmation_txt_font.render(
                    text, True, (0, 0, 0)
                ), (5 / 450 * bw, 100 / 450 * bh + i * confirmation_txt_font.get_height()))

            self.confirm_button = utils.Button(
                buy_screen_surf, (275 / 450 * bw, 350 / 450 * bh, 150 / 450 * bw, 75 / 450 * bh),
                (
                    lambda: self.buy_item(self.focused_item)
                ),
                (
                    (23, 156, 19) if common.coins - self.focused_item['price'] >= 0
                    else (70, 70, 70)
                ), "Confirm", (0, 0, 0),
                font_size=20, border_color=(100, 100, 100), border_width=int(5 / 450 * bw)
            )
            self.cancel_button = utils.Button(
                buy_screen_surf, (10 / 450 * bw, 350 / 450 * bh, 150 / 450 * bw, 75 / 450 * bh),
                self.remove_buy_popup, (171, 34, 0), "Cancel", (0, 0, 0),
                font_size=20, border_color=(100, 100, 100), border_width=int(5 / 450 * bw)
            )

            self.confirm_button.draw()
            self.cancel_button.draw()

            common.window.blit(buy_screen_surf, buy_screen_pos)

        pygame.display.update()

    def exit_shop(self):
        self.change_state(MainGameState)
        common.player.moved_after_shop_exit = False
        powerup.unpause()

    def handle_buypopup_buttons(self, mouse_pos):
        for button in [self.confirm_button, self.cancel_button]:
            if button.rect.collidepoint(mouse_pos):
                print(button)
                button.func_when_clicked()

    def remove_buy_popup(self):
        self.normal_shop_alpha = 0
        self.show_buy_screen = False
        self.focused_item = None

    def buy_item(self, item):
        if common.coins - item['price'] >= 0:
            common.coins -= item['price']
            item['on_purchase']()
            self.remove_buy_popup()


class PauseState(BaseState):
    def __init__(self):
        super().__init__()
        pause_background = pygame.Surface((common.window.get_width(), common.window.get_height()),
                                          flags=pygame.SRCALPHA)
        pause_background.fill((0, 0, 0))
        pause_background.set_alpha(200)
        common.window.blit(pause_background, (0, 0))
        common.window.blit(common.font64.render("Paused", False, (255, 255, 255)), (0, 0))
        pygame.display.update()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                powerup.unpause()
                self.change_state(MainGameState)
        elif event.type == pygame.VIDEORESIZE:
            common.window.fill((0, 0, 0))
            common.window.blit(common.font64.render("Paused", False, (255, 255, 255)), (0, 0))

    def run(self):
        pygame.display.update()


class MenuState(BaseState):
    def __init__(self):
        super().__init__()
        self.title_name = "ParaPac"
        self.title_idx = 0
        self.title_thing = 0

        self.TITLEUPDATE = pygame.USEREVENT + 1

        pygame.time.set_timer(self.TITLEUPDATE, 70)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.buttons:
                button.handle_event(event)
        if event.type == self.TITLEUPDATE:
            self.title_thing += 1
            self.title_thing %= len(self.title_name)

    def run(self):
        title_font = utils.load_font(int(80 / 620 * common.window.get_height()))
        w, h = common.window.get_size()
        self.buttons = {
            utils.Button(common.window, (w / 2, 150 / 620 * h, 300 / 620 * w, 80 / 620 * h),
                         lambda: self.change_state(MainGameState), (128, 128, 128), "Start", (0, 0, 0), 40,
                         border_color=(100, 100, 100), border_width=int(5 / 620 * w), hover_color=(150, 150, 150),
                         center=True),
            utils.Button(common.window, (w / 2, 260 / 620 * h, 300 / 620 * w, 80 / 620 * h), None, (128, 128, 128),
                         "Settings", (0, 0, 0),
                         40,
                         border_color=(100, 100, 100), border_width=int(5 / 620 * w), hover_color=(150, 150, 150),
                         center=True),
            utils.Button(common.window, (w / 2, 370 / 620 * h, 300 / 620 * w, 80 / 620 * h),
                         lambda: self.change_state(HelpState), (128, 128, 128), "Help", (0, 0, 0), 40,
                         border_color=(100, 100, 100), border_width=int(5 / 620 * w), hover_color=(150, 150, 150),
                         center=True),
            utils.Button(common.window, (w / 2, 480 / 620 * h, 300 / 620 * w, 80 / 620 * h),
                         self.exit_game, (128, 128, 128), "Exit", (0, 0, 0), 40,
                         border_color=(100, 100, 100), border_width=int(5 / 620 * w), hover_color=(150, 150, 150),
                         center=True)
        }
        common.window.fill((12, 25, 145))

        utils.blit_multicolor_text(
            title_font,
            {
                self.title_name[:self.title_thing]: (166, 151, 22),
                self.title_name[self.title_thing]: (229, 235, 52),
                self.title_name[self.title_thing + 1:]: (166, 151, 22),
            },
            (215 / 620 * w, 0)
        )

        for button in self.buttons:
            button.draw()

        pygame.display.flip()

    @staticmethod
    def exit_game():
        raise GameExit


class GameOverState(BaseState):
    def __init__(self):
        super().__init__()
        pause_background = pygame.Surface((common.window.get_width(), common.window.get_height()),
                                          flags=pygame.SRCALPHA)
        pause_background.fill((0, 0, 0))
        pause_background.set_alpha(200)
        common.window.blit(pause_background, (0, 0))
        pygame.display.update()
        try:
            with open(common.PATH / 'highscores.txt') as read_file:
                self.high_score = int(read_file.read().strip())
        except FileNotFoundError:
            self.high_score = common.score

        if common.score > self.high_score:
            self.high_score = common.score

        with open(common.PATH / "highscores.txt", 'w') as write_file:
            write_file.write(str(self.high_score))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.change_state(MenuState)

                common.player.health = 3
                common.score = 0
                common.coins = 0
                common.player.x, common.player.y = 19, 30
                common.active_map_id = 0
                common.active_map = common.maps[common.active_map_id][0]
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.retry_button.handle_event(event)
            self.exit_button.handle_event(event)

    def run(self):
        w, h = common.window.get_size()
        self.retry_button = utils.Button(
            common.window, (w/2, h/2 - 150/620*h, 300/620*w, 100/620*h),
            self.retry, (128, 128, 128), "Retry", (0, 0, 0), 40,
            border_color=(100, 100, 100), border_width=5, hover_color=(150, 150, 150), center=True
        )
        self.exit_button = utils.Button(
            common.window, (w / 2, h / 2 + 150/620*h, 300 / 620 * w, 100 / 620 * h),
            self.exit_to_menu, (128, 128, 128), "Exit to Menu", (0, 0, 0), 40,
            border_color=(100, 100, 100), border_width=5, hover_color=(150, 150, 150), center=True
        )
        common.window.blit(common.font64.render("Game Over", False, (255, 255, 255)), (0, 0))
        common.window.blit(common.font.render(f"Score: {common.score}", False, (255, 255, 255)),
                           (0, 550 / 620 * common.window.get_width()))
        common.window.blit(common.font.render(f"High Score: {self.high_score}", False, (255, 255, 255)),
                           (0, 570 / 620 * common.window.get_width()))
        self.retry_button.draw()
        self.exit_button.draw()

        pygame.display.update()

    def retry(self):
        self.change_state(MainGameState)

        common.player.health = 3
        common.score = 0
        common.coins = 0
        common.player.x, common.player.y = 19, 30
        common.active_map_id = 0
        common.active_map = common.maps[common.active_map_id][0]

    def exit_to_menu(self):
        self.change_state(MenuState)

        common.player.health = 3
        common.score = 0
        common.coins = 0
        common.player.x, common.player.y = 19, 30
        common.active_map_id = 0
        common.active_map = common.maps[common.active_map_id][0]


class GameFinishedState(BaseState):
    def __init__(self):
        super().__init__()
        pause_background = pygame.Surface((common.window.get_width(), common.window.get_height()),
                                          flags=pygame.SRCALPHA)
        pause_background.fill((0, 0, 0))
        pause_background.set_alpha(200)
        common.window.blit(pause_background, (0, 0))
        pygame.display.update()

        try:
            with open(common.PATH / 'highscores.txt') as read_file:
                self.high_score = int(read_file.read().strip())
        except FileNotFoundError:
            self.high_score = common.score

        if common.score > self.high_score:
            self.high_score = common.score

        with open(common.PATH / "highscores.txt", 'w') as write_file:
            write_file.write(str(self.high_score))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.change_state(MenuState)

                common.player.health = 3
                common.score = 0
                common.coins = 0
                common.player.x, common.player.y = 19, 30
                common.active_map_id = 0
                common.active_map = common.maps[common.active_map_id][0]
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.retry_button.handle_event(event)
            self.exit_button.handle_event(event)

    def run(self):
        w, h = common.window.get_size()
        self.retry_button = utils.Button(
            common.window, (w/2, h/2 - 120/620*h, 300/620*w, 100/620*h),
            self.retry, (128, 128, 128), "Retry", (0, 0, 0), 40,
            border_color=(100, 100, 100), border_width=5, hover_color=(150, 150, 150), center=True
        )
        self.exit_button = utils.Button(
            common.window, (w / 2, h / 2 + 150/620*h, 300 / 620 * w, 100 / 620 * h),
            self.exit_to_menu, (128, 128, 128), "Exit to Menu", (0, 0, 0), 40,
            border_color=(100, 100, 100), border_width=5, hover_color=(150, 150, 150), center=True
        )
        self.retry_button.draw()
        self.exit_button.draw()

        common.window.blit(common.font64.render("You won!", False, (255, 255, 255)), (0, 0))
        common.window.blit(common.font64.render(f"Score: {common.score}", False, (255, 255, 255)),
                           (0, 64 / 620 * common.window.get_width()))
        common.window.blit(common.font64.render(f"High Score: {self.high_score}", False, (255, 255, 255)),
                           (0, 500 / 620 * common.window.get_width()))

        pygame.display.update()

    def retry(self):
        self.change_state(MainGameState)

        common.player.health = 3
        common.score = 0
        common.coins = 0
        common.player.x, common.player.y = 19, 30
        common.active_map_id = 0
        common.active_map = common.maps[common.active_map_id][0]

    def exit_to_menu(self):
        self.change_state(MenuState)

        common.player.health = 3
        common.score = 0
        common.coins = 0
        common.player.x, common.player.y = 19, 30
        common.active_map_id = 0
        common.active_map = common.maps[common.active_map_id][0]


class HelpState(BaseState):
    def __init__(self):
        super().__init__()

        self.title_txt = """ParaPac - A multidimensional pac-man, with a few twists"""

        self.story_txt = (
            "The year is 1980. You have time-travelled over 4 decades back, into the era of arcade games. "
            "You visit your favorite arcade games, like Pong and Space Invaders, but when you play Pac-Man... well, it is a tiny bit "
            "different. Turns out, the arcade machine that contains this version of Pac-Man (dubbed \"ParaPac\") is a failed time machine, "
            "made by the government. A few years later, the goverment covered up project ParaPac, and replaced it with the Pac-Man we "
            "know today.  However, you think that if you finish the boss level, the arcade machine will time travel you back. "
            "It will be very difficult though, as NO ONE has finished a game of ParaPac. However, you are filled with determination, "
            "wanting to go back to your era."
        )

        self.overview_txt = (
            "OVERVIEW\n\nPacaPac is like Pac-Man, except that there are a few \"small\" twists\n"
            "1. After travelling to a parallel universe, you gained the ability to travel through dimensions."
            "Press P to activate this power.\n"
            "2. There are shops that allow you to buy numerous items, like powerups and extra lives. Each dimension has at least one "
            "shop. You use the coins you get from the yellow balls to buy items.\n\n"
            "To win, collect all the coins in the boss level, and get to the green square."
        )

        self.dimension_help_txt = (
            "DIMENSIONS\n\nLast page, we talked about dimensions. In simple terms, dimensions are kind of like a level, except that "
            "you can go between dimensions without needing to complete the previous one. Each dimension are different from each other: "
            "There are different maps, different enemies, etc.\n"
            "Dimensions are arranged into a linear style, where you teleport to a new dimension based on the direction you were moving. "
            "If you were moving up or right, you will go to the next dimension, "
            "while moving down or left moves you to the previous one.\n\n"
            "NOTE: There is a cooldown for dimension travelling (25 seconds), so be careful when to use it!\n"
            "SECOND NOTE: You will lose a life if you teleport to a non-player entry block (E.g walls)"
        )

        self.shop_help_txt = (
            "SHOPS\n\nIn the overview page, we talked briefly about shops. Unlike Pac-Man, ParaPac has a shop that allows you to buy "
            "items in exchange for coins. You get coins by collecting the yellow score dots.\n"
            "To enter the shop, you collide with the shop tiles. Every dimension has at least one, and some might have 2 or more!\n\n"
            "Exit the shop by either pressing F9, or pressing the \"Exit Shop\" button at the bottom right."
        )

        self.controls_help_txt = (
            "CONTROLS\n\n"
            "WASD or arrow keys to move\n"
            "P to teleport a previous or next dimension (Read DIMENSIONS manual)\n"
            "ESC to pause and resume the game\n\n\n\n"
            "DEBUG CONTROLS\n\n"
            "F1 to toggle debug mode\n"
            "F2 to save the modified map\n"
            "F3 to toggle freezing the game\n"
            "F4 to instantly go to the next dimension\n"
            "F5 to instantly go to the previous dimension"
        )

        self.pages = [
            [30, self.story_txt],
            [25, self.overview_txt],
            [25, self.dimension_help_txt],
            [25, self.shop_help_txt],
            [30, self.controls_help_txt]
        ]
        self.page_idx = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RIGHT, pygame.K_d]:
                self.page_idx = (self.page_idx + 1) % len(self.pages)
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                self.page_idx = (self.page_idx - 1) % len(self.pages)
            if event.key == pygame.K_ESCAPE:
                self.change_state(MenuState)
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.exit_button.handle_event(event)

    def run(self):
        w, h = common.window.get_size()

        common.window.fill((12, 25, 145))

        self.exit_button = utils.Button(
            common.window, (20 / 620 * w, 550 / 620 * h, 150 / 620 * w, 50 / 620 * h),
            lambda: self.change_state(MenuState),
            (128, 128, 128), "Exit Help", (0, 0, 0), 35,
            border_color=(100, 100, 100), border_width=int(3 / 620 * w), hover_color=(150, 150, 150)
        )

        self.exit_button.draw()

        title_font = utils.load_font(int(22 / 620 * h))
        title_font.italic = True
        title_surf = title_font.render(self.title_txt, True, (255, 255, 255))
        title_surf_pos = title_surf.get_rect(center=(w / 2, 10 / 620 * h))

        help_font = utils.load_font(int(self.pages[self.page_idx][0] / 620 * h))
        formatted_help_txt = utils.TextMessage.wrap_text(self.pages[self.page_idx][1], w - 20 / 620 * h, help_font)

        for i, split_help_line in enumerate(formatted_help_txt):
            split_story_line_surf = help_font.render(split_help_line, True, (220, 220, 220))
            common.window.blit(split_story_line_surf, (10 / 620 * w, 60 / 620 * h + i * help_font.get_height()))

        common.window.blit(title_surf, title_surf_pos)

        pages_font = utils.load_font(int(30 / 620 * h))
        pages = pages_font.render(
            f"Page {self.page_idx + 1} of {len(self.pages)}", True, (255, 255, 255)
        )
        pages_pos = pages.get_rect(bottomright=(w - 10 / 620 * w, h - 25 / 620 * h))
        common.window.blit(pages, pages_pos)

        footer_font = utils.load_font(int(15 / 620 * h))
        footer = footer_font.render(
            "Flip through the manual by pressing the arrow keys", True, (255, 255, 255)
        )
        footer_pos = footer.get_rect(bottomright=(w - 10 / 620 * w, h - 5 / 620 * h))
        common.window.blit(footer, footer_pos)

        pygame.display.flip()
