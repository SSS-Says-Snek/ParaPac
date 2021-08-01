from src import common
import pygame
import numpy

from typing import List, Tuple
from functools import lru_cache


def fit_to_screen(surface):
    ratio = surface.get_width() / surface.get_height()
    width, height = common.window.get_width(), common.window.get_height()
    if width > ratio * height:
        new_width = int(ratio * height)
        new_height = int(height)
        new_x = (width - new_width) // 2
        new_y = 0
    else:
        new_width = int(width)
        new_height = int(width / ratio)
        new_x = 0
        new_y = (height - new_height) // 2
    return pygame.transform.scale(surface, (new_width, new_height)), (new_x, new_y)


def polarity(x: float) -> int:
    if x == 0:
        return 0
    elif x < 0:
        return -1
    else:
        return 1


def clip(value_to_clip, lowest_value_to_clip, highest_value_to_clip):
    if value_to_clip > highest_value_to_clip:
        value_to_clip = highest_value_to_clip
    elif value_to_clip < lowest_value_to_clip:
        value_to_clip = lowest_value_to_clip
    return value_to_clip


def to_world_space(x: int, y: int) -> Tuple[float, float]:
    return (x - common.map_area_x) / common.map_area_width * common.active_map.width(), \
           (y - common.map_area_y) / common.map_area_height * common.active_map.height()


def from_world_space(x: int, y: int) -> Tuple[float, float]:
    return common.map_area_width / common.active_map.width() * x + common.map_area_x, \
           common.map_area_height / common.active_map.height() * y + common.map_area_y


def load_sprite_sheet(file_name: str, columns: int, rows: int) -> List[pygame.Surface]:
    sprite_sheet = pygame.image.load(file_name).convert_alpha()
    sprites = []

    width = sprite_sheet.get_width() // columns
    height = sprite_sheet.get_height() // rows

    for y in range(rows):
        for x in range(columns):
            sprites.append(sprite_sheet.subsurface(((x * width, y * height), (width, height))).copy())

    return sprites


def load_map_data(filepath):
    with open(filepath) as r:
        rows = r.read().strip('\r').split('\n')

    for row in rows:
        if not row:
            rows.remove(row)

    tile_map = numpy.zeros((len(rows[0]), len(rows)), dtype=numpy.uint8)

    for y, row in enumerate(rows):
        for x, tile in enumerate(row):
            tile = int(tile, 36)
            tile_map[x, y] = tile

    return tile_map


class TextMessage:
    def __init__(
            self,
            pos,
            width,
            height,
            rect_color,
            text,
            font,
            font_color=(0, 0, 0),
            border_color=None,
            border_width=None,
            instant_blit=True,
            text_width=None,
            height_offset=None,
            screen=common.window,
    ):
        """This class can be used to display text"""
        self.pos = pos
        self.width = width
        self.height = height
        self.rect_color = rect_color
        self.text = text
        self.font = font
        self.font_color = font_color
        self.border_color = border_color
        self.border_width = border_width
        self.instant_blit = instant_blit
        self.text_width = text_width
        self.height_offset = height_offset
        self.screen = screen

        self.text_rect = pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)
        self.split_text = self.wrap_text(
            self.text, (self.text_width or self.width) - (self.border_width or 0), self.font
        )

        if not self.instant_blit:
            self.blitted_chars = ["" for _ in self.split_text]
            self.char_blit_line = 0
            self.blit_line_idx = 0
            self.prev_line_text = ""

    def draw(self):
        pygame.draw.rect(self.screen, self.rect_color, self.text_rect)

        if self.border_color is not None and self.border_width is not None:
            pygame.draw.rect(
                self.screen, self.border_color, self.text_rect, width=self.border_width
            )

        if self.instant_blit:
            for i, text in enumerate(self.split_text):
                rendered_text = self.font.render(text, True, self.font_color)
                self.screen.blit(
                    rendered_text,
                    (
                        self.pos[0] + (self.border_width or 0),
                        self.pos[1] + i * self.font.get_height(),
                    ),
                )

        else:
            self.char_blit_line += 1

            prev_text = self.split_text[self.blit_line_idx][: self.char_blit_line]
            self.blitted_chars[self.blit_line_idx] = self.split_text[
                                                         self.blit_line_idx
                                                     ][: self.char_blit_line]

            if self.blitted_chars[self.blit_line_idx] == self.prev_line_text:
                if self.blit_line_idx + 1 < len(self.split_text):
                    self.char_blit_line = 0
                    self.blit_line_idx += 1

            for i, text in enumerate(self.blitted_chars):
                rendered_text = self.font.render(text, True, self.font_color)
                self.screen.blit(
                    rendered_text,
                    (
                        self.pos[0] + (self.border_width or 0),
                        self.pos[1] + i * self.font.get_height(),
                    ),
                )

            self.prev_line_text = prev_text

    def handle_events(self, event):
        if (
                event.type == pygame.KEYDOWN
                and not self.instant_blit
                and self.blitted_chars != self.split_text
        ):
            self.blitted_chars = self.split_text[:]
            self.blit_line_idx = len(self.blitted_chars) - 1
            self.char_blit_line = len(self.blitted_chars[-1])

    def reset_current_text(self):
        """Only applies for non-instant blit textboxes"""
        self.blitted_chars = ["" for _ in self.split_text]
        self.char_blit_line = 0
        self.blit_line_idx = 0
        self.prev_line_text = ""

    @staticmethod
    def wrap_text(text, width, font):
        """Wrap text to fit inside a given width when rendered.
        :param text: The text to be wrapped.
        :param font: The font the text will be rendered in.
        :param width: The width to wrap to.
        """
        text_lines = text.replace("\t", "    ").split("\n")
        if width is None or width == 0:
            return text_lines

        wrapped_lines = []
        for line in text_lines:
            line = line.rstrip() + " "
            if line == " ":
                wrapped_lines.append(line)
                continue

            # Get the leftmost space ignoring leading whitespace
            start = len(line) - len(line.lstrip())
            start = line.index(" ", start)
            while start + 1 < len(line):
                # Get the next potential splitting point
                next_splitting_point = line.index(" ", start + 1)
                if font.size(line[:next_splitting_point])[0] <= width:
                    start = next_splitting_point
                else:
                    wrapped_lines.append(line[:start])
                    line = line[start + 1:]
                    start = line.index(" ")
            line = line[:-1]
            if line:
                wrapped_lines.append(line)

        for i, row in enumerate(wrapped_lines):
            if len(row.split('\n')) > 1:
                split_row = row.split('\n')
                del wrapped_lines[i]
                for new_row in reversed(split_row):
                    wrapped_lines.insert(i, new_row)

        return wrapped_lines

    @property
    def is_finished(self):
        if not self.instant_blit and self.blitted_chars != self.split_text:
            print("bruv")
            return False
        return True


