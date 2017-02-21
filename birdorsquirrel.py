#!/usr/bin/env python

import datetime
import logging
import pytz
import RPi.GPIO as GPIO
import time
import tweepy

from astral import Astral
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
    city_name = 'San Francisco'

    def __init__(self, *args, **kwargs):
        logger.info('BirdOrSquirrel init.')
        self.setup_twitter()
        # Set up pins for motion detection
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(3, GPIO.IN)
        # Astral settings
        self.astral = Astral()
        self.astral.solar_depression = 'civil'
        self.city = self.astral[self.city_name]
        logger.info('BirdOrSquirrel initialized.')

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
        dawn = sun['dawn']
        dusk = sun['dusk']

        now = datetime.datetime.now()
        now = pytz.timezone(self.city.timezone).localize(now)

        return (now > dawn and now < dusk)

    def seconds_until_sunrise(self):
        sun_today = self.city.sun(date=datetime.date.today(), local=True)
        dawn_today = sun_today['dawn']

        sun_tomorrow = self.city.sun(date=datetime.date.today() + datetime.timedelta(days=1), local=True)
        dawn_tomorrow = sun_tomorrow['dawn']

        now = datetime.datetime.now()
        now = pytz.timezone(self.city.timezone).localize(now)

        if now < dawn_today:
            # return time until sunrise today
            delta = dawn_today - now
        else:
            # return time until sunrise tomorrow
            delta = dawn_tomorrow - now

        return delta.total_seconds()

    def listen(self):
        """Listen for motion to be detected."""
        while True:
            if not GPIO.input(3):
                logger.info('Motion detected.')
                self.take_image_and_tweet()
                time.sleep(self.motion_timeout)

    def tweet_minutely(self):
        while True:
            if not self.is_daylight():
                seconds = self.seconds_until_sunrise()
                logger.info('Pausing until daylight. {0} seconds.'.format(seconds))
                time.sleep(seconds)
            self.take_image_and_tweet()
            time.sleep(60)

    def do_nothing(self):
        while True:
            time.sleep(60)


if __name__ == '__main__':
    try:
        b = BirdOrSquirrel()
        b.listen()
        # b.tweet_minutely()
        # b.do_nothing()
    except BirdException as e:
        logger.error(e)
