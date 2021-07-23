import json
import pdb
import time
import urllib.parse
from os import path
import requests


class DiscoverDaily(object):
    """
    Root class for the DiscoverDaily operations
    """
    AUTH_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(self, config={}):
        """

        :param config: a dict with all the info needed to use the api.
        """
        exception_temp = ValueError
        # unpack config
        self._access_token = config.get("access_token")
        if self._access_token is None:
            raise exception_temp("config must have a access_token value")

        self._client_id = config.get("client_id")
        if self._client_id is None:
            raise exception_temp("config must have a client_id value")

        self._client_secret = config.get("client_secret")
        if self._client_secret is None:
            raise exception_temp("config must have a client_secret value")

        self._expires_in = config.get("expires_in")
        if self._expires_in is None:
            raise exception_temp("config must have a expires_in value")

        self._refresh_token = config.get("refresh_token")
        if self._refresh_token is None:
            raise exception_temp("config must have a refresh_token value")

        self._scope = config.get("scope")
        if self._scope is None:
            raise exception_temp("config must have a scope value")

        self._time_stamp = config.get("time_stamp")
        if self._time_stamp is None:
            raise exception_temp("config must have a time_stamp value")

        self._token_type = config.get("token_type")
        if self._token_type is None:
            raise exception_temp("config must have a token_type value")

        self._liked_songs = config.get("liked_songs")
        if not self._liked_songs:
            self._liked_songs = []
            print("liked_songs was invalid. Constructing liked songs list...")
            self.build_liked_songs()

    def build_liked_songs(self):
        api_url = "https://api.spotify.com/v1/me/tracks"
        off_set = 0
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        params = {
            "offset": off_set,
            "limit": 50
        }
        next_url = api_url + '?' + urllib.parse.urlencode(params)
        while True:
            self.validate_token()
            headers.update({"Authorization": self._token_type + ' ' + self._access_token})
            response = requests.get(next_url, headers=headers)
            if response.status_code == 200:
                tracks = response.json()["items"]
                for track in tracks:
                    self._liked_songs.append(track["track"]["id"])
                next_url = response.json().get("next")
                print(f"Number of liked songs found: {len(self._liked_songs)}")
                if next_url:
                    continue
                else:
                    break
        print("build song list successfully...")

    def validate_token(self):
        current_time = time.time()
        if (current_time - self._time_stamp) > self._expires_in:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data_params = {
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
                "client_id": self._client_id
            }
            response = requests.post(url=self.TOKEN_URL, headers=headers, data=data_params)
            if response.status_code == 200:
                response_json = response.json()
                self._access_token = response_json.get("access_token")
                self._token_type = response_json.get("token_type")
                self._expires_in = response_json.get("expires_in")
                self._refresh_token = response_json.get("refresh_token")
                self._scope = response_json.get("scope")
            else:
                print(response.status_code, response.reason)
                print(response.text)
                raise Exception("Something went wrong refreshing the token")

    def build_daily_discover_playlist(self):
        tracks_to_be_added = []
        discover_daily_info, daily_mix_playlists = self._get_playlists()
        for daily_mix_url in daily_mix_playlists:
            print(f"looking in {daily_mix_url}...")
            tracks_to_be_added += self._get_unliked_songs_from_playlist(daily_mix_url)

    def _get_unliked_songs_from_playlist(self, playlist_url: str, get_all_songs=False):
        songs = []
        headers = {
            "Authorization": self._token_type + ' ' + self._access_token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        while True:
            response = requests.get(playlist_url, headers=headers)
            if response.status_code == 200:
                response_json = response.json()
                for track in response_json.get("items"):
                    if get_all_songs:
                        songs.append(track.get("uri"))
                    else:
                        if not track.get("track").get("id") in self._liked_songs:
                            songs.append(track.get("uri"))
                            print(f'adding {track.get("track").get("name")}')
                playlist_url = response_json.get("next")
                if not playlist_url:
                    break
        return songs

    def _create_discover_daily(self, user_id: str):
        creation_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        headers = {
            "Authorization": self._token_type + ' ' + self._access_token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        data_params = {
            "name": "Discover Daily",
            "public": "false",
            "description": "All the unliked songs from the daily mixes in one convenient place."
        }
        response = requests.post(creation_url, headers=headers, json=data_params)
        # status code 201 indicates successful creation
        if response.status_code == 201:
            response_json = response.json()
            print("Created discover daily")
            return response_json.get("id"), response_json.get("uri")
        else:
            print(response.status_code, response.reason)
            print(response.text)
            raise Exception("Unable to create discover daily playlist")

    def _clear_playlist(self, playlist: []):
        songs_to_remove = self._get_unliked_songs_from_playlist(playlist[1], get_all_songs=True)

    def _get_playlists(self):
        playlist_urls = []
        discover_daily_info = []
        user_id = ""
        self.validate_token()
        api_url = "https://api.spotify.com/v1/me/playlists?limit=50"
        headers = {
            "Authorization": self._token_type + ' ' + self._access_token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            for playlist in response_json.get("items"):
                if "Daily Mix" in playlist.get("name"):
                    playlist_urls.append(playlist.get("tracks").get("href"))
                    print(f'found playlist: {playlist.get("tracks").get("href")}')

                if "Discover Daily" in playlist.get("name"):
                    print("found discover daily...")
                    discover_daily_info.append(playlist.get("id"))
                    discover_daily_info.append(playlist.get("uri"))
                else:
                    user_id = playlist.get("owner").get("id")

        if not discover_daily_info:
            discover_daily_info = self._create_discover_daily(user_id)
        return discover_daily_info, playlist_urls


    @classmethod
    def create_config(cls, client_id=None, client_secret=None):
        """
        sets up the everything needed to access the spotify api
        :return: dictionary with all the config information
        """
        # specific imports
        from urllib.parse import urlencode
        import socket
        # import base64
        # from http.server import HTTPServer, BaseHTTPRequestHandler

        # get cilent id and client secret, if not already supplied
        config_dict = {}
        if not client_id:
            client_id = input("Client ID?: ")
        if not client_secret:
            client_secret = input("Client secret?: ")

        # create user auth url
        user_auth_params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": "http://localhost:8000/",
            "scope": "playlist-modify-private playlist-read-private user-library-read",
        }
        print("please follow this link to authorize app")
        print(cls.AUTH_URL + '?' + urlencode(user_auth_params))
        print("Starting webserver to listen for the request...")

        # Unsure of how to get HTTPServer to work yet, so socket is my fall back
        # with HTTPServer(("127.0.0.1", 8000), BaseHTTPRequestHandler) as web_server:
        #     pass
        # this will listen for the request from the browser containing the code
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 8000))
            s.listen(1)
            print("Waiting for client secret...")
            c, addr = s.accept()
            with c:
                code = c.recv(4096).decode().split('=', maxsplit=1)[1].split(' ', maxsplit=1)[0]
                body = "<h1>Authorization successful</h1>\r\n"
                header = "HTTP/1.1 200 OK\r\n" \
                         f"Content-Length: {len(body)}\r\n" \
                         "Content-Type: text/html\r\n" \
                         "Connection: close\r\n" \
                         "\r\n\r\n"
                return_message = header + body
                # respond to the request with a return message
                c.sendall(return_message.encode())

            print(f"Authorization successful. Got from {addr}")
            print("Requesting token...")
            body_param = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": "http://localhost:8000/",
                "client_id": client_id,
                "client_secret": client_secret
            }

            # auth_header = base64.urlsafe_b64encode((client_id + ':' + code).encode('ascii')).replace(b'=', b'')
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'}
            token_response = requests.request("POST", cls.TOKEN_URL, data=body_param, headers=headers)
            if token_response.status_code == 200:
                # get user ID
                # construct config from all the info gathered
                config_dict.update({'client_id': client_id})
                config_dict.update({"client_secret": client_secret})
                config_dict.update(token_response.json())
                config_dict.update({"time_stamp": time.time()})
                config_dict.update({"liked_songs": []})
                return config_dict


if __name__ == "__main__":
    # check for config file
    CONFIG_FILE = "config.json"

    if path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as conf:
            discover_instance = DiscoverDaily(json.load(conf))
            discover_instance.build_daily_discover_playlist()
        print("COnfig file loaded...")
    else:
        print("Config file does not exist, so attempting to create one")
        Spotify_config = DiscoverDaily.create_config()
        with open(CONFIG_FILE, 'w') as conf:
            json.dump(Spotify_config, conf, indent=4, sort_keys=True)
