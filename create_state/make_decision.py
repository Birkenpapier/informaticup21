from game_state import game_state
from game_state import city_obj
from random import randrange


class Action:
    def __init__(self):
        pass
        # super(IC20Servicer, self).__init__()

    def get_sick_cities(game: game_state):
        sick_cities = []
        for city in game.cities:
            if city.events[0] != 0:
                sick_cities.append(city)
        lucky_city = sick_cities[randrange(len(sick_cities))]
        return lucky_city

    def create_Action(game, action_list):
        i = action_list.tolist().index(1)
        lucky_city = Action.get_sick_cities(game)
        points = game.points
        data = {"type": "endRound"}
        if i == 0:
            return {"type": "endRound"}
        elif i == 1:
            if points >= 30:
                data = {"type": "putUnderQuarantine", "city":
                        lucky_city.name, "rounds": 1}
            else:
                data = {"type": "endRound"}

        elif i == 2:
            if points >= 20:
                data = {"type": "closeAirport", "city":
                    lucky_city.name, "rounds": 1}
            else:
                data = {"type": "endRound"}

        elif i == 3:
            if points >= 6:
                city2 = [c.name for c in game.cities if c.id == lucky_city.connections[0]][0]
                data = {"type": "closeConnection", "fromCity":
                    lucky_city.name, "toCity": city2,
                        "rounds": 1}
            else:
                data = {"type": "endRound"}

        elif i == 4:
            if points >= 40:
                data = {"type": "developVaccine", "pathogen":
                    lucky_city.pathogen}
            else:
                data = {"type": "endRound"}

        elif i == 5:
            if points >= 5:
                for event in game.events:
                    if event.name == lucky_city.pathogen and event.type == 'vaccineAvailable':
                        data = {"type": "deployVaccine", "pathogen":
                            event.name, "city": lucky_city.name}
            else:
                data = {"type": "endRound"}

        elif i == 6:
            if points >= 20:
                data = {"type": "developMedication", "pathogen":
                    lucky_city.pathogen}
            else:
                data = {"type": "endRound"}

        elif i == 7:
            if points >= 10:
                for event in game.events:
                    if event.name == lucky_city.pathogen and event.type == 'medicationAvailable':
                        data = {"type": "deployMedication", "pathogen":
                            event.name, "city": lucky_city.name}
            else:
                data = {"type": "endRound"}
        elif i == 8:
            if points >= 3:
                data = {"type": "exertInfluence", "city": lucky_city.name}
            else:
                data = {"type": "endRound"}
        elif i == 9:
            if points >= 3:
                data = {"type": "callElections", "city": lucky_city.name}
            else:
                data = {"type": "endRound"}
        elif i == 10:
            if points >= 3:
                data = {"type": "applyHygienicMeasures", "city": lucky_city.name}
            else:
                data = {"type": "endRound"}
        elif i == 11:
            if points >= 3:
                data = {"type": "launchCampaign", "city": lucky_city.name}
            else:
                data = {"type": "endRound"}
        print(f"we're returning: type: {data['type']}")
        return data


import json

if __name__ == '__main__':
    game = game_state()
    with open('A.json', encoding="utf8") as f:
        data = json.load(f)
    game.update_state(data)

    action_generator = Action()
    print(action_generator.create_Action(game, 3))
