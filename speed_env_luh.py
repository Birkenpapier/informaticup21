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
def player_attacks_opponent(prev_game, spe_ed_game):

        ai_id = spe_ed_game.player.id

        enemy_prev_x_positions = []
        enemy_prev_y_positions = []

        enemy_now_x_positions = []
        enemy_now_y_positions = []

        #Get all player position
        for player in prev_game.gamestate.players:
            if(prev_game.player.id != player.id):
                enemy_prev_x_positions.append(player.x)
                enemy_prev_y_positions.append(player.y)
            else:
                ai_prev_x_pos = player.x
                ai_prev_y_pos = player.y
        for player in spe_ed_game.gamestate.players:
            if(spe_ed_game.player.id != player.id):
                enemy_now_x_positions.append(player.x)
                enemy_now_y_positions.append(player.y)
            else:
                ai_now_x_pos = player.x
                ai_now_y_pos = player.y


        # print(enemy_prev_x_positions)
        # print(enemy_prev_y_positions)

        # print(enemy_now_x_positions)
        # print(enemy_now_y_positions)

        #Check if ai moved to an enemyhead
        for enemy_prev_x in enemy_prev_x_positions:
            old_distance = abs(enemy_prev_x - ai_prev_x_pos)
            new_distance = abs(enemy_prev_x - ai_now_x_pos)
            if(new_distance < old_distance):
                return True

        for enemy_prev_y in enemy_prev_y_positions:
            old_distance = abs(enemy_prev_y - ai_prev_y_pos)
            new_distance = abs(enemy_prev_y - ai_now_y_pos)
            if(new_distance < old_distance):
                return True

        return False


def enemy_ran_into_aibody(prev_game, spe_ed_game):

        ai_id = spe_ed_game.player.id

        players = spe_ed_game.gamestate.players

        b = False

        for player in players:
            if(player.active == False):
                print("Dead")
                print(player.x)
                print(player.y)
                print(player.player_body_coords)
                b = True

            if(b == True):
                print(player.player_body_coords)

        if(b== True):
            time.sleep(500000)


        





        # #Get all player position
        # for player in prev_game.gamestate.players:
        #     if(prev_game.player.id != player.id):
        #         enemy_prev_x_positions.append(player.x)
        #         enemy_prev_y_positions.append(player.y)
        #     else:
        #         ai_prev_x_pos = player.x
        #         ai_prev_y_pos = player.y
        # for player in spe_ed_game.gamestate.players:
        #     if(spe_ed_game.player.id != player.id):
        #         enemy_now_x_positions.append(player.x)
        #         enemy_now_y_positions.append(player.y)
        #     else:
        #         ai_now_x_pos = player.x
        #         ai_now_y_pos = player.y


        # # print(enemy_prev_x_positions)
        # # print(enemy_prev_y_positions)

        # # print(enemy_now_x_positions)
        # # print(enemy_now_y_positions)

        # #Check if ai moved to an enemyhead
        # for enemy_prev_x in enemy_prev_x_positions:
        #     old_distance = abs(enemy_prev_x - ai_prev_x_pos)
        #     new_distance = abs(enemy_prev_x - ai_now_x_pos)
        #     if(new_distance < old_distance):
        #         return True

        # for enemy_prev_y in enemy_prev_y_positions:
        #     old_distance = abs(enemy_prev_y - ai_prev_y_pos)
        #     new_distance = abs(enemy_prev_y - ai_now_y_pos)
        #     if(new_distance < old_distance):
        #         return True

        return False

