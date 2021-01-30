# 1. Найти точку по адресу
# 2. Показать точку на карте вместе с найденной аптекой (ближайшая)
# 3. Рассчитайте расстояние от точки до аптеки и сформируйте сниппет (блок данных)
# из адреса и названия аптеки, времени её работы, а также расстояния до неё от исходной точки.
# Распечатайте его на экране.

from search_tools import *

import sys
import math
from io import BytesIO
from pprint import pprint

import requests
from PIL import Image, ImageDraw, ImageFont


def get_coords_from_geocoder(params):
    # Получение координат исходного объекта
    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        print(response.status_code, response.reason)
        sys.exit(1)

    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    original_coordinates = join_coords(toponym["Point"]["pos"])

    spn = calculate_spn(original_coordinates,
                        join_coords(toponym['boundedBy']['Envelope']['lowerCorner']),
                        join_coords(toponym['boundedBy']['Envelope']['upperCorner']))

    return original_coordinates, spn


def calculate_distance_from_two_coords(coord_tuple1, coord_tuple2):
    lat1, long1 = [(i * 3.14 / 180) for i in eval(coord_tuple1)]
    lat2, long2 = [(i * 3.14 / 180) for i in eval(coord_tuple2)]
    cl1, cl2, sl1, sl2 = math.cos(lat1), math.cos(lat2), math.sin(long1), math.sin(long2)

    delta = long2 - long1

    cdelta = math.cos(delta)
    sdelta = math.sin(delta)

    y = math.sqrt(pow(cl2 * sdelta, 2) + pow(cl1 * sl2 - sl1 * cl2 * cdelta, 2))
    x = sl1 * sl2 + cl1 * cl2 * cdelta

    ad = math.atan2(y, x)
    dist = ad * EARTH_RADIUS

    return round(dist, 2)


toponym_to_find = " ".join(sys.argv[1:])

# Константы апи серверов и радиуса Земли
geosearch_api_server = "https://search-maps.yandex.ru/v1/"
geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
map_api_server = "http://static-maps.yandex.ru/1.x/"
EARTH_RADIUS = 6372795

# Параметры
geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

original_coordinates, _ = get_coords_from_geocoder(geocoder_params)

# Увеличим spn наверняка

# Нахождение аптеки
geosearch_params = {
    "apikey": "bb1b9e9f-065d-4d9e-8a7d-8e643db56e66",
    "text": "Аптека",
    "lang": "ru_RU",
    "type": "biz",
    "ll": original_coordinates
}

response = requests.get(geosearch_api_server, params=geosearch_params)

if not response:
    print(response.status_code, response.reason)
    sys.exit(1)

json_response = response.json()

map_params = {
    "l": "map",
    "pt": f'{original_coordinates},org'
}
organizations = json_response['features']
for org in organizations:
    toponym_of_org = org['properties']['CompanyMetaData']
    drug_store_coords = ','.join(str(i) for i in org['geometry']['coordinates'])
    snippet = [toponym_of_org['name'],
               toponym_of_org['address'],
               toponym_of_org['Hours']['text'],
               drug_store_coords]
    map_params['pt'] = map_params['pt'] + f"~{drug_store_coords},vkbkm"
    map_params['pl'] = f'{original_coordinates},{drug_store_coords}'

    break

response = requests.get(map_api_server, params=map_params)

# Отрисовка изображения
with Image.open(BytesIO(response.content)) as im:
    drawer = ImageDraw.Draw(im)
    y_margin = 10
    font = ImageFont.truetype("arial.ttf", 10, encoding='UTF-8')
    try:
        for snip in snippet:
            drawer.text((10, y_margin), snip, font=font)
            y_margin += 15
        distance = calculate_distance_from_two_coords(original_coordinates, drug_store_coords)
        distance = f'Дистанция до аптеки: {distance}m'
        drawer.text((10, y_margin), distance, font=font)
    except NameError:
        drawer.text((10, 10), original_coordinates)
        drawer.text((10, 20), "Аптека не найдена :(", font=font)
    im.show()
