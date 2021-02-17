from flask import Blueprint, jsonify, request, render_template , flash, redirect
from .models import DB, User, Tweet
from .twitter import vectorize_tweet, predict_user
from os import getenv
from dotenv import load_dotenv
import tweepy  # Allows us to interact with Twitter

load_dotenv()

TWITTER_API_KEY = getenv("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = getenv("TWITTER_API_KEY_SECRET")

TWITTER_AUTH = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_KEY_SECRET)
TWITTER = tweepy.API(TWITTER_AUTH)




twitter_routes = Blueprint("twitter_routes", __name__)

@twitter_routes.route('/')
def default_route():
    return render_template('layout2.html')
    
@twitter_routes.route("/users")
def list_users():
    # SELECT * FROM users
    users = User.query.all()
    print(users)   

    return render_template("users2.html", message="Users and their 5 most recent tweets", users=users)

@twitter_routes.route("/users/new")
def new_user():
    return render_template("new_user.html")

@twitter_routes.route("/users/create", methods=["POST"])
def add_user():

    name=request.form['name']
    twitter_user = TWITTER.get_user(name)

    #If the user doesn't already exist add to the user table
    if user := User.query.get(twitter_user.id) is None:
        # create user based on the username passed into the function
        
        user = User(name=name, id = twitter_user.id)
        DB.session.add(user)
        DB.session.commit()
        flash(f"User {user.name} created successfully!", "success")

    
    return update_tweets()#redirect(f"/users")

@twitter_routes.route("/compare")
def compare_users():
    users = User.query.all()
    return render_template("predict.html", users=users)

@twitter_routes.route("/predict", methods=["POST"])
def user_prediction():

    users = {}
    print(request.form)
    users[0]=User.query.get(int(request.form['user1']))
    users[1]=User.query.get(int(request.form['user2']))

    print(users)

    tweet_text = request.form['tweet_text']

    predicted_user = predict_user(users[0], users[1], tweet_text)[0]

    print(predicted_user)
    
    return render_template('prediction.html', tweet_text=tweet_text, user=users[predicted_user])


@twitter_routes.route("/tweets/update", methods=["POST"])
def update_tweets():

    for user in User.query.all():
        try:
            twitter_user = TWITTER.get_user(user.name)

            tweets = twitter_user.timeline(
                count=200,
                exclude_replies=True,
                include_rts=False,
                tweet_mode="Extended",
                since_id=user.newest_tweet_id
            )  # A list of tweets from "username"

            # empty tweets list == false, full tweets list == true
            if tweets:
               # updates newest_tweet_id
                user.newest_tweet_id = tweets[0].id

            for tweet in tweets:
                # for each tweet we want to create an embedding
                vectorized_tweet = vectorize_tweet(tweet.text)
                # create tweet that will be added to our DB
                db_tweet = Tweet(id=tweet.id, text=tweet.text,
                                 vect=vectorized_tweet)
                # append each tweet from "username" to username.tweets
                user.tweets.append(db_tweet)
                # Add db_tweet to Tweet DB
                DB.session.add(db_tweet)
                flash(f"Tweet {db_tweet.text} added successfully!", "success")

        except Exception as e:
            print(f'Error processing {user.name}: {e}')
            raise e

        else:
            # commit everything to the database
            DB.session.commit()
    
    return redirect(f"/users")
