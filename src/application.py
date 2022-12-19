from flask import Flask, Response, request, redirect, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests
from datetime import datetime
import json
import rest_utils
from user_resource import UserResource, User
from flask_cors import CORS, cross_origin

import os

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Create the Flask application object.
app = Flask(__name__,
            static_url_path='/',
            static_folder='static/class-ui/',
            template_folder='web/templates')

CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

@app.route("/")
@cross_origin()
def index():
    if current_user.is_authenticated:
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email
            )
        )
    else:
        return '<a class="button" href="/login">Google Login</a>'

@login_manager.user_loader
def load_user(userId):
    return UserResource.getUserSSO(userId)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/login", methods=["GET"])
@cross_origin()
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Getting request args
    print(request)
    print(request.base_url)
    print(request.args)
    print(request.args.get("domain"))
    print("Done...")

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    print(request_uri)
    msg = {
        "request_uri": request_uri,
    }
    result = Response(json.dumps(msg), status=200, content_type="application/json")
    # Send user back to homepage
    return result
@app.before_request
def before_request_func():
    if not current_user.is_authenticated and request.endpoint != 'login' and request.endpoint != "callback" and request.endpoint != "logout" and request.endpoint != "index":
        print("User not logged in")
        return redirect(url_for("index"))

@app.route("/login/callback", methods=["GET"])
@cross_origin()
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    user = User(id_=unique_id, name=users_name, email=users_email)
    # Begin user session by logging the user in
    login_user(user)
    UserResource.addUserSSO(user)
    msg = {
        "userID": user.id,
        "email": user.email,
        "name": user.name
    }
    result = Response(json.dumps(msg), status=200, content_type="application/json")
    # Send user back to homepage
    return result

@app.route("/logout")
@cross_origin()
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.get("/api/health")
@cross_origin()
def get_health():
    t = str(datetime.now())
    msg = {
        "name": "User Microservice",
        "health": "Good",
        "at time": t
    }

    # DFF TODO Explain status codes, content type, ... ...
    result = Response(json.dumps(msg), status=200, content_type="application/json")

    return result



@app.route("/api/user", methods=["POST"])
@cross_origin()
def addUser():
    request_inputs = rest_utils.RESTContext(request)
    data = request_inputs.data
    res = UserResource.addUser(data)

    rsp = Response("CREATED User " + str(res), status=201, content_type="text/plain")

    return rsp

@app.route("/api/user/<userId>", methods=["GET"])
@cross_origin()
def getUser(userId):
    res = UserResource.getUser(userId)

    rsp = Response(json.dumps(res), status=200, content_type="text/plain")

    return rsp

@app.route("/api/users", methods=["GET"])
@cross_origin()
def getUsers():
    res = UserResource.getUsers()

    rsp = Response(json.dumps(res), status=200, content_type="text/plain")

    return rsp

@app.route("/api/user/<userId>", methods=["PUT"])
@cross_origin()
def updateUser(userId):
    request_inputs = rest_utils.RESTContext(request)

    res = UserResource.updatePlaylist(userId, new_values=request_inputs.data)
    rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")

    return rsp

@app.route("/api/user/<userId>", methods=["DELETE"])
@cross_origin()
def deleteUser(userId):
    request_inputs = rest_utils.RESTContext(request)

    res = UserResource.DeleteUser(userId)
    rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")

    return rsp

if __name__ == "__main__":
    context = ('local.crt', 'local.key')#certificate and key files
    app.run(host="0.0.0.0", port="5011", ssl_context=context)
