#!/usr/bin/env python
import urllib
from xml.dom import minidom
from optparse import OptionParser
import subprocess
import re
from html.parser import HTMLParser
import random
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import requests
from random import randrange

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
    quote = parser.quotes[random.randint(0, num_quotes)].rstrip('.')

    last_set = random.randint(3,5)
    words = quote.split()

    if last_set > len(words):
        last_set = len(words)

    return (" ").join(words[-last_set:])


def getPicsum():
    width_sizes = [400, 500, 600, 700]
    
    width = width_sizes[randrange(0, len(width_sizes), 1)]
    height = width + randrange(-1, 2, 1)*100
    
    name = "dummy.png"
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
    band_name = getBandName()

    bg_color = (randrange(0, 256, 1), randrange(0, 256, 1), randrange(0, 256, 1))
    fg_color = (randrange(0, 256, 1), randrange(0, 256, 1), randrange(0, 256, 1))

    draw.text((x_title-1, y_title+1), band_name, font=band_name_font, fill=bg_color)
    draw.text((x_title-1, y_title-1), band_name, font=band_name_font, fill=bg_color)
    draw.text((x_title+1, y_title+1), band_name, font=band_name_font, fill=bg_color)
    draw.text((x_title+1, y_title-1), band_name, font=band_name_font, fill=bg_color)
    draw.text((x_title, y_title), band_name, font=band_name_font, fill=fg_color)
    
    x_title = 10
    y_title = height - 40
    album_title = getAlbumTitle()

    bg_color = (randrange(0, 256, 1), randrange(0, 256, 1), randrange(0, 256, 1))
    fg_color = (randrange(0, 256, 1), randrange(0, 256, 1), randrange(0, 256, 1))

    draw.text((x_title-1, y_title+1), album_title, font=album_name_font, fill=bg_color)
    draw.text((x_title-1, y_title-1), album_title, font=album_name_font, fill=bg_color)
    draw.text((x_title+1, y_title+1), album_title, font=album_name_font, fill=bg_color)
    draw.text((x_title+1, y_title-1), album_title, font=album_name_font, fill=bg_color)
    draw.text((x_title, y_title), album_title, font=album_name_font, fill=fg_color)
    
    return img


if __name__=='__main__':
    img = getPicsum()
    img.save('test.png')


