# Playlist Generation

import warnings
warnings.filterwarnings("ignore")
import sys
import random
import math
import time
import csv
import pandas as pd
import numpy as np
# import shap
import webbrowser
from spotifywrapper import get_playlist_songs

# Learning model imports
from sklearn import tree
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree.export import export_text
from sklearn.ensemble import RandomForestRegressor

# Spotipy imports
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

# Tree visual imports
from sklearn.externals.six import StringIO
from IPython.display import Image
from sklearn.tree import export_graphviz
import pydotplus

sp = spotipy.Spotify()

CLIENT_ID ="2f3b64d6217f4c36b44b10718e88a860"
CLIENT_SECRET = "d948722ed8804508962d797d9a9d7206"
scope = 'user-library-read playlist-modify-public user-top-read'

PLAYLIST_MAX_SONGS = 25

audiofeatureKeys = [
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
attributeList = ['popularity'] + audiofeatureKeys
instances = []

# Function for adding playlist tracks to an instance set
def addPlaylistTracks (playlist_id, label):
    playlist = sp.user_playlist(CLIENT_ID, playlist_id)
    print("Adding tracks from playlist " + playlist['name'])
    tracks = get_playlist_songs(playlist_id, attributeList)
	# Extract actual track, don't include id in instance
    tracks = [i[1] for i in tracks]
    for track in tracks:
            instances.append([label, track])

# Welcome message
print("\nWelcome to Spotibot: " \
	+ "Your friendly neighborhood personalized playlist generator!")
time.sleep(1)
print("\nIn a moment, your web browser will open to the 'Account overview' " \
	+ "page of your Spotify account. \n")
time.sleep(1)
# Open account page and prompt for username
webbrowser.open("https://www.spotify.com/us/account/overview/")
username = input("Please enter your Spotify username.\nThis is the " \
	+ "seemingly random string of characters found on the 'Account overview' " \
	+ "page: \n")
# Get user token (with error handling)
try:
	token = util.prompt_for_user_token(username, scope, client_id=CLIENT_ID,
				client_secret=CLIENT_SECRET, redirect_uri='http://localhost/')
	if not token:
		sys.exit(1)
	sp = spotipy.Spotify(auth=token)
	if sp.user(username)['display_name'] != sp.current_user()['display_name']:
		sys.exit(1)
	sp.trace = False
except:
	print(f"Couldn't get token for {username}. "
		+ "\nPlease make sure you have the correct username and redirect URL.")
	sys.exit(1)

print(f"\nHi, {sp.current_user()['display_name']}!\nYou're using Spotibot, a " \
	+ "personalized playlist generator with engaging data visualizations \n" \
	+ "to give you a better idea of how we curate songs for your personally " \
	+ "generated playlists.")
print("We'll start by adding your Top Tracks and Liked Songs to get an idea " \
	+ "of what music you normally enjoy!\n")

# Add user's top tracks to training set with label 1
print("Now Adding Your Top Tracks!")
training_ids = []
results = sp.current_user_top_tracks(time_range='medium_term', limit=50)
for track in results['items']:
        af = sp.audio_features(track["id"])[0]
        audioAttributes = [af[key] for key in audiofeatureKeys]
        instance = [track['popularity']] + audioAttributes
        instances.append([1, instance])
        training_ids.append(track["id"])

# Add user's liked songs to training set with label 1
results = sp.current_user_saved_tracks(limit=50)
print("Now Adding your Liked Songs!")
for t in results['items']:
        track = t["track"]
		# Check id to make sure no duplicates added
        if track["id"] in training_ids:
                continue
		# Get audio features for instance attribute values
        af = sp.audio_features(track["id"])[0]
        audioAttributes = [af[key] for key in audiofeatureKeys]
        instance = [track['popularity']] + audioAttributes
        instances.append([1, instance])
        training_ids.append(track["id"])

# Print total number of songs added
testCut = len(instances)
print(f"{str(testCut)} Top Tracks and Liked songs added!")

# Prompt user for "dislike" playlist IDs to add to training set with label 0
userSelection = ''
print("\nNow, Spotify makes it much more difficult to find music that you " \
	+ "*don't* like, \nso we're going to ask you to give the playlist ID(s) " \
	+ "\nfor playlists of songs that you don't like.")
print("Type 'done' when you're done adding playlists.")
num_playlists = 0
while userSelection.lower() != "done":
	userSelection = input("Enter playlist ID: ")
	if userSelection.lower() == "done":
		if num_playlists == 0:
			print("Please enter at least one playlist ID.")
		else:
			break
	try:
		addPlaylistTracks(userSelection, 0)
		num_playlists += 1
	except:
		print(f"\nCouldn't get songs from playlist ID {userSelection}.\n" \
			+ "Please make sure you're copying the correct ID string \n" \
			+ "that can be found at the end of the playlist URL.\n")

print("\nOK! Now enter a search term/phrase, and our program will find " \
	+ "playlists related it!\nOur program will go through these playlists" \
	+ " and pick out songs that are similar to songs\nyou like according " \
	+ "to Spotify's song data attributes.")
while True:
	search_str = input("Enter search string: ")
	result = sp.search(q=search_str, limit=3, type='playlist')
	if result['playlists']['total'] == 0:
		print("\nNo results found for {search_str}. :( \n" \
			+ "Please try another keyword: ")
	else:
		break

# Get playlists from search query, add songs from playlists to test set
testInstances = []
for item in result['playlists']['items']:
	print(f"\nSearching for songs in playlist: {item['name']}")
	playlist_tracks = get_playlist_songs(item['id'], attributeList)
	testInstances.extend(playlist_tracks)

# Configure datasets for passing into learning algorithms
random.shuffle(instances)
random.shuffle(testInstances)
testInstances = testInstances[:testCut]
training = instances
trainingLabels = [i[0] for i in training]
trainingAttributes = [i[1] for i in training]
testAttributes = [i[1] for i in testInstances]
testIds = [i[0] for i in testInstances]

# Scaling attributes
scaler = MinMaxScaler()
scaler.fit(trainingAttributes)
scaler.fit(testAttributes)
trainingAttributes = scaler.transform(trainingAttributes)
testAttributes = scaler.transform(testAttributes)

# DECISION TREES
print("\nFinding songs using Decision Trees to make predictions!")
clf2 = tree.DecisionTreeClassifier()
clf2 = clf2.fit(trainingAttributes, trainingLabels)
predictedLabels = clf2.predict(testAttributes)

# Create new playlist
playlist_name = "Spotibot: " + search_str.capitalize() + " Playlist (DT)"
playlists = sp.user_playlist_create(username, playlist_name)

# For all tracks with a predicted label of 1, add to playlist
track_ids = []
for i, prediction in enumerate(predictedLabels):
	if (prediction == 1):
		track_ids.append(testIds[i])
	if len(track_ids) > PLAYLIST_MAX_SONGS:
		break

if track_ids:
        sp.user_playlist_add_tracks(username, playlists['id'], track_ids)
        url = playlists['external_urls']['spotify']
        print(f"\nPlaylist {playlist_name} has been added to your library! \n" \
			+ "You can find it at: " + url)
        webbrowser.open(url)
# shap_values = shap.TreeExplainer(clf2).shap_values(trainingAttributes)
# shap.summary_plot(shap_values, trainingAttributes, plot_type="bar",
# 					feature_names=attributeList)
# shap.dependence_plot("Feature 9", shap_values[0], trainingAttributes)
# shap.summary_plot(shap_values, trainingAttributes)

result = export_text(clf2, feature_names=attributeList)
print(result)

# NAIVE BAYES
print("\nFinding songs using Naive Bayes to make predictions!")
clf3 = GaussianNB()
clf3 = clf3.fit(trainingAttributes, trainingLabels)
predictedLabels2 = clf3.predict(testAttributes)

playlist_name2 = "Spotibot: " + search_str.capitalize() + " Playlist (NB)"
playlists2 = sp.user_playlist_create(username, playlist_name2)

# For all tracks with a predicted label of 1, add to playlist
track_ids2 = []
for i, prediction in enumerate(predictedLabels2):
	if (prediction == 1):
		track_ids2.append(testIds[i])
	if len(track_ids2) > PLAYLIST_MAX_SONGS:
		break

if track_ids2:
        sp.user_playlist_add_tracks(username, playlists2['id'], track_ids2)
        url = playlists2['external_urls']['spotify']
        print(f"\nPlaylist {playlist_name} has been added to your library! \n" \
			+ "You can find it at: " + url)
        webbrowser.open(url)

in_common = len([song for song in track_ids if song in track_ids2])
print(f"\nThe playlists have {in_common} tracks in common!")
