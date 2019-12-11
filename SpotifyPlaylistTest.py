import spotipy
import spotipy.util as util
sp = spotipy.Spotify()
import csv

from spotipy.oauth2 import SpotifyClientCredentials

cid ="2f3b64d6217f4c36b44b10718e88a860" 
secret = "d948722ed8804508962d797d9a9d7206"
username = "9qmimovhfjmws0vgx2gotnefa"


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

tracks = sp.user_playlist_tracks(sp.current_user()['id'], chosenPlaylist['id'])
for t in tracks['items']:
   # results = sp.current_user_saved_tracks(limit=50, offset=location)
    print(t['track']['name'])
    track = t['track']
    instance = []                     
    instance.append(track['name'])
    instance.append(track['artists'][0]['name'])
    instance.append(track['id'])
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
            instance = []                     
            instance.append(track['name'])
            instance.append(track['artists'][0]['name'])
            instance.append(track['id'])
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
                                
                trainingInstances.append(instance)
        


print("Done!") 
print(len(trainingInstances))



