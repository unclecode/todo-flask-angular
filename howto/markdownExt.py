__author__ = 'unclecode'

# Markdown rendering
# It's good for CMS
# https://pythonhosted.org/Flask-Markdown/

import sys, os, json, hashlib, uuid, base64, random
if '/Library/Python/2.7/site-packages' not in sys.path:
    sys.path.insert(0, '/Library/Python/2.7/site-packages')
from flask import Flask, make_response, redirect, request, url_for, Response, current_app, g, jsonify, views, render_template_string, session
from flaskMarkdown import Markdown


app = Flask(__name__)

Markdown(app)

# md = Markdown(app,
#               extensions=['footnotes'],
#               extension_configs={'footnotes': ('PLACE_MARKER','~~~~~~~~')},
#               safe_mode=True,
#               output_format='html4',
#              )

@app.route('/')
def index():
    return render_template_string(
        """
<h1>This is html</h1>
{% filter markdown %}
Your Markdown
=============
{% endfilter %}""")



if __name__ == "__main__":
    app.run(debug=True)
