import json
from os import path
from urllib.parse import quote
import pdb
import socket
# constants
import requests

CONFIG_FILE = "config.json"

# Globalals
Spotify_config = {}

# functions


def get_authentication_token(config: {}):
    """
    :param config: dictionary to add the auth token to
    :return: config param with an auth token present
    """
    auth_url = "https://accounts.spotify.com/authorize"
    return config

def create_config_structure():
    """
    Creates the structure for the config
    :return: config structure that is a bit populated.
    """
    config = {}
    auth_url = "https://accounts.spotify.com/authorize"
    token_url = "https://accounts.spotify.com/api/token"

    # promps user for all the info needed to build the config
    print("Hello! thank you for using the discover daily script!")
    print("For this setup, please provide all the necessary information for the app to work correctly.")

    client_id = input("What is the client id?: ")
    print("Please follow this link to authorize your account")
    print(auth_url+quote(f'?client_id={client_id}'
                f'&response_type=code&redirect_uri=http://localhost:8000/&scope=playlist-modify-private', safe="&=?"))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 8000))
        s.listen(1)
        print("Waiting for auth token...")
        c, addr = s.accept()
        with c:
            code = c.recv(4096).decode().split('=', maxsplit=1)[1].split(' ', maxsplit=1)[0]
            body = "<h1>Authorization successful</h1>\r\n"
            header = "HTTP/1.1 200 OK\r\n" \
                     f"Content-Length: {len(body)}\r\n" \
                     "Content-Type: text/html\r\n" \
                     "Connection: close\r\n" \
                     "\r\n\r\n"
            return_message = header+body
            c.sendall(return_message.encode())
        config.update({"client_id": client_id})
        print(f"Authorization successful. Got from {addr}")

        # grab the token
        print("Requesting token...")
        body_param = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "http://localhost:8000/"
        }

        response = requests.request("POST", token_url, headers= {"Authorization": f"Basic {client_id+code}"},
                                    data=body_param)
        pdb.set_trace()

        return config


if __name__ == "__main__":
    # check for config file
    if path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as conf:
            Spotify_config = json.load(conf)
    else:
        Spotify_config = create_config_structure()
        with open(CONFIG_FILE, 'w') as conf:
            json.dump(Spotify_config, conf)
