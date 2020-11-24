import asyncio
import websockets
from datetime import datetime
import json

uri = "wss://msoll.de/spe_ed?key=LSIS7VOFLXCISR3K4YUSZ3CN2Z3CF74PEB7EKE4AQ7PDVKAGTYVOZVXP"

class GameState:
		
	def __init__(self, data):
		self.width = data['width']
		self.height = data['height']
		self.cells = data['cells']
		self.pl = data['players']
		self.players = self.getPlayers(data['players'])
		self.you = data['you']
		self.running = data['running']
		self.deadline = data['deadline']
		
	def getPlayers(self, player_list):
		ret = []
		id = 1;
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

async def connection():

	async with websockets.connect(uri) as ws:
	
		print("Waiting for initial state...", flush=True)
		print("PRIOR game ready: TIME: ", datetime.now(), flush=True)
		while True:
			ans = await ws.recv()
			state = GameState(json.loads(ans))
			for x in state.players : 
				x.display()
		
	
	print("AFTER game ready: TIME: ", datetime.now(), flush=True)
		
		
asyncio.get_event_loop().run_until_complete(connection())