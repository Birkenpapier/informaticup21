import numpy as np
import matplotlib.pyplot as plt
from time import sleep
import json

height = 40
width = 40

REC_STEPS = 8

#--------------------------------------------------------

mat = np.zeros((height, width), dtype=int)

y1 = width/2 - width/4
y2 = width/2 + width/4

for x in range(int(height/2), height):
	mat[x, int(y1)] = 1
	mat[x, int(y2)] = 2
	mat[x-8, int(width/2)-7] = 3
#---------------------------------------------------------

	
def valid(m, x, y, ids, others):
	return (0 <= x < height and 0 <= y < width and m[x,y] not in (ids+others))
	#Bewertung möglich (other können wände usw sein)
	

def decision_start(m ,x_m, y_m, d_m, x_e, y_e, d_e, ids):
	color = 4
	if d_m == 'n':
		me_1_move(m, x_m, y_m-1, 'w', x_e, y_e, d_e, ids, 1, color)
		me_1_move(m, x_m-1, y_m, 'n', x_e, y_e, d_e, ids, 1, color)
		me_1_move(m, x_m, y_m+1, 'o', x_e, y_e, d_e, ids, 1, color)
	elif d_m == 'o':
		me_1_move(m, x_m-1, y_m, 'n', x_e, y_e, d_e, ids, 1, color)
		me_1_move(m, x_m, y_m+1, 'o', x_e, y_e, d_e, ids, 1, color)
		me_1_move(m, x_m+1, y_m, 's', x_e, y_e, d_e, ids, 1, color)
	elif d_m == 's':
		me_1_move(m, x_m, y_m+1, 'o', x_e, y_e, d_e, ids, 1, color)
		me_1_move(m, x_m+1, y_m, 's', x_e, y_e, d_e, ids, 1, color)
		me_1_move(m, x_m, y_m-1, 'w', x_e, y_e, d_e, ids, 1, color)
	elif d_m == 'w':
		me_1_move(m, x_m+1, y_m, 's', x_e, y_e, d_e, ids, 1, color)
		me_1_move(m, x_m, y_m-1, 'w', x_e, y_e, d_e, ids, 1, color)
		me_1_move(m, x_m-1, y_m, 'n', x_e, y_e, d_e, ids, 1, color)


def me_1_move(m, x_m, y_m, d_m, x_e, y_e, d_e, ids, step, c):
	
	if valid(m, x_m, y_m, ids, []):
		if step < REC_STEPS:
			m[x_m, y_m] = c
			if d_e == 'n':
				enemy_1_move(m, x_m, y_m, d_m, x_e, y_e-1, 'w', ids+[c], step+1, c+1)
				enemy_1_move(m, x_m, y_m, d_m, x_e-1, y_e, 'n', ids+[c], step+1, c+1)
				enemy_1_move(m, x_m, y_m, d_m, x_e, y_e+1, 'o', ids+[c], step+1, c+1)
			elif d_e == 'o':
				enemy_1_move(m, x_m, y_m, d_m, x_e-1, y_e, 'n', ids+[c], step+1, c+1)
				enemy_1_move(m, x_m, y_m, d_m, x_e, y_e+1, 'o', ids+[c], step+1, c+1)
				enemy_1_move(m, x_m, y_m, d_m, x_e+1, y_e, 's', ids+[c], step+1, c+1)
			elif d_e == 's':
				enemy_1_move(m, x_m, y_m, d_m, x_e, y_e+1, 'o', ids+[c], step+1, c+1)
				enemy_1_move(m, x_m, y_m, d_m, x_e+1, y_e, 's', ids+[c], step+1, c+1)
				enemy_1_move(m, x_m, y_m, d_m, x_e, y_e-1, 'w', ids+[c], step+1, c+1)
			elif d_e == 'w':
				enemy_1_move(m, x_m, y_m, d_m, x_e+1, y_e, 's', ids+[c], step+1, c+1)
				enemy_1_move(m, x_m, y_m, d_m, x_e, y_e-1, 'w', ids+[c], step+1, c+1)
				enemy_1_move(m, x_m, y_m, d_m, x_e-1, y_e, 'n', ids+[c], step+1, c+1)
			
		else:	# last step from me
			m[x_m, y_m] = c
		
		return
		#Bewertung
	return
	#Bewertung
	
