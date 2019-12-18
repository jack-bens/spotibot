import sys
import requests
#import random
#import math
import spotipy
import spotipy.util as util
#import pandas as pd
#import numpy as np
# from sklearn import tree
# from sklearn.neural_network import MLPClassifier
# from sklearn.naive_bayes import GaussianNB
# from sklearn.naive_bayes import BernoulliNB
# from sklearn.naive_bayes import MultinomialNB
# from sklearn.tree.export import export_text
# from sklearn import cluster
# from sklearn.linear_model import LogisticRegression
# import matplotlib.pyplot as plt
from spotifywrapper import get_playlist_songs
from spotifywrapper import set_playlist_image

RANDOM_SEED = 12345
TRAINING_PERCENT = 0.6

CLIENT_ID = '2f3b64d6217f4c36b44b10718e88a860'
SECRET = 'd948722ed8804508962d797d9a9d7206'
USERNAME = '9qmimovhfjmws0vgx2gotnefa'

LOFI_ID = '1yybUz6p7pwtmXsEt3rlR6'

# Set permissions scope:
scope = 'user-library-read playlist-modify-public playlist-modify-private ugc-image-upload'
# Request user library access, get authentication token:
token = util.prompt_for_user_token(USERNAME, scope, client_id=CLIENT_ID,
                                   client_secret=SECRET,
								   redirect_uri='http://localhost/')
if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for", username)

# Set random seeds for random and numpy random (used by scikit-learn):
# random.seed(RANDOM_SEED)
# np.random.seed(RANDOM_SEED)

# sp.user_playlist_create(USERNAME,
	# "lofi hip hop beats to have a mental breakdown to")

playlistname = sp.user_playlist(USERNAME, LOFI_ID)['name']
playlistnamewords = playlistname.split(' ')
i = int(playlistnamewords[-1])
i += 1
sp.user_playlist_change_details(USERNAME, LOFI_ID,
	name=f"lofi hip hop beats to have a mental breakdown to - iteration {i}")

sp.user_playlist_add_tracks(USERNAME, LOFI_ID, ['2PpruBYCo4H7WOBJ7Q2EwM'])
print(get_playlist_songs(LOFI_ID))

#set_playlist_image(LOFI_ID, 'crying.jpg')
