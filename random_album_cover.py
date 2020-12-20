#!/usr/bin/env python
import urllib
from xml.dom import minidom
from optparse import OptionParser
import subprocess
import re
from html.parser import HTMLParser
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import requests
from random import randrange
import os
import tweepy
from album_blurb import album_blurb
from band_blurb import band_blurb

consumer_key = os.getenv("TWITTER_API_KEY")
consumer_secret = os.getenv("TWITTER_API_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
token_secret = os.getenv("TWITTER_TOKEN_SECRET")

storage_dir = "/home/guimas/Software/randomalbumcover/"


def twitter_api():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, token_secret)

    # Create API object
    api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
    
    return api

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.get_data = False;
        self.quotes = []

    def handle_starttag(self, tag, attrs):
        if tag == "dt":
            if attrs[0][0] == 'class' and attrs[0][1] == 'quote':
                self.get_data = True
        pass

    def handle_endtag(self, data):
        pass

    def handle_data(self, data):
        if self.get_data:
            self.quotes.append(data)
            self.get_data = False

def getBandName():
    random_wiki_url = "http://en.wikipedia.org/w/api.php?format=xml&action=query&list=random&rnnamespace=0&rnlimit=1"
    dom = minidom.parse(urllib.request.urlopen(random_wiki_url))

    for line in dom.getElementsByTagName('page'):
        return line.getAttributeNode('title').nodeValue

    
def getAlbumTitle():
    random_quote_url = "http://www.quotationspage.com/random.php"
    page = urllib.request.urlopen(random_quote_url).read()
    parser = MyHTMLParser()
    parser.feed(str(page))

    num_quotes = len(parser.quotes)
    quote = parser.quotes[randrange(0, num_quotes)].rstrip('.')

    last_set = randrange(3,5)
    words = quote.split()

    if last_set > len(words):
        last_set = len(words)

    return (" ").join(words[-last_set:])


def message_sentence(s1, s2):
    s1index = randrange(0, len(s1))
    s2index = randrange(0, len(s2))

    full_sentence = s1[s1index] + " " +s2[s2index]
    
    return full_sentence


def getPicsum(band_name, album_title):
    width_sizes = [400, 500, 600, 700]
    
    width = width_sizes[randrange(0, len(width_sizes), 1)]
    height = width + randrange(-1, 2, 1)*100
    
    name = storage_dir +  "dummy.png"
    url = 'https://picsum.photos/' + str(width) + '/' + str(height)

    album_art = requests.get(url)

    with open(name, 'wb') as raw_file:
        raw_file.write(album_art.content)
    
    img = Image.open(name)
    draw = ImageDraw.Draw(img)
    
    band_name_font = ImageFont.truetype(r'/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
    album_name_font = ImageFont.truetype(r'/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
    
    x_title = 10
    y_title = 20

    bg_color = (randrange(0, 256, 1), randrange(0, 256, 1), randrange(0, 256, 1))
    fg_color = (randrange(0, 256, 1), randrange(0, 256, 1), randrange(0, 256, 1))

    draw.text((x_title-1, y_title+1), band_name, font=band_name_font, fill=bg_color)
    draw.text((x_title-1, y_title-1), band_name, font=band_name_font, fill=bg_color)
    draw.text((x_title+1, y_title+1), band_name, font=band_name_font, fill=bg_color)
    draw.text((x_title+1, y_title-1), band_name, font=band_name_font, fill=bg_color)
    draw.text((x_title, y_title), band_name, font=band_name_font, fill=fg_color)
    
    x_title = 10
    y_title = height - 40

    bg_color = (randrange(0, 256, 1), randrange(0, 256, 1), randrange(0, 256, 1))
    fg_color = (randrange(0, 256, 1), randrange(0, 256, 1), randrange(0, 256, 1))

    draw.text((x_title-1, y_title+1), album_title, font=album_name_font, fill=bg_color)
    draw.text((x_title-1, y_title-1), album_title, font=album_name_font, fill=bg_color)
    draw.text((x_title+1, y_title+1), album_title, font=album_name_font, fill=bg_color)
    draw.text((x_title+1, y_title-1), album_title, font=album_name_font, fill=bg_color)
    draw.text((x_title, y_title), album_title, font=album_name_font, fill=fg_color)
    
    return img


def message_sentence(s1, s2, band, album):

    s1index = randrange(0, len(s1))
    s2index = randrange(0, len(s2))

    full_sentence = s1[s1index]%(band) + " " +s2[s2index]%(album)
    
    return full_sentence

#################################################
def run_all():
    """
    Runs the entire beatbot process
    """

    # Creates a band name and the quotations to put in the blurb.
    band_name = getBandName()
    band = '\"' + band_name + '\"'

    # Creates the album title and the quotations to put in the blurb 
    album_title = getAlbumTitle()
    album = '\"' + album_title + '\"'

    #Gets the image from Picosia and the creates the image to upload
    img = getPicsum(band_name, album_title)
    stored_image = storage_dir + 'test.png'
    img.save(stored_image)

    # Creates the blurb
    message = message_sentence(band_blurb, album_blurb, band, album)
    
    # Gets the tokens and upload the picture with the blurb
    api = twitter_api()
    return_status = api.update_with_media(stored_image, status=message)


####################################################
run_all()