def enemy_1_move(m, x_m, y_m, d_m, x_e, y_e, d_e, ids, step, c):

	if valid(m, x_e, y_e, ids, []):
		m[x_e, y_e] = c
		if d_m == 'n':
			me_1_move(m, x_m, y_m-1, 'w', x_e, y_e, d_e, ids+[c], step, c+1)
			me_1_move(m, x_m-1, y_m, 'n', x_e, y_e, d_e, ids+[c], step, c+1)
			me_1_move(m, x_m, y_m+1, 'o', x_e, y_e, d_e, ids+[c], step, c+1)
		elif d_m == 'o':
			me_1_move(m, x_m-1, y_m, 'n', x_e, y_e, d_e, ids+[c], step, c+1)
			me_1_move(m, x_m, y_m+1, 'o', x_e, y_e, d_e, ids+[c], step, c+1)
			me_1_move(m, x_m+1, y_m, 's', x_e, y_e, d_e, ids+[c], step, c+1)
		elif d_m == 's':
			me_1_move(m, x_m, y_m+1, 'o', x_e, y_e, d_e, ids+[c], step, c+1)
			me_1_move(m, x_m+1, y_m, 's', x_e, y_e, d_e, ids+[c], step, c+1)
			me_1_move(m, x_m, y_m-1, 'w', x_e, y_e, d_e, ids+[c], step, c+1)
		elif d_m == 'w':
			me_1_move(m, x_m+1, y_m, 's', x_e, y_e, d_e, ids+[c], step, c+1)
			me_1_move(m, x_m, y_m-1, 'w', x_e, y_e, d_e, ids+[c], step, c+1)
			me_1_move(m, x_m-1, y_m, 'n', x_e, y_e, d_e, ids+[c], step, c+1)
		
		return
		#Bewertung
	return
	#Bewertung
	
plt.matshow(mat)
plt.show()

decision_start(mat, int(height/2), int(y1), 'n', int(height/2), int(y2), 'n', [1,2,3])

plt.matshow(mat)
plt.show()
# start(me) -> rec(me) 	-> rec(enemy)	-> rec(me)
#										-> rec(me)
#										-> rec(me)
#
#						-> rec(enemy)	-> rec(me)
#										-> rec(me)
#										-> rec(me)
#
#						-> rec(enemy)	-> rec(me)
#										-> rec(me)
#										-> rec(me)
#
#			-> rec(me)	-> rec(enemy)	-> rec(me)
#										-> rec(me)
#										-> rec(me)
#
#						-> rec(enemy)	-> rec(me)
#										-> rec(me)
#										-> rec(me)
#
#						-> rec(enemy)	-> rec(me)
#										-> rec(me)
#										-> rec(me)
#
#			-> rec(me)	-> rec(enemy)	-> rec(me)
#										-> rec(me)
#										-> rec(me)
#
#						-> rec(enemy)	-> rec(me)
#										-> rec(me)
#										-> rec(me)
#
#						-> rec(enemy)	-> rec(me)
#										-> rec(me)
#										-> rec(me)
class GameState:
	def __init__(self, data):
		#print(data) # print the received json
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
				ret.append(self.Player(id, player_list[str(id)]))
			except KeyError:
				break
			id += 1
		return ret
		
	class Player:
		def __init__(self, id, info):
			self.id = id
			self.x = info['x']
			self.y = info['y']
			self.direction = info['direction']
			self.speed = info['speed']
			self.active = info['active']
			#self.name = info['name'] nicht notwendig
	
		def display(self):
			print(self.id, ': ', self.x, self.y, self.direction, self.speed, self.active)

#