"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask, render_template
from openaq import OpenAQ


APP = Flask(__name__)

API = OpenAQ()

@APP.route('/')
def root():
    """Base view."""
    status, body = API.cities()
    return render_template('aq_layout.html')

if __name__ == "__main__":
    
    APP.run(debug=True)