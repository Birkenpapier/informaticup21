from gamestate import GameState, Player
from dqnagent import DQN

from keras.optimizers import Adam
import matplotlib.pyplot as plt
from keras.layers import Dense
from collections import deque
from datetime import datetime
from keras import Sequential
import numpy as np
import websockets
import asyncio
import turtle
import random
import keras
import time
import math
import json
import os


### Globals
URI = "wss://msoll.de/spe_ed?key=LSIS7VOFLXCISR3K4YUSZ3CN2Z3CF74PEB7EKE4AQ7PDVKAGTYVOZVXP"

COUNTER = 0

DECEASED_ENEMIES = []
###


class Speed():
    def __init__(self, data, env_info={'state_space' : None}):
        self.gamestate = GameState(data)
        self.returned_action = None

        self.done = False
        self.reward = 0
        self.action_space = 5
        self.state_space = 12

        self.total, self.maximum = 0, 0
        self.env_info = env_info

        self.player = self.gamestate.players[int(self.gamestate.you) - 1] # self.GameState.Player()
        self.snake_body = [] # snake body, add first element (for location of snake's head)

        if self.gamestate.players[0].id != self.player.id:
            self.dist = math.sqrt((self.player.x - self.gamestate.players[0].x)**2 + (self.player.y - self.gamestate.players[0].y)**2)
        else:
            self.dist = math.sqrt((self.player.x - self.gamestate.players[1].x)**2 + (self.player.y - self.gamestate.players[1].y)**2)
        
        self.prev_dist = 0

        self.dead_enemies = DECEASED_ENEMIES # list with all deceased enemies

    def measure_distance_async(self, prev_state, state):
        # print(f"2==2: die berechnung aus measure_distance_async: self.player.x: {self.player.x}, self.player.y: {self.player.y}, ")
        # print(f"3==3: die berechnung aus measure_distance_async: self.prev_state.players[0].x: {prev_state.gamestate.players[0].x}, self.prev_state.players[0].y: {prev_state.gamestate.players[0].y}, ")
        # print(f"4==4: die berechnung aus measure_distance_async: self.prev_state.players[0].x: {state.gamestate.players[0].x}, self.prev_state.players[0].y: {state.gamestate.players[0].y}, ")


        previous_distance = 2000
        closest_enemy = 0
        closest_dist = 0

        # TODO: check if good for loop and if good state in general
        for enemy in prev_state.gamestate.players:
            if enemy.id != self.player.id and enemy.active == True:
                closest_dist = math.sqrt((self.player.x - enemy.x)**2 + (self.player.y - enemy.y)**2)

            if closest_dist < previous_distance:
                previous_distance = closest_dist
                closest_enemy = enemy.id

        closest_enemy_to_player = prev_state.gamestate.players[closest_enemy - 1]

        """
        if state.gamestate.players[0].id != self.player.id:
            self.prev_dist = math.sqrt((prev_state.player.x - prev_state.gamestate.players[0].x)**2 + (prev_state.player.y - prev_state.gamestate.players[0].y)**2)
        else:
            self.prev_dist = math.sqrt((prev_state.player.x - prev_state.gamestate.players[1].x)**2 + (prev_state.player.y - prev_state.gamestate.players[1].y)**2)

        if state.gamestate.players[0].id != self.player.id:
            self.dist = math.sqrt((self.player.x - state.gamestate.players[0].x)**2 + (self.player.y - state.gamestate.players[0].y)**2)
        else:
            self.dist = math.sqrt((self.player.x - state.gamestate.players[1].x)**2 + (self.player.y - state.gamestate.players[1].y)**2)
        """

        self.prev_dist = math.sqrt((prev_state.player.x - closest_enemy_to_player.x)**2 + (prev_state.player.y - closest_enemy_to_player.y)**2)

        self.dist = math.sqrt((self.player.x - closest_enemy_to_player.x)**2 + (self.player.y - closest_enemy_to_player.y)**2)


    def wall_check(self):
        if self.player.x > 200 or self.player.x < -200 or self.player.y > 200 or self.player.y < -200:
            return True


    def enemy_dead_check(self):
        for enemy in self.gamestate.players:
            if enemy.id != self.player.id:
                if enemy.active == False:
                    is_already_dead = enemy.id in self.dead_enemies

                    # print(f"===============================> DEBUG FROM enemy_dead_check: is_already_dead: {is_already_dead}, enemy.id: {enemy.id}, self.dead_enemies: {self.dead_enemies}")
                    if not is_already_dead:
                        self.dead_enemies.append(enemy.id)

                        return True
                    else:

                        return False


    def run_game(self):
        reward_given = False
        if self.player.active == False:
            self.reward = -100 # punish the shit out of him for beeing dead
            reward_given = True
        
        if self.enemy_dead_check():
            self.reward = 10
            reward_given = True

        # comment this because we need previous distance from previous state which is called in __name__ == "__main__"
        # self.measure_distance()

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
        player_x, player_y = self.player.x, self.player.y

        # take closest enemy instead of the first enemy
        previous_distance = 2000
        closest_enemy = 0
        closest_dist = 0

        # TODO: check if good for loop and if good state in general
        for enemy in self.gamestate.players:
            if enemy.id != self.player.id and enemy.active == True:
                closest_dist = math.sqrt((self.player.x - enemy.x)**2 + (self.player.y - enemy.y)**2)

            if closest_dist < previous_distance:
                previous_distance = closest_dist
                closest_enemy = enemy.id

        enemy_x, enemy_y = self.gamestate.players[closest_enemy - 1].x, self.gamestate.players[closest_enemy - 1].y

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

        # check how we can implement the bodylength, we definetly need it -> Dominik implemented this
        # TODO: check whether it's good to determine between wall and enemy made obstacle
        # spe_ed_state: enemy_up, enemy_right, enemy_down, enemy_left, obstacle_up, obstacle_right, obstacle_down, obstacle_left, direction_up, direction_right, direction_down, direction_left (are we needing an action here?)
        state = [int(player_y < enemy_y), int(player_x < enemy_x), int(player_y > enemy_y), int(player_x > enemy_x), \
                int(wall_up), int(wall_right), int(wall_down), int(wall_left), \
                int(self.player.direction == 'up'), int(self.player.direction == 'right'), int(self.player.direction == 'down'), int(self.player.direction == 'left')]

        return state


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
            
            spe_ed_game = Speed(json.loads(ans))
            
            stateString = GameState(json.loads(ans))
            stateString.json_to_file(json.loads(ans), 0, initial_time)

            # print(spe_ed_game.gamestate.players)
            if not spe_ed_game.gamestate.running:
                stateString.json_to_file(json.loads(ans), 0, initial_time)
                break
            
            game_state = spe_ed_game.get_state_speed()
            game_state = np.reshape(game_state, (1, spe_ed_game.state_space))
            score = 0

            agent = DQN(spe_ed_game, params) # TODO: evaluate if it's smarter to create agent only once and only update state

            print(f"game_state: {game_state}")

            action = agent.act(game_state)
            prev_state = game_state # TODO: implement usage of var
            # exp
            prev_spe_ed_game = spe_ed_game
            # eexp

            next_state, reward, done, action_from_ai = spe_ed_game.step(action)

            action_json = json.dumps({"action": action_from_ai})
            
            if spe_ed_game.player.active != False:
                print(f"tot? :: !{spe_ed_game.player.active}")
                print(f"gesendete antwort :: {action_json}")
                await ws.send(action_json)
                # investigate why we are instant dead :-( -> wrong action send

            try:
                ans = await ws.recv()
            except Exception as e:
                print(f"the problem: {e}")
                time.sleep(2.0) # workaround for too quickly reconnecting
                break # needed, because game is over

            spe_ed_game = Speed(json.loads(ans))
            game_state = spe_ed_game.get_state_speed()
            game_state = np.reshape(game_state, (1, spe_ed_game.state_space))

            print(f"next_state ist eigentlich der previous state aus der fkt: {next_state} und hier der richtige next state: {game_state}")
            next_state = game_state # to fix this

            # TODO: evaluate if it's smart to punish if dead for the rest of the game, or only rewards for lifetime
            spe_ed_game.measure_distance_async(prev_spe_ed_game, spe_ed_game) # to fix wrong dist calculation (dirty workaround, needs to be cleaner)
            _, reward, _, _ = spe_ed_game.step(action) # reward after action is done

            score += reward
            next_state = np.reshape(next_state, (1, spe_ed_game.state_space))
            agent.remember(game_state, action, reward, next_state, done)
            game_state = next_state
            
            if params['batch_size'] > 1:
                agent.replay() # check this method here how it will be affected

            sum_of_rewards.append(score)

            results[params['name']] = sum_of_rewards

            file = open("JSON Logs/" + initial_time + "_RUNNING.txt", 'a+')
            file.write("Gewählte Aktion: ")
            file.write(action_json)
            file.write("\n")
            file.close
            
    print("AFTER game ready: TIME: ", datetime.now(), flush=True)

    agent.model.save('model/')


def main():
    global DECEASED_ENEMIES

    ep = 1 # 50
    sum_of_rewards = []

    for e in range(ep):
        asyncio.get_event_loop().run_until_complete(connection(sum_of_rewards))

        DECEASED_ENEMIES = [] # because list is always will be init with [] (maybe better implementation?)

    print(f"das ist die sum_of_rewards: {sum_of_rewards}")

if __name__ == '__main__':            
    main()
