import make_decision as make_d
import pylogging as IC20log
import tensorflow as tf
import numpy as np
import time
import os

from bottle import post, request, run, BaseRequest
from keras.utils import to_categorical
from drl_agent.DQN import DQNAgent
from create_training_data import *
from random import randint
from game_state import *
from PIL import Image

init_action = None
state_init1 = None
state_init2 = None
state_old = None
counter_games = 0

game_state = game_state()
agent = DQNAgent()


def reward_function(game):
    if game["round"] == 1:
        return 0
    if game["outcome"] == 'pending':
        return 1 # + game["population_reduction"] * 3
    elif game["outcome"] == 'win':
        return 20
    elif game["outcome"] == 'loss':
        return -20


def init_game(game):
    global state_init1
    state_init1 = game
    action = [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0] # init action without changes or moves

    return action


def init_game_next(game_json, game, action):
    global state_init1
    global state_init2
    state_init2 = game

    reward1 = reward_function(game_json)

    done = None
    if reward1 == 20 or reward1 == -20:
        done = True
    else:
        done = False

    agent.remember(state_init1, action, reward1, done)


@post("/")
def index():
    global init_action
    global counter_games
    global state_old

    game = request.json
    print(f'-----------------------> round: {game["round"]}, outcome: {game["outcome"]}')
    game_state.update_state(game)

    if game is not None:
        state = create_save_TD(game_state)

    try:
        if game["round"] == 1:
            init_action = init_game(state)
            init_action = {"type": "endRound"}
    
            return init_action
        
        if game["round"] == 2:
            init_action_next = init_game_next(game, state, init_action)
            # TODO here comes the answer from the agent

    except Exception as e:
        IC20log.getLogger("Index").error(str(e))
    # print(f"this is the action: {action}")

    agent.epsilon = 80 - counter_games

    try:
        state_old = np.hstack(state) # how to safe the old state after the call of the method?

        # perform random actions based on agent.epsilon, or choose the action
        if randint(0, 200) < agent.epsilon:
            final_move = to_categorical(randint(0, 11), num_classes=12)
            print(f"final_move based random:     {final_move}")
        else:
            # predict action based on the old state
            state_old = np.hstack(state)

            prediction = agent.model.predict(state_old.reshape((1, 4450)))        
            final_move = to_categorical(np.argmax(prediction[0]), num_classes=12)
            print(f"final_move based prediction: {final_move}")
            
        # perform new move and get new state
        state_new = np.hstack(state)

        # set reward for the new state
        reward = reward_function(game)
    except Exception as e:
        IC20log.getLogger("Index").error(str(e))

    done = None
    if reward == 20 or reward == -20:
        done = True
    else:
        done = False
    
    # store the new data into a long term memory
    agent.remember(state_old, final_move, reward, done)

    if game["outcome"] == 'loss' or game["outcome"] == 'win':
        counter_games += 1
    elif game["outcome"] == 'win':
        img = Image.open('./data/hiclipart.png')
        img.show()

    # saving the trained model    
    if counter_games == 20:
        agent.model.save_weights('weights.hdf5')
        counter_games += 1

    print(f"counter_games: {counter_games}")

    action = make_d.Action.create_Action(game_state, final_move)

    return action


if __name__ == '__main__':
    port = 50123

    # Workaround for the current problem of incopability to work with CUDA and TF -> using CPU this way in code
    # os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    os.environ['CUDA_VISIBLE_DEVICES'] = ''

    if tf.test.gpu_device_name():
        print('[DEBUG] GPU found')
    else:
        print("[DEBUG] No GPU found")
    # till here Workaround

    IC20log.getLogger("Server Main").info("starting server at Port %s" % port )
    BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
    run(host="0.0.0.0", port=port, quiet=True)