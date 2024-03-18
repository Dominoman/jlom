from abc import ABC
from typing import BinaryIO

import pygame
from pygame import Surface

from game import Midnight, Map


class Color(pygame.Color):
    WHITE = pygame.Color(255, 255, 255)
    BLACK = pygame.Color(0, 0, 0)
    BLUE = pygame.Color('#0100CE')
    RED = pygame.Color('#68372B')
    MAGENTA = pygame.Color('#CF01CE')
    GREEN = pygame.Color('#00CF15')
    CYAN = pygame.Color('#01CFCF')
    YELLOW = pygame.Color('#CFCF15')
    last_color = None
    color = (BLACK, BLUE, RED, MAGENTA, GREEN, CYAN, YELLOW, WHITE)


class Tile:
    def __init__(self, tile_data: bytes):
        self.tile_data = tile_data

    def draw_tile(self, surface: Surface, x: int, y: int, attribute=None, bg: Color = None) -> None:
        if attribute is None:
            fg = Color.last_color
        elif isinstance(attribute, int):
            fg = Color.color[attribute & 7]
            bg = Color.color[(attribute >> 3) & 7]
        else:
            fg = attribute
        for data in self.tile_data:
            for dx in range(7, -1, -1):
                if data & (1 << dx) != 0:
                    Color.last_color = fg
                    surface.set_at((x, y), fg)
                elif bg is not None:
                    Color.last_color = bg
                    surface.set_at((x, y), bg)
                x += 1
            y += 1
            x -= 8


