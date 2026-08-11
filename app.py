import os
from flask import Flask, render_template
from config import Config
from models.db import init_db
from routes.auth import auth_bp
from routes.user import user_bp
from routes.booking import booking_bp
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.url_map.strict_slashes = False

    # Initialize Database Schema & Seed Data
    with app.app_context():
        try:
            init_db()
            print("Database initialized successfully.")
        except Exception as e:
            print(f"Database initialization warning/notice: {str(e)}")

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(admin_bp)

    # Favicon Route
    @app.route('/favicon.ico')
    def favicon():
        return app.send_static_file('images/favicon.svg')

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