class Button:
    """Subset of Button, MenuButton adds features suitable for Menu Buttons"""

    def __init__(
            self,
            surface,
            coordinates: tuple,
            func_when_clicked,
            rect_color=(255, 255, 255),
            text=None,
            text_color=(0, 0, 0),
            font_size=None,
            rounded=False,
            border_color=None,
            border_width=None,
            hover_color=None,
            center=False
    ):
        self.screen = surface
        self.coords = coordinates
        self.rect_color = rect_color
        self.text = text
        self.text_color = text_color
        self.font_size = font_size
        self.rounded = rounded
        self.func_when_clicked = func_when_clicked
        self.border_color = border_color
        self.border_width = border_width
        self.hover_color = hover_color
        self.center = center

        self.rect = pygame.Rect(self.coords)
        if self.center:
            self.rect.center = (self.coords[0], self.coords[1])

    def draw(self, mouse_pos=None):
        """Draws the button onto previously inputted screen"""
        mouse_pos = mouse_pos or pygame.mouse.get_pos()
        if self.hover_color and self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(self.screen, self.rect_color, self.rect)

        if self.border_width and self.border_color:
            pygame.draw.rect(self.screen, self.border_color, self.rect, self.border_width)
        if self.text:
            if self.font_size is None:
                # Doesn't work but ok
                self.font_size = (
                    self.coords[3] // len(self.text)
                    if len(self.coords) == 4
                    else self.coords[1][0] // len(self.text)
                )
            font_different_size = load_font(self.font_size)
            text_surf = font_different_size.render(self.text, True, self.text_color)
            self.screen.blit(
                text_surf,
                (
                    self.rect.centerx - text_surf.get_width() // 2,
                    self.rect.centery - text_surf.get_height() // 2,
                ),
            )

    def handle_event(self, event, mouse_pos=None):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if mouse_pos is not None:
                pos = mouse_pos
            if self.rect.collidepoint(pos):
                if self.func_when_clicked is not None:
                    self.func_when_clicked()


@lru_cache(1000)
def load_font(size, text_font="VT323"):
    """Loads a font with a given size and an optional parameter for the font name"""
    return pygame.font.Font(common.PATH / f"assets/{text_font}.ttf", size)


def blit_multicolor_text(
    text_font, text_list: dict, coord_to_blit, screen=common.window, center=False
):
    """
    Function used to render multicolored text. Used as:
    >>> from src import utils
    >>> blit_multicolor_text(utils.load_font(20), {"Text lol": (128, 128, 128), "More Text": (128, 0, 0)})
    <blits font rendering with "Text lol" colored gray, and "More Text" colored red>
    """
    actual_coord_to_blit = coord_to_blit
    for key, value in text_list.items():
        text_font_part = text_font.render(key, True, value)
        if center:
            actual_coord_to_blit = text_font_part.get_rect(center=actual_coord_to_blit)
        screen.blit(text_font_part, actual_coord_to_blit)
        actual_coord_to_blit = (
            actual_coord_to_blit[0] + text_font.size(key)[0],
            actual_coord_to_blit[1],
        )
