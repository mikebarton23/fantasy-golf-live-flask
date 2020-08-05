from flaskapp import db, login_manager, create_app
from flask import current_app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import pandas as pd
from flaskapp.models import User, Team, Post, DraftedPlayer, AvailablePlayer
import os
from flaskapp import create_app
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from flask_sqlalchemy import SQLAlchemy

os.chdir(r'C:\Users\barto\OneDrive\Desktop\Python\flaskapp\flaskapp')
app = create_app()
app.app_context().push()

migrate = Migrate(app,db)
manager = Manager(app)

manager.add_command('db',MigrateCommand)

if __name__ == '__main__':
    manager.run()
