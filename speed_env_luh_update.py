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
    def __init__(self, env_info={'state_space' : None}):
        self.gamestate = None
        self.returned_action = None

        self.done = False
        self.reward = 0
        self.action_space = 5
        self.state_space = 12
        #tester
        self.step = 0
        self.running = True
        self.active = True
        #

        self.total, self.maximum = 0, 0
        self.env_info = env_info

        self.player = None # self.GameState.Player()
        self.snake_body = [] # snake body, add first element (for location of snake's head)

        self.dist = 3.0
        #
        #if self.gamestate.players[0].id != self.player.id:
        #    self.dist = math.sqrt((self.player.x - self.gamestate.players[0].x)**2 + (self.player.y - self.gamestate.players[0].y)**2)
        #else:
        #    self.dist = math.sqrt((self.player.x - self.gamestate.players[1].x)**2 + (self.player.y - self.gamestate.players[1].y)**2)
        
        self.prev_dist = 0 # TODO: evaluate if it's smarter if it only once get initialized (maybe better only speed once init?)
        self.prev_body_len = 0

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


    def player_length_check(self, prev_state, state):
        if len(prev_state.player.body_coords) < len(state.player.body_coords):
            
            return True


    def get_reward_speed(self):
        reward_given = False

        if self.player.active == False:
            self.reward = -100 # punish the shit out of him for beeing dead
            reward_given = True
        
        if self.enemy_dead_check():
            self.reward = 10
            reward_given = True

        if not reward_given:
            print(f"reward funktion results: {self.dist}, {self.prev_dist}, {self.dist < self.prev_dist}")
            if self.dist < self.prev_dist:
                self.reward = 1
            else:
                self.reward = -1
                
        return self.reward, self.returned_action, self.done


    # TODO: precheck if slow down or speed up is possible -> else is instant death
    # AI agent
    def move(self, action):
        move = 'change_nothing'
        if action == 0:
            self.returned_action = 0
            move = 'turn_left'
        if action == 1:
            self.returned_action = 1
            move = 'turn_right'
        if action == 2:
            self.returned_action = 2
            move = 'slow_down'
        if action == 3:
            self.returned_action = 3
            move = 'speed_up'
        if action == 4:
            self.returned_action = 4
            move = 'change_nothing'

        return move # {}
        
    def update(self, state):
        self.gamestate = state
        self.step += 1
        self.running = state.running
        self.player = state.get_player()
        self.active = self.player.active


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
       
    def get_player(self):
        return self.game_state.get_player()


async def connection():
    # injection of DQN agent
    results = dict()

    spe_ed_enviroment = {
        "action_space": 5,
        "state_space": 12
    }
    
    agent = DQN(spe_ed_enviroment) # init agent only once instead of every iteration
    score = 0
    
    try:

        async with websockets.connect(URI) as ws:

            print("Waiting for initial state...", flush=True)
            print("PRIOR game ready: TIME: ", datetime.now(), flush=True)
            start_time = datetime.now()
            initial_time = start_time.strftime("%m.%d.%Y, %H.%M.%S")
            started = False
            
            #Speed game
            env = Speed()
            
            prev_state = np.zeros(shape=(env.state_space,))
            cur_state = np.zeros(shape=(env.state_space,))
            
            while True:
                ans = None
                try:
                    ans = await ws.recv()
                except :
                    print("Connection:: Second attempt to receive")
                    try:
                        ans = await ws.recv()
                    except Exception as e:
                        print(e)
                        print("Connecton:: No Connection.")
                        break
                        
                print("Connection:: Received")
                
                #load answ
                json_ans = json.loads(ans)
                state = GameState(json_ans)
                
                env.update(state)
                print("Speed:: State updated")
                
                cur_state = np.reshape(env.get_state_speed(), (env.state_space,))
                
                if started :
                    
                    reward, action_taken, done = env.get_reward_speed()
                    
                    score += reward
                    
                    print("Speed:: Score:", score, "Reward:", reward)
                    
                    agent.remember(prev_state, action_taken, reward, cur_state, done)
                    
                    if agent.batch_size > 1:
                        agent.replay()
                    
                else :
                    started = True
                    #enemies_alive, enemies_dead = env.get_enemies()
                    
                if not env.running :
                    print("Speed:: Game no longer running")
                    break
                    
                if not env.active:
                    print("Speed:: Player not active. Game ended")
                    break
                #abbruch!!!
                
                print("------------------------------------")
                
                #the agent predicts a move
                action = agent.act(cur_state)
                
                prev_state = cur_state
                #Speed returns the next action (step)
                move = env.move(action)
                
                await ws.send(json.dumps({"action": move}))
                
                print("Connection:: Action sent:", move)
            await ws.close()
            print("Connection:: Connection closed")
    except :
        print("HTTP 429")
        time.sleep(30)
    print("AFTER game ready: TIME: ", datetime.now(), flush=True)

    agent.model.save('model/')
    print("AI:: Model saved")
    agent.save_memory('memories.obj')
    agent.save_params('params.obj')
    return score

def main():
    global DECEASED_ENEMIES

    ep = 10 # 20, 50
    sum_of_rewards = []

    for e in range(ep):
        print("===================================")
        print(f"EPOCH {e} from {ep}")

        sum_of_rewards.append(asyncio.get_event_loop().run_until_complete(connection()))
        
        DECEASED_ENEMIES = [] # because list is always will be init with [] (maybe better implementation?)

    print(f"das ist die sum_of_rewards: {sum_of_rewards}")

if __name__ == '__main__':            
    main()
