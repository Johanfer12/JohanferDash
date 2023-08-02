from dash import Dash, dcc, html
import sqlite3
import plotly.graph_objs as go
import os
from datetime import datetime, timedelta

# Obtener la ruta absoluta al directorio raíz del código
base_dir = os.path.dirname(os.path.abspath(__file__))

# Conectar a la base de datos en el directorio raíz
db_path = os.path.join(base_dir, 'spotify_stats.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

#Top artist
cursor.execute('''SELECT artist_name, COUNT(*) as play_count
                  FROM spotify_favorites
                  GROUP BY artist_name
                  ORDER BY play_count DESC
                  LIMIT 1''')

most_played_artist = cursor.fetchone()

#Top songs
cursor.execute('SELECT * FROM spotify_top_songs')
most_played_songs_list = cursor.fetchall()
most_played_songs_bullet = html.P([
    html.P([
        html.A(html.Img(src="assets/Play.svg", className="song-icon"), href=str(song[3])),
        html.A(f"{str(song[1]).split(' -')[0].split('(')[0].strip()} - {str(song[2])}", href=str(song[3]))
    ])
    for song in most_played_songs_list
])

#Duración Total
cursor.execute('SELECT SUM(duration_ms) FROM spotify_favorites')
total_duration_ms = cursor.fetchone()[0]
total_playtime_seconds = total_duration_ms // 1000  # Dividir para obtener los segundos sin decimales

# Convertir el tiempo total de reproducción a días, horas, minutos y segundos enteros
seconds = total_playtime_seconds % 60
minutes = (total_playtime_seconds // 60) % 60
hours = (total_playtime_seconds // 3600) % 24
days = total_playtime_seconds // 86400

# Obtener las canciones guardadas como favoritas
cursor.execute('SELECT * FROM spotify_favorites ORDER BY added_at ASC LIMIT 5')
recent_favorite_songs_list = cursor.fetchall()

recent_favorite_songs_bullet = html.P([
    html.P([
        html.A(html.Img(src="assets/Play.svg", className="song-icon"), href=str(song[3])),
        html.A(f"{str(song[1]).split(' -')[0].split('(')[0].strip()} - {str(song[2])}", href=str(song[3]))
    ])
    for song in recent_favorite_songs_list
])

# Calcular la fecha hace 4 semanas desde la fecha actual
end_date = datetime.now()
start_date = end_date - timedelta(weeks=4)

# Convertir las fechas a formato de texto (YYYY-MM-DD HH:MM:SS) para utilizar en la consulta
start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')

# Ejecutar la consulta SQL para obtener los 5 artistas más frecuentes en las últimas 4 semanas
cursor.execute('''SELECT artist_name, COUNT(*) as frequency
                  FROM spotify_favorites
                  WHERE added_at BETWEEN ? AND ?
                  GROUP BY artist_name
                  ORDER BY frequency DESC
                  LIMIT 5''', (start_date_str, end_date_str))

# Obtener todos los registros y almacenarlos en una lista de tuplas (artista, frecuencia)
top_artists_list = cursor.fetchall()

top_artists_bullet = html.P([
    html.P([
        html.Img(src="assets/mic.svg", className="artist-icon"),
        artist[0]
    ])
    for artist in top_artists_list
])

# Ejecutar la consulta SQL para obtener el máximo valor del ID en la tabla
cursor.execute('SELECT MAX(id) FROM spotify_favorites')

# Obtener el resultado de la consulta
total_favorites = cursor.fetchone()[0]

playtime = html.P(
    html.Div([
        html.Img(src="assets/time.svg", className="time-icon"),
        html.Span(f' {days} Días, {hours} Horas, {minutes} Minutos, {seconds} Segundos en {total_favorites} Canciones.', className='songs-time')
    ], className="time-container")
)

# Convertir los géneros y porcentajes en datos para la gráfica de torta

# Ejecutar la consulta para obtener la duración total por género
cursor.execute('''SELECT genre, SUM(duration_ms) AS total_duration
                  FROM spotify_favorites
                  WHERE genre != 'N/A'
                  GROUP BY genre
                  ORDER BY total_duration DESC
                  LIMIT 5''')

# Obtener los resultados de la consulta
top_genres_results = cursor.fetchall()

# Obtener los géneros y porcentajes
top_genres_list = [genre for genre, _ in top_genres_results]
total_duration = sum(duration for _, duration in top_genres_results)
top_genres_percentages_list = [(duration / total_duration) * 100 for _, duration in top_genres_results]

# Definir los colores personalizados en tonos de azul y violeta
custom_colors = ['#d193ff', '#9783ff', '#7d2799', '#3345b4', '#a836cc']

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
                html.H3(f'Artista más escuchado: {most_played_artist[0]}', className='margin-left'),
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