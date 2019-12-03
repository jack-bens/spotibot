# Testing methods of getting and storing data for user's liked songs/artists

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

CLIENT_ID = "2f3b64d6217f4c36b44b10718e88a860"
CLIENT_SECRET = "d948722ed8804508962d797d9a9d7206"
USERNAME = "9qmimovhfjmws0vgx2gotnefa"

ccManager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=ccManager)

scope = "user-library-read user-top-read user-follow-read playlist-read-private"

username = ""
token = util.prompt_for_user_token(username, scope, client_id=CLIENT_ID,
                                   client_secret=CLIENT_SECRET, redirect_uri="http://localhost/")

if token:
    sp = spotipy.Spotify(auth=token)
else:
    print(f"Can't get token for {username}")
    sys.exit(1)

songs = {}
artists = {}

nextartist = None
while True:
	results = sp.current_user_followed_artists(limit=50, after=nextartist)
	for item in results["artists"]["items"]:
		name = item["name"]
		artists[name] = {"id": item["id"], "numSongs": 0, "numAlbums": 0,}
	nextartist = results["artists"]["cursors"]["after"]
	if not nextartist:
		break

while True:
	results = sp.current_user_saved_albums(limit=50) # TODO: offset
	for item in results["items"]:
		for artist in item["album"]["artists"]:
			name = artist["name"]
			if name in artists:
				artists[name]["numAlbums"] += 1
			else:
				artists[name] = {"id": artist["id"], "numSongs": 0, "numAlbums": 1,}
	if not results["next"]:
		break

print("Artists: ")
for artist in artists:
	print(f"{artist}: {artists[artist]}")

# Question: Do we want to include artists who were featured in songs / albums
# but aren't the primary artist?

print("\nTop tracks: ")
while True:
	results = sp.current_user_top_tracks(limit=50) # TODO: offset
	for item in results["items"]:
		print(f"{item['name']} (from {item['album']['name']})")
	if not results["next"]:
		break

print("\nTop artists: ")
while True:
	results = sp.current_user_top_artists(limit=50) # TODO: offset
	for item in results["items"]:
		print(f"{item['name']}") #(from {item['album']['name']})")
	if not results["next"]:
		break

print("\nbeep")
