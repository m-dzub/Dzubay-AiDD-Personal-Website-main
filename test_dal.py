"""
Tests for the Data Access Layer (DAL)
"""
import pytest
import sqlite3
import os
import tempfile
from DAL import DAL


class TestDALBasicOperations:
    """Test suite for basic DAL operations"""
    
    def test_dal_initialization(self, test_dal):
        """Test that DAL initializes correctly"""
        assert test_dal is not None
        assert test_dal.db_path is not None
    
    def test_get_connection(self, test_dal):
        """Test that get_connection returns a valid connection"""
        conn = test_dal.get_connection()
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        conn.close()
    
    def test_connection_row_factory(self, test_dal):
        """Test that connections use Row factory"""
        conn = test_dal.get_connection()
        assert conn.row_factory == sqlite3.Row
        conn.close()


class TestDALQueries:
    """Test suite for DAL query operations"""
    
    def test_execute_query(self, test_dal):
        """Test executing a SELECT query"""
        results = test_dal.execute_query("SELECT * FROM projects WHERE IsActive = 1")
        assert isinstance(results, list)
        assert len(results) == 2  # Two active projects from test data
    
    def test_execute_query_with_params(self, test_dal):
        """Test executing a query with parameters"""
        results = test_dal.execute_query(
            "SELECT * FROM projects WHERE Title = ?",
            ('Test Project 1',)
        )
        assert len(results) == 1
        assert results[0]['Title'] == 'Test Project 1'
    
    def test_execute_scalar(self, test_dal):
        """Test executing a scalar query"""
        count = test_dal.execute_scalar("SELECT COUNT(*) FROM projects")
        assert count == 3  # Total projects in test data
    
    def test_execute_scalar_no_result(self, test_dal):
        """Test executing a scalar query with no results"""
        result = test_dal.execute_scalar("SELECT Title FROM projects WHERE ProjectID = 9999")
        assert result is None


class TestDALInsert:
    """Test suite for DAL insert operations"""
    
    def test_insert_project(self, test_dal):
        """Test inserting a new project"""
        project_data = {
            'Title': 'Brand New Project',
            'Description': 'Testing insert functionality',
            'ImageFileName': 'brand_new.jpg',
            'TechnologiesUsed': 'Python, Pytest',
            'ProjectURL': 'https://example.com',
            'GitHubURL': 'https://github.com/test',
            'IsActive': 1
        }
        
        project_id = test_dal.insert('projects', project_data)
        assert project_id > 0
        
        # Verify the insert
        result = test_dal.select_by_id('projects', project_id, 'ProjectID')
        assert result is not None
        assert result['Title'] == 'Brand New Project'
    
    def test_insert_minimal_data(self, test_dal):
        """Test inserting with minimal required data"""
        project_data = {
            'Title': 'Minimal Project',
            'IsActive': 1
        }
        
        project_id = test_dal.insert('projects', project_data)
        assert project_id > 0


class TestDALUpdate:
    """Test suite for DAL update operations"""
    
    def test_update_project(self, test_dal):
        """Test updating a project"""
        # First, get an existing project
        projects = test_dal.execute_query("SELECT * FROM projects WHERE Title = ?", ('Test Project 1',))
        project_id = projects[0]['ProjectID']
        
        # Update it
        update_data = {'Description': 'Updated description'}
        rows_affected = test_dal.update('projects', update_data, 'ProjectID = ?', (project_id,))
        assert rows_affected == 1
        
        # Verify the update
        result = test_dal.select_by_id('projects', project_id, 'ProjectID')
        assert result['Description'] == 'Updated description'
    
    def test_update_multiple_fields(self, test_dal):
        """Test updating multiple fields at once"""
        projects = test_dal.execute_query("SELECT * FROM projects LIMIT 1")
        project_id = projects[0]['ProjectID']
        
        update_data = {
            'Title': 'Updated Title',
            'TechnologiesUsed': 'New Tech Stack',
            'IsActive': 0
        }
        
        rows_affected = test_dal.update('projects', update_data, 'ProjectID = ?', (project_id,))
        assert rows_affected == 1
        
        # Verify
        result = test_dal.select_by_id('projects', project_id, 'ProjectID')
        assert result['Title'] == 'Updated Title'
        assert result['TechnologiesUsed'] == 'New Tech Stack'
        assert result['IsActive'] == 0


