import logging
import json

from kalliope.core.NeuronModule import NeuronModule, InvalidParameterException
from mpd import MPDClient

from random import randint

logging.basicConfig()
logger = logging.getLogger("kalliope")

class Kalliopempd (NeuronModule):
    def __init__(self, **kwargs):
        super(Kalliopempd, self).__init__(**kwargs)

        # get parameters form the neuron
        self.configuration = {
            "mpd_action": kwargs.get('mpd_action', None),
            "mpd_url": kwargs.get('mpd_url', 'localhost'),
            "mpd_port": kwargs.get('mpd_port', '6600'),
            "mpd_random": kwargs.get('mpd_random', 0),
            "query": kwargs.get('query', None),
            "mpd_pass": kwargs.get('mpd_password', None),
            "mpd_volume": kwargs.get('mpd_volume', "100")
        }

        # check parameters
        if self._is_parameters_ok():

            self.init_mpd_client()

            if self.configuration['mpd_action'] == "playlist":
                logger.debug("MPD Action: playlist")
                self.mpd_action_playlist()
            elif self.configuration['mpd_action'] == "playlist_spotify":
                logger.debug("MPD Action: spotify playlist")
                self.mpd_action_spotify_playlist()
            elif self.configuration['mpd_action'] == "toggle_play":
                logger.debug("MPD Action: toggle play")
                self.mpd_action_toggle_play()
            elif self.configuration['mpd_action'] == "search":
                logger.debug("MPD Action: search")
                self.mpd_action_search()
            elif self.configuration['mpd_action'] == "file":
                logger.debug("MPD Action: read file")
                self.mpd_action_file()
            elif self.configuration['mpd_action'] == "play_next":
                self.client.next()
            elif self.configuration['mpd_action'] == "play_previous":
                self.client.previous()
            elif self.configuration['mpd_action'] == "play_stop":
                self.client.stop()
            else :
                logger.debug("MPD Action: Not found")
                # TODO

        self.mpd_disconnect()


    def mpd_action_playlist(self):
	logger.debug("In Playlist action:")
	logger.debug(self.configuration['query'])
        self.clear_playlist()
        try:
            self.client.load(self.configuration['query'])

            #self.client.count() returns 0 as the playlist is not loaded yet
            #Temp workaround: random number between 0 and 20
            r = 0
            if self.configuration['mpd_random'] == 1:
                r = randint(0, 20)
            self.client.play(r)
        except Exception, e:
            logger.debug("MPD playlist not found")
            logger.debug(e)

    def mpd_action_spotify_playlist(self):
	logger.debug("In Spotify Playlist action:")
	logger.debug(self.configuration['query'])
        self.clear_playlist()
        try:
            results = self.client.lsinfo(self.configuration['query'])
            for result in results:
                self.client.add(result['file'])

            r = 0
            if self.configuration['mpd_random'] == 1:
                r = randint(0,len(results))
            self.client.play(r)
        except Exception, e:
            logger.debug("MPD playlist not found on spotify")
            logger.debug(e)

    def mpd_action_search(self):
	logger.debug("In search action:")
        self.clear_playlist()
        results = self.client.findadd('any', self.configuration['query'])
        self.client.play(0)

    def mpd_action_file(self):
	logger.debug("In read file action:")
        self.clear_playlist()
        results = self.client.add(self.configuration['query'])
        self.client.play(0)

    def mpd_action_toggle_play(self):
	logger.debug("In toggle action:")
        self.client.pause()

    def init_mpd_client(self):
        client = MPDClient()
        client.timeout = 10
        client.idletimeout = None
        client.connect(self.configuration['mpd_url'], self.configuration['mpd_port'])  # connect to localhost:6600
        client.random(self.configuration['mpd_random'])
        client.setvol(self.configuration['mpd_volume'])

        if self.configuration['mpd_pass']:
            client.password(self.configuration['mpd_pass'])

        self.client = client

    def clear_playlist(self):
        self.client.clear()

    def mpd_disconnect(self):
        self.client.close()
        self.client.disconnect()

    def _is_parameters_ok(self):
        """
        Check if received parameters are ok to perform operations in the neuron
        :return: true if parameters are ok, raise an exception otherwise
        .. raises:: InvalidParameterException
        """

        if self.configuration['mpd_url'] is None:
            raise InvalidParameterException("MPD needs a url")

        if self.configuration['mpd_action'] is None:
            raise InvalidParameterException("MPD needs an action")
        elif self.configuration['mpd_action'] in ['playlist', 'playlist_spotify', 'search', 'file'] \
            and self.configuration['mp_query'] is None:
            raise InvalidParameterException("MPD requires a query for this action")

        return True

