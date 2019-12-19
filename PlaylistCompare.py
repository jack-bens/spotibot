#Playlist Comparison Tool
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
    result = get_playlist_songs(PLAYLIST_ID, attributeList)
    tracks = [i[1] for i in result]
    for track in tracks:#["items"]:
            #track = t["track"]
            #print("Adding track to data set: " + track['name'])
            #af = sp.audio_features(track["id"])[0]
            #attributeKeys = [
            #        'duration_ms',
            #        'danceability',
            #        'energy',
            #        'instrumentalness',
            #        'liveness',
            #        'loudness',
            #        'speechiness',
            #        'tempo',
            #        'valence',
            #        'mode',
            #        'key',
            #        'time_signature'
            #]
            #audioAttributes = [af[key] for key in af.keys() if key in attributeKeys]
            #instance = [track['popularity']] + audioAttributes
            instances.append([label, track])


username = input("Hello! Please enter your spotify username (this may be a seemingly random string of characters found on your 'account details' page): ")
scope = 'user-library-read'
token = util.prompt_for_user_token(username, scope, client_id=cid,
                                   client_secret=secret, redirect_uri='http://localhost/')

if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for", username)

location = 0
lenSongs = int(sp.current_user_saved_tracks()['total'])
trainingInstances = []

userSelection = ''
print("This program lets you input a series of playlists and split them into two sets.")
print("the program will read all of the songs from these playlists and give them a label according to which set it belongs to.")
print("You will then be given the option of running a number of different learning algorithms to see how a computer might go about guessing which of the sets a song comes from based on its Spotify features")
print("Playlist URL's have the format: ")
print("'https://open.spotify.com/playlist/3DFoRKv3xS2cHTIr0h3txX'. ")
print("You will be asked to give the ID for each playlist, which is the part after '/playlist/")
print("so in the previous example, it would be '3DFoRKv3xS2cHTIr0h3txX'")
print("Enter playlist ID's to be part of the first set (type 'done' to continue and add playlists to the second set): ")
while userSelection != 'done':
    userSelection = input("Enter playlist ID: ")
    if userSelection == 'done':
        break
    addPlaylistTracks(userSelection, 1)

print("Now enter playlists to go in the second set.")
userSelection = ''
while userSelection != 'done':
    userSelection = input("Enter playlist ID: ")
    if userSelection == 'done':
        break
    addPlaylistTracks(userSelection, 0)

random.shuffle(instances)
print(instances)

trainingLabels = []
trainingAttributes = []
for i in instances:
	trainingLabels.append(i[0])
	trainingAttributes.append(i[1])

# trainingAttributes = preprocessing.normalize(trainingAttributes, norm='l1')

div = int(TRAINING_PERCENT * float(len(instances)))
training = instances[:div]
testing = instances[div:]
trainingLabels = [i[0] for i in training]
trainingAttributes = [i[1] for i in training]
testLabels = [i[0] for i in testing]
testAttributes = [i[1] for i in testing]

trainingAttributes = preprocessing.scale(trainingAttributes)
testAttributes = preprocessing.scale(testAttributes)


print("Running Naive Bayes: ")
clf1 = GaussianNB()

clf1 = clf1.fit(trainingAttributes, trainingLabels)
predictedLabels = clf1.predict(testAttributes)

print(predictedLabels)
matrix = writeConfMatrix([0,1], testLabels, predictedLabels)
print(calculateAccuracy([0,1], len(predictedLabels), matrix))

print("Running neural network:")
clf3 = MLPClassifier(
			hidden_layer_sizes=(50,), # 1 hidden layer, 50 hidden neurons
			activation="logistic", # Activation function = Logistic
			solver="sgd", # Weight optimization: stochastic gradient descent
			max_iter=500, # Number of epochs
			#verbose=True, # Print progress messages to stdout
		)
clf3 = clf3.fit(trainingAttributes, trainingLabels)
predictedLabels = clf3.predict(testAttributes)
print(predictedLabels)
matrix = writeConfMatrix([0,1], testLabels, predictedLabels)
print(calculateAccuracy([0,1], len(predictedLabels), matrix))


print("Now running decision trees")
clf2 = tree.DecisionTreeClassifier()
clf2 = clf2.fit(trainingAttributes, trainingLabels)
predictedLabels = clf2.predict(testAttributes)
print(predictedLabels)
matrix = writeConfMatrix([0,1], testLabels, predictedLabels)
print(calculateAccuracy([0,1], len(predictedLabels), matrix))
shap_values = shap.TreeExplainer(clf2).shap_values(trainingAttributes)
shap.summary_plot(shap_values, trainingAttributes, plot_type="bar", feature_names=attributeList)
#shap.dependence_plot("Feature 9", shap_values[0], trainingAttributes)
shap.summary_plot(shap_values, trainingAttributes)

result = export_text(clf2, feature_names=attributeList)

# Plot decision tree:
tree.plot_tree(clf2)
# Visualize the tree and save as png file:
dot_data = StringIO()
export_graphviz(clf2, out_file=dot_data,
    filled=True, rounded=True,
    special_characters=True)
graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
# Save file:
graph.write_png("PlaylistComparisonTree.png")

print(result)


print("Done!") 
print(len(trainingAttributes))
