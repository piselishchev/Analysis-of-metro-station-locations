from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'j76B6jH1'
    
    from .modules.flask.views import views
    from .modules.flask.citymap import citymap

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(citymap, url_prefix='/')
    
    return app
