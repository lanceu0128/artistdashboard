# import numpy as np
import matplotlib.pyplot as plt # unused graphs made in matplotlib
import sqlite3
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS
import json

# plt.style.use('seaborn-v0_8-pastel')

conn = sqlite3.connect('eminem')
c = conn.cursor()

stopwords = set(STOPWORDS)

features = ['acousticness', 'danceability', 'energy', 'instrumentalness', 'speechiness', 'tempo', 'valence', 'acousticness']

def getAlbumFeatures(album):
    c.execute("""SELECT album, AVG(acousticness) as avg_acousticness, 
    AVG(danceability) as avg_danceability,
    AVG(energy) as avg_energy,
    AVG(instrumentalness) as avg_instrumentalness,
    AVG(speechiness) as avg_speechiness,
    AVG(tempo) as avg_tempo,
    AVG(valence) as avg_valence
    FROM albums WHERE album='{}' GROUP BY album""".format(album)) # all Spotify metrics except Liveness, Loudness, and Popularity

    for row in c.fetchall():
        row_list = list(row)
        row_list.pop(0)
        row_list[5] = row_list[5]/220 # tempo needs to be converted to a 0-1 scale for consistency

        row_list = [*row_list, row_list[0]] # adds first feature to end of list for radar chart consistency
        return (row_list)

def getAlbumPopularity(album):
    c.execute("""SELECT album, name, popularity
    FROM albums WHERE album='{}'""".format(album))
    row_list = []

    for row in c.fetchall():
        row_list.append(row[2])
    return row_list    

def getSongFeatures(albums):
    features = {}
    colors = ["blue", "red", "green", "purple", "orange", "light blue", "pink", "light green", "light pink", "gold"]

    for data_type in ["album", "track", "danceability", "valence", "popularity", "color", "text", "opacity"]:
        features[data_type] = []

    col = 0
    for album in albums:
        c.execute("""SELECT album, name, danceability, valence, popularity
        FROM albums WHERE album='{}' """.format(album))

        for row in c.fetchall():
            i = 0
            for data_type in ["album", "track", "danceability", "valence", "popularity"]:
                features[data_type].append(row[i])
                i += 1
            features["color"].append(colors[col]) # cycles through default graph colors
            features["text"].append(row[0] + "<br>" + row[1] + "<br> Popularity Score: " + str(row[4]))
            features["opacity"].append(row[4] / 100) # convert popularity score into usable opacity measure from 0-1
        col += 1

    return features   

def getFeaturesGraph(artist, albums):

    album_features = []

    for album in albums:
        album_features.append(getAlbumFeatures(album))

    fig = go.Figure()
    
    for i in range(len(album_features)):
        fig.add_trace(go.Scatterpolar(
        r = album_features[i],
        theta = features,
        fill = 'toself',
        name=albums[i]
    ))

    fig.update_layout(
        title='Feature Metrics by Album',
        paper_bgcolor='rgb(243, 243, 243)',
        plot_bgcolor='rgb(243, 243, 243)',
        polar=dict(
            radialaxis = dict(
            visible = True,
            range= [0, 1]
            )),
        showlegend=False
    )

    return fig

    # # # MATPLOTLIB VERSION # # #

    # label_loc = np.linspace(start=0, stop=2 * np.pi, num=len(features))

    # plt.figure(figsize=(8, 8))
    # ax = plt.subplot(polar=True)

    # for i in range(len(albums)):
    #     try:
    #         plt.plot(label_loc, album_features[i], label=albums[i])
    #         # ax.fill(label_loc, album_features[i], color=colors[i], alpha=0.25)
    #     except:
    #         print("Invalid Album")
    #         return

    # plt.title('Album Feature Comparison', size=20)
    # lines, labels = plt.thetagrids(np.degrees(label_loc), labels=features)

    # plt.legend()
    # plt.show()

def getPopularityGraph(artist, albums):
    
    album_popularities = [] 

    for album in albums:
        album_popularities.append(getAlbumPopularity(album))

    fig = go.Figure()

    for i in range(len(album_popularities)):
        fig.add_trace(go.Box(
            x = album_popularities[i],
            name = albums[i],
        ))

    fig.update_layout(
        title='Distribution of Popularity by Album',
        xaxis=dict(
            title='Popularity (0-100)',
            gridcolor='white',
            gridwidth=2,
        ),
        yaxis=dict(
            title='Album',
            gridcolor='white',
            gridwidth=2,
        ),
        paper_bgcolor='rgb(243, 243, 243)',
        plot_bgcolor='rgb(243, 243, 243)',
    )

    return fig

    # # # MATPLOTLIB VERSION # # #

    # min_y = min(album_popularities) - 5
    # max_y = max(album_popularities) + 5
    
    # fig = plt.figure(figsize = (10, 5))
    # ax = plt.bar(albums, album_popularities)

    # for i in range(len(albums)):
    #     # lbl = albums[i][0:19] + "..." if len(albums[i]) > 20 else albums[i]
    #     plt.bar(albums[i], album_popularities[i])

    # plt.xlabel("Album")
    # plt.ylabel("Spotify Popularity Metric")
    # plt.ylim(min_y, max_y)
    # plt.title("Album Popularity")
    # plt.show()

def getWordCloud(artist, album):
    
    f = open('lyrics.json')
    data = json.load(f)
    f.close()

    tracks = data[album]['tracks']
    lyrics = ''

    for track in tracks:
        lyrics = lyrics + track["song"]["lyrics"]
    
    wordcloud = WordCloud(width = 400, height = 300, background_color ='white', stopwords = stopwords, min_font_size = 10).generate(lyrics)
    # stopwords are words to not be included (the, and, etc.)

    return wordcloud.to_image()

def getBubbleChart(artist, albums):

    features = getSongFeatures(albums)

    fig = go.Figure(data=[go.Scatter(
    x = features["danceability"], y = features["valence"], 
    text = features["text"],
    mode='markers',
    marker=dict(
        color = features["color"],
        size = features["popularity"],
        sizemode = 'diameter',
        opacity = features["opacity"], # list of converted popularity scores
        )
    )])

    fig.update_layout(
        title='Danceability and Valence vs. Popularity Per Song',
        xaxis=dict(
            title='Danceability (0-1)',
            gridcolor='white',
            type='log',
            gridwidth=2,
        ),
        yaxis=dict(
            title='Valcence (0,1)',
            gridcolor='white',
            gridwidth=2,
        ),
        paper_bgcolor='rgb(243, 243, 243)',
        plot_bgcolor='rgb(243, 243, 243)',
    )

    return fig