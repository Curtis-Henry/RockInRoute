import requests
import json

API_KEY = "WEVqY4AR8RjLNORXcmiYuG3A4RDL2Qpa"
URL = "https://app.ticketmaster.com/discovery/v2/events.json?city={0}&stateCode={1}&apikey={2}&segmentName=Music"
artists = {}

def get_tm_artists(city, state):
    REQUEST_URL = URL.format(city, state, API_KEY)
    response = requests.get(url= REQUEST_URL)
    json_data = json.loads(response.text)
    return get_artist_list(json_data)

def get_artist_list(json_data):
    # print(json_data)
    if json_data["page"]["totalElements"] == 0:
        return []

    for elem in json_data["_embedded"]["events"]:
       value = elem["name"]
       if ':' in value:
           value = value.split(':')[0]
       if '-' in value:
           value = value.split(' - ')[0]
       if 'w/' in value:
           value = value.split('w/')[0]
       if '&' in value:
           value = value.split('&')[0]
       if '/' in value:
           for string in value.split('/'):
               artists[string] = 1
       artists[value] = 1
    artists_list  = [key for key in artists.keys()]
    return artists_list

# print(get_tm_artists("Tampa", "FL"))
print(get_tm_artists("Port St. Lucie", "FL"))
# print(get_tm_artists("Tampa", "FL"))
# print(get_tm_artists("Tampa", "FL"))
