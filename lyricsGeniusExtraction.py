from lyricsgenius import Genius 
import time
import json
import numpy as np

genius = Genius("6wlsY_-R8KlnB4kg6o8BSAyyLN97jkD8aAaFDV7K5NME5BP9vEGCb_RU5euo20C0", skip_non_songs=True, excluded_terms=["Remix", "(Live)", "Instrumental", "A Cappella", "Skit", "Album Version", "Edited", "Live From", "Live On"], remove_section_headers=True)
artist = genius.search

# removes website features from API values
def cleanLyrics(lyrics): 
    lyrics = lyrics.split("\n")
    lines_to_remove = []

    for count, line in enumerate(lyrics):
        if "Translations" in line:
            if "Lyrics" in line:
                lines_to_remove.append(count) 
        
        lyrics[count] = line.replace("You might also like", "").replace("Embed", "")

    for line in lines_to_remove:
        lyrics[line] = ""

    lyrics = "\n".join(lyrics)
    return lyrics

def getAlbumLyrics(artist, albums):
    album_list = []
    albums_dict = {}

    for album_name in albums:
        time.sleep(np.random.uniform(5, 7)) # wait between API calls

        albums_dict[album_name] = {}

        processed_album_name = album_name.replace("Deluxe", "").replace("Edition", "").replace("Version", "") # removes extraneous features from Spotify album names
        album = genius.search_album(processed_album_name, artist, text_format=True)
        album_list.append(album)

    for count, album in enumerate(album_list):    
        album_dict = album.to_dict()

        for track in album_dict["tracks"]:
            song_dict = track
            lyrics = song_dict["song"]["lyrics"]
            song_dict["song"]["lyrics"] = cleanLyrics(lyrics) # returns cleaned lyrics without website features

        albums_dict[albums[count]] = album_dict
    
    with open('lyrics.json', 'w') as fp:
        json.dump(albums_dict, fp, indent=4)