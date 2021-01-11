from speed_env_luh_update import Speed
from gamestate import GameState, Player
import math

class Evaluation():
    
    def __init__(self, env):    #env = Speed()
        self.env = env
        self.reward = 0
        
    def get_reward(self):
    
        prev_gamestate = self.env.prev_gamestate
        cur_gamestate = self.env.gamestate
        
        #evaluate state/cells/positions
        self.player_attacks_opponent(prev_gamestate, cur_gamestate)
        self.ai_suicide(prev_gamestate, cur_gamestate)
        self.measure_distance_async(prev_gamestate, cur_gamestate)
        #calculate the following reward based on the evaluation
        self.env.reward = self.calc_reward()
        
        return self.env.reward, self.env.returned_action, self.env.done
        
    def calc_reward(self):
        reward_given = False

        if self.moved_to_enemy_check():
            self.reward = 1
            reward_given = True

        if self.env.player.active == False:
            self.reward = -100 # punish the shit out of him for beeing dead
            reward_given = True
        
        if self.enemy_dead_check(self.env.gamestate):
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
            print(f"reward funktion results: {self.env.dist}, {self.env.prev_dist}, {self.env.dist < self.env.prev_dist}")
            if self.env.dist < self.env.prev_dist:
                self.reward = 1
            else:
                self.reward = -1
                
        #add reward to game
        return self.reward
        
    def player_length_check(self, prev_gamestate, cur_gamestate):
        return (len(prev_gamestate.get_player().body_coords) < len(cur_gamestate.get_player().body_coords))
        
    def moved_to_enemy_check(self):
        return self.env.moved_to_enemy
        
    def ai_suicide_check(self):
        return self.env.suicide
        
    def enemy_dead_check(self, cur_gamestate):
        for enemy in cur_gamestate.players:
            if enemy.id != cur_gamestate.get_player().id:
                if enemy.active == False:
                    is_already_dead = enemy.id in self.env.dead_enemies

                    # print(f"===============================> DEBUG FROM enemy_dead_check: is_already_dead: {is_already_dead}, enemy.id: {enemy.id}, self.dead_enemies: {self.dead_enemies}")
                    if not is_already_dead:
                        self.env.dead_enemies.append(enemy.id)

                        return True
                    else:

                        return False
    
    #not used ... could use instead off 200 the width and height
    def wall_check(self):
        if self.player.x > 200 or self.player.x < -200 or self.player.y > 200 or self.player.y < -200:
            return True
    
    #all are getting GameStates: prev_gamestate and cur_gamestate 
    def measure_distance_async(self, prev_gamestate, cur_gamestate):        #check
        # print(f"2==2: die berechnung aus measure_distance_async: self.player.x: {self.player.x}, self.player.y: {self.player.y}, ")
        # print(f"3==3: die berechnung aus measure_distance_async: self.prev_state.players[0].x: {prev_state.gamestate.players[0].x}, self.prev_state.players[0].y: {prev_state.gamestate.players[0].y}, ")
        # print(f"4==4: die berechnung aus measure_distance_async: self.prev_state.players[0].x: {state.gamestate.players[0].x}, self.prev_state.players[0].y: {state.gamestate.players[0].y}, ")

        previous_distance = 2000
        closest_enemy = 0
        closest_dist = 0
        
        cur_player = cur_gamestate.get_player()
        prev_player = prev_gamestate.get_player()

        # TODO: check if good for loop and if good state in general
        for enemy in prev_gamestate.players:
            if enemy.id != cur_player.id and enemy.active == True:
                closest_dist = math.sqrt((cur_player.x - enemy.x)**2 + (cur_player.y - enemy.y)**2)

            if closest_dist < previous_distance:
                previous_distance = closest_dist
                closest_enemy = enemy.id

        closest_enemy_to_player = prev_gamestate.players[closest_enemy - 1]

        self.env.prev_dist = math.sqrt((prev_player.x - closest_enemy_to_player.x)**2 + (prev_player.y - closest_enemy_to_player.y)**2)

        self.env.dist = math.sqrt((cur_player.x - closest_enemy_to_player.x)**2 + (cur_player.y - closest_enemy_to_player.y)**2)

    
    def player_attacks_opponent(self, prev_gamestate, cur_gamestate):       #check
        ai_id = cur_gamestate.get_player().id

        enemy_prev_x_positions = []
        enemy_prev_y_positions = []

        enemy_now_x_positions = []
        enemy_now_y_positions = []

        #Get all player position
        for player in prev_gamestate.players:
            if(prev_gamestate.get_player().id != player.id):
                enemy_prev_x_positions.append(player.x)
                enemy_prev_y_positions.append(player.y)
            else:
                ai_prev_x_pos = player.x
                ai_prev_y_pos = player.y
        for player in cur_gamestate.players:
            if(cur_gamestate.get_player().id != player.id):
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
                self.env.moved_to_enemy = True
                return

        for enemy_prev_y in enemy_prev_y_positions:
            old_distance = abs(enemy_prev_y - ai_prev_y_pos)
            new_distance = abs(enemy_prev_y - ai_now_y_pos)
            if(new_distance < old_distance):
                self.env.moved_to_enemy = True
                return
                
        self.env.moved_to_enemy = False
        return
        
    def ai_suicide(self, prev_gamestate, cur_gamestate):
        ai_id = cur_gamestate.get_player().id

        players = cur_gamestate.players

        #Check if player was dead in the last round
        players_last_round = prev_gamestate.players
        for player in players_last_round:
            if(player.id == ai_id):
                if(player.active == False):
                    self.env.suicide = False
                    return

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
                                for x, y in enemy.body_coords:
                                    if(((x == ai_x -1) or (x == ai_x +1) or (x == ai_x )) and ((y == ai_y - 1) or (y == ai_y +1) or (y == ai_y))):
                                        print("Ai ran into enemy")
                                        self.env.suicide = False
                                        return 



                        #print("suicide")
                        self.env.suicide = True
                        return
        self.env.suicide = False
        return
        
    def enemy_ran_into_aibody(self, prev_gamestate, cur_gamestate):

        ai_id = cur_gamestate.get_player().id

        players = cur_gamestate.players

        b = False

        for player in players:
            if(player.active == False):
                print("Dead")
                print(player.x)
                print(player.y)
                print(player.body_coords)
                b = True

            if(b == True):
                print(player.body_coords)

        if(b== True):
            time.sleep(500000)


        





        # #Get all player position
        # for player in prev_gamestate.gamestate.players:
        #     if(prev_gamestate.player.id != player.id):
        #         enemy_prev_x_positions.append(player.x)
        #         enemy_prev_y_positions.append(player.y)
        #     else:
        #         ai_prev_x_pos = player.x
        #         ai_prev_y_pos = player.y
        # for player in cur_gamestate.gamestate.players:
        #     if(cur_gamestate.player.id != player.id):
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