import spotipy
import spotipy.util as util
import sqlite3
from config import CLIENT_ID, CLIENT_SECRET, USERNAME
import os

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

# Obtén un token de acceso
scope = "user-top-read user-library-read"
redirect_uri = "http://localhost:8888/callback"
token = util.prompt_for_user_token(USERNAME, scope, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=redirect_uri)

# Crea una instancia de Spotipy usando el token de acceso
sp = spotipy.Spotify(auth=token)

# Obtén el artista más escuchado
top_artists = sp.current_user_top_artists(limit=1, time_range='long_term')
if top_artists['items']:
    most_played_artist = top_artists['items'][0]['name']
    most_played_artist_image = top_artists['items'][0]['images'][0]['url'] if top_artists['items'][0]['images'] else None
else:
    most_played_artist = "N/A"
    most_played_artist_image = None

# Obtén las 5 canciones más reproducidas
top_tracks = sp.current_user_top_tracks(limit=5, time_range='long_term')
most_played_songs = []
for track in top_tracks['items']:
    song_name = track['name']
    artist_name = track['artists'][0]['name']
    song_url = track['external_urls']['spotify']
    most_played_songs.append({'song_name': song_name, 'artist_name': artist_name, 'song_url': song_url})

# Obtén la duración total de reproducción
playlists = sp.current_user_playlists()
total_playtime = 0

# Obtén las canciones guardadas como favoritos
favorite_songs = sp.current_user_saved_tracks(limit=50)  # Aumenta el límite si es necesario

# Suma la duración de cada canción
for track in favorite_songs['items']:
    duration_ms = track['track']['duration_ms']
    total_playtime += duration_ms

# Obtén las listas de reproducción
playlists = sp.current_user_playlists()

# Suma la duración de cada canción en las listas de reproducción
for playlist in playlists['items']:
    tracks = sp.playlist_tracks(playlist['id'], fields='items(track(duration_ms))')
    total_playtime += sum(track['track']['duration_ms'] for track in tracks['items'])

total_playtime = total_playtime // 1000  # Convertir de milisegundos a segundos

print(total_playtime)


# Obtén los 5 artistas más escuchados
top_artists = sp.current_user_top_artists(limit=5, time_range='long_term')
top_artists_names = [artist['name'] for artist in top_artists['items']]

# Obtén las 5 canciones más recientes añadidas a favoritos
favorite_songs = sp.current_user_saved_tracks(limit=5)
recent_favorite_songs = []
for track in favorite_songs['items']:
    song_name = track['track']['name']
    artist_name = track['track']['artists'][0]['name']
    song_url = track['track']['external_urls']['spotify']
    recent_favorite_songs.append({'song_name': song_name, 'artist_name': artist_name, 'song_url': song_url})

# Inserta las estadísticas en la base de datos
cursor.execute('DELETE FROM spotify_stats')
cursor.execute('INSERT INTO spotify_stats (most_played_artist, most_played_songs, total_playtime, top_artists, recent_favorite_songs) VALUES (?, ?, ?, ?, ?)',
               (most_played_artist, str(most_played_songs), total_playtime, ", ".join(top_artists_names), str(recent_favorite_songs)))

# Guarda los cambios y cierra la conexión con la base de datos
conn.commit()
conn.close()
