import torch
import random
import numpy as np
from collections import deque
from snake_game_ai import SnakeGameAI
from utils import Direction
from model import Linear_QNet, QTrainer
from plot import plot


MAX_MEM = 100_000
BATCH_SIZE = 1000
LR  = .001

class Agent:

    def __init__(self) -> None:
        self.num_of_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEM)

        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, LR, self.gamma)

    def get_state(self, game: SnakeGameAI):
        head = game.head
        direction = game.direction

        coord_north, coord_east, coord_south, coord_west = head.get_all_adjacent_coords()
        is_dir_north = direction == Direction.NORTH
        is_dir_east = direction == Direction.EAST
        is_dir_south = direction == Direction.SOUTH
        is_dir_west = direction == Direction.WEST

        # danger is straight
        danger_straight = \
        (is_dir_north and game.is_collision(coord_north)) or \
        (is_dir_east and game.is_collision(coord_east)) or \
        (is_dir_south and game.is_collision(coord_south)) or \
        (is_dir_west and game.is_collision(coord_west))

        danger_right = \
        (is_dir_north and game.is_collision(coord_east)) or \
        (is_dir_east and game.is_collision(coord_south)) or \
        (is_dir_south and game.is_collision(coord_west)) or \
        (is_dir_west and game.is_collision(coord_north))

        danger_left = \
        (is_dir_north and game.is_collision(coord_west)) or \
        (is_dir_east and game.is_collision(coord_north)) or \
        (is_dir_south and game.is_collision(coord_east)) or \
        (is_dir_west and game.is_collision(coord_south))

        state = [danger_straight,
                 danger_right,
                 danger_left,
                 is_dir_east,
                 is_dir_west,
                 is_dir_north,
                 is_dir_south,
                 game.food.x < head.x,
                 game.food.x > head.x,
                 game.food.y < head.y,
                 game.food.y > head.y]

        return np.array(state, dtype=int)


    def store(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # pop left is reach max memory

    def train_long_mem(self):
        if len(self.memory) > BATCH_SIZE:
            batch = random.sample(self.memory, BATCH_SIZE)
        else:
            batch = self.memory
        states, actions, rewards, next_states, dones = zip(*batch)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_mem(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random move: trade off exploration vs exploitation
        self.epsilon = 80 - self.num_of_games
        final_move = [0 , 0 , 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
        else:
            state_tensor = torch.tensor(state, dtype=torch.float)
            predication = self.model(state_tensor)  # execute model.forward
            move = torch.argmax(predication).item()

        final_move[move] = 1
        return final_move

def run():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()

    while True:

        # retrieve state
        old_state = agent.get_state(game)
        action = agent.get_action(old_state)

        # play step
        done, reward = game.play_step(action)
        new_state = agent.get_state(game)

        # train
        agent.train_short_mem(state=old_state, action=action, reward=reward, next_state=new_state, done=done)
        agent.store(state=old_state, action=action, reward=reward, next_state=new_state, done=done)

        if done:
            score = game.score
            game.reset()
            agent.num_of_games += 1
            agent.train_long_mem()

            if score > record:
                record = score
                # agent.model.save

            print(f"Game: {agent.num_of_games} Score: {score}, Record {record}")

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.num_of_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

if __name__ == '__main__':
    run()