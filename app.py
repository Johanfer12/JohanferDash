from dash import Dash, dcc, html
import sqlite3
import plotly.graph_objs as go
import os
from datetime import datetime, timedelta
from collections import defaultdict
from dateutil.parser import parse 
import numpy as np
import pandas as pd
import json
from dash_holoniq_wordcloud import DashWordcloud

# Obtener la ruta absoluta al directorio raíz del código
base_dir = os.path.dirname(os.path.abspath(__file__))

#####    Seccion Spotify    ####

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
        html.A(html.Img(src="assets/Play.svg", className="song-icon"), href=str(song[4])),
        html.A(f"{str(song[1]).split(' -')[0].split('(')[0].strip()} - {str(song[2])}", href=str(song[4]))
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
                                            paper_bgcolor= 'rgba(2, 0, 0, 0)',
                                            template='plotly_dark',
                                            margin=dict(t=70, b=30, l=20, r=20),
                                            autosize=True,
                                            dragmode=False,
                                            legend=dict(orientation="h", yanchor="auto", y=-0.6, xanchor="auto", x=0.35),
                                            )
                    },
                    config={'displayModeBar': False},
                    className='graph'
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
                                #template='plotly_dark',
                                font=dict(color='#ffffff'),
                                paper_bgcolor='rgba(2, 0, 0, 0)',
                                plot_bgcolor='rgba(2, 0, 0, 0)',
                                margin=dict(t=70, b=30, l=45, r=20),
                                autosize=True,
                                dragmode=False,
                                legend=dict(orientation="h", yanchor="auto", y=-0.7, xanchor="auto", x=0.35)
                                )
                            },
                            config={'displayModeBar': False},
                            className='graph'
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
    paper_bgcolor='rgba(2, 0, 0, 0)',
    plot_bgcolor='rgba(2, 0, 0, 0)',
    font=dict(color='#ffffff'),
    showlegend=False,
    dragmode=False,
    autosize=True
)

# Crear la figura con la gráfica y el layout
fig = go.Figure(data=[trace], layout=layout)

# Crear la gráfica de burbujas
bubbles_chart = dcc.Graph(
    id='bubbles-chart',
    figure=fig,
    config={'displayModeBar': False},
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
    paper_bgcolor='rgba(2, 0, 0, 0)',
    plot_bgcolor='rgba(2, 0, 0, 0)',
    font=dict(color='#ffffff'),
    showlegend=True,
    autosize=True,
    dragmode=False,
    legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=1)
)

fig_songs = go.Figure(data=data_songs, layout=layout_songs)

# Crear la gráfica de cantidad de canciones añadidas por mes usando dcc.Graph
songs_chart = dcc.Graph(
    id='songs-chart',
    figure=fig_songs,
    config={'displayModeBar': False},
    className='graph'
)

#Linea separadora de secciones
line = html.Div(
    children=[
        html.Div(className='gradient-line')
    ]
)

# Extraer fecha de adición de la última canción de la base de datos:
cursor.execute('''SELECT added_at FROM spotify_favorites ORDER BY added_at DESC LIMIT 1''')
last_updated_tuple = cursor.fetchone()

if last_updated_tuple:
    last_updated = last_updated_tuple[0]
    last_updated = datetime.strptime(last_updated, '%Y-%m-%dT%H:%M:%SZ').strftime('%d de %B de %Y')
else:
    print("No se encontraron registros de nuevas canciones en la base de datos.")


#Diseño de la sección Spotify
spotify_tab_layout = html.Div(children=[
    html.Div(className='left-column',children=[
        html.H1('Estadísticas Spotify', style={'textAlign': 'center'}),
        html.H3(f'Artista más escuchado: {most_played_artist[0]}', className='content-left'),
        line,
        html.H3('Canciones más reproducidas:', className='content-left'),
        most_played_songs_bullet,
        line,
        html.H3(f'Tiempo total de reproducción:', className='content-left'),
        playtime,
        line,
        html.H3('Artistas más escuchados:', className='content-left'),
        top_artists_bullet,
        line,
        html.H3('Canciones favoritas recientes:', className='content-left'),
        recent_favorite_songs_bullet,
        line,
        html.Br(),        
        html.H4(f'Última actualización: {last_updated}', className='content-left'), 
        html.Br(),
    ]),
    html.Div(className='right-column',children=[
            top_genres_chart,
            html.Abbr("🛈", title="La energía muestra la intensidad y actividad percibida en una canción. (Escala de 0 a 1)", className="Abbr_1"),
            bubbles_chart                
    ]),
    html.Div(className='right-column',children=[
            html.Abbr("🛈", title="La valencia indica la positividad o negatividad emocional de una canción. (Escala de 0 a 1)", className="Abbr_2"),
            valence_chart,
            songs_chart
    ])
])


