__author__ = 'unclecode'

# ShortURL Extension
# https://github.com/lepture/flask-shorturl

import sys, os, json, hashlib, uuid, base64, random
if '/Library/Python/2.7/site-packages' not in sys.path:
    sys.path.insert(0, '/Library/Python/2.7/site-packages')
from flask import Flask, make_response, redirect, request, url_for, Response, current_app, g, jsonify, views, render_template_string, session
from flask_shorturl import ShortUrl

app = Flask(__name__)

"""
SHORT_URL_ALPHABET	The alphabet to be used by Encoder, default value: mn6j2c4rv8bpygw95z7hsdaetxuk3fq
SHORT_URL_MIN_LENGTH	default value: 5
SHORT_URL_BLOCK_SIZE	default value: 24
"""

su = ShortUrl(app)

# Us numerical ID for items you need short link
url = su.encode_url(3232)
uid = su.decode_url(url)

@app.route('/')
def index():
    return render_template_string("""Please go to <a href="{{link}}">{{link}}</a> which is {{mlink}}""", link = url, mlink = uid)

if __name__ == "__main__":
    app.run(debug=True)
