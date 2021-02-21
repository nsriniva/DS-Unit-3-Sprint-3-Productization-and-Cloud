"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask, render_template
from openaq import OpenAQ
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


CITY='Los Angeles'
COUNTRY='CL' 
LATEST_MEASUREMENT = None

APP = Flask(__name__)

API = OpenAQ()


APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)

def get_results(data='pm25'):
    global LATEST_MEASUREMENT

    params = {'city':CITY, 'country':COUNTRY, 'parameter':data}
    if LATEST_MEASUREMENT:
        params['date_from'] = LATEST_MEASUREMENT

    print(params)
    _, _ret = API.measurements(**params)
    
    print(len(_ret['results']))
    ret = [(elem['date']['utc'], elem['value']) for elem in _ret['results']]

    if len(ret):
        LATEST_MEASUREMENT = ret[0][0]

    return ret

class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.DateTime)
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f'<{datetime}>:<{value}>'

@APP.route('/')
def root():
    """Base view."""
    return render_template('aq_layout.html')


@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    # TODO Get data from OpenAQ, make Record objects with it, and add to db
    DB.session.commit()
    return 'Data refreshed!'

if __name__ == "__main__":
    
    APP.run(debug=True)