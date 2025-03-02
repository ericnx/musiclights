from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, render_template
import ct
import spotipy
import os

app = Flask(__name__)
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

scopes = "user-read-playback-state, user-read-currently-playing, app-remote-control, streaming, playlist-read-private"
# authorize the user to get access token
sp_oauth = SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=scopes)    
token = sp_oauth.get_access_token()
access_token = token["access_token"]

# automatically refreshes the access token when it expires
def get_token():
    token = sp_oauth.get_cached_token()
    if not token or sp_oauth.is_token_expired(token):
        token = sp_oauth.refresh_access_token(token["refresh_token"])

    return token["access_token"]

@app.route("/")
def login():
    token = sp_oauth.get_cached_token()
    if not token:
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    return redirect(url_for("current_song"))

@app.route("/current_song")
def current_song():
    access_token = get_token()
    # use access token get to the current song
    sp = spotipy.Spotify(auth=access_token)
    current_song = sp.current_user_playing_track()

    if current_song:
        name = current_song["item"]["name"]
        artists = ", ".join([artist["name"] for artist in current_song["item"]["artists"]])
        if len(current_song["item"]["album"]["images"]) != 0:
            cover = current_song["item"]["album"]["images"][1]["url"]
        else:
            cover = "https://raw.githubusercontent.com/ericnx/MusicPalette/main/images/localfile.png"
        color_palette = ct.get_color_palette(cover)

        return render_template("index.html", name=name, artists=artists, cover=cover, color_palette=color_palette)
    else:
        cover = "https://images.squarespace-cdn.com/content/v1/58b451af03596efb0e7d5f95/1573658559239-QS8M0JG5RJXW4ARFZJXB/white-square-border-png-4.png"
        color_palette = ct.get_color_palette(cover)
        return render_template("index.html", name="No song is currently playing.", cover=cover, color_palette=color_palette)

if __name__ == "__main__":
    app.run(debug=True, port=3000)