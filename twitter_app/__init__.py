import os
from flask import Flask
from dotenv import load_dotenv
from .models import DB, MIGRATE, User, Tweet
from .routes import twitter_routes
load_dotenv()

DB_FILE = os.getenv("DB_FILE")

DB_FILEPATH = os.path.join(os.path.dirname(__file__), DB_FILE)

DB_URI = f'sqlite:////{DB_FILEPATH}'

print(DB_URI)
 # using absolute filepath on Mac (recommended)

def create_app():
    app = Flask(__name__)

    app.secret_key = os.urandom(42)

    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    DB.init_app(app)
    MIGRATE.init_app(app, DB)

    app.register_blueprint(twitter_routes)    
    return app

if __name__ == "__main__":

    my_app = create_app()
    my_app.run(debug=True)

    new_user = User(name='user1')
