from game_state import game_state
import ast


def test_update_state():
    game = game_state()

    assert game.current_round is None
    assert game.population is None
    assert game.cities == []

    with open('update_state_test_1.txt') as data:
        data = str(data.read())
        data = ast.literal_eval(data)

    game.update_state(data)
    assert game.population is not None
    assert game.points == 40
    assert game.cities[0].name == 'Abuja'
    assert game.cities[0].connections == ['Boston', 'Roma', 'Melbourne', 'Warszawa', 'Libreville']
    assert game.cities[1].name == 'Accra'
    assert game.cities[1].economy == 2

    assert game.current_round == 1
    assert game.population == 1594 + 2750

    with open('update_state_test_2.txt') as data2:
        data2 = str(data2.read())
        data2 = ast.literal_eval(data2)

    game.update_state(data2)

    assert game.population == 1494 + 1750
    assert game.population_reduction is not None
    assert game.population_reduction == (1494 + 1750) / (1594 + 2750)
    assert game.points == 55


def test_distance():
    with open('update_state_test_1.txt', 'r') as data:
        data = data.read()
        data = ast.literal_eval(data)

    game = game_state()
    game.update_state(data)

    city1 = game.cities[0]
    city2 = game.cities[1]

    assert game.distance(city1, city2) is not None
    assert game.distance(city1, city2) == 8.35


def test_neighbor_cities():
    with open('update_state_test_1.txt', 'r') as data:
        data = data.read()
        data = ast.literal_eval(data)

    game = game_state()
    game.update_state(data)

    accra = [x for x in game.cities if x.name == 'Accra'][0]
    assert game.find_neighbor_cities(accra, 4) == []
    assert game.find_neighbor_cities(accra) == ['Abuja']
