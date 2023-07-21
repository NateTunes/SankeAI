from typing import Optional
import pygame
import random
import numpy as np
from utils import BLACK, BLOCK_SIZE, BLUE1, BLUE2, FONT, RED, SPEED, WHITE, Direction, Coord

class SnakeGame:
    def __init__(self, w: int=648, h: int=480) -> None:
        self.w = w
        self.h = h

        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()


        self.direction: Direction = None
        self.snake: list[Coord] = None
        self.head: Coord = None
        self.food: Optional[Coord] = None
        self.score: int = 0
        self.frame_iteration: int = 0

        self.reset()

    def reset(self):
        # init game state
        self.direction = Direction.RIGHT

        self.head = Coord(self.w / 2, self.h / 2)
        self.snake = [self.head,
                      Coord(self.head.x - BLOCK_SIZE, self.head.y),
                      Coord(self.head.x - (2 * BLOCK_SIZE))]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self) -> None:
        def get_rand_point() -> Coord:
            x: int = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y: int = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            return Coord(x, y)

        p: Coord = get_rand_point()
        while Coord in self.snake:
            p = get_rand_point()

        self.food = p

    def _move(self, action) -> None:
        # [straight, right, left]
        clockwise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clockwise.index(self.direction)

    def play_step(self, action: np.ndarray) -> tuple[int, bool, int]:
        self.frame_iteration += 1

        # 1. handle user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # 2. move
        self._move(action) # update the head
        self.snake.insert(0, self.head)

        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)

        # 6. return game over and score
        return reward, game_over, self.score

    def is_collision(self, p=None) -> bool:

        p = p or self.head

        # hits boundary
        if p.x > self.w - BLOCK_SIZE or p.x < 0 or p.y > self.h - BLOCK_SIZE or p.y < 0:
            return True

        # hits itself
        if p in self.snake[1:]:
            return True

        return False

    def _update_ui(self):
        self.display.fill(BLACK)

        # draw snake
        for p in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(p.x, p.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(p.x + 4, p.y + 4, 12, 12))

        # draw food
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        # add text
        text = FONT.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
