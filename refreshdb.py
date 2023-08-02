import spotipy
import spotipy.util as util
import sqlite3
import datetime
from config import CLIENT_ID, CLIENT_SECRET, USERNAME
import os

# Obtener la ruta absoluta al directorio raíz del código
base_dir = os.path.dirname(os.path.abspath(__file__))

# Conectar a la base de datos en el directorio raíz
db_path = os.path.join(base_dir, 'spotify_stats.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Modificar la tabla para incluir las nuevas columnas (valencia, energía y fecha de adición)
cursor.execute('''CREATE TABLE IF NOT EXISTS spotify_favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_name TEXT,
                artist_name TEXT,
                genre TEXT,
                song_url TEXT,
                duration_ms INTEGER,
                valence REAL,
                energy REAL,
                added_at TEXT
            )''')

# Modificar la tabla para incluir las top canciones
cursor.execute('''CREATE TABLE IF NOT EXISTS spotify_top_songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_name TEXT,
                artist_name TEXT,
                song_url TEXT
            )''')

# Obtener el token de acceso
scope = "user-library-read user-top-read"
redirect_uri = "http://localhost:8888/callback"
token = util.prompt_for_user_token(USERNAME, scope, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=redirect_uri)

# Crear una instancia de Spotipy usando el token de acceso
sp = spotipy.Spotify(auth=token)

# Obtener todas las canciones guardadas como favoritos
def get_all_saved_tracks(sp):
    all_tracks = []
    results = sp.current_user_saved_tracks(limit=50)
    all_tracks.extend(results['items'])
    
    while results['next']:
        results = sp.next(results)
        all_tracks.extend(results['items'])
    
    return all_tracks

# Obtener las 5 canciones más reproducidas
top_tracks = sp.current_user_top_tracks(limit=5, time_range='short_term')
most_played_songs = []
for track in top_tracks['items']:
    song_name = track['name']
    artist_name = track['artists'][0]['name']
    song_url = track['external_urls']['spotify']
    most_played_songs.append({'song_name': song_name, 'artist_name': artist_name, 'song_url': song_url})

# Insertar las top canciones en la tabla spotify_top_songs
cursor.execute('DELETE FROM spotify_top_songs')
for song in most_played_songs:
    cursor.execute('INSERT INTO spotify_top_songs (song_name, artist_name, song_url) VALUES (?, ?, ?)',
                   (song['song_name'], song['artist_name'], song['song_url']))

# Obtener todas las canciones guardadas como favoritos
favorite_songs = get_all_saved_tracks(sp)

# Obtener el número total de canciones favoritas actuales y el número total en la base de datos
num_favorites_current = len(favorite_songs)
cursor.execute('SELECT COUNT(*) FROM spotify_favorites')
num_favorites_db = cursor.fetchone()[0]

# Obtener las URLs de las canciones favoritas actuales
favorite_urls = {track['track']['external_urls']['spotify'] for track in favorite_songs}

# Eliminar las canciones que ya no están en favoritos de la base de datos
cursor.execute('SELECT song_url FROM spotify_favorites')
existing_urls = {url[0] for url in cursor.fetchall()}
urls_to_delete = existing_urls - favorite_urls

for url in urls_to_delete:
    cursor.execute('DELETE FROM spotify_favorites WHERE song_url = ?', (url,))

# Verificar si el número total de canciones favoritas ha cambiado
if num_favorites_current != num_favorites_db:
    # Actualizar la base de datos si el número de canciones ha cambiado

    # Insertar cada canción favorita en la base de datos con su información relevante
    for track in favorite_songs:
        song_name = track['track']['name']
        artist_name = track['track']['artists'][0]['name']

        # Obtener el género del artista
        artist = sp.artist(track["track"]["artists"][0]["external_urls"]["spotify"])
        genres = artist.get("genres", [])
        genre = genres[0] if genres else "N/A"  # Si no hay género, se usará "N/A"
        
        song_url = track['track']['external_urls']['spotify']
        duration_ms = track['track']['duration_ms']

        # Obtener la valencia y energía de la canción
        audio_features = sp.audio_features(track['track']['id'])[0]
        valence = audio_features['valence']
        energy = audio_features['energy']

        # Obtener la fecha de adición a favoritos (esta información no se proporciona por la API de Spotify,
        # por lo que almacenaremos la fecha actual en formato de texto)
        added_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Verificar si la canción ya existe en la base de datos por su URL
        cursor.execute('SELECT * FROM spotify_favorites WHERE song_url = ?', (song_url,))
        existing_song = cursor.fetchone()

        if not existing_song:
            # Insertar la canción en la base de datos si no existe
            cursor.execute('INSERT INTO spotify_favorites (song_name, artist_name, genre, song_url, duration_ms, valence, energy, added_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                           (song_name, artist_name, genre, song_url, duration_ms, valence, energy, added_at))
else:
    print("No se encontraron cambios en la lista de canciones favoritas.")

# Guarda los cambios y cierra la conexión con la base de datos
conn.commit()
conn.close()
