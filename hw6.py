# coolvapetricks.py
# 12/1/19
# Maya Shanmugam, Jack Bens

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

# Tree visual imports
#from sklearn.externals.six import StringIO
#from IPython.display import Image
#from sklearn.tree import export_graphviz
#import pydotplus

TRAINING_PERCENT = 0.6
DATASETS = [
	"monks1.csv",
	"mnist_1000.csv",
	"votes.csv",
	"hypothyroid.csv",
]

################################################################################
##### DATASETS

class Datasets:

	# Read in and process files, store data in class variable self.data:
	def __init__(self):
		self.data = {}
		for filename in DATASETS:
			try:
				filedata = pd.read_csv(filename)
			except Exception as e:
				print(f"Error while reading training data files: {e}")
				sys.exit(1)
			columns = list(filedata.columns.values)
			# Convert categorical attributes (ignoring label) to one-hot:
			dataframe = pd.concat([filedata[[columns[0]]],
				pd.get_dummies(filedata[columns[1:]], drop_first=True)], axis=1)
			# Shuffle instances
			instances = [[i[0], list(i)[1:]] for i in dataframe.values]
			random.shuffle(instances)
			# Divide into training and test sets:
			div = int(TRAINING_PERCENT * float(len(instances)))
			training = instances[:div]
			testing = instances[div:]
			# Reformat data as label list and attribute list (ID = list index):
			trainingLabels = [i[0] for i in training]
			trainingAttributes = [i[1] for i in training]
			testLabels = [i[0] for i in testing]
			testAttributes = [i[1] for i in testing]
			# Store list of all possible labels:
			labels = list(set(trainingLabels + testLabels))
			# Storing processed dataset in dictionary:
			dataset = {
				"trainingAttr": trainingAttributes,
				"trainingLabels": trainingLabels,
				"testAttr": testAttributes,
				"testLabels": testLabels,
				"labels": labels,
			}
			self.data[filename] = dataset

	# Retrieve pre-processed dataset from dictionary (default: return all):
	def getData(self, filename="all"):
		if filename == "all":
			return self.data
		else:
			return self.data[filename]

################################################################################
##### DECISION TREE

class DecisionTree:

	def __init__(self, dataset):
		self.ds = dataset
		# Set up decision tree:
		self.dtree = tree.DecisionTreeClassifier()
		# Train on training set:
		self.dtree.fit(self.ds["trainingAttr"], self.ds["trainingLabels"])

	# Predict test set, return predicted labels:
	def predictTestSet(self):
		return self.dtree.predict(self.ds["testAttr"])

	# Plot decision tree:
	def plotDT(self):
		tree.plot_tree(self.dtree)
		# Visualize the tree and save as png file:
		dot_data = StringIO()
		export_graphviz(self.dtree, out_file=dot_data,
			filled=True, rounded=True,
			special_characters=True)
		graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
		# Save file:
		graph.write_png("vote_tree.png")

################################################################################
##### NEURAL NETWORK

class NeuralNet:

	def __init__(self, dataset):
		self.ds = dataset
		# Set up neural network:
		self.nnet = MLPClassifier(
			hidden_layer_sizes=(50,), # 1 hidden layer, 50 hidden neurons
			activation="logistic", # Activation function = Logistic
			solver="sgd", # Weight optimization: stochastic gradient descent
			max_iter=500, # Number of epochs
			#verbose=True, # Print progress messages to stdout
		)
		# Train on training set:
		self.nnet.fit(self.ds["trainingAttr"], self.ds["trainingLabels"])

	# Predict test set, return predicted labels:
	def predictTestSet(self):
		return self.nnet.predict(self.ds["testAttr"])

################################################################################
##### NAIVE BAYES

class NaiveBayes:

	def __init__(self, dataset):
		self.ds = dataset
		# Set up naive bayes:
		self.nbayes = GaussianNB()
		#self.nbayes = BernoulliNB()
		#self.nbayes = MultinomialNB()
		# Train on training set:
		self.nbayes.fit(self.ds["trainingAttr"], self.ds["trainingLabels"])

	# Predict test set, return predicted labels:
	def predictTestSet(self):
		return self.nbayes.predict(self.ds["testAttr"])

################################################################################
##### CALCULATE ACCURACY AND CONFUSION MATRIX

# Write output file with confusion matrix:
def writeConfMatrix(approach, dsFilename, labels, trueLabels, predictedLabels):
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
	with open(f"results_{approach}_{dsFilename}", "w") as output:
		writer = csv.writer(output, lineterminator=',\n')
		writer.writerow(matrix[0])
		writer = csv.writer(output, lineterminator='\n')
		writer.writerows(matrix[1:])
		output.close()
	# Return confusion matrix:
	return confMatrix

# Calculate and print the accuracy and 95% confidence interval:
def calculateAccuracy(approach, dsFilename, labels, numPredictions, confMatrix):
	correct = 0
	for l in labels:
		correct += confMatrix[l][l]
	accuracy = float(correct) / float(numPredictions)
	interval = 2.24 * math.sqrt((accuracy * (1 - accuracy)) \
				/ (numPredictions))
	print(f"{approach} approach with {dsFilename}: ")
	print("Accuracy on test set: %.4f"%(accuracy))
	print("Confidence interval: [%.4f,%.4f]"%((accuracy-interval), \
			(accuracy+interval)))
	print()

################################################################################
##### INITIALIZATION

def main():
	# Read and validate command line argument:
	try:
		if len(sys.argv) != 2:
			sys.exit(1)
		seed = int(sys.argv[1])
		# Set random seed:
		random.seed(seed)
		np.random.seed(seed)
	except:
		print("Please enter a positive integer for random seed.")
		sys.exit(1)
	# Initialize datasets:
	datasets = Datasets()
	# Run all ML approaches on all datasets:
	for file in DATASETS:
		# Get dataset:
		ds = datasets.getData(file)
		# Initialize decision tree and predict on test set:
		dt = DecisionTree(ds)
		predictions = dt.predictTestSet()
		# Calculate confusion matrix and print accuracy for decision tree:
		confMatrix = writeConfMatrix("DecisionTrees", file, ds["labels"],
			ds["testLabels"], predictions)
		calculateAccuracy("Decision Tree", file, ds["labels"],
			len(ds["testLabels"]), confMatrix)
		Initialize neural net and predict on test set:
		nn = NeuralNet(ds)
		predictions = nn.predictTestSet()
		# Calculate confusion matrix and print accuracy for neural net:
		confMatrix = writeConfMatrix("NeuralNetworks", file, ds["labels"],
			ds["testLabels"], predictions)
		calculateAccuracy("Neural Network", file, ds["labels"],
			len(ds["testLabels"]), confMatrix)
		# Run Naive Bayes on all datasets:
		nb = NaiveBayes(ds)
		predictions = nb.predictTestSet()
		# Calculate confusion matrix and print accuracy for naive bayes:
		confMatrix = writeConfMatrix("NaiveBayes", file, ds["labels"],
			ds["testLabels"], predictions)
		calculateAccuracy("Naive Bayes", file, ds["labels"],
			len(ds["testLabels"]), confMatrix)
		print()

main()
