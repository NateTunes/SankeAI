import random
import pygame
from enum import Enum, auto
from collections import namedtuple

pygame.init()

FONT = pygame.font.Font(pygame.font.get_default_font(), 15)

class Direction(Enum):
    WEST = 1
    EAST = 2
    NORTH = 3
    SOUTH = 4


class Coord:
    def __init__(self, x: int, y: int) -> None:
        self.x = int(x)
        self.y = int(y)

    @classmethod
    def get_rand_point(cls, w, h):
        x: int = random.randint(0, (w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y: int = random.randint(0, (h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        return cls(x, y)

    def get_north_coord(self):
        return Coord(self.x, self.y + BLOCK_SIZE)

    def get_east_coord(self):
        return Coord(self.x + BLOCK_SIZE, self.y)

    def get_south_coord(self):
        return Coord(self.x, self.y - BLOCK_SIZE)

    def get_west_coord(self):
        return Coord(self.x - BLOCK_SIZE, self.y)

    def get_all_adjacent_coords(self):
        return self.get_north_coord(), self.get_east_coord(), self.get_south_coord(), self.get_west_coord()

    def __eq__(self, other: object) -> bool:
        return self.x == other.x and self.y == other.y

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

# set colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 20

# Status
GAMEOVER = True
SUCCESS = False

