import spotipy
from spotipy.oauth2 import SpotifyClientCredentials 
import time
import numpy as np
import pandas as pd
import sqlite3

artist = "Eminem"

conn = sqlite3.connect(artist)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS albums (album text, track_number number, id number, name text, uri text, acousticness number, danceability number, energy number, instrumentalness number, liveness number, loudness number, speechiness number, tempo number, valence number, popularity number)')
conn.commit()

# client info for Spotify API
client_id= "5682e53212274b6eb78494ecfa315539"
client_secret = "ff5c7417e0f34576b41d5e84a8dfa9e6"
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager) 

# access album's audio features by looping through each song
def getSongsFromAlbum(album):
    spotify_albums[album] = {}

    for data_type in ['album', 'track_number', 'id', 'name', 'uri']:
        spotify_albums[album][data_type] = []

    songs = sp.album_tracks(album)

    for k in range(len(songs['items'])):
        spotify_albums[album]['album'].append(album_names[album_count])

        for data_type in ['track_number', 'id', 'name', 'uri']:
            spotify_albums[album][data_type].append(songs['items'][k][data_type])

def getAudioFeatures(album):
    features = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence', 'popularity']

    for feature in features:
        spotify_albums[album][feature] = []

    song_count = 0
    
    features.pop()
    for song in spotify_albums[album]['uri']:
        trackFeatures = sp.audio_features(song)

        for feature in features:
            spotify_albums[album][feature].append(trackFeatures[0][feature])

        pop = sp.track(song)
        spotify_albums[album]['popularity'].append(pop['popularity'])
        song_count += 1

# # # INITIALIZATION # # #

result = sp.search(artist)
artist_uri = result['tracks']['items'][0]['artists'][0]['uri']
albums = sp.artist_albums(artist_uri, album_type="album", limit="50")
print('made it here')
album_names = []
album_uris = []
album_dict = {}

for i in range(len(albums['items'])):
    album_names.append(albums['items'][i]['name'])
    album_uris.append(albums['items'][i]['uri'])

# # # GET SONGS FROM ALBUM # # #

spotify_albums = {}
album_count = 0
for i in album_uris:
    getSongsFromAlbum(i)
    print("Album " + str(album_names[album_count]) + " songs has been added to spotify_albums dictionary")
    album_count+=1 

# # # GET AUDIO FEATURES # # #

sleep_min = 2
sleep_max = 5
start_time = time.time()
request_count = 0

for i in spotify_albums:
    getAudioFeatures(i)
    request_count+=1
    if request_count % 5 == 0:
        print(str(request_count) + " albums processed")
        time.sleep(np.random.uniform(sleep_min, sleep_max))
        print('Loop #: {}'.format(request_count))
        print('Elapsed Time: {} seconds'.format(time.time() - start_time))

dic_df = {}

# # # CONVERT TO EASIER DICTIONARY # # #

for data_type in ['album', 'track_number', 'id', 'name', 'uri', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'valence', 'popularity']:
    dic_df[data_type] = []

# new dictionary has no album column
for album in spotify_albums:
    for feature in spotify_albums[album]:
        dic_df[feature].extend(spotify_albums[album][feature])

# # # FILTERING PROCESS # # #

df = pd.DataFrame.from_dict(dic_df)
print('Original Size: {}'.format(len(df)))

# remove depulicates with name variations ("Album Version", "Instrumental", etc.), skits, remixes, and edits
df = df[df['name'].str.contains('Instrumental|A Cappella|Skit|Album Version|Edited|Live From|- Live|Live On') == False]
# sort by popularity and index, moving duplicate albums to the bottom of the list
df = df.sort_values('popularity', ascending=False).sort_index()

print('Filtered Size: {}'.format(len(df)))

# # # CONVERT TO SQL / CSV # # #

df.to_sql("albums", conn, if_exists='replace', index = False)
c.execute("SELECT * FROM albums")

for row in c.fetchall():
    print (row)