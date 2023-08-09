# JohanferDash

# Spotify Stats Dashboard

This is a project that utilizes the Dash library in Python to create an interactive dashboard displaying statistics related to the most listened-to songs and artists on Spotify. The application uses an SQLite database to store and retrieve the relevant data.

## Requirements

Before running the application, make sure you have the following Python libraries installed:

- Dash
- dash-core-components
- dash-html-components
- plotly
- sqlite3
- os
- datetime
- collections
- dateutil.parser
- numpy

You can install these libraries using the following command:

```bash
pip install dash dash-core-components dash-html-components plotly sqlite3 datetime collections python-dateutil numpy
```

## Database Setup

The application uses an SQLite database named `spotify_stats.db` to store the data. Make sure the database is located in the same directory as the code file.

## Running the Application

To run the application, simply execute the Python file `app.py`. The application will run on a local server, and you can access it using your web browser at `http://localhost:8050`.

```bash
python app.py
```

## Key Features

- **Most Played Artist**: Displays the most played artist on Spotify based on the play count.

- **Top Played Songs**: Displays a list of the most played songs, along with links to play them.

- **Total Playtime**: Shows the total playtime in days, hours, minutes, and seconds, along with the total number of songs listened to.

- **Top Artists Recently**: Displays a list of the top listened-to artists in the last 4 weeks.

- **Top Genres**: Displays a pie chart of the most listened-to music genres and their percentages.

- **Valence Over Years**: Shows a bar chart representing the average valence of songs over the years.

- **Energy and Valence Bubbles By Genre**: Displays a bubble chart relating energy and valence of songs by genre, with bubble size representing the number of songs in that genre.

- **Songs Added per Month**: Displays the number of songs added to favorites per month, along with a trendline.

## Notes

- Make sure you have a Spotify account and access to the Spotify API to obtain the necessary data.

- The icons used in the application are located in the `assets` directory.

- The `app.py` file contains the complete code for the Dash application, including the user interface setup and database queries.

- The application runs on port 8050 of your local machine and can be accessed from any web browser.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.