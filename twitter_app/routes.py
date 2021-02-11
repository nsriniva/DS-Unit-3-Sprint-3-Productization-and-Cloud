from flask import Blueprint, jsonify, request, render_template , flash, redirect
from .models import DB, User, Tweet

twitter_routes = Blueprint("twitter_routes", __name__)

@twitter_routes.route('/')
def default_route():
    return render_template('layout.html')
    
@twitter_routes.route("/users")
def list_users():
    # SELECT * FROM users
    users = User.query.all()
    print(users)   

    return render_template("users.html", message="Here's some users", users=users)

@twitter_routes.route("/users/new")
def new_user():
    return render_template("new_user.html")

@twitter_routes.route("/users/create", methods=["POST"])
def create_user():
    users = User.query.all()
    print(users)
    print("FORM DATA:", dict(request.form))
    # todo: store in database
    # INSERT INTO users ...
    name=request.form['name']
    #If the user doesn't already exist add to the user table
    if User.query.filter(User.name==name).first() is None:
        new_user = User(name=name, id = len(users)+1)
        DB.session.add(new_user)
        DB.session.commit()
        flash(f"User {new_user.name} created successfully!", "success")
    
    return redirect(f"/users")



@twitter_routes.route("/tweets")
def list_tweets():
    # SELECT * FROM tweets
    tweets = Tweet.query.all()
    print(tweets)   

    return render_template("tweets.html", message="Here's some tweets", tweets=tweets)

@twitter_routes.route("/tweets/new")
def new_tweet():
    return render_template("new_tweet.html")

@twitter_routes.route("/tweets/create", methods=["POST"])
def create_tweet():
    tweets = Tweet.query.all()
    print(tweets)
    print("FORM DATA:", dict(request.form))
    # todo: store in database
    # INSERT INTO users ...
    name=request.form['name']
    tweet = request.form['tweet']
    #If the user doesn't already exist add to the user table
    if User.query.filter(User.name==name).first() is None:
        users = User.query.all()
        new_user = User(name=name, id = len(users)+1)
        DB.session.add(new_user)
        DB.session.commit()

    user = User.query.filter(User.name==name).first()

    new_tweet = Tweet(id = len(tweets)+1, text=tweet, user_id=user.id, vect='123')
    DB.session.add(new_tweet)
    DB.session.commit()
    
    flash(f"Tweet {new_tweet.text} added successfully!", "success")
    return redirect(f"/tweets")
