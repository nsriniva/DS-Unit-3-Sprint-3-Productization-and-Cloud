"""OpenAQ Air Quality Dashboard with Flask."""
from os import urandom
from flask import Flask, render_template, request
from openaq import OpenAQ
from flask_sqlalchemy import SQLAlchemy


CITY = 'Los Angeles'
COUNTRY = 'CL'
LATEST_MEASUREMENT = None

APP = Flask(__name__)
APP.secret_key = urandom(42)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
APP.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

DB = SQLAlchemy(APP)


API = OpenAQ()


class City(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    city = DB.Column(DB.String, nullable=False)
    country = DB.Column(DB.String)
    latest_measurement = DB.Column(DB.String)


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f'{self.datetime}:{self.value}'


def get_city_from_db():
    global CITY, COUNTRY, LATEST_MEASUREMENT

    try:
        print(City.__table__.exists())
    except Exception:
        DB.create_all()

    city = City.query.get(1)

    if city:
        COUNTRY = None
        LATEST_MEASUREMENT = None

        CITY = city.city
        if city.country:
            COUNTRY = city.country
        if city.latest_measurement:
            LATEST_MEASUREMENT = city.latest_measurement


def update_city_in_db():
    global CITY, COUNTRY, LATEST_MEASUREMENT

    city = City.query.get(1)

    if city:
        DB.session.delete(city)
        DB.session.commit()

    params = {'id': 1, 'city': CITY, 'country': COUNTRY}
    if COUNTRY:
        params['country'] = COUNTRY
    if LATEST_MEASUREMENT:
        params['latest_measurement'] = LATEST_MEASUREMENT

    city = City(**params)

    DB.session.add(city)
    DB.session.commit()


def get_results(data='pm25'):
    global LATEST_MEASUREMENT, CITY, COUNTRY

    params = {'city': CITY, 'parameter': data}
    if COUNTRY:
        params['country'] = COUNTRY
    if LATEST_MEASUREMENT:
        params['date_from'] = LATEST_MEASUREMENT

    _, _ret = API.measurements(**params)

    ret = [(elem['date']['utc'], elem['value']) for elem in _ret['results']]

    if len(ret):
        LATEST_MEASUREMENT = ret[0][0]
        update_city_in_db()

    return ret


def root():
    return str(Record.query.filter(Record.value >= 10).all())


def refresh():
    get_city_from_db()
    data = get_results()
    for elem in data:
        rec = Record(datetime=elem[0], value=elem[1])
        DB.session.add(rec)
    DB.session.commit()
    return 'Data refreshed!'


@APP.route('/')
def root_page():
    """Base view."""
    get_city_from_db()

    danger_list = Record.query.filter(Record.value >= 10).all()
    all_list = Record.query.all()

    page_params = {'CITY': CITY, 'COUNTRY': COUNTRY,
                   'danger_list': danger_list,
                   'data': 'PM25', 'num_risky': len(danger_list),
                   'num_all': len(all_list)}

    return render_template('aq_layout.html', **page_params)


@APP.route('/refresh', methods=["POST"])
def refresh_measure():

    refresh()

    return root_page()


@APP.route('/change', methods=["POST"])
def change():
    global CITY, COUNTRY, LATEST_MEASUREMENT

    def sanitize(cc):
        if cc is not None:
            cc = cc.strip()

            if len(cc) != 2 or not cc.isupper():
                cc = None
        return cc

    form_data = request.form

    CITY = form_data['city_name']
    COUNTRY = sanitize(form_data['country_code'])

    LATEST_MEASUREMENT = None

    DB.drop_all()
    DB.create_all()

    update_city_in_db()

    return refresh_measure()


if __name__ == "__main__":

    APP.run(debug=True)
