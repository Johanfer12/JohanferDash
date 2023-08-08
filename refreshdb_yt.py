import os
import sqlite3
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import google_auth_oauthlib.flow

# Obtener la ruta absoluta al directorio raíz del código
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Configura la conexión a la base de datos SQLite
db_path = "youtube_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
client_secrets_file = "client.json"

# Crea la tabla si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS youtube_data (
        id INTEGER PRIMARY KEY,
        channel_name TEXT,
        video_title TEXT,
        view_count INTEGER,
        like_count INTEGER,
        dislike_count INTEGER,
        comment_count INTEGER,
        video_url TEXT,
        thumbnail_url TEXT,
        video_duration TEXT
    )
''')
conn.commit()

# Configura la autenticación con la API de YouTube
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    client_secrets_file, scopes
)
credentials = flow.run_local_server(port=0)
youtube = build("youtube", "v3", credentials=credentials)

# Obtiene los datos de vídeos recientes
request = youtube.videos().list(
    part="snippet,statistics,contentDetails",
    maxResults=10,
    myRating="like"  # Cambia esto según tu interés
)
response = request.execute()

# Inserta los datos en la base de datos
for item in response.get("items", []):
    video_data = item["snippet"]
    statistics = item["statistics"]
    content_details = item["contentDetails"]
    cursor.execute(
        '''
        INSERT INTO youtube_data (
            channel_name,
            video_title,
            view_count,
            like_count,
            dislike_count,
            comment_count,
            video_url,
            thumbnail_url,
            video_duration
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            video_data["channelTitle"],
            video_data["title"],
            int(statistics["viewCount"]),
            int(statistics.get("likeCount", 0)),
            int(statistics.get("dislikeCount", 0)),
            int(statistics.get("commentCount", 0)),
            f"https://www.youtube.com/watch?v={item['id']}",
            video_data["thumbnails"]["default"]["url"],
            content_details["duration"],
        )
    )

conn.commit()
conn.close()
