#!/usr/bin/env python3

import asyncio
import json
import os
import random
from datetime import datetime
import websockets


async def play():
    url = os.environ["URL"]
    key = os.environ["KEY"]

    async with websockets.connect(f"{url}?key={key}") as websocket:
        print("Waiting for initial state...", flush=True)
        print("PRIOR game ready: TIME: ", datetime.now(), flush=True)
        while True:
            state_json = await websocket.recv()
            print("AFTER await command: TIME: ", datetime.now())
            state = json.loads(state_json)
            print("<", state)
            own_player = state["players"][str(state["you"])]
            # IMPLEMENT LOGIC/AI
            if not state["running"] or not own_player["active"]:
                break
            valid_actions = ["turn_left", "turn_right", "change_nothing"]
            if own_player["speed"] < 10:
                valid_actions += ["speed_up"]
            if own_player["speed"] > 1:
                valid_actions += ["slow_down"]
            action = random.choice(valid_actions)
            print(">", action)
            action_json = json.dumps({"action": action})
            await websocket.send(action_json)
    print("AFTER game ready: TIME: ", datetime.now(), flush=True)


asyncio.get_event_loop().run_until_complete(play())
