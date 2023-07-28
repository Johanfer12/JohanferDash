from dash import Dash, dcc, html
import sqlite3
import ast
import plotly.graph_objs as go
import os

# Obtener la ruta absoluta al directorio raíz del código
base_dir = os.path.dirname(os.path.abspath(__file__))

# Conectar a la base de datos en el directorio raíz
db_path = os.path.join(base_dir, 'spotify_stats.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear una tabla para almacenar las estadísticas
cursor.execute('''CREATE TABLE IF NOT EXISTS spotify_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    most_played_artist TEXT,
                    most_played_songs TEXT,
                    total_playtime INTEGER,
                    total_favorites	INTEGER,
                    top_artists TEXT,
                    top_genres TEXT,
                    top_genres_percentages TEXT,
                    recent_favorite_songs TEXT
                )''')

# Obtén las estadísticas desde la base de datos
cursor.execute('SELECT * FROM spotify_stats LIMIT 1')
row = cursor.fetchone()
if row:
    most_played_artist = row[1]
    most_played_songs = row[2]
    total_playtime = row[3]
    total_favorites = row[4]
    top_artists = row[5]
    top_genres = row[6]
    top_genres_percentages = row[7]
    recent_favorite_songs = row[8]
else:
    most_played_artist = "N/A"
    most_played_songs = "N/A"
    total_playtime = 0
    top_artists = "N/A"
    top_genres = "N/A"
    top_genres_percentages = "N/A"
    recent_favorite_songs = "N/A"

most_played_songs_list = ast.literal_eval(most_played_songs)
most_played_songs_bullet = html.P([
    html.P([
        html.A(html.Img(src="assets/Play.svg", className="song-icon"),href=song['song_url']),
        html.A(f"{song['song_name'].split(' -')[0].strip()} - {song['artist_name']}",href=song['song_url'])
    ])
    for song in most_played_songs_list
])

# Convertir el tiempo total de reproducción a días, horas, minutos y segundos
seconds = total_playtime % 60
minutes = (total_playtime // 60) % 60
hours = (total_playtime // 3600) % 24
days = total_playtime // 86400

# Obtener las canciones guardadas como favoritas
recent_favorite_songs_list = ast.literal_eval(recent_favorite_songs)
recent_favorite_songs_bullet = html.P([
    html.P([
        html.A(html.Img(src="assets/Play.svg", className="song-icon"),href=song['song_url']),
        html.A(f"{song['song_name'].split(' -')[0].strip()} - {song['artist_name']}", href=song['song_url'])
    ])
    for song in recent_favorite_songs_list
])

top_artists_list = top_artists.split(", ")
top_artists_bullet = html.P([
    html.P([
        html.Img(src="assets/mic.svg", className="artist-icon"),
        artist
    ])
    for artist in top_artists_list
])

playtime = html.P(
    html.Div([
        html.Img(src="assets/time.svg", className="time-icon"),
        html.Span(f' {days} Días, {hours} Horas, {minutes} Minutos, {seconds} Segundos en {total_favorites} Canciones.', className='songs-time')
    ], className="time-container")
)

# Convertir los géneros y porcentajes en datos para la gráfica de torta
top_genres_list = ast.literal_eval(top_genres)
top_genres_percentages_list = ast.literal_eval(top_genres_percentages)

# Definir los colores personalizados en tonos de azul y violeta
custom_colors = ['#5472d3', '#7e58c2', '#a647ba', '#d43d80', '#d33da2']

data = [go.Pie(
    labels=[label.title() for label in top_genres_list],  # Aplica title() a cada etiqueta
    values=top_genres_percentages_list,
    marker=dict(colors=custom_colors),
)]

line = html.Div(
    children=[
        html.Div(className='gradient-line')
    ]
)

# Crear una instancia de la aplicación Dash
app = Dash(__name__)
app.title = 'Dash de Johan'

# Definir el diseño de la aplicación
app.layout = html.Div(
    className='container',
    children=[
        html.Div(
            className='left-column',
            children=[
                html.H1('Estadísticas Spotify de Johan', style={'textAlign': 'center'}),
                html.H3(f'Artista más escuchado: {most_played_artist}', className='margin-left'),
                line,
                html.H3('Canciones más reproducidas:', className='margin-left'),
                most_played_songs_bullet,
                line,
                html.H3(f'Tiempo total de reproducción:', className='margin-left'),
                playtime,
                line,
                html.H3('Artistas más escuchados:', className='margin-left'),
                top_artists_bullet,
                line,
                html.H3('Canciones favoritas recientes:', className='margin-left'),
                recent_favorite_songs_bullet,
            ]
        ),
        html.Div(
            className='right-column',
            children=[
                dcc.Graph(
                    id='top-genres-chart',
                    figure={
                        'data': data,
                        'layout': go.Layout(title='Géneros Más Escuchados', 
                                            title_x=0.5, title_font_size=18, 
                                            paper_bgcolor= '#191B28',
                                            template='plotly_dark',
                                            margin=dict(t=70, b=30, l=20, r=20),
                                            autosize=True,
                                            legend=dict(orientation="h", yanchor="auto", y=-0.7, xanchor="auto", x=0.35),
                                            )
                    },className='graph'
                )
            ]
        )
    ]
)

# Iniciar el servidor Dash
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)