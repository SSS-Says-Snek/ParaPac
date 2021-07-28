from src import common, powerup
import pygame, time


class Dashboard:
    """
    ParaPac GUI. Displays health, effects, score, etc.
    """

    def __init__(self):
        self.current_powers = {}
        self.current_color = None

    def render(self, width):
        dashboard = pygame.Surface((width, 100))
        self.current_color = common.maps[common.active_map_id][1]
        # First Column
        score_txt = common.font.render(
            f"Score: {str(common.score).zfill(6)}",
            False, (255, 255, 255)
        )
        health_txt = common.font.render(
            f"Health: {str(common.player.health)}",
            False, (255, 255, 255)
        )
        coin_txt = common.font.render(
            f"Coins: {str(common.coins).zfill(6)}",
            False, (255, 255, 255)
        )
        dashboard.fill((self.current_color[0] * 0.75, self.current_color[1] * 0.75, self.current_color[2] * 0.75))
        dashboard.blit(score_txt, (10, 10))
        dashboard.blit(health_txt, (10, 30))
        dashboard.blit(coin_txt, (10, 50))

        # Second Column

        # Update new powerups data
        self.current_powers = {}
        for power, data in powerup.powerups.items():
            if powerup.is_powerup_on(power):
                self.current_powers[power] = data

        # Sort powerups by time left
        self.current_powers = {k: v for k, v in sorted(self.current_powers.items(),
                                                       key=lambda item: int(item[1][1]) - int(
                                                           time.perf_counter() - item[1][0]))}
        # Render powerups
        y = 10
        for power, data in self.current_powers.items():
            time_left = time.perf_counter() - data[0]
            if time_left >= data[1]:
                powerup.powerups[power][0] = 0
                powerup.powerups[power][1] = 0
                break
            widget = pygame.Surface((150, 30))
            widget.fill((self.current_color[0] * 0.5, self.current_color[1] * 0.5, self.current_color[2] * 0.5))
            # Current placeholder for image:
            image = pygame.Surface((25, 25))
            image.fill((200, 0, 0))
            widget.blit(image, (5, 2))
            # Uncomment this code when loading real image:
            # image = pygame.transform.scale(data[2], (25,25))
            # widget.blit(image, (5,2))

            time_txt = common.font.render(
                f"{data[1] - int(time_left)}",
                False, (255, 255, 255)
            )
            name_txt = common.font.render(
                f"{data[3]}",
                False, (255, 255, 255)
            )
            widget.blit(name_txt, (35, 2))
            widget.blit(time_txt, (130, 2))
            dashboard.blit(widget, (width - 400, y))
            y += 30

        return dashboard
