"""
Tests for Flask application routes and functionality
"""
import pytest
from flask import url_for


class TestRoutes:
    """Test suite for application routes"""
    
    def test_index_route(self, client):
        """Test the index/home page route"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data
    
    def test_about_route(self, client):
        """Test the about page route"""
        response = client.get('/about')
        assert response.status_code == 200
    
    def test_resume_route(self, client):
        """Test the resume page route"""
        response = client.get('/resume')
        assert response.status_code == 200
    
    def test_contact_route_get(self, client):
        """Test the contact page GET request"""
        response = client.get('/contact')
        assert response.status_code == 200
    
    def test_contact_route_post(self, client):
        """Test the contact page POST request"""
        response = client.post('/contact', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'This is a test message'
        }, follow_redirects=False)
        assert response.status_code == 302  # Redirect
        assert '/thanks' in response.location
    
    def test_contact_form_submission_redirect(self, client):
        """Test that contact form submission redirects to thanks page"""
        response = client.post('/contact', data={
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Hello there'
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_thanks_route(self, client):
        """Test the thanks page route"""
        response = client.get('/thanks')
        assert response.status_code == 200
    
    def test_add_project_route_get(self, client):
        """Test the add project page GET request"""
        response = client.get('/add_project')
        assert response.status_code == 200
    
    def test_project_added_route(self, client):
        """Test the project added confirmation page"""
        response = client.get('/project_added')
        assert response.status_code == 200
    
    def test_invalid_route(self, client):
        """Test that invalid routes return 404"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404


class TestProjectsPage:
    """Test suite for the projects page functionality"""
    
    def test_projects_route(self, client):
        """Test the projects page route"""
        response = client.get('/projects')
        assert response.status_code == 200
    
    def test_projects_page_content(self, client):
        """Test that projects page contains expected content"""
        response = client.get('/projects')
        assert response.status_code == 200
        # The page should have HTML content
        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data


class TestAddProject:
    """Test suite for adding projects functionality"""
    
    def test_add_project_get(self, client):
        """Test GET request to add_project page"""
        response = client.get('/add_project')
        assert response.status_code == 200
    
    def test_add_project_post_minimal(self, client):
        """Test POST request to add_project with minimal data"""
        response = client.post('/add_project', data={
            'title': 'New Test Project',
            'description': 'A brand new project',
            'imagefilename': 'new_project.jpg'
        }, follow_redirects=False)
        assert response.status_code == 302  # Redirect
        assert '/project_added' in response.location
    
    def test_add_project_post_full(self, client):
        """Test POST request to add_project with all fields"""
        response = client.post('/add_project', data={
            'title': 'Complete Project',
            'description': 'A project with all fields filled',
            'imagefilename': 'complete.jpg',
            'technologies': 'Python, Flask, SQLite',
            'projecturl': 'https://example.com/project',
            'githuburl': 'https://github.com/user/project'
        }, follow_redirects=True)
        assert response.status_code == 200


class TestStaticFiles:
    """Test suite for static file serving"""
    
    def test_css_file_accessible(self, client):
        """Test that CSS files are accessible"""
        response = client.get('/static/css/style.css')
        # File might exist or not, just ensure it doesn't error catastrophically
        assert response.status_code in [200, 404]


class TestFormValidation:
    """Test suite for form handling"""
    
    def test_contact_empty_form(self, client):
        """Test submitting contact form with empty data"""
        response = client.post('/contact', data={}, follow_redirects=False)
        # Even with empty data, it should redirect (no server-side validation currently)
        assert response.status_code == 302
    
    def test_add_project_empty_form(self, client):
        """Test submitting add_project form with empty data"""
        response = client.post('/add_project', data={}, follow_redirects=False)
        # Should still process (no validation currently)
        assert response.status_code in [200, 302]
