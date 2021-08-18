from src import common, powerup, notification
import pygame, time


class Dashboard:
    """
    ParaPac GUI. Displays health, effects, score, etc.
    """

    def __init__(self):
        self.current_powers = {}
        self.current_color = None

    def render(self, width):
        dashboard = pygame.Surface((width, 100))  # lgtm [py/call/wrong-arguments]
        self.current_color = common.maps[common.active_map_id][1]

        transition_timer_left = 25 - (time.perf_counter() - common.transition_timer)
        # First Column
        score_txt = common.font.render(
            f"Score: {str(common.score).zfill(6)}",
            False, (255, 255, 255)
        )
        health_txt = common.font.render(
            f"Lives: {common.player.health}",
            False, (255, 255, 255)
        )
        coin_txt = common.font.render(
            f"Coins: {str(common.coins).zfill(6)}",
            False, (255, 255, 255)
        )
        travel_timer_txt = common.font.render(
            f"Travel {f'ready in: {round(transition_timer_left)} sec' if 0 < transition_timer_left <= 25 else 'ready!'}",
            False, (255, 255, 255)
        )
        dashboard.fill((self.current_color[0] * 0.75, self.current_color[1] * 0.75, self.current_color[2] * 0.75))
        dashboard.blit(score_txt, (10, 5))
        dashboard.blit(health_txt, (10, 30))
        dashboard.blit(coin_txt, (10, 55))
        dashboard.blit(travel_timer_txt, (10, 80))

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
        y = 2
        for power, data in list(self.current_powers.items())[:3]:
            time_left = time.perf_counter() - data[0]
            if time_left >= data[1]:
                powerup.powerups[power][0] = 0
                powerup.powerups[power][1] = 0
                break
            widget = pygame.Surface((150, 30))  # lgtm [py/call/wrong-arguments]
            widget.fill((self.current_color[0] * 0.5, self.current_color[1] * 0.5, self.current_color[2] * 0.5))
            # Current placeholder for image:
            image = pygame.Surface((25, 25))  # lgtm [py/call/wrong-arguments]
            image.fill((200, 0, 0))
            widget.blit(image, (5, 2))
            # Uncomment this code when loading real image:
            # image = pygame.transform.scale(data[2], (25,25))
            # widget.blit(image, (5,2))

            time_txt = common.font.render(
                f"{data[1] - int(time_left)}",
                False, (255, 255, 255)
            )
            name_txt = data[3]
            widget.blit(name_txt, (35, 2))
            widget.blit(time_txt, (130, 2))
            dashboard.blit(widget, (175, y))
            y += 32

        # Third Column
        y = 2
        for notif in notification.notifications[:3]:
            widget = pygame.Surface((250, 30))  # lgtm [py/call/wrong-arguments]
            widget.fill(notif[3])
            widget.blit(notif[0], (3, 2))
            opac = int(255 * (((notif[1] + notif[2]) - time.perf_counter()) / (notif[1])))
            if opac <= 0:
                notification.notifications.remove(notif)
                break
            widget.set_alpha(opac)
            dashboard.blit(widget, (375, y))
            y += 32

        return dashboard