def ai_suicide(prev_game, spe_ed_game):

        ai_id = spe_ed_game.player.id

        players = spe_ed_game.gamestate.players

        #Check if player was dead in the last round
        players_last_round = prev_game.gamestate.players
        for player in players_last_round:
            if(player.id == ai_id):
                if(player.active == False):
                    return False

        #Check if players died between the 2 rounds
        for player in players:
            if(player.id == ai_id):
                    ai_x = player.x
                    ai_y = player.y

                    if(player.active == False):
                        #print("AI is dead")

                        #Check if ran into enemy body
                        for enemy in players:
                            if(enemy.id != ai_id):
                                for x, y in enemy.player_body_coords:
                                    if(((x == ai_x -1) or (x == ai_x +1) or (x == ai_x )) and ((y == ai_y - 1) or (y == ai_y +1) or (y == ai_y))):
                                        print("Ai ran into enemy")
                                        return False 



                        #print("suicide")
                        return True

        return False

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
        
        self.prev_dist = 0 # TODO: evaluate if it's smarter if it only once get initialized (maybe better only speed once init?)
        self.prev_body_len = 0

        self.dead_enemies = DECEASED_ENEMIES # list with all deceased enemies
        self.suicide = False
        self.moved_to_enemy = False

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


    #check if ai kills itself
    def ai_suicide_check(self):
        return self.suicide

    def moved_to_enemy_check(self):
        return self.moved_to_enemy
    



        

       

    def run_game(self):
        reward_given = False

        if self.moved_to_enemy_check():
            self.reward = 1
            reward_given = True

        if self.player.active == False:
            self.reward = -100 # punish the shit out of him for beeing dead
            reward_given = True
        
        if self.enemy_dead_check():
            self.reward = 10
            reward_given = True

        if self.ai_suicide_check():
            self.reward = -150
            reward_given = True


        #if self.player_attacks_opponent(self.prev_state, self.state):
         #   self.reward = 15

        # comment this because we need previous distance from previous state which is called in __name__ == "__main__"
        # self.measure_distance()

        if not reward_given:
            print(f"reward funktion results: {self.dist}, {self.prev_dist}, {self.dist < self.prev_dist}")
            if self.dist < self.prev_dist:
                self.reward = 1
            else:
                self.reward = -1


    # TODO: precheck if slow down or speed up is possible -> else is instant death
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
    params['epsilon'] = 0.5
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

            print(f"previouse game_state: {game_state}")
            prev_state = game_state

            action = agent.act(game_state)
            # prev_state = game_state # TODO: implement usage of var
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

            # TODO: investivate -> AttributeError: 'NoneType' object has no attribute 'resume_reading'; why is this happening?
            try:
                ans = await ws.recv()
            except Exception as e:
                print(f"the problem: {e}")
                time.sleep(2.0) # workaround for too quickly reconnecting
                break # needed, because game is over

            spe_ed_game = Speed(json.loads(ans))
            game_state = spe_ed_game.get_state_speed()
            game_state = np.reshape(game_state, (1, spe_ed_game.state_space))

            print(f"new next game_state:  {game_state}")
            next_state = game_state # to fix this old state as next state

            # #check if player moved to enemys head            
            if player_attacks_opponent(prev_spe_ed_game, spe_ed_game):
                self.moved_to_enemy = True

            #check if player moved to enemys head
            # if enemy_ran_into_aibody(prev_spe_ed_game, spe_ed_game):
            #     print("Enemy died")
            # else:
            #     print("Enmey alive")

            if ai_suicide(prev_spe_ed_game, spe_ed_game):
                self.suicide = True


            # TODO: evaluate if it's smart to punish if dead for the rest of the game, or only rewards for lifetime
            spe_ed_game.measure_distance_async(prev_spe_ed_game, spe_ed_game) # to fix wrong dist calculation (dirty workaround, needs to be cleaner)
            # spe_ed_game.player_length_check(prev_spe_ed_game, spe_ed_game) # TODO: improve shitty calculation in gamestate.py
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

    ep = 20 # 50
    sum_of_rewards = []

    for e in range(ep):
        print(f"EPOCH {e} from {ep}")

        asyncio.get_event_loop().run_until_complete(connection(sum_of_rewards))

        DECEASED_ENEMIES = [] # because list is always will be init with [] (maybe better implementation?)

    print(f"das ist die sum_of_rewards: {sum_of_rewards}")

if __name__ == '__main__':            
    main()
