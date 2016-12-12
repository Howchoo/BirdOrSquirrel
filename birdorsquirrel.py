#!/usr/bin/env python

import logging
import time
import tweepy

from gpiozero import MotionSensor
from picamera import PiCamera
from settings import (consumer_key, consumer_secret,
                      access_token, access_token_secret)


# logging.basicConfig(filename='/var/log/birdorsquirrel.log', level=logging.DEBUG)
logger = logging.getLogger('birdorsquirrel')
handler = logging.FileHandler('/var/log/birdorsquirrel.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class BirdException(Exception):
    pass


class BirdOrSquirrel():
    motion_timeout = 60  # 1 minute
    tmp_img = '/tmp/twitter-photo.jpg'

    def __init__(self, *args, **kwargs):
        logger.info('BirdOrSquirrel init.')
        self.setup_twitter()
        self.pir = MotionSensor(4)
        self.camera = PiCamera()

    def setup_twitter(self):
        if not (access_token and access_token_secret and consumer_key
                and consumer_secret):
            raise BirdException('Add your Twitter API credentials to settings.py.')

        # Authenticate
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.twitter_api = tweepy.API(auth)
        logger.info('twitter authenticated.')

    def take_image_and_tweet(self):
        # Take the picture
        self.camera.start_preview()
        time.sleep(5)
        self.camera.capture(self.tmp_img)
        self.camera.stop_preview()
        logger.info('Picture taken.')

        # Send the tweet
        self.twitter_api.update_with_media(self.tmp_img)
        logger.info('Tweet sent.')

    def listen(self):
        """Listen for motion to be detected."""
        while True:
            if self.pir.motion_detected:
                logger.info('Motion detected.')
                self.take_image_and_tweet()
                time.sleep(self.motion_timeout)


if __name__ == '__main__':
    try:
        b = BirdOrSquirrel()
        b.listen()
    except BirdException as e:
        logger.error(e)
