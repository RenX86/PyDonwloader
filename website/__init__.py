from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'This is a secret'

    from .routes import links 
    app.register_blueprint(links, url_prefix='/')    
    return app