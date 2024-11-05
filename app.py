from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the base class for declarative models
Base = declarative_base()

# Define a simple User model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, age={self.age})>"

# MySQL connection string: 'mysql+mysqlconnector://<user>:<password>@<host>:<port>/<database>'
# Or you can use 'mysql+pymysql://<user>:<password>@<host>:<port>/<database>' with PyMySQL
DATABASE_URL = 'mysql+mysqlconnector://sql:sql1245@172.17.0.3/test_db'

# Create an engine to connect to MySQL
engine = create_engine(DATABASE_URL, echo=True)

# Create all tables in the database (if they don't exist)
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Insert new users
new_user1 = User(name='Alice', age=30)
new_user2 = User(name='Bob', age=25)

session.add(new_user1)
session.add(new_user2)

# Commit the transaction to save to the database
session.commit()

# Query the database to retrieve users
users = session.query(User).all()
for user in users:
    print(user)

# Clean up by closing the session
session.close()
