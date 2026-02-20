import osmnx as ox
from flask import Flask
from .config import Config

def create_app():
    cache_dir = Config.DATA_DIR / "osmnx_cache"
    ox.settings.use_cache = True
    ox.settings.cache_folder = str(cache_dir)
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'j76B6jH1'
    
    from modules.views import views
    from modules.auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    return app
