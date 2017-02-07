import logging
import json

from kalliope.core.NeuronModule import NeuronModule, InvalidParameterException
from mpd import MPDClient

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
            "mpd_pass": kwargs.get('mpd_pass', None)
        }

        # check parameters
        if self._is_parameters_ok():

            self.init_mpd_client()
 
            if self.configuration['mpd_action'] == "playlist":
                logger.debug("MPD Action: playlist")
                self.mpd_action_playlist()
            elif self.configuration['mpd_action'] == "toggle_play":
                logger.debug("MPD Action: toggle play")
                self.mpd_action_toggle_play()
            elif self.configuration['mpd_action'] == "search":
                logger.debug("MPD Action: search")
                self.mpd_action_search()
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
            # TODO update to a random number.
            self.client.play(0)
        except Exception:
            logger.debug("MPD playlist not found") 
        
    def mpd_action_search(self):
	logger.debug("In search action:")
        self.clear_playlist()
        results = self.client.findadd('any', 'Michael Jackson')
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

        # TODO

        return True

