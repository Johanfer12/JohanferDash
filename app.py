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
    top_artists = row[4]
    top_genres = row[5]
    top_genres_percentages = row[6]
    recent_favorite_songs = row[7]
else:
    most_played_artist = "N/A"
    most_played_songs = "N/A"
    total_playtime = 0
    top_artists = "N/A"
    top_genres = "N/A"
    top_genres_percentages = "N/A"
    recent_favorite_songs = "N/A"

# Convertir las listas en bullet points con enlaces
most_played_songs_list = ast.literal_eval(most_played_songs)
most_played_songs_bullet = html.P([
    html.P([
        html.I(className="fas fa-play", style={"margin-right": "5px", "margin-left": "12px"}),
        html.A(f"{song['song_name']} - {song['artist_name']}", href=song['song_url'])
    ])
    for song in most_played_songs_list
])

recent_favorite_songs_list = ast.literal_eval(recent_favorite_songs)
recent_favorite_songs_bullet = html.P([
    html.P([
        html.I(className="fas fa-play", style={"margin-right": "5px", "margin-left": "12px"}),
        html.A(f"{song['song_name']} - {song['artist_name']}", href=song['song_url'])
    ])
    for song in recent_favorite_songs_list
])

top_artists_list = top_artists.split(", ")
top_artists_bullet = html.Ul([html.Li(artist) for artist in top_artists_list])

# Convertir el tiempo total de reproducción a días, horas, minutos y segundos
seconds = total_playtime % 60
minutes = (total_playtime // 60) % 60
hours = (total_playtime // 3600) % 24
days = total_playtime // 86400

# Convertir los géneros y porcentajes en datos para la gráfica de torta
top_genres_list = ast.literal_eval(top_genres)
top_genres_percentages_list = ast.literal_eval(top_genres_percentages)

data = [go.Pie(
    labels=[label.title() for label in top_genres_list],  # Aplica title() a cada etiqueta
    values=top_genres_percentages_list,
)]

line = html.Div(
    children=[
        html.Div(className='gradient-line')
    ]
)

# Incluir los estilos de Font Awesome
external_stylesheets = [
    "https://use.fontawesome.com/releases/v5.15.3/css/all.css"
]

# Crear una instancia de la aplicación Dash
app = Dash(__name__, external_stylesheets=external_stylesheets)
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
                html.P(f' {days} días, {hours} horas, {minutes} minutos, {seconds} segundos', className='margin-left'),
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
                                            height=300, width=400, 
                                            title_x=0.5, title_font_size=18, 
                                            paper_bgcolor= '#191B28',
                                            template='plotly_dark',
                                            )
                    }
                )
            ]
        )
    ]
)

# Iniciar el servidor Dash
if __name__ == '__main__':
    app.run_server(debug=True)
