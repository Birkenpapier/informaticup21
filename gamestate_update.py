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

COUNTER = 0

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

    # Method to get the bodylocations for each playe
    def get_players_body_locations(self, cells):

        # Get and save the location of all playerbodys
        allPlayerBodyCords = []

        playerNr = 1
        # Check for each player the location and save as a list (0-58 rows, 0-76 columns in this example)
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
    
    def get_players(self, player_list, cells):
        # Get body coordinates for each player
        body_coords = self.get_players_body_locations(cells)

        ret = []
        id = 1
        while True:
            try:
                ret.append(Player(id, player_list[str(id)], body_coords))
            except KeyError:
                break
            id += 1
        return ret
        
    def get_player(self):
        return self.players[self.you-1]

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


class Player():
    def __init__(self, id, info, body_coords):
        self.id = id
        self.x = info['x']
        self.y = info['y']
        self.direction = info['direction']
        self.speed = info['speed']
        self.active = info['active']
        self.body_coords = body_coords[id - 1]
        # self.name = info['name'] # nicht notwendig
        # TODO: implement only length of our player and not all players
        # print(f"body_coords: {body_coords}, len(body_coords): {len(body_coords)}")

    def display(self):
        print(self.id, ': ', self.x, self.y, self.direction, self.speed, self.active)

