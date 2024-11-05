import argparse
import logging
import sys
import json
import re
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask app
app = Flask(__name__)

# Load the configuration from config.json based on the environment
def load_config(environment):
    with open('config.json') as f:
        config = json.load(f)

    # Get the environment-specific config, fallback to 'development' if not found
    if environment:
        config = config.get(environment, config.get('development'))

    return config

# Configure logging based on the environment
def configure_logging(config):
    environment = config.get('environment', 'development')
    
    if environment == 'development':
        log_level = logging.DEBUG
    elif environment == 'staging':
        log_level = logging.DEBUG
    else:  # For 'production'
        log_level = logging.ERROR

    # Clear any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Set the logging basic configuration
    logging.basicConfig(level=log_level, format='%(asctime)s [%(levelname)s] %(message)s')

    # Add the correct handlers based on the environment
    for handler_config in config['logging']['handlers']:
        if handler_config['type'] == 'StreamHandler':
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setLevel(handler_config['level'])
            logging.getLogger().addHandler(stream_handler)
        elif handler_config['type'] == 'FileHandler':
            file_handler = logging.FileHandler(handler_config['filename'])
            file_handler.setLevel(handler_config['level'])
            formatter = logging.Formatter(handler_config['format'])
            file_handler.setFormatter(formatter)
            logging.getLogger().addHandler(file_handler)

# Set up command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Start Flask app with a specific environment.")
    parser.add_argument(
        '--env', 
        choices=['development', 'staging', 'production'], 
        default=None,
        help="Specify the environment: development, staging, or production."
    )
    return parser.parse_args()

# Initialize the database
def initialize_database(app, config):
    # Get the database configuration for the selected environment
    db_config = config.get('database', {})

    # Set SQLAlchemy database URI and other settings
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['name']}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database
    db = SQLAlchemy(app)
    return db

# Initialize app and load config
args = parse_args()  # Parse the command-line arguments
config = load_config(args.env)  # Load config with overridden environment if specified
configure_logging(config)  # Set up logging based on the config

# Initialize the database connection from config
db = initialize_database(app, config)

# Define the User model with an HKID field
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    hkid = db.Column(db.String(10), unique=True, nullable=False)

    @staticmethod
    def is_valid_hkid(hkid):
        pattern = r'^[A-Z]{1,2}[0-9]{6}\([0-9A]\)$'
        return bool(re.match(pattern, hkid))

# Create the table (for testing purposes)
with app.app_context():
    db.create_all()

# Define the routes (Example)
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    app.logger.debug("Received data for user creation: %s", data)
    
    if not User.is_valid_hkid(data['hkid']):
        app.logger.error("Invalid HKID format for input: %s", data)
        return jsonify({'error': 'Invalid HKID format.'}), 400

    new_user = User(name=data['name'], email=data['email'], hkid=data['hkid'])
    app.logger.info("Attempting to add user: %s", new_user.name)
    db.session.add(new_user)
    
    try:
        db.session.commit()
        app.logger.debug("User created successfully: %s", new_user.name)
    except Exception as e:
        app.logger.error("Error creating user: %s", e)
        db.session.rollback()
        return jsonify({'error': 'User creation failed.'}), 500

    app.logger.info("User created: %s", new_user.name)
    return jsonify({'message': 'User created successfully!'}), 201

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=False)
