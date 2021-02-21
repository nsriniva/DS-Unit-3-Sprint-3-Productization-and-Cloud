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

    _, _ret = API.measurements(**params)
    
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
    
    danger_list = Record.query.filter(value >= 10).all()
    all_list = Record.query.all()

    page_params = {'CITY':CITY, 'COUNTRY':COUNTRY, 'danger_list':danger_list, 'all_list':all_list}
    return render_template('aq_layout.html', **page_params)


@APP.route('/refresh')
def refresh():
    
    data = get_results()
    for elem in data:
        rec = Record(datetime=elem[0], value=elem[1])
        DB.session.add(rec)
    DB.session.commit()
    return root()

if __name__ == "__main__":
    
    APP.run(debug=True)