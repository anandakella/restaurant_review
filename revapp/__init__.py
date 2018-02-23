from flask import Flask, abort
import default_settings as settings
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()

__all__ = [app, db]

def create_app():
    app.config.from_object(settings)
    db.init_app(app)
    
    from .revapp import main
    app.register_blueprint(main, url_prefix='/api/v1')
    return app