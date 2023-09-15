import json
import sqlite3
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Abre el archivo JSON
with open('tweet.json', 'r', encoding='utf-8') as file:
    tweets_data = json.load(file)

# Conecta a la base de datos SQLite (asegúrate de que la base de datos no exista previamente)
conn = sqlite3.connect('tweets.db')
cursor = conn.cursor()

# Crea una tabla para almacenar los datos
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tweets (
        mention TEXT,
        create_day TEXT,
        created_at TEXT,
        text TEXT
    )
''')

# Itera a través de los tweets y almacena los datos en la base de datos
for tweet in tweets_data:
    entities = tweet['tweet']['entities']
    
    if 'user_mentions' in entities and len(entities['user_mentions']) > 0:
        mention = entities['user_mentions'][0]['screen_name']
    else:
        mention = None

    create_date = tweet['tweet']['created_at']
    create_day = create_date.split()[0]  # Corregido para obtener el día de la semana
    created_at = ' '.join(create_date.split()[1:])
    text = tweet['tweet']['full_text']

    # Inserta los datos en la base de datos
    cursor.execute('INSERT INTO tweets (mention, create_day, created_at, text) VALUES (?, ?, ?, ?)', (mention, create_day, created_at, text))

# Guarda los cambios y cierra la conexión
conn.commit()
conn.close()

print("Los datos se han almacenado en la base de datos SQLite 'tweets.db'.")
