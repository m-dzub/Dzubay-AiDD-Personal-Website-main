import sqlite3
from typing import List, Tuple, Any, Optional


class DAL:
    """Data Access Layer for SQLite database operations"""
    
    def __init__(self, db_path: str = 'database.db'):
        """
        Initialize the Data Access Layer
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Create and return a database connection
        
        Returns:
            sqlite3.Connection: Database connection object
        """
        conn = sqlite3.Connection(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """
        Execute a SELECT query and return results
        
        Args:
            query: SQL SELECT query string
            params: Query parameters tuple
            
        Returns:
            List of rows from the query result
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            return results
        finally:
            conn.close()
    
    def execute_non_query(self, query: str, params: Tuple = ()) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            Number of affected rows
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def execute_scalar(self, query: str, params: Tuple = ()) -> Any:
        """
        Execute a query and return a single value
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            Single value from the query result
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            conn.close()
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """
        Execute a query multiple times with different parameters
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Total number of affected rows
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def create_table(self, table_name: str, schema: str) -> None:
        """
        Create a new table if it doesn't exist
        
        Args:
            table_name: Name of the table to create
            schema: Column definitions for the table
        """
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})"
        self.execute_non_query(query)
    
    def drop_table(self, table_name: str) -> None:
        """
        Drop a table if it exists
        
        Args:
            table_name: Name of the table to drop
        """
        query = f"DROP TABLE IF EXISTS {table_name}"
        self.execute_non_query(query)
    
    def insert(self, table_name: str, data: dict) -> int:
        """
        Insert a row into a table
        
        Args:
            table_name: Name of the table
            data: Dictionary of column names and values
            
        Returns:
            ID of the inserted row
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def update(self, table_name: str, data: dict, where_clause: str, where_params: Tuple = ()) -> int:
        """
        Update rows in a table
        
        Args:
            table_name: Name of the table
            data: Dictionary of column names and new values
            where_clause: WHERE clause (without 'WHERE' keyword)
            where_params: Parameters for the WHERE clause
            
        Returns:
            Number of affected rows
        """
        set_clause = ', '.join([f"{col} = ?" for col in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        params = tuple(data.values()) + where_params
        return self.execute_non_query(query, params)
    
    def delete(self, table_name: str, where_clause: str, where_params: Tuple = ()) -> int:
        """
        Delete rows from a table
        
        Args:
            table_name: Name of the table
            where_clause: WHERE clause (without 'WHERE' keyword)
            where_params: Parameters for the WHERE clause
            
        Returns:
            Number of affected rows
        """
        query = f"DELETE FROM {table_name} WHERE {where_clause}"
        return self.execute_non_query(query, where_params)
    
    def select_all(self, table_name: str, order_by: Optional[str] = None) -> List[sqlite3.Row]:
        """
        Select all rows from a table
        
        Args:
            table_name: Name of the table
            order_by: Optional ORDER BY clause
            
        Returns:
            List of all rows
        """
        query = f"SELECT * FROM {table_name}"
        if order_by:
            query += f" ORDER BY {order_by}"
        return self.execute_query(query)
    
    def select_by_id(self, table_name: str, id_value: int, id_column: str = 'id') -> Optional[sqlite3.Row]:
        """
        Select a single row by ID
        
        Args:
            table_name: Name of the table
            id_value: Value of the ID
            id_column: Name of the ID column (default: 'id')
            
        Returns:
            Single row or None if not found
        """
        query = f"SELECT * FROM {table_name} WHERE {id_column} = ?"
        results = self.execute_query(query, (id_value,))
        return results[0] if results else None
