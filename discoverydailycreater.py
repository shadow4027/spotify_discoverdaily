import json
from os import path
# constants
CONFIG_FILE = "config.json"

# Globalals
Spotify_config = {}

# check for config file
if path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as conf:
        Spotify_config = json.load(conf)
else:
    with open(CONFIG_FILE, "w"):
        json.dump(Spotify_config)

# functions

def get_authentication_token(config: {}):
    """
    :param config: dictionary to add the auth token to
    :return: config param with an auth token present
    """
    auth_url = ""
    return config