from dash import Dash, dcc, html
import sqlite3
import os
import ast

# Obtiene la ruta absoluta al directorio raíz del código
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
    recent_favorite_songs = row[5]
else:
    most_played_artist = "N/A"
    most_played_songs = "N/A"
    total_playtime = 0
    top_artists = "N/A"
    recent_favorite_songs = "N/A"

# Convertir las listas en bullet points con enlaces
most_played_songs_list = ast.literal_eval(most_played_songs)
most_played_songs_bullet = html.Ul([html.Li(html.A(f"{song['song_name']} - {song['artist_name']}", href=song['song_url'])) for song in most_played_songs_list])

recent_favorite_songs_list = ast.literal_eval(recent_favorite_songs)
recent_favorite_songs_bullet = html.Ul([html.Li(html.A(f"{song['song_name']} - {song['artist_name']}", href=song['song_url'])) for song in recent_favorite_songs_list])

top_artists_list = top_artists.split(", ")
top_artists_bullet = html.Ul([html.Li(artist) for artist in top_artists_list])

# Convertir el tiempo total de reproducción a días, horas, minutos y segundos
seconds = total_playtime % 60
minutes = (total_playtime // 60) % 60
hours = (total_playtime // 3600) % 24
days = total_playtime // 86400

# Crear una instancia de la aplicación Dash
app = Dash(__name__)
app.title = 'Dash de Johan'

# Definir el diseño de la aplicación
app.layout = html.Div(
    children=[
        html.H1('Estadísticas del Spotify de Johan'),
        html.P(f'Artista más escuchado: {most_played_artist}'),
        html.P('Canciones más reproducidas:'),
        most_played_songs_bullet,
        html.P(f'Tiempo total de reproducción: {days} días, {hours} horas, {minutes} minutos, {seconds} segundos'),
        html.P('Artistas más escuchados:'),
        top_artists_bullet,
        html.P('Canciones favoritas recientes:'),
        recent_favorite_songs_bullet
    ]
)

# Iniciar el servidor Dash
if __name__ == '__main__':
    app.run_server(debug=True)
