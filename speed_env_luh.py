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

URI = "wss://msoll.de/spe_ed?key=LSIS7VOFLXCISR3K4YUSZ3CN2Z3CF74PEB7EKE4AQ7PDVKAGTYVOZVXP"

HEIGHT = 20      # number of steps vertically from wall to wall of screen
WIDTH = 20       # number of steps horizontally from wall to wall of screen

SNAKE_SHAPE = 'square'
SNAKE_COLOR = 'black'
SNAKE_START_LOC_H = 0
SNAKE_START_LOC_V = 0

APPLE_SHAPE = 'circle'
APPLE_COLOR = 'green'


class GameState():
    def __init__(self, data):
        print(data) # print the received json
        self.width = data['width']
        self.height = data['height']
        self.cells = data['cells']
        self.pl = data['players']
        self.players = self.get_players(data['players'])
        self.you = data['you']
        self.running = data['running']
        try:
            self.deadline = data['deadline']
        except KeyError:
            self.deadline = ''
        
    def get_players(self, player_list):
        ret = []
        id = 1
        while True:
            try:
                ret.append(Player(id, player_list[str(id)]))
            except KeyError:
                break
            id += 1
        return ret


class Player():
    def __init__(self, id, info):
        self.id = id
        self.x = info['x']
        self.y = info['y']
        self.direction = info['direction']
        self.speed = info['speed']
        self.active = info['active']
        # self.name = info['name'] # nicht notwendig

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

        self.player = self.gamestate.players[int(self.gamestate.you)] # self.GameState.Player()
        self.snake_body = [] # snake body, add first element (for location of snake's head)

        # TODO: implement here all the enemys
        # distance between first enemy and player
        self.dist = math.sqrt((self.player.x - self.gamestate.players[0].x,)**2 + (self.player.y - self.gamestate.players[0].y)**2)

        """
        # distance between apple and snake
        self.dist = math.sqrt((self.snake.xcor()-self.apple.xcor())**2 + (self.snake.ycor()-self.apple.ycor())**2)
        """

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def measure_distance(self):
        self.prev_dist = self.dist
        # self.dist = math.sqrt((self.snake.xcor()-self.apple.xcor())**2 + (self.snake.ycor()-self.apple.ycor())**2)
        self.dist = math.sqrt((self.player.x - self.gamestate.players[0].x,)**2 + (self.player.y - self.gamestate.players[0].y)**2)

    """
    def body_check_snake(self):
        if len(self.snake_body) > 1:
            for body in self.snake_body[1:]:
                if body.distance(self.snake) < 20:
                    # self.reset_score()
                    return True     


    def body_check_apple(self):
        if len(self.snake_body) > 0:
            for body in self.snake_body[:]:
                if body.distance(self.apple) < 20:
                    return True


    def wall_check(self):
        if self.snake.xcor() > 200 or self.snake.xcor() < -200 or self.snake.ycor() > 200 or self.snake.ycor() < -200:
            # self.reset_score()
            return True
    """

    """
    def reset(self):
        for body in self.snake_body:
            body.goto(1000, 1000)

        self.snake_body = []
        self.snake.goto(SNAKE_START_LOC_H, SNAKE_START_LOC_V)
        self.snake.direction = 'stop'
        self.reward = 0
        self.total = 0
        self.done = False

        state = self.get_state()

        return state
    """
    """
    def run_game(self):
        reward_given = False
        self.move_snake()
        
        if self.move_apple():
            self.reward = 10
            reward_given = True
        
        self.move_snakebody()
        self.measure_distance()
        
        if self.body_check_snake():
            self.reward = -100
            reward_given = True
            self.done = True
        
        if self.wall_check():
            self.reward = -100
            reward_given = True
            self.done = True

        if not reward_given:
            if self.dist < self.prev_dist:
                self.reward = 1
            else:
                self.reward = -1
    """
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
        
        if self.wall_check():
            self.reward = -100
            reward_given = True
            self.done = True
        """

        if not reward_given:
            if self.dist < self.prev_dist:
                self.reward = 1
            else:
                self.reward = -1

    """
    # AI agent
    def step(self, action):
        if action == 0:
            self.go_up()
        if action == 1:
            self.go_right()
        if action == 2:
            self.go_down()
        if action == 3:
            self.go_left()
        self.run_game()
        state = self.get_state()
        return state, self.reward, self.done, {}
    """
    
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

        return state, self.reward, self.done, {}

    """
    def get_state(self):
        # snake coordinates abs
        self.snake.x, self.snake.y = self.snake.xcor()/WIDTH, self.snake.ycor()/HEIGHT   
        # snake coordinates scaled 0-1
        self.snake.xsc, self.snake.ysc = self.snake.x/WIDTH+0.5, self.snake.y/HEIGHT+0.5
        # apple coordintes scaled 0-1 
        self.apple.xsc, self.apple.ysc = self.apple.x/WIDTH+0.5, self.apple.y/HEIGHT+0.5

        # wall check
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

        # state: apple_up, apple_right, apple_down, apple_left, obstacle_up, obstacle_right, obstacle_down, obstacle_left, direction_up, direction_right, direction_down, direction_left
        # spe_ed_state: enemy_up, enemy_right, enemy_down, enemy_left, obstacle_up, obstacle_right, obstacle_down, obstacle_left, turn_left, turn_right, slow_down, speed_up, change_nothing
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
            
        # print(state) # state of the current step of the game

        return state
    """

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


        return state



async def connection():

	async with websockets.connect(URI) as ws:
	
		print("Waiting for initial state...", flush=True)
		print("PRIOR game ready: TIME: ", datetime.now(), flush=True)
		
		started = False

		while True:
			ans = await ws.recv()
			
			if not started : started = True
			
			# state = Speed.GameState(json.loads(ans))
			state = Speed(json.loads(ans))
			# print(state.gamestate.players)
			if not state.gamestate.running:
				break
			
			action = "speed_up"
			action_json = json.dumps({"action": action})
			await ws.send(action_json)
			print("Action sent: ", action)
			
	
	print("AFTER game ready: TIME: ", datetime.now(), flush=True)
	

asyncio.get_event_loop().run_until_complete(connection())


"""
if __name__ == '__main__':            
    human = True
    env = Speed(human=human)

    if human:
        while True:
            env.run_game()
"""