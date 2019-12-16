import sys
import random
#import math
import spotipy
import spotipy.util as util
#import pandas as pd
import numpy as np
# from sklearn import tree
# from sklearn.neural_network import MLPClassifier
# from sklearn.naive_bayes import GaussianNB
# from sklearn.naive_bayes import BernoulliNB
# from sklearn.naive_bayes import MultinomialNB
# from sklearn.tree.export import export_text
# from sklearn import cluster
# from sklearn.linear_model import LogisticRegression
# import matplotlib.pyplot as plt

RANDOM_SEED = 12345
TRAINING_PERCENT = 0.6

CLIENT_ID = '2f3b64d6217f4c36b44b10718e88a860'
SECRET = 'd948722ed8804508962d797d9a9d7206'
USERNAME = '9qmimovhfjmws0vgx2gotnefa'

# Set permissions scope:
scope = 'user-library-read'
# Request user library access, get authentication token:
token = util.prompt_for_user_token(USERNAME, scope, client_id=CLIENT_ID,
                                   client_secret=SECRET,
								   redirect_uri='http://localhost/')
if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for", username)

# Set random seeds for random and numpy random (used by scikit-learn):
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Iterate through current user's playlists and build dataset:
playlists = sp.current_user_playlists()
i = 0
for p in playlists['items']:
	print(p['name'])
	playlist = sp.user_playlist_tracks(CLIENT_ID, p['id'])
	instances = []
	for t in playlist['items']:
		track = t['track']
		af = sp.audio_features(track['id'])[0]
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
		try:
			audioAttributes = [af[key] for key in af.keys() if key in attributeKeys]
			instance = [track['popularity']] + audioAttributes
			instances.append([i, instance])
		except:
			print(track)
			# There's something in the Jazz Vibes playlist that for some reason
			# isn't technically a track, and causes issues here
	# Increment i; playlists are labeled as buckets:
	i += 1
	# Print statement to check that label is correct and attributes look good:
	print(instances[-1])
