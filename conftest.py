"""
Pytest configuration and fixtures for Flask website tests
"""
import os
import pytest
import tempfile
from app import app as flask_app
from DAL import DAL


@pytest.fixture
def app():
    """Create and configure a test Flask application instance."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure the app for testing
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': db_path,
    })
    
    # Initialize test database
    dal = DAL(db_path)
    create_test_database(dal)
    
    yield flask_app
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the Flask application."""
    return app.test_cli_runner()


@pytest.fixture
def test_dal():
    """Create a test DAL instance with a temporary database."""
    db_fd, db_path = tempfile.mkstemp()
    dal = DAL(db_path)
    create_test_database(dal)
    
    yield dal
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


def create_test_database(dal):
    """Create the projects table and insert test data."""
    # Create projects table
    dal.create_table(
        'projects',
        '''
        ProjectID INTEGER PRIMARY KEY AUTOINCREMENT,
        Title TEXT NOT NULL,
        Description TEXT,
        ImageFileName TEXT,
        TechnologiesUsed TEXT,
        ProjectURL TEXT,
        GitHubURL TEXT,
        DateCreated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        IsActive INTEGER DEFAULT 1
        '''
    )
    
    # Insert test data
    test_projects = [
        {
            'Title': 'Test Project 1',
            'Description': 'This is a test project',
            'ImageFileName': 'test1.jpg',
            'TechnologiesUsed': 'Python, Flask',
            'ProjectURL': 'https://example.com/project1',
            'GitHubURL': 'https://github.com/user/project1',
            'IsActive': 1
        },
        {
            'Title': 'Test Project 2',
            'Description': 'Another test project',
            'ImageFileName': 'test2.jpg',
            'TechnologiesUsed': 'JavaScript, React',
            'ProjectURL': 'https://example.com/project2',
            'GitHubURL': 'https://github.com/user/project2',
            'IsActive': 1
        },
        {
            'Title': 'Inactive Project',
            'Description': 'This project is inactive',
            'ImageFileName': 'test3.jpg',
            'TechnologiesUsed': 'Java',
            'ProjectURL': '',
            'GitHubURL': '',
            'IsActive': 0
        }
    ]
    
    for project in test_projects:
        dal.insert('projects', project)
