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
