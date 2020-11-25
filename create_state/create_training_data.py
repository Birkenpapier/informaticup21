from game_state import game_state as game
import csv


def create_priority_list(gm: game):
    priority_list = [city for city in gm.cities]
    # add_cities = []
    # for x in priority_list:
    #     for y in x.connections_2:
    #         city = [q for q in gm.cities if q.name == y][0]
    #         if city not in priority_list:
    #             add_cities.append(city)
    # for x in add_cities:
    #     priority_list.append(x)
    return priority_list


def create_data(p_list):
    data_list = []
    for city in p_list:
        temp_list = [city.id, city.population, city.economy, city.government,city.hygiene, city.awareness,
                     city.latitude, city.longitude,
                     city.events[0], city.events[1], city.events[2], city.events[3]]
        for x in city.connections:
            temp_list.append(x)
        data_list.append(temp_list)

    return data_list


def save_data(p_list):
    with open('T_Data.csv', 'w', newline='', encoding="utf8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Id', 'Pop', 'Ec', 'Gov', 'Hyg', 'Aw','Lat','Long', 'Inf', 'Mob', 'Dur', 'Leth', 'Connections(0 to 13 static)'])
        for vector in p_list:
            writer.writerow(vector)


def create_save_TD(gm: game):
    l = create_priority_list(gm)
    l = create_data(l)
    save_data(l)

    return l


def save_reward():
    pass


def send_data():
    pass


