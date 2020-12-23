from gym.utils import seeding
from datetime import datetime
from gym import spaces
import websockets
import asyncio
import turtle
import random
import time
import math
import gym
import json
import os


###
# DQN Agent

import random
import numpy as np
from keras import Sequential
from collections import deque
from keras.layers import Dense
import matplotlib.pyplot as plt
from keras.optimizers import Adam

###

###
# Globals

URI = "wss://msoll.de/spe_ed?key=LSIS7VOFLXCISR3K4YUSZ3CN2Z3CF74PEB7EKE4AQ7PDVKAGTYVOZVXP"

HEIGHT = 20      # number of steps vertically from wall to wall of screen
WIDTH = 20       # number of steps horizontally from wall to wall of screen

COUNTER = 0

###
class DQN:

    """ Deep Q Network """

    def __init__(self, env, params):

        self.action_space = env.action_space
        self.state_space = env.state_space
        self.epsilon = params['epsilon'] 
        self.gamma = params['gamma'] 
        self.batch_size = params['batch_size'] 
        self.epsilon_min = params['epsilon_min'] 
        self.epsilon_decay = params['epsilon_decay'] 
        self.learning_rate = params['learning_rate']
        self.layer_sizes = params['layer_sizes']
        self.memory = deque(maxlen=2500)
        self.model = self.build_model()


    def build_model(self):
        model = Sequential()
        for i in range(len(self.layer_sizes)):
            if i == 0:
                model.add(Dense(self.layer_sizes[i], input_shape=(self.state_space,), activation='relu'))
            else:
                model.add(Dense(self.layer_sizes[i], activation='relu'))
        model.add(Dense(self.action_space, activation='softmax'))
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model


    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))


    def act(self, state):

        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_space)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])


    def replay(self):

        if len(self.memory) < self.batch_size:
            return

        minibatch = random.sample(self.memory, self.batch_size)
        states = np.array([i[0] for i in minibatch])
        actions = np.array([i[1] for i in minibatch])
        rewards = np.array([i[2] for i in minibatch])
        next_states = np.array([i[3] for i in minibatch])
        dones = np.array([i[4] for i in minibatch])

        states = np.squeeze(states)
        next_states = np.squeeze(next_states)

        targets = rewards + self.gamma*(np.amax(self.model.predict_on_batch(next_states), axis=1))*(1-dones)
        targets_full = self.model.predict_on_batch(states)

        ind = np.array([i for i in range(self.batch_size)])
        targets_full[[ind], [actions]] = targets

        self.model.fit(states, targets_full, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


class GameState():
    def __init__(self, data):
        # print(data) # print the received json
        self.width = data['width']
        self.height = data['height']
        self.cells = data['cells']
        self.pl = data['players']
        self.players = self.get_players(data['players'], data['cells'])
        self.you = data['you']
        self.running = data['running']
        try:
            self.deadline = data['deadline']
        except KeyError:
            self.deadline = ''
        
    def get_players(self, player_list, cells):
        #Get body coordinates for each player
        bodyCoords = getPlayersBodyLocations(cells)

        ret = []
        id = 1
        while True:
            try:
                ret.append(Player(id, player_list[str(id)], bodyCoords))
            except KeyError:
                break
            id += 1
        return ret

    def json_to_file(self, input, status, initial_time):
        if (status == 0):
            if not os.path.exists("JSON Logs/"):
                os.makedirs("JSON Logs/")
            file = open("JSON Logs/" + initial_time + "_RUNNING.txt", 'a+')
            file.write("JSON STATE: ")
            file.write(json.dumps(input))
            file.write("\n")
            global COUNTER
            file.write("COUNTER: " + str(COUNTER))
            file.write("\n")
            COUNTER = COUNTER + 1
        file.close

        return None

    #Method to get the bodylocations for each player
    def getPlayersBodyLocations(cells):

        #Get and save the location of all playerbodys
        allPlayerBodyCords = []

        playerNr = 1
        #Check for each player the location and save as a list (0-58 rows, 0-76 columns in this example)
        while playerNr < 7:
            playerBodyCords = []

            rowNr = -1
            for cellRow in cells:
                rowNr = rowNr + 1
                columNr = 0
                for cell in cellRow:
                    if(cell == playerNr):
                        playerBodyCords.append((columNr, rowNr))
                    columNr = columNr + 1


            allPlayerBodyCords.append(playerBodyCords)
            playerNr = playerNr + 1


        return allPlayerBodyCords # Tuplelist with player locations

class Player():
    def __init__(self, id, info, bodyCoords):
        self.id = id
        self.x = info['x']
        self.y = info['y']
        self.direction = info['direction']
        self.speed = info['speed']
        self.active = info['active']
        self.bodyCoords = bodyCoords[id-1]
        # self.name = info['name'] # nicht notwendig
        print(bodyCoords)

    def display(self):
        print(self.id, ': ', self.x, self.y, self.direction, self.speed, self.active)


class Speed(gym.Env):
    def __init__(self, data, human=False, env_info={'state_space' : None}):
        self.gamestate = GameState(data)
        self.returned_action = None

        #########

        self.done = False
        self.seed() # check why this is used
        self.reward = 0
        self.action_space = 5 # changed from 4 -> 5 because we have choose from 5 actions in total
        self.state_space = 12 # changed from 12 -> 12 because we have 13 nececessary information about state 

        self.total, self.maximum = 0, 0
        self.env_info = env_info

        self.player = self.gamestate.players[int(self.gamestate.you) - 1] # self.GameState.Player()
        self.snake_body = [] # snake body, add first element (for location of snake's head)

        # TODO: implement here all the enemies
        # distance between first enemy and player
        self.dist = math.sqrt((self.player.x - self.gamestate.players[0].x)**2 + (self.player.y - self.gamestate.players[0].y)**2)


    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def measure_distance(self):
        self.prev_dist = self.dist
        # self.dist = math.sqrt((self.snake.xcor()-self.apple.xcor())**2 + (self.snake.ycor()-self.apple.ycor())**2)
        if self.gamestate.players[0].id != self.player.id:
            self.dist = math.sqrt((self.player.x - self.gamestate.players[0].x)**2 + (self.player.y - self.gamestate.players[0].y)**2)
        else:
            self.dist = math.sqrt((self.player.x - self.gamestate.players[1].x)**2 + (self.player.y - self.gamestate.players[1].y)**2)


    def wall_check(self):
        if self.player.x > 200 or self.player.x < -200 or self.player.y > 200 or self.player.y < -200:
            return True

    def run_game(self):
        reward_given = False
        # self.move_snake()
        """        
        if self.move_apple():
            self.reward = 10
            reward_given = True
        
        # self.move_snakebody()
        # self.measure_distance()
        
        if self.body_check_snake():
            self.reward = -100
            reward_given = True
            self.done = True
        """
        """
        if self.wall_check():
            self.reward = -100
            reward_given = True
            self.done = True
        """
        """output"""
        
        self.measure_distance()

        if not reward_given:
            print(f"reward funktion results: {self.dist}, {self.prev_dist}, {self.dist < self.prev_dist}")
            if self.dist < self.prev_dist:
                self.reward = 1
            else:
                self.reward = -1


    # AI agent
    def step(self, action):
        if action == 0:
            self.returned_action = 'turn_left'
        if action == 1:
            self.returned_action = 'turn_right'
        if action == 2:
            self.returned_action = 'slow_down'
        if action == 3:
            self.returned_action = 'speed_up'
        if action == 4:
            self.returned_action = 'change_nothing'
        
        self.run_game() # here is the reward function

        state = self.get_state_speed()

        return state, self.reward, self.done, self.returned_action # {}


    def get_state_speed(self):
        # snake coordinates abs
        # self.snake.x, self.snake.y = self.snake.xcor()/WIDTH, self.snake.ycor()/HEIGHT   
        # spe_ed
        player_x, player_y = self.player.x, self.player.y

        # snake coordinates scaled 0-1
        # self.snake.xsc, self.snake.ysc = self.snake.x/WIDTH+0.5, self.snake.y/HEIGHT+0.5
        # spe_ed
        player_xsc, player_ysc = self.player.x / self.gamestate.width + 0.5, self.player.y / self.gamestate.height + 0.5


        # apple coordintes scaled 0-1 
        # self.apple.xsc, self.apple.ysc = self.apple.x/WIDTH+0.5, self.apple.y/HEIGHT+0.5
        # spe_ed
        # not scaled
        enemy_x, enemy_y = self.gamestate.players[0].x, self.gamestate.players[0].y
        # enemy_x, enemy_y = self.gamestate.players[0].x / self.gamestate.width + 0.5, self.gamestate.players[0].y  / self.gamestate.height + 0.5

        # wall check
        """
        if self.snake.y >= HEIGHT/2:
            wall_up, wall_down = 1, 0
        elif self.snake.y <= -HEIGHT/2:
            wall_up, wall_down = 0, 1
        else:
            wall_up, wall_down = 0, 0
        if self.snake.x >= WIDTH/2:
            wall_right, wall_left = 1, 0
        elif self.snake.x <= -WIDTH/2:
            wall_right, wall_left = 0, 1
        else:
            wall_right, wall_left = 0, 0
        """

        # wall check
        if player_y >= self.gamestate.height / 2:
            wall_up, wall_down = 1, 0
        elif player_y <= -self.gamestate.height / 2:
            wall_up, wall_down = 0, 1
        else:
            wall_up, wall_down = 0, 0
        if player_x >= self.gamestate.width / 2:
            wall_right, wall_left = 1, 0
        elif player_x <= -self.gamestate.width / 2:
            wall_right, wall_left = 0, 1
        else:
            wall_right, wall_left = 0, 0

        # check how we can implement the bodylength, we definetly need it
        """
        # body close
        body_up = []
        body_right = []
        body_down = []
        body_left = []
        if len(self.snake_body) > 3:
            for body in self.snake_body[3:]:
                if body.distance(self.snake) == 20:
                    if body.ycor() < self.snake.ycor():
                        body_down.append(1)
                    elif body.ycor() > self.snake.ycor():
                        body_up.append(1)
                    if body.xcor() < self.snake.xcor():
                        body_left.append(1)
                    elif body.xcor() > self.snake.xcor():
                        body_right.append(1)
        
        if len(body_up) > 0: body_up = 1
        else: body_up = 0
        if len(body_right) > 0: body_right = 1
        else: body_right = 0
        if len(body_down) > 0: body_down = 1
        else: body_down = 0
        if len(body_left) > 0: body_left = 1
        else: body_left = 0
        """

        # state: apple_up, apple_right, apple_down, apple_left, obstacle_up, obstacle_right, obstacle_down, obstacle_left, direction_up, direction_right, direction_down, direction_left
        # spe_ed_state: enemy_up, enemy_right, enemy_down, enemy_left, obstacle_up, obstacle_right, obstacle_down, obstacle_left, direction_up, direction_right, direction_down, direction_left, turn_left, turn_right, slow_down, speed_up, change_nothing
        # spe_ed_state: enemy_up, enemy_right, enemy_down, enemy_left, obstacle_up, obstacle_right, obstacle_down, obstacle_left, direction_up, direction_right, direction_down, direction_left (are we needing an action here?)
        """
        if self.env_info['state_space'] == 'coordinates':
            state = [self.apple.xsc, self.apple.ysc, self.snake.xsc, self.snake.ysc, \
                    int(wall_up or body_up), int(wall_right or body_right), int(wall_down or body_down), int(wall_left or body_left), \
                    int(self.snake.direction == 'up'), int(self.snake.direction == 'right'), int(self.snake.direction == 'down'), int(self.snake.direction == 'left')]
        elif self.env_info['state_space'] == 'no direction':
            state = [int(self.snake.y < self.apple.y), int(self.snake.x < self.apple.x), int(self.snake.y > self.apple.y), int(self.snake.x > self.apple.x), \
                    int(wall_up or body_up), int(wall_right or body_right), int(wall_down or body_down), int(wall_left or body_left), \
                    0, 0, 0, 0]
        elif self.env_info['state_space'] == 'no body knowledge':
            state = [int(self.snake.y < self.apple.y), int(self.snake.x < self.apple.x), int(self.snake.y > self.apple.y), int(self.snake.x > self.apple.x), \
                    wall_up, wall_right, wall_down, wall_left, \
                    int(self.snake.direction == 'up'), int(self.snake.direction == 'right'), int(self.snake.direction == 'down'), int(self.snake.direction == 'left')]
        else:
            state = [int(self.snake.y < self.apple.y), int(self.snake.x < self.apple.x), int(self.snake.y > self.apple.y), int(self.snake.x > self.apple.x), \
                    int(wall_up or body_up), int(wall_right or body_right), int(wall_down or body_down), int(wall_left or body_left), \
                    int(self.snake.direction == 'up'), int(self.snake.direction == 'right'), int(self.snake.direction == 'down'), int(self.snake.direction == 'left')]
        """ 
        # print(state) # state of the current step of the game

        state = [int(player_y < enemy_y), int(player_x < enemy_x), int(player_y > enemy_y), int(player_x > enemy_x), \
                int(wall_up), int(wall_right), int(wall_down), int(wall_left), \
                int(self.player.direction == 'up'), int(self.player.direction == 'right'), int(self.player.direction == 'down'), int(self.player.direction == 'left')]

        print(f"der state aus der get_state funktion: {state}")

        return state



def train_dqn(episode, env):

    sum_of_rewards = []
    agent = DQN(env, params)

    for e in range(episode):
        state = env.reset()
        state = np.reshape(state, (1, env.state_space))
        score = 0
        max_steps = 10000
        for i in range(max_steps):
            action = agent.act(state)
            # print(action) # outcomment this for better visibility
            prev_state = state
            next_state, reward, done, _ = env.step(action)
            score += reward
            next_state = np.reshape(next_state, (1, env.state_space))
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            if params['batch_size'] > 1:
                agent.replay()
            if done:
                print(f'final state before dying: {str(prev_state)}')
                print(f'episode: {e+1}/{episode}, score: {score}')
                break
        sum_of_rewards.append(score)
    return sum_of_rewards


async def connection(sum_of_rewards):
    # injection of DQN agent
    params = dict()
    params['name'] = None
    params['epsilon'] = 1
    params['gamma'] = .95
    params['batch_size'] = 500
    params['epsilon_min'] = .01
    params['epsilon_decay'] = .995
    params['learning_rate'] = 0.00025
    params['layer_sizes'] = [128, 128, 128]

    results = dict()
    
    async with websockets.connect(URI) as ws:

        print("Waiting for initial state...", flush=True)
        print("PRIOR game ready: TIME: ", datetime.now(), flush=True)
        start_time = datetime.now()
        initial_time = start_time.strftime("%m.%d.%Y, %H.%M.%S")
        started = False

        while True:
            if not started:
                ans = await ws.recv()
            
            if not started : started = True
            
            if ans is not None:
                # state = Speed.GameState(json.loads(ans))
                state = Speed(json.loads(ans))
                
                stateString = GameState(json.loads(ans))
                stateString.json_to_file(json.loads(ans), 0, initial_time)

                # print(state.gamestate.players)
                if not state.gamestate.running:
                    stateString.json_to_file(json.loads(ans), 0, initial_time)
                    break
                
                game_state = state.get_state_speed()
                game_state = np.reshape(game_state, (1, state.state_space))
                score = 0

                agent = DQN(state, params)

                # TODO: investigate why there are some games where the state does not change
                # our fault or GI's fault? !!!!!!!!!!!!!!
                print(f"game_state: {game_state}")

                action = agent.act(game_state)
                # print(action) # outcomment this for better visibility
                prev_state = game_state
                # inject here the next state based on send action


                # experiment: needs next state for learning of agent
                action_json = json.dumps({"action": action})
                
                if state.player.active != False:
                    print(f"tot? :: {state.player.active}")
                    await ws.send(action_json)
                    # investigate why we are instant dead :-(

            try:
                ans = await ws.recv()
            except Exception as e:
                # TODO: why are we having here an exception?
                ans = None
                print('Reconnecting')
                # ws = await websockets.connect(URI)
                break # needed? -> yes
                print(f"the problem: {e}")

            print("kommen wir nach dem senden, noch weiter?")

            if ans is not None:
                # next_state, reward, done, _ = state.step(action)
                next_state, reward, done, action_from_ai = state.step(action) # fix wrong next state bug
                # print(f"next_state: {next_state}")

                
                state = Speed(json.loads(ans))
                game_state = state.get_state_speed()
                game_state = np.reshape(game_state, (1, state.state_space))


                print(f"next_state ist eigentlich der previous state aus der fkt: {next_state} und hier der richtige next state: {game_state}")


                score += reward
                next_state = np.reshape(next_state, (1, state.state_space))
                agent.remember(game_state, action, reward, next_state, done)
                game_state = next_state
                if params['batch_size'] > 1:
                    agent.replay()

                sum_of_rewards.append(score)

                results[params['name']] = sum_of_rewards
                # end of injection

                action = action_from_ai
                

                # action_json = json.dumps({"action": action})


                file = open("JSON Logs/" + initial_time + "_RUNNING.txt", 'a+')
                file.write("Gewählte Aktion: ")
                file.write(action_json)
                file.write("\n")
                file.close
                
                
                # await ws.send(action_json)


                print("Action sent: ", action)

    print("AFTER game ready: TIME: ", datetime.now(), flush=True)


def main():
    ep = 2 # 50
    sum_of_rewards = []

    for e in range(ep):
        asyncio.get_event_loop().run_until_complete(connection(sum_of_rewards))

    print(f"das ist die sum_of_rewards: {sum_of_rewards}")

if __name__ == '__main__':            
    main()