from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Initialize Flask app
app = Flask(__name__)

# Define the base class for declarative models
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, age={self.age})>"

# MySQL connection string (adjust with your actual credentials)
#DATABASE_URL = 'mysql+mysqlconnector://test_user:password@localhost/test_db'
DATABASE_URL = 'mysql+mysqlconnector://sql:sql1245@172.17.0.3/test_db'

# Create an engine to connect to MySQL
engine = create_engine(DATABASE_URL, echo=True)

# Create all tables in the database (if they don't exist)
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)

# ============================
# Flask Routes for CRUD
# ============================

# CREATE: Add a new user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if 'name' not in data or 'age' not in data:
        return jsonify({"error": "Missing required fields: name, age"}), 400

    name = data['name']
    age = data['age']

    session = Session()
    new_user = User(name=name, age=age)
    session.add(new_user)
    session.commit()
    session.close()

    return jsonify({"message": f"User {name} created successfully!"}), 201

# READ: Get all users
@app.route('/users', methods=['GET'])
def get_all_users():
    session = Session()
    users = session.query(User).all()
    session.close()

    # Convert users to a list of dicts for JSON response
    users_list = [{"id": user.id, "name": user.name, "age": user.age} for user in users]

    return jsonify(users_list), 200

# READ: Get a user by ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"id": user.id, "name": user.name, "age": user.age}), 200

# UPDATE: Update an existing user
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()

    name = data.get('name')
    age = data.get('age')

    session = Session()
    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        session.close()
        return jsonify({"error": "User not found"}), 404

    if name:
        user.name = name
    if age is not None:
        user.age = age

    session.commit()
    session.close()

    return jsonify({"message": f"User {user_id} updated successfully!"}), 200

# DELETE: Delete a user by ID
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        session.close()
        return jsonify({"error": "User not found"}), 404

    session.delete(user)
    session.commit()
    session.close()

    return jsonify({"message": f"User {user_id} deleted successfully!"}), 200

# ============================
# Run Flask Application
# ============================
if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
