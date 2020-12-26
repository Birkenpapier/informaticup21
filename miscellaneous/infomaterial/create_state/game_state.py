import math

class event:
    def __init__(self, x:dict):
        self.type = x["type"]
        # self.since_round = x["round"]
        self.name = None
        if 'pathogen' in x:
            self.name = x["pathogen"]["name"]


class city_obj:

    def __init__(self, x: dict, index):
        Mapping = {'x': 0, '--': 1, '-': 2, 'o': 3, '+': 4, '++': 5}
        self.id = index
        self.name = x['name']
        self.latitude = round(x['latitude'], 2)
        self.longitude = round(x['longitude'], 2)
        self.population = x['population']
        self.connections = x['connections']
        self.connections_2 = None
        self.economy = Mapping[x['economy']]
        self.government = Mapping[x['government']]
        self.hygiene = Mapping[x['hygiene']]
        self.awareness = Mapping[x['awareness']]
        self.pathogen = None
        self.events = ['x', 'x', 'x', 'x']

        if 'events' in x:
            for element in x['events']:
                if 'pathogen' in element:
                    self.pathogen = element['pathogen']['name']
                    self.events = [element['pathogen']['infectivity'], element['pathogen']['mobility'],
                                   element['pathogen']['duration'],element['pathogen']['lethality']]
                    break
        self.events = [Mapping[x] for x in self.events]

    def __eq__(self, other):
        return self.name == other.name

    def city_possible_actions(self, pts, rnd=2):
        cpa = [self.name, "Null"]
        if pts >= 3:
            cpa.append("PE")
            cpa.append("NW")
            cpa.append("Hy")
        if 10*rnd+20 <= pts:
            cpa.append("Qu")
        if 5*rnd+15 <= pts:
            cpa.append("FS")

        return cpa


class game_state:

    def __init__(self):
        self.current_round = None
        self.outcome = None
        self.points = None
        self.cities = []
        self.initial_population = None
        self.population = None
        self.population_reduction = None
        self.Mapping = None
        self.events = []

    def update_state(self, payload: dict):
        self.current_round = payload['round']
        self.outcome = payload['outcome']
        self.points = payload['points']

        for val in payload['events']:
            self.events.append(event(val))


        self.cities = []
        for val in payload['cities'].values():
            city = city_obj(val, len(self.cities))
            self.cities.append(city)

        for city in self.cities:
            city.connections = [c.id for c in self.cities if c.name in city.connections]

        if self.current_round == 1:
            self.initial_population = sum([x.population for x in self.cities])

        temp_population = sum([x.population for x in self.cities])

        if self.current_round == 1:
            self.population_reduction = None
        else:
            self.population_reduction = temp_population / self.population

        self.population = temp_population

        for city in self.cities:
            city.connections_2 = self.find_neighbor_cities(city)

    @staticmethod
    def distance(a: city_obj, x: city_obj):
        return round(math.sqrt((a.latitude - x.latitude) ** 2 + (a.longitude - x.longitude) ** 2), 2)

    def find_neighbor_cities(self, city: city_obj, max_distance=10):
        neighbor_cities = []
        for neighbors in self.cities:
            if 0 < self.distance(city, neighbors) <= max_distance:
                neighbor_cities.append(neighbors.name)
        return neighbor_cities

    def reward(self):
        if self.current_round == 1:
            raise ValueError('rewards start in round 2')
        if self.outcome == 'pending':
            return 1 + self.population_reduction * 3
        elif self.outcome == 'win':
            return 20
        elif self.outcome == 'loss':
            return -20
