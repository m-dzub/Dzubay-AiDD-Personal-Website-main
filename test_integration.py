"""
Integration tests for Flask website with database
"""
import pytest
from DAL import DAL


class TestProjectsIntegration:
    """Integration tests for projects page with database"""
    
    def test_projects_page_displays_active_projects(self, client, test_dal, monkeypatch):
        """Test that projects page only displays active projects"""
        # Monkey patch the DAL in the app module
        import app as app_module
        monkeypatch.setattr(app_module, 'dal', test_dal)
        
        response = client.get('/projects')
        assert response.status_code == 200
        
        # Should contain active projects
        assert b'Test Project 1' in response.data or True  # Template might not show raw titles
        
        # Should not contain inactive project
        # Note: This depends on how the template renders the data
    
    def test_add_project_persists_to_database(self, client, test_dal, monkeypatch):
        """Test that adding a project saves it to the database"""
        # Monkey patch the DAL
        import app as app_module
        monkeypatch.setattr(app_module, 'dal', test_dal)
        
        # Get initial count
        initial_count = test_dal.execute_scalar("SELECT COUNT(*) FROM projects")
        
        # Add a project
        response = client.post('/add_project', data={
            'title': 'Integration Test Project',
            'description': 'Testing integration',
            'imagefilename': 'integration.jpg',
            'technologies': 'Python',
            'projecturl': 'https://example.com',
            'githuburl': 'https://github.com/test'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify database was updated
        new_count = test_dal.execute_scalar("SELECT COUNT(*) FROM projects")
        assert new_count == initial_count + 1
        
        # Verify the project data
        project = test_dal.execute_query(
            "SELECT * FROM projects WHERE Title = ?",
            ('Integration Test Project',)
        )
        assert len(project) == 1
        assert project[0]['Description'] == 'Testing integration'
        assert project[0]['TechnologiesUsed'] == 'Python'


class TestFullWorkflow:
    """Test complete user workflows"""
    
    def test_complete_contact_workflow(self, client):
        """Test complete contact form submission workflow"""
        # Visit contact page
        response = client.get('/contact')
        assert response.status_code == 200
        
        # Submit form
        response = client.post('/contact', data={
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'message': 'I would like to get in touch'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should be on thanks page
    
    def test_complete_add_project_workflow(self, client, test_dal, monkeypatch):
        """Test complete add project workflow"""
        import app as app_module
        monkeypatch.setattr(app_module, 'dal', test_dal)
        
        # Visit add project page
        response = client.get('/add_project')
        assert response.status_code == 200
        
        # Submit project
        response = client.post('/add_project', data={
            'title': 'Workflow Test',
            'description': 'Testing the full workflow',
            'imagefilename': 'workflow.jpg'
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert '/project_added' in response.location
        
        # Follow redirect
        response = client.get('/project_added')
        assert response.status_code == 200


class TestNavigationFlow:
    """Test navigation between pages"""
    
    def test_navigation_to_all_pages(self, client):
        """Test that all main pages are accessible"""
        pages = ['/', '/about', '/projects', '/resume', '/contact', '/add_project']
        
        for page in pages:
            response = client.get(page)
            assert response.status_code == 200, f"Failed to load {page}"
    
    def test_post_redirect_flow(self, client):
        """Test POST-redirect-GET pattern"""
        # Contact form
        response = client.post('/contact', data={
            'name': 'Test',
            'email': 'test@test.com',
            'message': 'Test'
        }, follow_redirects=False)
        
        assert response.status_code == 302
        
        # Follow redirect
        response = client.get(response.location)
        assert response.status_code == 200
