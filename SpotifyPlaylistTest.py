import spotipy
import spotipy.util as util
sp = spotipy.Spotify()
from spotipy.oauth2 import SpotifyClientCredentials

cid ="2f3b64d6217f4c36b44b10718e88a860" 
secret = "d948722ed8804508962d797d9a9d7206"
username = "9qmimovhfjmws0vgx2gotnefa?si=hrhvcv_mQ0O_hCErTn5TIQ"


#client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret) 
#sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

scope = 'user-library-read'
token = util.prompt_for_user_token(username, scope, client_id=cid,
                                   client_secret=secret, redirect_uri='http://localhost/')

if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for", username)

lizzo_uri = 'spotify:artist:56oDRnqbIiwx4mymNEv7dS'

results = sp.artist_albums(lizzo_uri, album_type='album')
albums = results['items']
while results['next']:
    results = sp.next(results)
    albums.extend(results['items'])

for album in albums:
    print(album['name'])
