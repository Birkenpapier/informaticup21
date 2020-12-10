import asyncio
import websockets
from datetime import datetime
import json

uri = "wss://msoll.de/spe_ed?key=LSIS7VOFLXCISR3K4YUSZ3CN2Z3CF74PEB7EKE4AQ7PDVKAGTYVOZVXP"

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

async def connection():
	
	client_time = 0
	connection_lost = 0
	
	async with websockets.connect(uri) as ws:
		
		start_time = datetime.now()
		print("Waiting for initial state...", flush=True)
		print("PRIOR game ready: TIME: ", start_time, flush=True)
		
		started = False

		while True:
			print("------------------------------------")
			ans = None
			try:
				ans = await ws.recv()
			except ConnectionClosedError:
				print("second try...")
				connection_lost += 1
				try:
					ans = await ws.recv()
				except ConnectionClosedError as e:
					print("No Connection.")
					print(e)
					connection_lost += 1
					break
					
			print("Received")
			if not started :
				started = True
				client_time = datetime.now()
			
			state = GameState(json.loads(ans))
			
			if not state.running:
				print("Game ended")
				break
			
			if not state.players[state.you - 1].active:
				print("You lose")
				break
			
			action = "speed_up"
			action_json = json.dumps({"action": action})
			await ws.send(action_json)
			print("Action sent: ", action)
			
		await ws.close()
		print("Connection closed.", connection_lost, "times connection lost")
		
	print("Client started:", start_time)
	print("Game started:", client_time)
	print("AFTER game ready: TIME: ", datetime.now(), flush=True)
	
asyncio.get_event_loop().run_until_complete(connection())

#for x in range(3):
#	print("\n\nGame", x, "started\n\n")
#	asyncio.get_event_loop().run_until_complete(connection())