class TileSet:
    def __init__(self, glyphs: bytes):
        self.tiles = []
        for i in range(len(glyphs) // 8):
            self.tiles.append(Tile(glyphs[i * 8:i * 8 + 8]))

    def draw_tile(self, tile: int, surface: Surface, x: int, y: int, attribute: int = -1) -> None:
        self.tiles[tile].draw_tile(surface, x, y, attribute)


class Font:
    @staticmethod
    def make_font(ix: BinaryIO) -> TileSet:
        return TileSet(ix.read(96 * 8))


shieldPartData = (
    (6, 7, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
     0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x02, 0x01, 0x01, 0x01, 0x01, 0x05,
     0x03, 0x01, 0x01, 0x01, 0x01, 0x06, 0x00, 0x04, 0x01, 0x01, 0x07, 0x00,
     0x00, 0x00, 0x04, 0x07, 0x00, 0x00),
    (2, 3, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D),
    (2, 2, 0x0E, 0x10, 0x0F, 0x11),
    (1, 2, 0x12, 0x13),
    (3, 1, 0x14, 0x15, 0x16),
    (4, 2, 0x17, 0x18, 0x19, 0x1A, 0x00, 0x1B, 0x1C, 0x00),
    (4, 2, 0x1D, 0x1E, 0x1F, 0x20, 0x21, 0x22, 0x23, 0x24),
)

shieldData = [
    [0x03, 0x29, 0x0B, 0x32, 0x11],
    [0x02, 0x21, 0x09, 0x33, 0x14, 0x33, 0x23],
    [0x02, 0x35, 0x09],
    [0x05, 0x0C, 0x09, 0x3D, 0x19],
    [0x03, 0x3E, 0x09, 0x32, 0x22],
    [0x02, 0x36, 0x09, 0x3A, 0x2],
    [0x03, 0x36, 0x09, 0x2A, 0x22],
    [0x00, 0x16, 0x11],
    [0x05, 0x3E, 0x11],
    [0x04, 0x3E, 0x11],
    [0x02, 0x3E, 0x11],
    [0x06, 0x16, 0x11],
    [0x02, 0x36, 0x09, 0x2D, 0x21],
    [0x03, 0x36, 0x09, 0x3D, 0x21],
    [0x04, 0x3D, 0x09],
    [0x05, 0x15, 0x09],
    [0x00, 0x1D, 0x09],
    [0x03, 0x35, 0x09],
    [0x07, 0x15, 0x09],
    [0x07, 0x25, 0x09],
    [0x02, 0x31, 0x0A],
    [0x05, 0x39, 0x0A],
    [0x07, 0x19, 0x0A],
    [0x02, 0x32, 0x0A],
    [0x00, 0x22, 0x0A],
    [0x00, 0x11, 0x0A],
    [0x04, 0x39, 0x0A],
    [0x03, 0x3A, 0x0A],
    [0x00, 0x1E, 0x09, 0x24, 0x22],
    [0x00, 0x32, 0x09, 0x1B, 0x1B],
    [0x06, 0x14, 0x09, 0x0B, 0x1B],
    [0x02, 0x33, 0x09, 0x33, 0x14, 0x33, 0x22],
]


class ShieldPart:
    def __init__(self, width: int, height: int, part_data: list[int], tile_set: TileSet) -> None:
        self.width = width
        self.height = height
        self.part_data = part_data
        self.shield_tiles = tile_set

    def draw(self, surface: Surface, column: int, row: int, attribute: int) -> None:
        attribute |= 0x40

        i = 0
        for dy in range(self.height):
            for dx in range(self.width):
                ch = self.part_data[i]
                i += 1
                if ch != 0:
                    self.shield_tiles.draw_tile(ch, surface, (column + dx) * 8, (row + dy) * 8, attribute)


class Shield:
    def __init__(self, shield_set: 'ShieldSet', shield_data: list[int]) -> None:
        self.shield_set = shield_set
        self.shield_data = shield_data

    def draw(self, surface: Surface, column: int, row: int) -> None:
        shield_ink = self.shield_data[0]
        shield_paper = 1 << 3
        attribute = shield_paper | shield_ink
        self.shield_set.get_shield_part(0).draw(surface, column, row, attribute)
        i = 1
        while i < len(self.shield_data):
            part = self.shield_data[i] & 0x07
            shield_paper = self.shield_data[i] & 0xF0
            attribute = shield_paper | shield_ink
            i += 1

            dx = self.shield_data[i] & 0x07
            dy = self.shield_data[i] >> 3
            i += 1

            self.shield_set.get_shield_part(part).draw(surface, column + dx, row + dy, attribute)


class ShieldSet:
    shields: list[Shield]
    shield_parts: list[ShieldPart]
    shield_tiles: TileSet

    def __init__(self, tile_stream: BinaryIO):
        self.create_shield_tiles(tile_stream)
        self.create_shield_parts()
        self.create_shields()

    @staticmethod
    def make_shields(ix: BinaryIO) -> list[Shield]:
        return ShieldSet(ix).shields

    def get_shield_part(self, part_index: int) -> ShieldPart:
        return self.shield_parts[part_index]

    def create_shield_tiles(self, ix: BinaryIO) -> None:
        shield_glyphs = ix.read(37 * 8)
        self.shield_tiles = TileSet(shield_glyphs)

    def create_shield_parts(self) -> None:
        self.shield_parts = []
        for i in range(len(shieldPartData)):
            part_width = shieldPartData[i][0]
            part_height = shieldPartData[i][1]
            part_tiles = shieldPartData[i][2:]
            part = ShieldPart(part_width, part_height, part_tiles, self.shield_tiles)
            self.shield_parts.append(part)

    def create_shields(self) -> None:
        self.shields = []
        for shield_dt in shieldData:
            self.shields.append(Shield(self, shield_dt))


class Entity:
    def __init__(self, tiles: TileSet, width: int, height: int, characters: list[int], attributes: list[int]) -> None:
        self.tile_set = tiles
        self.width = width
        self.height = height
        self.tiles = characters
        self.attributes = attributes

    def draw(self, surface: Surface, column: int, row: int, is_night: bool = False) -> None:
        row = row - self.height + 1
        windowAttribute = 0x40 if is_night else 0x7f
        printInk = 0x41 if is_night else 0
        i = 0
        for dy in range(self.height):
            for dx in range(self.width):
                ch = self.tiles[i]
                attribute = self.attributes[i]
                attribute &= windowAttribute
                attribute |= printInk
                self.tile_set.draw_tile(ch, surface, (column + dx) * 8, (row + dy) * 8, attribute)
                i += 1


class GameScreen(ABC):
    def __init__(self, applet, game: Midnight) -> None:
        self.applet = applet
        self.game = game

    def get_game(self) -> Midnight:
        return self.game

    def get_map(self) -> Map:
        return self.game.get_map()

    def update(self):
        pass

    def draw(self, surface: Surface):
        self.clear_screen(surface)

    def clear_screen(self, surface: Surface, color: Color = Color.WHITE):
        surface.fill(color)


class SplashScreen(GameScreen):

    def __init__(self, applet, game: Midnight) -> None:
        super().__init__(applet, game)
        self.image = pygame.image.load("data\\banner.gif").convert_alpha()

    def draw(self, surface: Surface):
        super().draw(surface)
        surface.blit(self.image, (0, 200))
