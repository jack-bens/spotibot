# spotifywrapper.py

import sys
import requests
import json
import spotipy
import spotipy.util as util

CLIENT_ID = '2f3b64d6217f4c36b44b10718e88a860'
SECRET = 'd948722ed8804508962d797d9a9d7206'

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

attributeList = ['popularity'] + attributeKeys

def get_playlist_name(token, id):
	""" Returns a playlist name

	Keyword arguments:
	token -- Spotify API authorization token
    id -- playlist ID
	"""
	r = requests.get(f'https://api.spotify.com/v1/playlists/{id}',
        headers={'Content-Type':'application/json',
                'Authorization':f'Bearer {token}'})
	if not r:
		print(f"Couldn't get playlist with ID {id}: Response {r.status_code}")
	else:
		return r.json()['name']

def get_playlist_songs(token, id, label=None, attributes=attributeKeys):
	""" Returns a list of instances, each as a list of attributes

	Keyword arguments:
	token -- Spotify API authorization token
	id -- playlist ID
	label -- label to associate with returned instances
		(default: if not specified, track IDs returned as labels)
	attributes -- list of attribute keys to get from audio features
	    (default: pre-determined attributes list)
	"""
	h = {'Content-Type':'application/json', 'Authorization':f'Bearer {token}'}
	r = requests.get(f'https://api.spotify.com/v1/playlists/{id}', headers=h)
	if not r:
		print(f"Couldn't get playlist with ID {id}: Response {r.status_code}")
	else:
		instances = []
		for t in r.json()['tracks']['items']:
			track = t['track']
			if track is None:
				continue
			r2 = requests.get('https://api.spotify.com/v1/audio-features/' \
				+ f"{track['id']}", headers=h)
			if r2:
				af = r2.json()
				instanceAttr = [af[key] for key in attributeKeys]
				instanceAttr = [track['popularity']] + instanceAttr
				if label != None:
					instances.append([label, instanceAttr])
				else:
					instances.append([track['id'], instanceAttr])
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
