from pprint import pprint

import requests
import sys
from search_tools import *

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"


def get_json_response(params):
    # Получение координат исходного объекта
    response = requests.get(geocoder_api_server, params=params)

    if not response:
        print(response.status_code, response.reason)
        sys.exit(1)

    json_response = response.json()

    return json_response


# Нахождение координат

toponym_object = ' '.join(sys.argv[1:])

get_coords_params = {
    'format': 'json',
    'geocode': toponym_object,
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b"
}

json_response = get_json_response(params=get_coords_params)

toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
address = join_coords(toponym["Point"]["pos"])

# Нахождение района

get_distict_params = {
    'format': 'json',
    'geocode': address,
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    'kind': 'district'
}

json_response = get_json_response(get_distict_params)
toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
district = toponym['description']
print(f'Объект "{toponym_object}"\nнаходится в районе "{district}"')