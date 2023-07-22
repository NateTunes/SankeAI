import sys
from typing import Optional
import pygame
import numpy as np
from utils import BLACK, BLOCK_SIZE, BLUE1, BLUE2, FONT, GAMEOVER, RED, SUCCESS, WHITE, Direction, Coord

class SnakeGameAI:
    SPEED = 40
    def __init__(self, w: int=560, h: int=520) -> None:
        self.w = w
        self.h = h

        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()

        # Init game
        self.reset()

    def reset(self) -> None:
        self.direction: Direction = Direction.EAST
        self.head: Coord = Coord(self.w / 2, self.h / 2)
        self.snake: list[Coord] = [self.head,
                      Coord(self.head.x - BLOCK_SIZE, self.head.y),
                      Coord(self.head.x - (2 * BLOCK_SIZE), self.head.y)]

        self.food: Optional[Coord] = None
        self.score = 0
        self.iterations = 0
        self._place_food()

    def _place_food(self) -> None:
        p: Coord = Coord.get_rand_point(self.w, self.h)
        while p in self.snake:
            p = Coord.get_rand_point(self.w, self.h)

        self.food = p

    def _new_direction(self, action) -> Direction:
        # [straight, right, left]

        # keep straight - do not change direction
        if np.array_equal(action, [1, 0, 0]):
            return self.direction

        # find new direction according to action
        directions_turn_right_order = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
        directions_turn_left_order = [Direction.NORTH, Direction.WEST, Direction.SOUTH, Direction.EAST]

        # turn right
        if np.array_equal(action, [0, 1, 0]):
            curr_dir_id = directions_turn_right_order.index(self.direction)
            next_dir_id = (curr_dir_id + 1) % 4
            new_direction = directions_turn_right_order[next_dir_id] # right turn n -> e -> s -> w -> n
        else: # turn left
            curr_dir_id = directions_turn_left_order.index(self.direction)
            next_dir_id = (curr_dir_id + 1) % 4
            new_direction = directions_turn_left_order[next_dir_id] # left turn n -> w -> s -> e -> n

        return new_direction

    def _new_head(self) -> Coord:
        x = self.head.x
        y = self.head.y

        if self.direction == Direction.EAST:
            x += BLOCK_SIZE
        elif self.direction == Direction.WEST:
            x -= BLOCK_SIZE
        elif self.direction == Direction.SOUTH:
            y += BLOCK_SIZE
        elif self.direction == Direction.NORTH:
            y -= BLOCK_SIZE

        return Coord(x, y)

    def play_step(self, action) -> tuple[bool, int]:

        self.iterations += 1

        # 1. user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    SnakeGameAI.SPEED += 5
                elif event.key == pygame.K_DOWN and SnakeGameAI.SPEED > 5:
                    SnakeGameAI.SPEED -=5

        # 2. move
        self.direction = self._new_direction(action)
        self.head = self._new_head()
        self.snake.insert(0, self.head)

        # 3. check if game over
        reward = 0
        if self.is_collision() or self.iterations > 100 * len(self.snake):
            reward = -10
            return GAMEOVER, reward

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SnakeGameAI.SPEED)

        # 6. return game over
        return SUCCESS, reward

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
        score = FONT.render("Score: " + str(self.score), True, WHITE)
        speed = FONT.render("Speed: " + str(SnakeGameAI.SPEED), True, WHITE)
        steps = FONT.render("Steps: " + str(self.iterations), True, WHITE)
        self.display.blit(score, [0, 0])
        self.display.blit(steps, [0, 20])
        self.display.blit(speed, [0, 40])
        pygame.display.flip()
