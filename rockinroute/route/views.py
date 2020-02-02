from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.urls import reverse

import googlemaps
from datetime import datetime
import json
import polyline
import threading
import requests
import time
import base64
import sys

gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_KEY)

def index(request):
    return redirect('https://accounts.spotify.com/authorize?response_type=code&client_id='+ str(settings.SOCIAL_AUTH_SPOTIFY_KEY) + '&redirect_uri=' + 'http://127.0.0.1:8000/route/spotify/' + "&scope=playlist-modify-public%20playlist-modify-private")
    # return HttpResponse("Hello test")

def spotify(request):
    
    # headers = {"Authorization":"Basic {}:{}".format(settings.SOCIAL_AUTH_SPOTIFY_KEY, settings.SOCIAL_AUTH_SPOTIFY_SECRET)}
    data = {"grant_type":"authorization_code", "code":request.GET["code"], "redirect_uri":"http://127.0.0.1:8000/route/spotify/", "client_id":settings.SOCIAL_AUTH_SPOTIFY_KEY, "client_secret":settings.SOCIAL_AUTH_SPOTIFY_SECRET}
    r = requests.post('https://accounts.spotify.com/api/token', data=data)
    print("home")
    data = json.loads(r.text)

    access_token = data["access_token"]

    # return HttpResponseRedirect(reverse('route:spotify', kwargs={'access_token': access_token}))
    return redirect('../search?access_token='+access_token)

def search(request):
    print(request.GET["access_token"])
    return render(request, 'route/index.html', {"access_token": request.GET["access_token"]})

def calculate(request):
    start_point = request.POST["start_point"]
    end_point = request.POST["end_point"]
    access_token = request.POST["access_token"]

    city_state_list = []
    start_location, end_location = get_cities(start_point, end_point, city_state_list)
    
    album_name = start_location + " to "+ end_location

    user_id = get_user_id(access_token)
    artists_list = get_artists_cities(city_state_list)
    
    artist_dict = {}
    for artist in artists_list:

        id = get_artist_id(artist, access_token)
        if id:
            artist_dict[artist] = id
    # print(artist_dict)

    song_list = []

    for artist, artist_id in artist_dict.items():
        get_artist_songs(song_list, artist_id, access_token)
    print(song_list)

    album_id = make_playlist(album_name, user_id, access_token)
    add_songs_to_playlist(album_id, user_id, song_list, access_token)

    return HttpResponse("Hello test")

def add_songs_to_playlist(album_id, user_id, song_list, access_token):
    headers = {"Authorization": "Bearer " + access_token,"Accept":"application/json#"}
    
    count = 0
    amount = 50
    rounds = int(len(song_list)/amount)
    for i in range(0, 1 if rounds == 0 else rounds):
        song_uri_array = []
        for j in range(0,amount):
            if j+count < len(song_list):
                song_uri_array.append(song_list[count+j][1])
        params = (('uris', ",".join(song_uri_array)),)
        print(params)
        # print(len(song_uri_array))
        # print(",".join(song_uri_array))
        print(len(song_uri_array))
        r = requests.post("https://api.spotify.com/v1/playlists/{}/tracks".format(album_id), params=params, headers=headers)
        print(r.status_code)
        print(r.text)
        # break
        count += amount

def get_user_id(access_token):
    headers = {"Authorization": "Bearer " + access_token}
    r = requests.get("https://api.spotify.com/v1/me", headers=headers)
    return json.loads(r.text)["id"]

def make_playlist(album_name, user_id, access_token):
    headers = {"Authorization": "Bearer " + access_token,"Content-Type":"application/json"}
    data = {'name':album_name, 'public':'false'}
    
    r = requests.post("https://api.spotify.com/v1/users/{}/playlists".format(user_id), data=json.dumps(data), headers=headers)
    album_id = json.loads(r.text)["id"]

    return album_id


def get_artist_songs(song_list, artist_id, access_token):
    headers = {"Authorization": "Bearer " + access_token,"Content-Type":"application/json", "Accept":"application/json"}
    params = (
    ('id', artist_id),
    ('country', 'US'))

    r = requests.get("https://api.spotify.com/v1/artists/{}/top-tracks".format(artist_id), params=params, headers=headers)
    data = json.loads(r.text)
    # print(data["tracks"]  )
    for track in data["tracks"]:
        song_list.append((track["name"], track["uri"]))
    return song_list

def get_artist_id(artist_string, access_token):
    headers = {"Authorization": "Bearer " + access_token,"Content-Type":"application/json", "Accept":"application/json"}
    params = (
    ('q', artist_string),
    ('type', 'artist'),
    ('limit','1'))

    r = requests.get("https://api.spotify.com/v1/search", params=params, headers=headers)
    data = json.loads(r.text)
    
    if data["artists"]["total"] != 0:
        return data["artists"]["items"][0]["id"]
    else:
        return ''

def test(ar1, ar2):
    print(ar1, ar2)

def get_cities(start_point, end_point, city_state_list):
    # city_state_list = []
    points = []
    now = datetime.now()

    #query google for direction
    directions_query = gmaps.directions(start_point, end_point, mode="driving", departure_time=now)[0]

    start_location = directions_query["legs"][0]["start_address"].split(",")[0]
    end_location = directions_query["legs"][0]["end_address"].split(",")[0]    

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

    return start_location, end_location

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

    for city,state in city_state_list:
        artists = get_artists(city, state)
        for artist in artists:
            if artist not in artists_list and artist:
                artists_list.append(artist)

        time.sleep(1)

    return artists_list