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
sp = spotipy.Spotify()
import csv

RANDOM_SEED = 473463298
TRAINING_PERCENT = 0.75
UPBEAT_ID = "3DFoRKv3xS2cHTIr0h3txX"
NONUPBEAT_ID = "3fNcrDFpar3QMWAc5fji9G"


from spotipy.oauth2 import SpotifyClientCredentials

cid ="2f3b64d6217f4c36b44b10718e88a860"
CLIENT_ID = cid
secret = "d948722ed8804508962d797d9a9d7206"
username = "9qmimovhfjmws0vgx2gotnefa"

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
attributeList = ['duration_ms',
		'danceability',
		'energy',
		'instrumentalness',
		'liveness',
		'loudness',
		'speechiness',
		'tempo',
		'valence','mode', 'popularity']

print(attributeList)

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
	instances.append([1, instance])


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
	instances.append([0, instance])

# Shuffle instances and split into label array and attribute array:
random.shuffle(instances)

trainingLabels = []
trainingAttributes = []
for i in instances:
	trainingLabels.append(i[0])
	trainingAttributes.append(i[1])

trainingAttributes = preprocessing.normalize(trainingAttributes, norm='l1')

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
'''
print(trainingLabels)
#clf = GaussianNB()
#clf = clf.fit(trainingAttributes, trainingLabels)
#result = export_text(clf)
print(result)
tree.plot_tree(clf)'''

## data visualizations
# shap_values = shap.TreeExplainer(clf).shap_values()
# shap.summary_plot(shap_values, X_train, plot_type="bar")



############ Splitting into trainin/test sets
div = int(TRAINING_PERCENT * float(len(instances)))
training = instances[:div]
testing = instances[div:]
trainingLabels = [i[0] for i in training]
trainingAttributes = [i[1] for i in training]
testLabels = [i[0] for i in testing]
testAttributes = [i[1] for i in testing]

trainingAttributes = preprocessing.scale(trainingAttributes)
testAttributes = preprocessing.scale(testAttributes)

# clf = tree.DecisionTreeClassifier()
clf = GaussianNB()
# clf = RandomForestRegressor()

'''
clf = MLPClassifier(
			hidden_layer_sizes=(50,), # 1 hidden layer, 50 hidden neurons
			activation="logistic", # Activation function = Logistic
			solver="sgd", # Weight optimization: stochastic gradient descent
			max_iter=500, # Number of epochs
			#verbose=True, # Print progress messages to stdout
		)'''
clf = clf.fit(trainingAttributes, trainingLabels)
predictedLabels = clf.predict(testAttributes)
'''
newPredict = []
for label in predictedLabels:
    if label > 0.5:
        newPredict.append(1)
    else:
        newPredict.append(0)
predictedLabels = newPredict'''
print(predictedLabels)
matrix = writeConfMatrix([0,1], testLabels, predictedLabels)
print(calculateAccuracy([0,1], len(predictedLabels), matrix))
# shap_values = shap.TreeExplainer(clf).shap_values(trainingAttributes)
# shap.summary_plot(shap_values, trainingAttributes, plot_type="bar", feature_names=attributeList)
#shap.dependence_plot("Feature 9", shap_values[0], trainingAttributes)
#shap.summary_plot(shap_values, trainingAttributes)

#result = export_text(clf)
#print(result)

print("Done!") 
print(len(trainingAttributes))