#cerrar conexion base de datos spotify
conn.close()

#####    Seccion X-Twitter    ####

#Abrir Conexion a la base de datos
db_path = os.path.join(base_dir, 'tweets.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

#Extraer el total de tweets de X-Twitter
cursor.execute('SELECT COUNT(*) FROM tweets')
total_tweets = cursor.fetchone()[0]

# Obtener los usuarios mencionados con más frecuencia (top 5)
cursor.execute('''
    SELECT mention, COUNT(mention) as mention_count
    FROM tweets
    WHERE mention IS NOT NULL
    GROUP BY mention
    ORDER BY mention_count DESC
    LIMIT 5
''')
top_mentioned_users_list = cursor.fetchall()

# Crear una lista de elementos HTML para mostrar los usuarios mencionados
top_mentioned_users_bullet = html.P([
    html.P([
        html.Img(src="assets/user.svg", className="user-icon"),  # Asegúrate de ajustar la ruta de la imagen
        html.A(f"@{user[0]} - {user[1]} Menciones", href=f"https://twitter.com/{user[0]}")  # Agrega el enlace a su perfil de X-Twitter
    ])
    for user in top_mentioned_users_list
])

#Gráfico cantidad de tweets por mes

# Obtener las fechas de creación de los tweets
cursor.execute('SELECT created_at FROM tweets')
dates = cursor.fetchall()

# Crear un DataFrame de Pandas a partir de los datos
df = pd.DataFrame(dates, columns=['created_at'])

# Convertir la columna 'created_at' a tipo datetime
df['created_at'] = pd.to_datetime(df['created_at'], format='%b %d %H:%M:%S +0000 %Y')

# Agregar una columna 'month_year' para el mes y año
df['month_year'] = df['created_at'].dt.strftime('%Y-%m')

# Contar la cantidad de tweets por mes
tweets_by_month = df['month_year'].value_counts().sort_index()

# Obtener los meses y la cantidad de tweets por mes
months = tweets_by_month.index.tolist()
tweets_count = tweets_by_month.tolist()

# Crear la gráfica de cantidad de tweets por mes con área sombreada
data_tweets = [
    go.Scatter(
        x=months,
        y=tweets_count,
        mode='lines',
        name='Tweets por Mes',
        fill='tozeroy',  # Rellenar área por debajo de la línea
        marker=dict(color='blue'),
        line=dict(color='#636efa', width=2)
    )
]

layout_tweets = go.Layout(
    title='Tweets por Mes',
    title_x=0.5, title_font_size=18,
    xaxis=dict(title='Mes'),
    yaxis=dict(title='Cantidad de Tweets'),
    margin=dict(t=100, b=30, l=20, r=20),
    hovermode='closest',
    paper_bgcolor='rgba(2, 0, 0, 0)',
    plot_bgcolor='rgba(2, 0, 0, 0)',
    font=dict(color='#ffffff'),
    dragmode=False,
    showlegend=False,  # No mostrar leyenda, ya que solo hay una serie de datos
    autosize=True,
)

fig_tweets = go.Figure(data=data_tweets, layout=layout_tweets)

# Crear la gráfica de cantidad de tweets por mes usando dcc.Graph
tweets_chart = dcc.Graph(
    id='tweets-chart',
    figure=go.Figure(data=data_tweets, layout=layout_tweets),
    config={'displayModeBar': False},
    className='graph'
)

#Gráfico de tweets por día

# Obtener los datos de create_day y contar la cantidad de tweets por día de la semana
cursor.execute('SELECT create_day FROM tweets')
days = cursor.fetchall()

# Crear un DataFrame de Pandas a partir de los datos
df = pd.DataFrame(days, columns=['create_day'])

# Contar la cantidad de tweets por día de la semana
tweets_by_day_of_week = df['create_day'].value_counts().sort_index()

# Definir los nombres de los días de la semana
day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

# Definir los colores personalizados
custom_colors = ['#d193ff', '#9783ff', '#7d2799', '#3345b4', '#a836cc', '#636efa']

# Crear un gráfico de torta
fig = go.Figure(data=[go.Pie(
    labels=day_names,
    values=tweets_by_day_of_week,
    marker=dict(colors=custom_colors),
    textinfo='percent+label',
    hole=0.3,
)])

# Personalizar el diseño del gráfico de torta
fig.update_layout(
    title='Tweets por Día de la Semana',
    title_x=0.5, title_font_size=18,
    margin=dict(t=100, b=30, l=20, r=20),
    hovermode='closest',
    paper_bgcolor='rgba(2, 0, 0, 0)',
    plot_bgcolor='#191B28',
    font=dict(color='#ffffff'),
    autosize=True,
    #legend=dict(orientation='h', yanchor='bottom', y=-0.3, xanchor='center', x=0.5),
)

# Crear el gráfico de torta usando dcc.Graph
days_chart = dcc.Graph(
    id='pie-chart',
    figure=fig,
    config={'displayModeBar': False},
    className='graph'
)

#Nube de palabras en tweets:

# Ruta al archivo donde se guardará la nube de palabras
wordcloud_file = 'wordcloud.json'

# Verificar si el archivo de la nube de palabras ya existe, para no recalcular toda la nube
if os.path.exists(wordcloud_file):
    # Cargar la nube de palabras desde el archivo
    with open(wordcloud_file, 'r') as f:
        wordcloud_data = json.load(f)
else:
    # Extraer los datos de texto de la columna 'text' en la DB
    cursor.execute('SELECT text FROM tweets')
    text_data = cursor.fetchall()

    # Procesa los datos para obtener una lista de palabras
    words = []
    for row in text_data:
        text = row[0]
        # Divide el texto en palabras y filtra las que tienen 4 letras o más
        words.extend([word for word in text.split() if len(word) >= 5])

    # Crea una lista de palabras con su frecuencia
    wordcloud_data = [[word, words.count(word)] for word in set(words)]

    # Filtrar las palabras que aparecen 5 o más veces
    wordcloud_data = [
        [word, count]
        for word, count in wordcloud_data
        if count >= 5 and '@' not in word and '#' not in word and ':' not in word and '!' not in word and '&' not in word and '¡' not in word
    ]

    # Ordenar la lista de palabras por frecuencia de mayor a menor
    wordcloud_data = sorted(wordcloud_data, key=lambda x: x[1], reverse=True)

    # Guardar la nube de palabras en un archivo
    with open(wordcloud_file, 'w') as f:
        json.dump(wordcloud_data, f)

# Ahora tienes la nube de palabras en la variable `wordcloud_data` o cargada desde el archivo si ya existía

word_cloud =DashWordcloud(
            id='wordcloud',
            list=wordcloud_data,
            width=310,
            height=370,
            gridSize=16,
            color='#ffffff',  
            backgroundColor='rgba(2, 0, 0, 0)',  
            shuffle=False,
            rotateRatio=1,
            shrinkToFit=False,
            shape='circle',
            hover=True
        )

wordcloud_chart = html.Div(className='wordcloud',children=[
    html.H2('Palabras Frecuentes', className='wordcloud-title'),
    word_cloud])

#Gráfico de tweets por hora del día

# Consulta SQL para contar la cantidad de tweets por hora, corrección de zona horaria -5 dado que originalmente es UTC
cursor.execute('''
    SELECT (CAST(SUBSTR(created_at, 8, 2) AS INTEGER) - 5 + 24) % 24 as hour, COUNT(*) as tweet_count
    FROM tweets
    WHERE created_at IS NOT NULL
    GROUP BY hour
    ORDER BY hour
''')

# Obtener los resultados de la consulta
hourly_tweet_data = cursor.fetchall()

# Crear un DataFrame de Pandas a partir de los datos
df = pd.DataFrame(hourly_tweet_data, columns=['hour', 'tweet_count'])

# Crear el gráfico de barras
bar_chart = go.Bar(
    x=df['hour'],
    y=df['tweet_count'],
    marker=dict(color='#636efa'),  # Color de las barras
)

# Diseñar el diseño del gráfico
layout = go.Layout(
    title='Distribución de Tweets por Hora del Día',
    title_x=0.5, title_font_size=18,
    xaxis=dict(title='Hora del Día'),
    yaxis=dict(title='Cantidad de Tweets'),
    margin=dict(t=70, b=30, l=20, r=20),
    paper_bgcolor='rgba(2, 0, 0, 0)',  
    plot_bgcolor='rgba(2, 0, 0, 0)',  
    font=dict(color='#ffffff'),  
    dragmode=False,
)

# Crear la figura que incluye el gráfico y el diseño
fig = go.Figure(data=[bar_chart], layout=layout)

# Personalizar las etiquetas en el eje x dado que se ajustó a la zona horaria -5
fig.update_xaxes(tickvals=list(range(24)), ticktext=[str(i) for i in range(24)])

# Cerrar la conexión a la base de datos de tweets
conn.close()

# Crear el gráfico de barras
hourly_tweets_chart = dcc.Graph(
    id='hourly-tweets-chart',
    figure=fig,
    config={'displayModeBar': False},
    className='graph'
)
               
#Diseño de la sección X-Twitter
xt_tab_layout = html.Div(children=[
	html.Div(className='left-column',children=[
        html.H1('Estadísticas X-Twitter', style={'textAlign': 'center'}),
        html.H3(f'Total de Tweets: {total_tweets}', className='content-left'),
        line,
        html.H3('Usuarios más mencionados:', className='content-left'),
        top_mentioned_users_bullet,
        line,
    ]),
	html.Div(className='right-column',children=[
            days_chart,
            hourly_tweets_chart,               
            ]
        ),
	html.Div(className='right-column',children=[
            
            wordcloud_chart,
            tweets_chart
        ])
])

#Diseño de la sección Información
nfo_tab_layout = html.Div(className='info-tab', children=[    

    html.H1('Dash de Johan', style={'textAlign': 'center'}),
    html.P(
        "Herramienta para explorar y visualizar datos de mi música y tweets favoritos."
    ),
    html.P(
        "Se hace uso de Dash, Plotly, SQL y Pandas; Adicionalmente se extrae información de las bases de datos de twitter y spotify, generadas desde un archivo csv de datos de Twitter y la API de Spotify."
    ),
    html.P(
        "Descubre cuáles son mis artistas, géneros y canciones más escuchados en Spotify, el tiempo total que he dedicado a la música, y las emociones detrás de mis canciones favoritas."
    ),
    html.P(
        "En la sección de X-Twitter, se obtiene información sobre mis tweets, usuarios más mencionados, patrones de publicación y las palabras más frecuentes en mis tweets en una nube."
    ),
    html.P(
        "Explora las diversas gráficas e información proporcionadas y disfruta de un análisis personalizado de mi actividad en Spotify y X-Twitter."
    ),
    html.H3('Gráficas de Energía y Valencia'),
    html.P(
        "Las gráficas de Energía y Valencia proporcionan información sobre las características emocionales y musicales de mis canciones favoritas en Spotify:"
    ),
    html.Ul([
        html.Li(
            "La gráfica de Energía muestra la intensidad y actividad percibida en una canción, en una escala de 0 a 1. "
            "Una mayor energía indica una canción más enérgica y activa."
        ),
        html.Br(),
        html.Li(
            "La gráfica de Valencia indica la positividad o negatividad emocional de una canción, en una escala de 0 a 1. "
            "Una valencia alta sugiere una canción con una atmósfera más positiva, mientras que una valencia baja indica una atmósfera más negativa."
        ),
    ]),
    html.P(
        "Estas gráficas permiten explorar las emociones y la energía presentes en mis canciones favoritas, lo que puede ayudar a entender mis preferencias musicales y estado de ánimo musical."
    ),
    html.P([
    "Si deseas ver el código fuente de esta aplicación, puedes encontrarlo en mi ",
    html.A("GitHub", href="https://github.com/Johanfer12", target="_blank", className="github-link")
    ])
])

# Crear instancia de la aplicación Dash
app = Dash(__name__)
app.title = 'Dash de Johan'

# Definir el diseño de la aplicación
app.layout = dcc.Tabs(id='vertical-tabs', value='tab-spotify', colors={'border': '#191B28', 'primary': '#191B28', 'background': '#191B28'}, children=[
                dcc.Tab(label=' ',value='tab-spotify', className='tab-style-sp', children=[
                    html.Div(style={'width': '95vw', 'height': '100vh'}, children=[
                        spotify_tab_layout
                    ])
                ]),
                dcc.Tab(label=' ', value='tab-xt', className='tab-style-xt', children=[
                    html.Div(style={'width': '95vw', 'height': '100vh'}, children=[
                        xt_tab_layout
                    ])    
                ]),
                dcc.Tab(label=' ', value='tab-nfo', className='tab-style-nfo', children=[
                    html.Div(style={'width': '95vw', 'height': '100vh'}, children=[
                        nfo_tab_layout
                    ])    
                ])
            ], vertical=True)

# Iniciar el servidor Dash
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)