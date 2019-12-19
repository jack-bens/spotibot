# Query Testing


import warnings
warnings.filterwarnings("ignore")
import sys
import random
import math
import requests
import csv
import pandas as pd
import numpy as np
import shap
import pprint

from sklearn import tree
from sklearn import preprocessing
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree.export import export_text
from sklearn.ensemble import RandomForestRegressor
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

# Tree visual imports
from sklearn.externals.six import StringIO
from IPython.display import Image
from sklearn.tree import export_graphviz
import pydotplus

#from spotifywrapper import get_playlist_songs

sp = spotipy.Spotify()

RANDOM_SEED = 473463298
TRAINING_PERCENT = 0.75

cid ="2f3b64d6217f4c36b44b10718e88a860"
CLIENT_ID = cid
secret = "d948722ed8804508962d797d9a9d7206"
instances = []
attributeList = ['duration_ms',
		'danceability',
		'energy',
		'instrumentalness',
		'liveness',
		'loudness',
		'speechiness',
		'tempo',
		'valence','mode', 'key', 'time_signature', 'popularity']

def get_playlist_songs(id):
    r = requests.get(f'https://api.spotify.com/v1/playlists/{id}',
                     headers={"Content-Type":"application/json",
                              "Authorization":f"Bearer {token}"})
    if not r:
        print(f"Couldn't get playlist with ID {id}: Response {r.status_code}")
    else:
        #instances = []
        for t in r.json()['tracks']['items']:
            track = t['track']
            if track is None:
                continue
            else:
                print(track['name'])
			#af = sp.audio_features(track['id'])[0]
			#instanceAttr = [af[key] for key in af.keys() if key in attributes]
			#instanceAttr.append(track['popularity'])
			#instances.append(instanceAttr)
	#return(instances)


def addPlaylistTracks (PLAYLIST_ID, label):
    playlist = sp.user_playlist(CLIENT_ID, PLAYLIST_ID)
    print("Adding tracks from playlist " + playlist['name'])
    #tracks = sp.user_playlist_tracks(CLIENT_ID, PLAYLIST_ID)
    tracks = get_playlist_songs(PLAYLIST_ID, attributeList)
    for track in tracks:#["items"]:
            instances.append([label, track])


username = input("Hello! Please enter your spotify username (this may be a seemingly random string of characters found on your 'account details' page): ")
scope = 'user-library-read'
token = util.prompt_for_user_token(username, scope, client_id=cid,
                                   client_secret=secret, redirect_uri='http://localhost/')

if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for", username)

search_str = input("Enter search string: ")

result = sp.search(q=search_str, type='playlist')
#print(len(result['playlists']['items']))
for item in result['playlists']['items']:
    print(item['id'])
    get_playlist_songs(item['id'])
#pprint.pprint(result)
