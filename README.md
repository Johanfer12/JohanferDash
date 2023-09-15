# Spotify and X-Twitter Dashboard

This is a Python web application built using Dash for visualizing Spotify and X-Twitter statistics.

## Table of Contents

- [Spotify Section](#spotify-section)
- [X-Twitter Section](#x-twitter-section)

### Spotify Section <a name="spotify-section"></a>

#### Overview
- This section provides statistics and visualizations related to your Spotify listening history.

#### Top Artist
- The most-played artist in your Spotify history is displayed.

#### Top Songs
- The top songs you've listened to are listed, along with links to play them.

#### Total Playtime
- The total playtime of your Spotify favorites is displayed in days, hours, minutes, and seconds.

#### Top Artists
- The top 5 most-listened-to artists in the last 4 weeks are displayed.

#### Recent Favorite Songs
- The 5 most recently added songs to your favorites are listed.

#### Top Genres
- A pie chart displays the top 5 genres you've listened to, along with their percentages.

#### Valence Over Time
- A bar chart shows the average valence (positivity/negativity) of songs over the years.

#### Energy and Valence by Genre
- A bubble chart displays the relationship between energy and valence for different genres, with bubble size indicating the number of songs in each genre.

#### Songs Added Over Time
- A line chart shows the number of songs added to your favorites over time.

### X-Twitter Section <a name="x-twitter-section"></a>

#### Overview
- This section provides statistics and visualizations related to X-Twitter activity.

#### Total Tweets
- The total number of tweets in X-Twitter history is displayed.

#### Top Mentioned Users
- The top 5 users mentioned in tweets are listed, along with the number of mentions.

#### Tweets Per Month
- A line chart displays the number of tweets posted each month.

#### Tweets Per Day of the Week
- A pie chart shows the distribution of tweets by day of the week.

#### Word Cloud
- A word cloud visualizes the most frequently used words in tweets.

## How to Run the Application

1. Make sure you have Python installed on your machine.

2. Install the required Python packages by running the following command in your terminal:

   ```
   pip install dash plotly pandas numpy sqlite3 dateutil
   ```

3. Run the application by executing the following command in the same directory as your code:

   ```
   python your_app_name.py
   ```

4. Open a web browser and visit `http://localhost:8050` to access the Spotify and X-Twitter Dashboard.

Enjoy exploring your Spotify and X-Twitter statistics!

**Note:** You may need to adjust the file paths, database names, and other configurations in the code to match your setup.