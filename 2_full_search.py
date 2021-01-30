from search_tools import *

import sys
from io import BytesIO
from pprint import pprint

import requests
from PIL import Image, ImageDraw


toponym_to_find = " ".join(sys.argv[1:])

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    print(response.status_code, response.reason)

json_response = response.json()
toponym = json_response["response"]["GeoObjectCollection"][
    "featureMember"][0]["GeoObject"]
toponym_coordinates = join_coords(toponym["Point"]["pos"])
spn = calculate_spn(toponym_coordinates,
                    join_coords(toponym['boundedBy']['Envelope']['lowerCorner']),
                    join_coords(toponym['boundedBy']['Envelope']['upperCorner']))

map_params = {
    "ll": toponym_coordinates,
    "spn": spn,
    "l": "map",
    "pt": f'{toponym_coordinates},org~{toponym_coordinates},73'
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
response = requests.get(map_api_server, params=map_params)

with Image.open(BytesIO(response.content)) as im:
    drawer = ImageDraw.Draw(im)
    drawer.text((10, 10), toponym_coordinates)
    im.show()
