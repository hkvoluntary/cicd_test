import logging
import os
import sys
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://sql:sql@localhost/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Configure logging based on the FLASH_ENVIRONMENT variable
def configure_logging():
    environment = os.getenv('FLASH_ENVIRONMENT', 'production')  # Default to 'production'
    log_level = logging.DEBUG if environment in ['development', 'staging'] else logging.ERROR

    # Clear any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(level=log_level,
                        format='%(asctime)s [%(levelname)s] %(message)s')

    # Setup additional handlers
    if environment == 'development':
        logging.debug("Logging is set to DEBUG level for development.")
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(stream_handler)
    else:
        logging.error("Logging is set to ERROR level for production or staging.")
        file_handler = logging.FileHandler('app.log')
        file_handler.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)

# Load configuration and set up logging
configure_logging()
logging_level = logging.getLogger().getEffectiveLevel()
print("Effective logging level:", logging.getLevelName(logging_level))  # Debugging line

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

# Create the table
with app.app_context():
    db.create_all()

# Create a new user
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

# Read all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    app.logger.info("Retrieved all users")
    return jsonify([{'id': user.id, 'name': user.name, 'email': user.email, 'hkid': user.hkid} for user in users]), 200

# Get a user by ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    app.logger.info("Retrieved user: %s", user.name)
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email, 'hkid': user.hkid}), 200

# Update a user
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = User.query.get_or_404(user_id)

    app.logger.debug("Received data for user update: %s", data)

    if not User.is_valid_hkid(data['hkid']):
        app.logger.error("Invalid HKID format for input: %s", data)
        return jsonify({'error': 'Invalid HKID format.'}), 400

    user.name = data['name']
    user.email = data['email']
    user.hkid = data['hkid']
    db.session.commit()
    app.logger.info("User updated: %s", user.name)
    return jsonify({'message': 'User updated successfully!'}), 200

# Delete a user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    app.logger.info("User deleted: %s", user.name)
    return jsonify({'message': 'User deleted successfully!'}), 200

if __name__ == '__main__':
    app.run(debug=False)
