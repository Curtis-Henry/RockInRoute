from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings

import googlemaps
from datetime import datetime
import json
import polyline
import threading
import requests
import time

gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_KEY)

def index(request):
    return redirect('https://accounts.spotify.com/authorize?response_type=code&client_id='+ str(settings.SOCIAL_AUTH_SPOTIFY_KEY) + '&redirect_uri=' + 'http://127.0.0.1:8000/route/search/')
    # return HttpResponse("Hello test")

def spotify(request):
    return

def search(request):
    return render(request, 'route/index.html')

def calculate(request):
    start_point = request.POST["start_point"]
    end_point = request.POST["end_point"]
    # city_state_list = get_cities(start_point, end_point)
    # print(city_state_list)
    city_state_list = []
    calc_thread = threading.Thread(target=get_cities, args=(start_point,end_point, city_state_list))
    calc_thread.start()
    calc_thread.join()
    get_artists_cities(city_state_list)
    
    return HttpResponse("Hello test")

def test(ar1, ar2):
    print(ar1, ar2)

def get_cities(start_location, end_location, city_state_list):
    # city_state_list = []
    points = []
    now = datetime.now()

    #query google for direction
    directions_query = gmaps.directions(start_location, end_location, mode="driving", departure_time=now)[0]
    
    for step in directions_query["legs"][0]["steps"]:
        pline = step["polyline"]["points"]
        poly_points  = polyline.decode(pline)

        for point in poly_points:
            points.append(point)

    for point in points[0:-1:400]:
            lat = point[0]
            lng = point[1]
        
            address_components = gmaps.reverse_geocode((lat,lng))[0]["address_components"]

            city = ""
            state = ""

            for component in address_components:
                if "locality" in component["types"]:
                    city = component["long_name"]

                if "administrative_area_level_1" in component["types"]:
                    state = component["short_name"]

            if (city, state) not in city_state_list and (city and state):
                city_state_list.append((city, state))

    return city_state_list

ticketmaster_key = settings.TICKETMASTER_KEY
URL = "https://app.ticketmaster.com/discovery/v2/events.json?city={0}&stateCode={1}&apikey={2}&segmentName=Music"

#get artists for one city, state
def get_artists(city, state):
    REQUEST_URL = URL.format(city, state, ticketmaster_key)
    response = requests.get(url= REQUEST_URL)
    print("Making query")
    json_data = json.loads(response.text)
    return get_artist_list(json_data)

def get_artist_list(json_data):
    artists = {}
    # print(json_data)
    try:
        if json_data["page"]["totalElements"] == 0:
            return []
    except KeyError:
        print(json_data)

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
    # print(artists)
    artists_list  = [key for key in artists.keys()]
    return artists_list

def get_artists_cities(city_state_list):
    artists_list = []

    count = 0

    start_time = time.time()
    

    for city,state in city_state_list:
        artists = get_artists(city, state)
        for artist in artists:
            if artist not in artists_list and artist:
                artists_list.append(artist)

        count += 1
        time.sleep(1)
        # if count == 5:
            # print("done 5")
            # time.sleep(4)
            # count = 0

    print(artists_list)