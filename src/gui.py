from src import common
import pygame


class Dashboard:
    """
    ParaPac GUI. Displays health, effects, score, etc.
    """

    def __init__(self):
        pass

    def render(self, width):
        score_txt = common.font.render(
            f"Score: {str(common.score).zfill(6)}",
            False, (255, 255, 255)
        )
        health_txt = common.font.render(
            f"Health: {str(common.health)}",
            False, (255, 255, 255)
        )
        coin_txt = common.font.render(
            f"Coins: {str(common.coins).zfill(6)}",
            False, (255, 255, 255)
        )
        dashboard = pygame.Surface((width, 100))
        current_color = common.maps[common.active_map_id][1]
        dashboard.fill((current_color[0]*0.75,current_color[1]*0.75,current_color[2]*0.75))
        dashboard.blit(score_txt, (10, 10))
        dashboard.blit(health_txt, (10, 30))
        dashboard.blit(coin_txt, (10, 50))
        return dashboard
