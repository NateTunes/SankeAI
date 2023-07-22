import sys
from typing import Optional
import pygame
import random
import numpy as np
from utils import BLACK, BLOCK_SIZE, BLUE1, BLUE2, FONT, GAMEOVER, RED, SPEED, SUCCESS, WHITE, Direction, Coord

class SnakeGame:
    def __init__(self, w: int=560, h: int=520) -> None:
        self.w = w
        self.h = h

        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()


        self.direction: Direction = Direction.EAST
        self.head: Coord = Coord(self.w / 2, self.h / 2)
        self.snake: list[Coord] = [self.head,
                      Coord(self.head.x - BLOCK_SIZE, self.head.y),
                      Coord(self.head.x - (2 * BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food: Optional[Coord] = None
        self._place_food()
        self._update_ui()

    def _place_food(self) -> None:
        p: Coord = Coord.get_rand_point(self.w, self.h)
        while p in self.snake:
            p = Coord.get_rand_point(self.w, self.h)

        self.food = p

    def _update_head(self, direction) -> Coord:
        x = self.head.x
        y = self.head.y

        if direction is None:
            return self.head
        if direction == Direction.EAST:
            x += BLOCK_SIZE
        elif direction == Direction.WEST:
            x -= BLOCK_SIZE
        elif direction == Direction.SOUTH:
            y += BLOCK_SIZE
        elif direction == Direction.NORTH:
            y -= BLOCK_SIZE

        return Coord(x, y)

    def play_step(self) -> bool:

        # 1. user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.direction != Direction.EAST:
                    self.direction = Direction.WEST
                    break
                elif event.key == pygame.K_RIGHT and self.direction != Direction.WEST:
                    self.direction = Direction.EAST
                    break
                elif event.key == pygame.K_UP  and self.direction != Direction.SOUTH:
                    self.direction = Direction.NORTH
                    break
                elif event.key == pygame.K_DOWN  and self.direction != Direction.NORTH:
                    self.direction = Direction.SOUTH
                    break

        # 2. move
        self.head = self._update_head(self.direction) # update the head
        self.snake.insert(0, self.head)

        # 3. check if game over
        if self._is_collision():
            return GAMEOVER

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)

        # 6. return game over
        return SUCCESS

    def _is_collision(self, p=None) -> bool:

        p = self.head
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


if __name__ == '__main__':

    # import os
    # os.environ['SDL_AUDIODRIVER'] = 'dsp'

    game = SnakeGame()

    # game loop
    while not game.play_step():
        pass

    print('Final Score', game.score)

    pygame.quit()