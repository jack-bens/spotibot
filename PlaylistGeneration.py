# Playlist Generation

import warnings
warnings.filterwarnings("ignore")
import sys
import random
import math
import csv
import pandas as pd
import numpy as np
import shap

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

from spotifywrapper import get_playlist_songs

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


def writeConfMatrix(labels, trueLabels, predictedLabels):
	# Calculate confusion matrix:
	confMatrix = {}
	for l in labels:
		confMatrix[l] = {}
		for l2 in labels:
			confMatrix[l][l2] = 0
	for i in range(len(trueLabels)):
		confMatrix[trueLabels[i]][predictedLabels[i]] += 1
	# Format to be an actual matrix:
	matrix = [[]]
	matrix[0] = confMatrix.keys()
	for trueLabel in matrix[0]:
		row = []
		for predictedLabel in matrix[0]:
			row.append(confMatrix[trueLabel][predictedLabel])
		row.append(trueLabel)
		matrix.append(row)
	# Output to file:
	with open(f"test", "w") as output:
		writer = csv.writer(output, lineterminator=',\n')
		writer.writerow(matrix[0])
		writer = csv.writer(output, lineterminator='\n')
		writer.writerows(matrix[1:])
		output.close()
	# Return confusion matrix:
	return confMatrix

def calculateAccuracy(labels, numPredictions, confMatrix):
    correct = 0
    for l in labels:
        correct += confMatrix[l][l]
    accuracy = float(correct) / float(numPredictions)
    interval = 1.96 * math.sqrt((accuracy * (1 - accuracy)) \
                                        / (numPredictions))
    print("Accuracy on test set: %.4f"%(accuracy))
    print("Confidence interval: [%.4f,%.4f]"%((accuracy-interval), \
                                (accuracy+interval)))
    print()

def addPlaylistTracks (PLAYLIST_ID, label):
    playlist = sp.user_playlist(CLIENT_ID, PLAYLIST_ID)
    print("Adding tracks from playlist " + playlist['name'])
    #tracks = sp.user_playlist_tracks(CLIENT_ID, PLAYLIST_ID)
    tracks = get_playlist_songs(PLAYLIST_ID, attributeList)
    for track in tracks:#["items"]:
            instances.append([label, track])


username = input("Hello! Please enter your spotify username (this may be a seemingly random string of characters found on your 'account details' page): ")
scope = 'user-library-read playlist-modify-public user-top-read'
token = util.prompt_for_user_token(username, scope, client_id=cid,
                                   client_secret=secret, redirect_uri='http://localhost/')

if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for", username)

location = 0
lenSongs = int(sp.current_user_saved_tracks()['total'])
trainingInstances = []

print("general info message-- Fill in later!!!!!!!!!!!!!!")

# Add user's top tracks
results = sp.current_user_top_tracks(time_range='medium_term', limit=50)
print("results size before merge: " + repr(len(results['items'])))
results2 = sp.current_user_top_tracks(time_range='medium_term', limit=50, offset=50)        
#results.update(results2)
#print("new size: " + repr(len(results['items'])))
for track in results['items']:
        #track = t["track"]
        print("Adding track to data set: " + track['name'])
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
                'mode',
                'key',
                'time_signature'
                ]
        audioAttributes = [af[key] for key in af.keys() if key in attributeKeys]
        instance = [track['popularity']] + audioAttributes
        instances.append([1, instance])
for track in results2['items']:
        #track = t["track"]
        print("Adding track to data set: " + track['name'])
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
                'mode',
                'key',
                'time_signature'
                ]
        audioAttributes = [af[key] for key in af.keys() if key in attributeKeys]
        instance = [track['popularity']] + audioAttributes
        instances.append([1, instance])

