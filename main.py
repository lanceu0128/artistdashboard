from dash import Dash, html, dcc, dependencies
import graphCreators
import sqlite3

artist = 'Eminem'
albums = []

conn = sqlite3.connect(artist)
c = conn.cursor()

c.execute("""SELECT album, name, popularity
    FROM albums ORDER BY popularity DESC""")

for row in c.fetchall():
    if row[0] not in albums:
        albums.append(row[0])
    albums = albums[:10] # returns top 10 most popular albums by artist

app = Dash(__name__)

features_graph = graphCreators.getFeaturesGraph(artist, albums)
popularity_graph = graphCreators.getPopularityGraph(artist, albums)
bubble_chart = graphCreators.getBubbleChart(artist, albums)

app.layout = html.Div(children=[
    html.H1(children='{} Visualized'.format(artist), style = {'text-align': 'center'}),

    html.Div(children='''
        Artist: {} Albums Being Tested: {}
    '''.format(artist, albums)),

    html.Div(children = [ 
        html.Div(
            dcc.Graph(
                id = 'features-graph',
                figure = features_graph
            ),
        style = {'grid-area ': 'feature-div'}),

        html.Div(
            dcc.Graph(
                id = 'popularity-graph',
                figure = popularity_graph
            ),
        style = {'grid-area': 'popularity-div'}),

        html.Div(
            dcc.Graph(
                id = 'bubble-chart',
                figure = bubble_chart
            ),
        style = {'grid-area': 'bubble-div'}),

    ], style={'display': 'grid', 'gap': '5px', 
    'grid-template-areas': ' "feature-div popularity-div popularity-div" "bubble-div bubble-div bubble-div" '}) # creates grid of graphs
])

if __name__ == '__main__':
    app.run_server(debug=True)