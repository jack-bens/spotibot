# spotifywrapper.py

import sys
import requests
import json
import spotipy
import spotipy.util as util

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
			'time_signature',
			'key',
		]

def get_playlist_songs(id, attributes=attributeKeys):
	""" Returns a list of instances, each as a list of attributes

	Keyword arguments:
	id -- playlist ID
	attributes -- list of attribute keys to get from audio features
		(default: pre-determined attributes list)
	"""
	r = requests.get(f'https://api.spotify.com/v1/playlists/{id}',
		headers={'Content-Type':'application/json',
				'Authorization':f'Bearer {token}'})
	if not r:
		print(f"Couldn't get playlist with ID {id}: Response {r.status_code}")
	else:
		instances = []
		for t in r.json()['tracks']['items']:
			track = t['track']
			af = sp.audio_features(track['id'])[0]
			instanceAttr = [af[key] for key in af.keys() if key in attributes]
			instanceAttr.append(track['popularity'])
			instances.append(instanceAttr)
	return(instances)

# Does not work yet:
def set_playlist_image(id, filename):
	""" Sets the playlist image

	id -- playlist ID
	filename -- image filename in spotibot directory
	"""
	try:
		image = open(filename, 'rb')
	except Exception as e:
		print(f"Couldn't open image: {e}")
		return None
	files = {'crying.jpg': image.read()}
	r = requests.put(f'https://api.spotify.com/v1/playlists/{id}/images',
		headers={'Content-Type':'image/jpeg',
				'Authorization':f'Bearer {token}'},
		body=image.read())
	print(r)
	print(r.text)
	if not r:
		print(f"Couldn't modify playlist image: Response {r.status_code}")