class TestDALDelete:
    """Test suite for DAL delete operations"""
    
    def test_delete_project(self, test_dal):
        """Test deleting a project"""
        # Get initial count
        initial_count = test_dal.execute_scalar("SELECT COUNT(*) FROM projects")
        
        # Delete a project
        rows_affected = test_dal.delete('projects', 'Title = ?', ('Test Project 1',))
        assert rows_affected == 1
        
        # Verify count decreased
        new_count = test_dal.execute_scalar("SELECT COUNT(*) FROM projects")
        assert new_count == initial_count - 1
    
    def test_delete_multiple(self, test_dal):
        """Test deleting multiple projects"""
        rows_affected = test_dal.delete('projects', 'IsActive = ?', (1,))
        assert rows_affected == 2  # Two active projects in test data


class TestDALSelect:
    """Test suite for DAL select operations"""
    
    def test_select_all(self, test_dal):
        """Test selecting all projects"""
        results = test_dal.select_all('projects')
        assert len(results) == 3
    
    def test_select_all_with_order(self, test_dal):
        """Test selecting all projects with ordering"""
        results = test_dal.select_all('projects', 'Title ASC')
        assert len(results) == 3
        # Verify ordering (alphabetically)
        assert results[0]['Title'] == 'Inactive Project'
    
    def test_select_by_id(self, test_dal):
        """Test selecting a project by ID"""
        # Get an ID first
        all_projects = test_dal.select_all('projects')
        project_id = all_projects[0]['ProjectID']
        
        # Select by ID
        result = test_dal.select_by_id('projects', project_id, 'ProjectID')
        assert result is not None
        assert result['ProjectID'] == project_id
    
    def test_select_by_id_not_found(self, test_dal):
        """Test selecting a non-existent project"""
        result = test_dal.select_by_id('projects', 99999, 'ProjectID')
        assert result is None


class TestDALTableOperations:
    """Test suite for DAL table operations"""
    
    def test_create_table(self):
        """Test creating a new table"""
        db_fd, db_path = tempfile.mkstemp()
        dal = DAL(db_path)
        
        dal.create_table('test_table', 'id INTEGER PRIMARY KEY, name TEXT')
        
        # Verify table exists
        result = dal.execute_scalar(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'"
        )
        assert result == 'test_table'
        
        # Cleanup
        os.close(db_fd)
        os.unlink(db_path)
    
    def test_drop_table(self, test_dal):
        """Test dropping a table"""
        # Create a temporary table
        test_dal.create_table('temp_table', 'id INTEGER PRIMARY KEY')
        
        # Drop it
        test_dal.drop_table('temp_table')
        
        # Verify it's gone
        result = test_dal.execute_scalar(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='temp_table'"
        )
        assert result is None


class TestDALExecuteMany:
    """Test suite for DAL execute_many operation"""
    
    def test_execute_many(self, test_dal):
        """Test executing multiple inserts at once"""
        query = "INSERT INTO projects (Title, Description, IsActive) VALUES (?, ?, ?)"
        params_list = [
            ('Batch Project 1', 'First batch', 1),
            ('Batch Project 2', 'Second batch', 1),
            ('Batch Project 3', 'Third batch', 0)
        ]
        
        rows_affected = test_dal.execute_many(query, params_list)
        assert rows_affected == 3
        
        # Verify the inserts
        results = test_dal.execute_query("SELECT * FROM projects WHERE Title LIKE 'Batch%'")
        assert len(results) == 3


class TestDALErrorHandling:
    """Test suite for DAL error handling"""
    
    def test_invalid_table_name(self, test_dal):
        """Test querying a non-existent table"""
        with pytest.raises(sqlite3.OperationalError):
            test_dal.execute_query("SELECT * FROM nonexistent_table")
    
    def test_invalid_sql_syntax(self, test_dal):
        """Test executing invalid SQL"""
        with pytest.raises(sqlite3.OperationalError):
            test_dal.execute_query("INVALID SQL QUERY")
