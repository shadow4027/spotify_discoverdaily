import json
import requests


class DiscoverDaily(object):
    """
    Root class for the DiscoverDaily operations
    """
    def __init__(self, config={}):
        """

        :param config: a dict with all the info needed to use the api.
        """
        self.CLIENT_ID = config.get('client_id')
        self.CLIENT_SECRET = config.get('client_secret')

