from game_state import game_state
import create_training_data as td
import ast


def test_create_p_list():
    with open('data_test_1.txt', encoding="utf8") as data:
        data = str(data.read())
        data = ast.literal_eval(data)

    game = game_state()
    game.update_state(data)

    assert td.create_priority_list(game) is not None
    p_list = td.create_priority_list(game)
    data2 = td.create_data(p_list)
    td.save_data(data2)
    td.possible_actions(game.points, p_list)

# def test_cation_data():
#     with open('data_test_1.txt', encoding="utf8") as data:
#         data = str(data.read())
#         data = ast.literal_eval(data)
#
#     game = game_state()
#     game.update_state(data)

