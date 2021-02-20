"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask

APP = Flask(__name__)

print(APP)

@APP.route('/')
def root():
    """Base view."""
    return 'TODO - part 2 and beyond!'

if __name__ == "__main__":
    
    APP.run(debug=True)