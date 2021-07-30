import pygame

from src import common, tiles, utils, powerup, notification, items
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
                common.active_map.render_world()
            # Changes the map dimension
            elif event.key == pygame.K_p:
                common.transitioning_mode = common.Transition.FADING
                common.alpha = 255
            # Pause Game
            elif event.key == pygame.K_ESCAPE:
                powerup.pause()
                self.change_state(PauseState)

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

        if common.transitioning_mode != common.Transition.NOT_TRANSITIONING:
            world.set_alpha(common.alpha)
            if common.transitioning_mode == common.Transition.FADING:
                common.alpha -= 15
            elif common.transitioning_mode == common.Transition.REAPPEARING:
                common.alpha += 15

            if common.alpha < 0:
                common.transitioning_mode = common.Transition.REAPPEARING
                common.active_map_id = (common.active_map_id + 1) % len(common.maps)
                common.active_map = common.maps[common.active_map_id][0]

            if common.alpha == 255:
                common.transitioning_mode = common.Transition.NOT_TRANSITIONING

        game_surf, chords = utils.fit_to_screen(game_surf)
        common.map_area_x, common.map_area_y = chords
        common.map_area_width, common.map_area_height = game_surf.get_width(), game_surf.get_height()
        common.map_area_ratio = game_surf.get_width()/game_surf.get_height()
        common.window.blit(game_surf, chords)

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
            if not self.show_buy_screen:
                for i, item in enumerate(items.store_items):
                    try:
                        if item['rect'].collidepoint(event.pos):
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

        self.exit_shop_button.handle_event(event)

    def run(self):
        surf_to_blit = pygame.Surface(common.window.get_size())
        common.window.fill((12, 25, 145))
        surf_to_blit.fill((12, 25, 145))
        mouse_pos = pygame.mouse.get_pos()

        self.exit_shop_button = utils.Button(
            surf_to_blit, (425, 550, 150, 50), self.exit_shop,
            rect_color=(128, 128, 128), text="Exit Shop", font_size=20,
            border_color=(100, 100, 100), border_width=5,
            hover_color=(150, 150, 150)
        )

        self.exit_shop_button.draw()
        w = surf_to_blit.get_width()
        h = surf_to_blit.get_height()

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
                    if len(truncated_text) > 200:
                        truncated_text = item['description'][:197] + '...'
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

        common.window.blit(surf_to_blit, (0, 0))

        darken_surf = pygame.Surface(common.window.get_size()).convert_alpha()
        darken_surf.fill((0, 0, 0, self.normal_shop_alpha))
        common.window.blit(darken_surf, (0, 0))

        if self.show_buy_screen:
            buy_screen_surf = pygame.Surface((450 / 620 * w, 450 / 620 * h))
            buy_screen_pos = buy_screen_surf.get_rect(center=(w // 2, h // 2))
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
                    lambda: self.buy_item(self.focused_item) if common.coins - self.focused_item['price'] >= 0
                    else lambda: None
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
                button.func_when_clicked()

    def remove_buy_popup(self):
        self.normal_shop_alpha = 0
        self.show_buy_screen = False
        self.focused_item = None

    def buy_item(self, item):
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
        pygame.display.update()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                powerup.unpause()
                self.change_state(MainGameState)

    def run(self):

        pygame.display.update()


class TestState(BaseState):
    def __init__(self):
        super().__init__()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F9:
                self.change_state(MainGameState)

    def run(self):
        common.window.fill((0, 0, 0))
        pygame.display.update()
