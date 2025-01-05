from .database import db
from .user import User
from .project import Project
from .task import Task

# Function to initialize tables if dey dont exist.
def init_db():
    User.create_table()
    Project.create_table()
    Task.create_table()
