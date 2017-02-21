#!/usr/bin/env python

import datetime
import logging
import pytz
import RPi.GPIO as GPIO
import os
import time
import tweepy

from astral import Astral
from picamera import PiCamera


# Set up logger
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

        # Set up pins for motion detection
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(3, GPIO.IN)

        # Astral settings
        city_name = os.environ.get('CITY', 'San Francisco')
        self.astral = Astral()
        self.astral.solar_depression = 'civil'
        self.city = self.astral[city_name]

        logger.info('BirdOrSquirrel initialized.')

    def setup_twitter(self):
        # Retrieve the secrets from the environment
        access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
        consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
        consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')

        if not (access_token and access_token_secret and consumer_key
                and consumer_secret):
            raise BirdException('Twitter credentials must be passed as '
                                'environment variables.')

        # Authenticate
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.twitter_api = tweepy.API(auth)
        logger.info('twitter authenticated.')

    def take_image_and_tweet(self):
        # If it's not daylight, skip
        if not self.is_daylight():
            logger.info('Skipping picture, too dark.')
            return

        # Set up the camera
        camera = PiCamera()
        camera.vflip = True
        camera.brightness = 50
        camera.contrast = 10
        # Take the picture
        camera.start_preview()
        time.sleep(5)
        camera.capture(self.tmp_img)
        camera.stop_preview()
        logger.info('Picture taken.')

        # Send the tweet
        self.twitter_api.update_with_media(self.tmp_img)
        logger.info('Tweet sent.')

    def is_daylight(self):
        sun = self.city.sun(date=datetime.date.today(), local=True)
        sunrise = sun['sunrise']
        sunset = sun['sunset']

        now = datetime.datetime.now()
        now = pytz.timezone(self.city.timezone).localize(now)

        return (now > sunrise and now < sunset)

    def listen(self):
        """Listen for motion to be detected."""
        while True:
            if not GPIO.input(3):
                logger.info('Motion detected.')
                self.take_image_and_tweet()
                time.sleep(self.motion_timeout)


if __name__ == '__main__':
    try:
        b = BirdOrSquirrel()
        b.listen()
    except BirdException as e:
        logger.error(e)
