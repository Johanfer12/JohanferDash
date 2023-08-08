from dash import Dash, dcc, html
import sqlite3
import plotly.graph_objs as go
import os
from datetime import datetime, timedelta
from collections import defaultdict
from dateutil.parser import parse 
import numpy as np

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
cursor.execute('SELECT * FROM spotify_favorites ORDER BY added_at DESC LIMIT 5')
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
cursor.execute('SELECT COUNT(*) FROM spotify_favorites')

# Obtener el resultado de la consulta
total_favorites = cursor.fetchone()[0]

playtime = html.P(
    html.Div([
        html.Img(src="assets/time.svg", className="time-icon"),
        html.Span(f' {days} Días, {hours} Horas, {minutes} Minutos, {seconds} Segundos en {total_favorites} Canciones.', className='songs-time')
    ], className="time-container")
)

#Gráfica de géneros y porcentajes

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
total_duration_top_genres = sum(duration for _, duration in top_genres_results)

# Obtener el total de duración para todos los géneros
cursor.execute('''SELECT SUM(duration_ms) FROM spotify_favorites WHERE genre != 'N/A' ''')
total_duration_all_genres = cursor.fetchone()[0]

# Calcular el porcentaje total de los géneros que no están en el top 5
other_genres_percentage = ((total_duration_all_genres - total_duration_top_genres) / total_duration_all_genres) * 100

# Agregar "otros" a la lista de géneros y a los porcentajes
top_genres_list.append("Otros")
top_genres_percentages_list = [duration / total_duration_all_genres * 100 for _, duration in top_genres_results]
top_genres_percentages_list.append(other_genres_percentage)

# Definir los colores personalizados en tonos de azul y violeta
custom_colors = ['#d193ff', '#9783ff', '#7d2799', '#3345b4', '#a836cc', '#636efa']

data_genre = [go.Pie(
    labels=[label.title() for label in top_genres_list],  # Aplica title() a cada etiqueta
    values=top_genres_percentages_list,
    marker=dict(colors=custom_colors),
)]

