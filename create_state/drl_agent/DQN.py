from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers.core import Dense, Dropout
import random
import numpy as np
import pandas as pd
from operator import add


class DQNAgent(object):

    def __init__(self):
        self.reward = 0
        self.gamma = 0.9
        self.dataframe = pd.DataFrame()
        self.short_memory = np.array([])
        self.agent_target = 1
        self.agent_predict = 0
        self.learning_rate = 0.0005
        self.model = self.network()
        # self.model = self.network("weights.hdf5") # TODO: to load already trained model
        self.epsilon = 0
        self.actual = []
        self.memory = []

    def set_reward(self, player, crash):
        self.reward = 0
        if crash:
            self.reward = -10
            return self.reward
        if player.eaten:
            self.reward = 10
        return self.reward

    def network(self, weights=None):
        model = Sequential()
        model.add(Dense(output_dim=13350, activation='relu', input_dim=4450))
        model.add(Dropout(0.15))
        model.add(Dense(output_dim=13350, activation='relu'))
        model.add(Dropout(0.15))
        model.add(Dense(output_dim=13350, activation='relu'))
        model.add(Dropout(0.15))
        model.add(Dense(output_dim=12, activation='softmax'))
        opt = Adam(self.learning_rate)
        model.compile(loss='mse', optimizer=opt)

        if weights:
            model.load_weights(weights)
        return model

    def remember(self, state, action, reward, done):
        self.memory.append((state, action, reward, done))
