# backend/controllers/user_datastore.py
from flask_security import SQLAlchemyUserDatastore
from controllers.models import User, Role
from controllers.database import db

# Create user datastore for Flask-Security-Too
user_datastore = SQLAlchemyUserDatastore(db, User, Role)