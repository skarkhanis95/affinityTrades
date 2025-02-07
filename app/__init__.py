from flask import Flask, redirect
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Setup logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('App startup')

    # Register Blueprints
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.profile_info import profile_bp
    from .routes.wallets import wallets_bp
    from .routes.funds import funds_bp
    from .routes.team import team_bp
    from .routes.pamm import pamm_bp
    from .routes.register import register_bp
    from .routes.manager import manager_bp
    from .routes.transactions import transactions_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(wallets_bp)
    app.register_blueprint(funds_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(pamm_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(manager_bp)
    app.register_blueprint(transactions_bp)
    # Default Routes
    @app.route('/')
    def home():
        return redirect('/auth/login')

    @app.template_filter('format_date')
    def format_date(value):
        if not value:
            return "-"
        date_obj = datetime.strptime(value, "%Y-%m-%d")
        return date_obj.strftime("%b %d, %Y")

    return app
