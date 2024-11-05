import json
import os
import logging
from flask import Flask, jsonify

# Initialize Flask app
app = Flask(__name__)

# Load configuration from config.json
def load_config():
    config_file_path = 'config.json'
    if not os.path.exists(config_file_path):
        raise FileNotFoundError(f"{config_file_path} not found.")
    
    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)
    
    # Set the Flask app configurations from JSON
    app.config['FLASK_ENV'] = config.get('FLASK_ENV', 'production')
    app.config['DEBUG'] = config.get('DEBUG', False)
    
    # Set up database credentials and host from the config file
    db_user = config.get('DATABASE_USER', 'default_user')
    db_password = config.get('DATABASE_PASSWORD', 'default_password')
    db_name = config.get('DATABASE_NAME', 'default_db')
    db_host = config.get('DATABASE_HOST', 'localhost')  # Default to localhost if not provided
    
    # Construct the database URI (assuming PostgreSQL, modify for other DBs as needed)
    #app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}/{db_name}'
    
    # Setup logging from config.json
    log_config = config.get('LOGGING', {})
    log_level = log_config.get('LEVEL', 'DEBUG').upper()
    log_format = log_config.get('FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_filename = log_config.get('FILENAME', 'app.log')

    logging.basicConfig(level=log_level, format=log_format, filename=log_filename)
    
    return config

# Load the config at app startup
config = load_config()

@app.route('/')
def home():
    # Simple route to test the app
    app.logger.info("Home route accessed")
    return jsonify({
        'message': 'Welcome to the Flask app!',
        'flask_env': app.config['FLASK_ENV'],
        'database_uri': app.config['SQLALCHEMY_DATABASE_URI']
    })

@app.route('/config')
def get_config():
    # Route to view the loaded config settings
    app.logger.debug("Config route accessed")
    return jsonify({
        'FLASK_APP': app.config['FLASK_APP'],
        'FLASK_ENV': app.config['FLASK_ENV'],
        'DATABASE_URI': app.config['SQLALCHEMY_DATABASE_URI'],
        'DEBUG': app.config['DEBUG']
    })

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
