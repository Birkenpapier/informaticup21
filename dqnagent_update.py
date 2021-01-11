from keras.optimizers import Adam
import matplotlib.pyplot as plt
from keras.layers import Dense
from collections import deque
from datetime import datetime
from keras import Sequential
from keras.utils.vis_utils import plot_model
import numpy as np
import pickle
import websockets
import asyncio
import turtle
import random
import keras
import time
import math
import json
import os

class DQN():
    """ Deep Q Network """
    def __init__(self, env):
        self.params = dict()
        self.load_params('params.obj', False)
    
        self.action_space = env['action_space']
        self.state_space = env['state_space']
        
        self.epsilon = self.params['epsilon'] 
        self.gamma = self.params['gamma'] 
        self.batch_size = self.params['batch_size'] 
        self.epsilon_min = self.params['epsilon_min'] 
        self.epsilon_decay = self.params['epsilon_decay'] 
        self.learning_rate = self.params['learning_rate']
        self.layer_sizes = self.params['layer_sizes']
        self.memory = deque(maxlen=2500)
        # self.model = self.build_model()

        if os.path.isfile('models/saved_model.pb'):
            # print("model exist") # he's loading it every time?
            self.model = keras.models.load_model('models/')
            print("AI:: Model loaded")
            self.load_memory('memories.obj')
        else:
            # print ("File not exist")
            self.model = self.build_model()
            plot_model(self.model, to_file='model_pl.png', show_shapes=True, show_layer_names= True)
            print("AI:: Model built")
            #self.load_params('params.obj', False)   


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
            print("AI:: Random")
            return random.randrange(self.action_space)
        act_values = self.model.predict(state.reshape(1,-1))
        print("AI:: Predicted", act_values)
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
    
    def save_memory(self, file_path):
        file = open(file_path, 'wb')
        pickle.dump(self.memory, file)
        file.close()
        print("AI:: Memory saved")
        
    def load_memory(self, obj_name):
        if os.path.isfile(obj_name): 
            file = open(obj_name, 'rb')
            obj_deque = pickle.load(file)
            self.memory += obj_deque    #what if saved_memory > memory len
            file.close()
            print("AI:: Memory loaded")
        else:
            print("AI:: No file found")
    
    def save_params(self, file_path):
        file = open(file_path, 'wb')
        self.params['epsilon'] = self.epsilon    #nur raten = 1
        self.params['gamma'] = self.gamma
        self.params['batch_size'] = self.batch_size
        self.params['epsilon_min'] = self.epsilon_min
        self.params['epsilon_decay'] = self.epsilon_decay
        self.params['learning_rate'] = self.learning_rate
        self.params['layer_sizes'] = self.layer_sizes
        pickle.dump(self.params, file)
        file.close()
        print("AI:: Params saved")
    
    def load_params(self, obj_name, reset):
        if not reset and  os.path.isfile(obj_name):
            file = open(obj_name, 'rb')
            self.params = pickle.load(file)
            file.close()
            print("AI:: Params loaded    Epsilon:", self.params['epsilon'])
        else:
            self.params['epsilon'] = 1    #nur raten = 1
            self.params['gamma'] = .9
            self.params['batch_size'] = 8
            self.params['epsilon_min'] = .01
            self.params['epsilon_decay'] = .995
            self.params['learning_rate'] = 0.0005
            self.params['layer_sizes'] = [94, 188, 94]
            self.params['tau'] = 0.125           
            print("AI:: Params set to standard")
