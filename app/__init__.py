from flask import Flask
from flask_mysql_connector import MySQL
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from flask import session
from authlib.integrations.flask_client import OAuth
import os
from config import CLOUDINARY_API_KEY, CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_SECRET, SECRET_KEY, DB_HOST,DB_NAME, DB_PASSWORD, DB_USERNAME,DB_PORT
import cloudinary
from cloudinary.utils import cloudinary_url

mysql = MySQL()
oauth = OAuth()
bootstrap = Bootstrap()  # Initialize Bootstrap extension
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,
        MYSQL_USER=DB_USERNAME,
        MYSQL_PASSWORD=DB_PASSWORD,
        MYSQL_DATABASE=DB_NAME,
        MYSQL_HOST=DB_HOST,
        MYSQL_PORT=DB_PORT
    )

    mysql.init_app(app)
    oauth.init_app(app, fetch_token=lambda: session.get('token'))
    google = oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_params=None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        access_params=None,
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        userinfo_endpoint='https://www.googleapis.com/oauth2/v1/userinfo',
        client_kwargs={'scope': 'openid email profile'},
        client_id_issuer='http://accounts.google.com',
        client_id_realm=None,
        jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
        client_id_public_key=None
    )
    
    bootstrap.init_app(app)  # Initialize Bootstrap extension
    csrf.__init__(app)
    #cors.init_app(app,resources={r"/update_click_count/*": {"origins": "http://127.0.0.1:5000"}})

    cloudinary.config(cloud_name=CLOUDINARY_CLOUD_NAME,
                    api_key=CLOUDINARY_API_KEY,
                    api_secret=CLOUDINARY_API_SECRET
                    )
    

    from .routes.signin.signinroute import signinroute
    app.register_blueprint(signinroute, url_prefix="/")

    from .routes.signup.signuproute import signuproute
    app.register_blueprint(signuproute, url_prefix="/")

    from app.routes.events_feed.controller import bp_events
    app.register_blueprint(bp_events)

    from .routes.user_profile.controller import user_profile_blueprint
    app.register_blueprint(user_profile_blueprint)

    from .routes.research_feed.controller import research_blueprint
    app.register_blueprint(research_blueprint)

    from .routes.admin.signin.admin_routes import adminroute
    app.register_blueprint(adminroute, url_prefix="/")
    
    from .routes.search.controller import search_blueprint
    app.register_blueprint(search_blueprint)
    

    return app