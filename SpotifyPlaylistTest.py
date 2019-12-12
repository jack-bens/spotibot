import sys
import random
import math
import csv
import pandas as pd
import numpy as np
from sklearn import tree
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree.export import export_text
import spotipy
import spotipy.util as util
sp = spotipy.Spotify()
import csv

RANDOM_SEED = 12345
TRAINING_PERCENT = 0.75
UPBEAT_ID = "2grWws6IB2nbfwEuxz83t0"
NONUPBEAT_ID = "6ZiAdL4ta0XRnkraUpBKYe"

from spotipy.oauth2 import SpotifyClientCredentials

cid ="2f3b64d6217f4c36b44b10718e88a860"
CLIENT_ID = cid
secret = "d948722ed8804508962d797d9a9d7206"
username = "9qmimovhfjmws0vgx2gotnefa"


#client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret) 
#sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

scope = 'user-library-read'
token = util.prompt_for_user_token(username, scope, client_id=cid,
                                   client_secret=secret, redirect_uri='http://localhost/')

if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for", username)

# lizzo_uri = 'spotify:artist:56oDRnqbIiwx4mymNEv7dS'

#location = 0
#batchSize = 50
#while location < len(sp.current_user_saved_track().):
location = 0
# print(sp.current_user_recently_played())
lenSongs = int(sp.current_user_saved_tracks()['total'])

trainingInstances = []
playlists = sp.current_user_playlists()

print("Hello! Which playlist would you like to generate more songs for?")
print()
for playlist in playlists['items']:
    print(playlist['name'])

print()
choice = int(input("Enter the 0-based index of your selection: "))
chosenPlaylist = playlists['items'][choice]

print("You've selected " + playlists['items'][choice]['name'])

print("Constructing the Training Set...")
print()
print("Adding songs from the playlist")


# Set random seeds for random and numpy random (used by scikit-learn):
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Create dataset
instances = []
upbeat_tracks = sp.user_playlist_tracks(CLIENT_ID, UPBEAT_ID)
for t in upbeat_tracks["items"]:
	track = t["track"]
	af = sp.audio_features(track["id"])[0]
	attributeKeys = [
		'duration_ms',
		'danceability',
		'energy',
		'instrumentalness',
		'liveness',
		'loudness',
		'speechiness',
		'tempo',
		'valence',
		'mode'
	]
	audioAttributes = [af[key] for key in af.keys() if key in attributeKeys]
	instance = [track['popularity']] + audioAttributes
	instances.append([0, instance])

nonupbeat_tracks = sp.user_playlist_tracks(CLIENT_ID, NONUPBEAT_ID)
for t in upbeat_tracks["items"]:
	track = t["track"]
	af = sp.audio_features(track["id"])[0]
	attributeKeys = [
		'duration_ms',
		'danceability',
		'energy',
		'instrumentalness',
		'liveness',
		'loudness',
		'speechiness',
		'tempo',
		'valence',
		'mode'
	]
	audioAttributes = [af[key] for key in af.keys() if key in attributeKeys]
	instance = [track['popularity']] + audioAttributes
	instances.append([1, instance])

# Shuffle instances and split into label array and attribute array:
random.shuffle(instances)
trainingLabels = []
trainingAttributes = []
for i in instances:
	trainingLabels.append(i[0])
	trainingAttributes.append(i[1])

'''
tracks = sp.user_playlist_tracks(sp.current_user()['id'], chosenPlaylist['id'])
for t in tracks['items']:
   # results = sp.current_user_saved_tracks(limit=50, offset=location)
    print(t['track']['name'])
    track = t['track']
    instance = [1]                     
    instance.append(track['name'])
    instance.append(track['id'])
    instance.append(track['artists'][0]['name'])
    instance.append(track['duration_ms'])
    instance.append(track['popularity'])
    instance.append(sp.audio_features(track['id'])[0]['danceability'])
    instance.append(sp.audio_features(track['id'])[0]['energy'])
    instance.append(sp.audio_features(track['id'])[0]['instrumentalness'])
    instance.append(sp.audio_features(track['id'])[0]['liveness'])
    instance.append(sp.audio_features(track['id'])[0]['loudness'])
    instance.append(sp.audio_features(track['id'])[0]['speechiness'])
    instance.append(sp.audio_features(track['id'])[0]['tempo'])
    instance.append(sp.audio_features(track['id'])[0]['valence'])
    instance.append(sp.audio_features(track['id'])[0]['mode'])
    #pair = [1, instance]
    trainingInstances.append(instance)


print()
print("Other Playlists")
for playlist in playlists['items']:
    if (playlist['id'] != chosenPlaylist['id']):
        playlistTracks = sp.user_playlist_tracks(sp.current_user()['id'], playlist['id'])
        for t in playlistTracks['items']:
            # results = sp.current_user_saved_tracks(limit=50, offset=location)
            # print(t['track']['name'])
            track = t['track']
            instance = [0]
            instance.append(track['name'])
            instance.append(track['id'])
            instance.append(track['artists'][0]['name'])
            instance.append(track['duration_ms'])
            instance.append(track['popularity'])
            if (sp.audio_features((track['id'])) is not None): 
                instance.append(sp.audio_features(track['id'])[0]['danceability'])
                instance.append(sp.audio_features(track['id'])[0]['energy'])
                instance.append(sp.audio_features(track['id'])[0]['instrumentalness'])
                instance.append(sp.audio_features(track['id'])[0]['liveness'])
                instance.append(sp.audio_features(track['id'])[0]['loudness'])
                instance.append(sp.audio_features(track['id'])[0]['speechiness'])
                instance.append(sp.audio_features(track['id'])[0]['tempo'])
                instance.append(sp.audio_features(track['id'])[0]['valence'])
                instance.append(sp.audio_features(track['id'])[0]['mode'])
                #pair2 = [0, instance]    
                trainingInstances.append(instance)




############ TODO: MAKE LESS JANKY ############
#dataframe = pd.DataFrame(data = trainingInstances)
#dataframe = pd.get_dummies(dataframe, drop_first = True)
instances = [[i[0], list(i)[3:]] for i in trainingInstances]#dataframe.values]

random.shuffle(instances)
labels = [i[0] for i in instances]
attributes = [i[1] for i in instances]
print(labels)
print(attributes)


'''


clf = tree.DecisionTreeClassifier()
clf = clf.fit(trainingAttributes, trainingLabels)
result = export_text(clf)
print(result)
tree.plot_tree(clf)


'''
############ Splitting into trainin/test sets
div = int(TRAINING_PERCENT * float(len(instances)))
training = instances[:div]
testing = instances[div:]
trainingLabels = [i[0] for i in training]
trainingAttributes = [i[1] for i in training]
testLabels = [i[0] for i in testing]
testAttributes = [i[1] for i in testing]
'''
print("Done!") 
print(len(trainingInstances))


