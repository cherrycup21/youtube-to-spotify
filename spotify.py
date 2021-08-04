#Below is a program which automatically adds all of the songs from a Youtube Playlist of my choice into a Spotify Playlist of my choice.

#APIs used: Youtube Data API. Spotify Web API and the Youtube DL Libary.

import json
import requests
import os

from secrets import spotify_user_id, spotify_token

import google_auth_oathlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl

class CreatePlaylist(object):
    
    def __init__(self):
        self.user_id = spotify_user_id
        self.spotify_token = spotify_token
        self.youtube_client = self.get_youtube_client()
        self.all_song_info = {}

    #Step 1: Log into Youtube
    def get_youtube_client(self):
        #copied from the Youtube Data APO
        # Disable OAuthlib's HTTPS verification when running locally,
        #*DO NOT LEAVE THIS OPTION ENABLED IN PRODUCTION.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_File = "client_secret.json"

        #Get credentials and create API client
        scopes = ["http://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
        credentials = flow.run_console()

        #from the Youtube DATA API
        youtube_client = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

        return youtube_client

    #Step 2: Grab Our Liked Videos and Creating a Dictinary Of Important Song Information
    def get_liked_videos(self):
        request = self.youtube_client.videos().list(
            part="snippet,contentDetails,statistics",
            myRating="like"
        )
        response = request.execute()

        #collect each video and get important information
        for item in response["items"]:
            video_title = item["snippet"]["title"]
            youtube_url = "https://www.youtube/watch?v={}".format(item["id"])

            #use youtube_dl to collect the song name and artist name
            video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download=False)

            song_name= video["track"]
            artist = video["artist"]

            #save all important info
            self.all_song_info[video_title]={
                 "youtube_url": youtube_url,
                 "song_name": song_name,
		 "artist": artists,

                 #add the url, easy to get song to put into playlist
                 "spotify_uri": self.get_spotify_uri(song_name,artist)
            }

    #Step 3: Create a New Playlist
    def create_playlist(self):
        
        request_body = json.dumps({
            "name": "Youtube Liked Videos",
            "description": "All Liked Youtube Videos",
            "public": True
        })

        query = "https://api.spotify.com/v1/users/{user_id}/playlists".format(self.user_id)
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type":"application/json",
                "Authorization":"Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()

        #playlist id
        return response_json["id"]
    
    #Step 4: Search For the Song
    def get_spotify_uri(self, song_name, artist):
        query = "https://api.spotify.com/v1/search".format(
            song_name,
            artist
        )
        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]

        #only use the first song
        uri = songs[0]["uri"]

        return uri

        #Next function is copy and pasted directly from the Youtube Data API Documentations to get a Youtube client to use later


    #Step 5: Add this song into the new Spotify playlist
    def add_song_to_playlist(self):
        #populate our songs dictionary
        self.get_liked_videos()
        
        #collect all of uri
        uris = []
        for song in self.all_song_info.items():
            uri.append(info["spotify_uri"])

        
        #create  new playlist
        playlist_id = self.create_playlist()
        
        #add all songs into new playlist
        request_data = json.dumps(uris)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)

        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(Self.spotify_token)
            }
        )
        response_json = response.json()
        return response_json

    