top_genres_chart = dcc.Graph(
                    id='top-genres-chart',
                    figure={
                        'data': data_genre,
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

#Gráfica de barras valencia en el tiempo

# Ejecutar la consulta para obtener la valencia y fecha de lanzamiento de cada canción
cursor.execute('''SELECT valence, added_at
                  FROM spotify_favorites
                  WHERE valence IS NOT NULL AND added_at IS NOT NULL''')

# Obtener los resultados de la consulta
valence_and_dates = cursor.fetchall()

# Crear un diccionario para almacenar la valencia media por año
valence_by_year = defaultdict(list)

# Procesar los resultados de la consulta y agrupar por año
for valence, release_date in valence_and_dates:
    year = release_date[:4]  # Obtener el año de la fecha de lanzamiento
    valence_by_year[year].append(valence)

# Calcular la valencia media para cada año
years = []
mean_valence = []
for year, valences in valence_by_year.items():
    years.append(year)
    mean_valence.append(sum(valences) / len(valences))

# Crear la gráfica de barras valencia en el tiempo

data_val= [go.Bar(x=years, y=mean_valence, name='Valencia Media')]

valence_chart = dcc.Graph(
    id='valence-chart', figure={
            'data': data_val,
            'layout': go.Layout(title='Valencia Por Año',
                                title_x=0.5, title_font_size=18,
                                xaxis=dict(title='Año'),
                                yaxis=dict(title='Valencia Media'),
                                template='plotly_dark',
                                paper_bgcolor='#191B28',
                                plot_bgcolor='#191B28',
                                margin=dict(t=70, b=30, l=20, r=20),
                                autosize=True,
                                legend=dict(orientation="h", yanchor="auto", y=-0.7, xanchor="auto", x=0.35)
                                )
                            },className='graph'
                         )

#Gráfica de burbujas de energía y valencia por cada género y su tamaño relativo

# Obtener los datos para la gráfica de burbujas
cursor.execute('''SELECT genre, COUNT(*) AS num_songs, AVG(valence) AS avg_valence, AVG(energy) AS avg_energy
                  FROM spotify_favorites
                  WHERE genre != "N/A"
                  GROUP BY genre
                  HAVING COUNT(*) >= 10''')
    
data = cursor.fetchall()

# Definir una lista de colores personalizados para cada género
custom_colors = ['#5472d3', '#7e58c2', '#a647ba', '#d43d80', '#d33da2', '#ff9500', '#ff3b30', '#d193ff', '#9783ff', '#7d2799', '#3345b4', '#a836cc']

# Crear la gráfica de burbujas
trace = go.Scatter(
    x=[song[2] for song in data],  # Valence
    y=[song[3] for song in data],  # Energy
    mode='markers',
    text=[f'Género: {song[0]}<br>Número de canciones: {song[1]}' for song in data],  # Información al pasar el mouse sobre las burbujas
    marker=dict(
        size=[song[1] for song in data],  # Tamaño de las burbujas según la cantidad de canciones
        sizemode='area',  # Determina cómo se interpreta el tamaño (area = tamaño relativo al área)
        sizeref=2.0 * max([song[1] for song in data]) / (50 ** 2),  # Escala para ajustar el tamaño de las burbujas (aquí el tamaño máximo será para 50 canciones)
        sizemin=10,  # Tamaño mínimo de las burbujas
        color=custom_colors[:len(data)],  # Asignar colores diferentes a cada burbuja
        opacity=0.7,  # Opacidad de las burbujas
        line=dict(width=2)  # Ancho del borde de las burbujas
    )
)

# Definir el layout de la gráfica
layout = go.Layout(
    title='Canciones por Género, Valencia, Energía',
    title_x=0.5, title_font_size=18,
    xaxis=dict(title='Valencia'),
    yaxis=dict(title='Energía'),
    margin=dict(t=100, b=30, l=20, r=20),
    hovermode='closest',
    paper_bgcolor='#191B28',
    plot_bgcolor='#191B28',
    font=dict(color='#ffffff'),
    showlegend=False,
    autosize=True
)

# Crear la figura con la gráfica y el layout
fig = go.Figure(data=[trace], layout=layout)

# Crear la gráfica de burbujas
bubbles_chart = dcc.Graph(
    id='bubbles-chart',
    figure=fig,
    className='graph'
)

#Gráfica de añadidas a favoritos en el tiempo

# Obtener las fechas de adición de las canciones
cursor.execute('''SELECT added_at FROM spotify_favorites''')
dates = cursor.fetchall()

# Crear un diccionario para almacenar la cantidad de canciones añadidas por mes
songs_by_month = defaultdict(int)

# Procesar las fechas y contar la cantidad de canciones por mes
for date_str in dates:
    date = parse(date_str[0])  # Parsear la fecha en formato ISO 8601
    month_year = date.strftime('%Y-%m')
    songs_by_month[month_year] += 1

# Obtener los meses y la cantidad de canciones añadidas por mes
months = list(songs_by_month.keys())
songs_added = list(songs_by_month.values())

# Calcular la línea de tendencia usando un ajuste polinómico
z = np.polyfit(np.arange(len(months)), songs_added, 1)
p = np.poly1d(z)
trend_line = p(np.arange(len(months)))

# Crear la gráfica de cantidad de canciones añadidas por mes con línea de tendencia
data_songs = [
    go.Scatter(
        x=months,
        y=songs_added,
        mode='markers+lines',
        name='Canciones Añadidas por Mes',
        marker=dict(color='blue'),
        line=dict(color='#636efa', width=2)
    ),
    go.Scatter(
        x=months,
        y=trend_line,
        mode='lines',
        name='Línea de Tendencia',
        line=dict(color='orange', width=2, dash='dash')
    )
]

layout_songs = go.Layout(
    title='Canciones Añadidas por Mes',
    title_x=0.5, title_font_size=18,
    xaxis=dict(title='Mes'),
    yaxis=dict(title='Cantidad de Canciones Añadidas'),
    margin=dict(t=100, b=30, l=20, r=20),
    hovermode='closest',
    paper_bgcolor='#191B28',
    plot_bgcolor='#191B28',
    font=dict(color='#ffffff'),
    showlegend=True,
    autosize=True,
    legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=1)
)

fig_songs = go.Figure(data=data_songs, layout=layout_songs)

# Crear la gráfica de cantidad de canciones añadidas por mes usando dcc.Graph
songs_chart = dcc.Graph(
    id='songs-chart',
    figure=fig_songs,
    className='graph'
)

#Linea separadora de secciones
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
                top_genres_chart,
                html.Abbr("🛈", title="La energía muestra la intensidad y actividad percibida en una canción. (Escala de 0 a 1)", className="Abbr_1"),
                bubbles_chart                
            ]
        ),
        html.Div(
            className='right-column',
            children=[
                html.Abbr("🛈", title="La valencia indica la positividad o negatividad emocional de una canción. (Escala de 0 a 1)", className="Abbr_2"),
                valence_chart,
                songs_chart
            ]
        )
    ]
)

# Iniciar el servidor Dash
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)