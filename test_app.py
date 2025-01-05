from contextlib import contextmanager

import pytest
import os
from app import app
from cs50 import SQL
from flask_session import Session

TEST_DB_PATH = "test.db"
app.config.update({
    'TESTING': True,
    'WTF_CSRF_ENABLED': False,
    'SECRET_KEY': 'test_key',
    'SESSION_TYPE': 'filesystem'
})
Session(app)


@pytest.fixture(scope='function')
def setup_database():
    # Create a database file if it doesn't exist
    if not os.path.exists(TEST_DB_PATH):
        open(TEST_DB_PATH, 'a').close()

    db = SQL(f"sqlite:///{TEST_DB_PATH}")

    # Create fresh tables
    db.execute("DROP TABLE IF EXISTS tasks")
    db.execute("DROP TABLE IF EXISTS projects")
    db.execute("DROP TABLE IF EXISTS users")

    db.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            hash TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            detailed_description TEXT,
            status TEXT DEFAULT 'to do',
            priority TEXT DEFAULT 'medium',
            deadline DATETIME,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    db.execute("""
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            detailed_description TEXT,
            status TEXT DEFAULT 'to do',
            priority TEXT DEFAULT 'medium',
            deadline DATETIME,
            project_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    yield db


@pytest.fixture
def client():
    return app.test_client()


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    from flask import template_rendered
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


def test_register(client, setup_database):
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)

    users = setup_database.execute("SELECT * FROM users WHERE username = 'testuser'")
    assert len(users) == 1
    assert users[0]['email'] == 'test@example.com'


def test_login(client, setup_database):
    # Register first
    client.post('/register', data={
        'username': 'logintest',
        'email': 'login@test.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })

    with client.session_transaction() as sess:
        response = client.post('/login', data={
            'username': 'logintest',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200


def test_profile(client, setup_database):
    # Register user
    client.post('/register', data={
        'username': 'profiletest',
        'email': 'profile@test.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })

    # Login
    response = client.post('/login', data={
        'username': 'profiletest',
        'password': 'password123'
    }, follow_redirects=True)

    # Update profile
    response = client.post('/profile', data={
        'username': 'profiletest',
        'email': 'profile@test.com',
        'password': 'newpassword123',
        'confirm_password': 'newpassword123'
    }, follow_redirects=True)

    assert response.status_code == 200


def test_projects(client, setup_database):
    # Register and login
    client.post('/register', data={
        'username': 'projecttest',
        'email': 'project@test.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    client.post('/login', data={
        'username': 'projecttest',
        'password': 'password123'
    })

    response = client.post('/add_project', data={
        'title': 'Test Project',
        'description': 'Test Description',
        'status': 'to do'
    }, follow_redirects=True)

    projects = setup_database.execute("SELECT * FROM projects WHERE title = 'Test Project'")
    assert len(projects) == 1


def test_tasks(client, setup_database):
    # Register and login
    client.post('/register', data={
        'username': 'tasktest',
        'email': 'task@test.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    client.post('/login', data={
        'username': 'tasktest',
        'password': 'password123'
    })

    response = client.post('/add_task', data={
        'title': 'Test Task',
        'description': 'Test Description',
        'status': 'to do'
    }, follow_redirects=True)

    tasks = setup_database.execute("SELECT * FROM tasks WHERE title = 'Test Task'")
    assert len(tasks) == 1


if __name__ == '__main__':
    pytest.main()