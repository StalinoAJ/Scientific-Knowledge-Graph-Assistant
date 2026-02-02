"""
Database connection and utilities for Neo4j graph database.
"""

import os
from typing import Optional, List, Dict, Any
from neo4j import GraphDatabase, Session
from contextlib import contextmanager


class Neo4jConnection:
    """Neo4j database connection manager."""
    
    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None
    ):
        """Initialize Neo4j connection.
        
        Args:
            uri: Neo4j connection URI (default: from env NEO4J_URI)
            user: Neo4j username (default: from env NEO4J_USER)
            password: Neo4j password (default: from env NEO4J_PASSWORD)
        """
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "scientifickg123")
        
        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password)
        )
        
    def close(self):
        """Close the database connection."""
        if self.driver:
            self.driver.close()
    
    @contextmanager
    def session(self) -> Session:
        """Context manager for database sessions."""
        session = self.driver.session()
        try:
            yield session
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test if database connection is working.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.session() as session:
                result = session.run("RETURN 1 AS num")
                return result.single()["num"] == 1
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def create_constraints(self):
        """Create uniqueness constraints for node IDs."""
        constraints = [
            "CREATE CONSTRAINT paper_id IF NOT EXISTS FOR (p:Paper) REQUIRE p.node_id IS UNIQUE",
            "CREATE CONSTRAINT author_id IF NOT EXISTS FOR (a:Author) REQUIRE a.node_id IS UNIQUE",
            "CREATE CONSTRAINT institution_id IF NOT EXISTS FOR (i:Institution) REQUIRE i.node_id IS UNIQUE",
            "CREATE CONSTRAINT method_id IF NOT EXISTS FOR (m:Method) REQUIRE m.node_id IS UNIQUE",
            "CREATE CONSTRAINT dataset_id IF NOT EXISTS FOR (d:Dataset) REQUIRE d.node_id IS UNIQUE",
            "CREATE CONSTRAINT result_id IF NOT EXISTS FOR (r:Result) REQUIRE r.node_id IS UNIQUE",
        ]
        
        with self.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    print(f"Created constraint: {constraint.split('FOR')[1].split('REQUIRE')[0].strip()}")
                except Exception as e:
                    print(f"Constraint already exists or error: {e}")
    
    def create_indexes(self):
        """Create indexes for efficient querying."""
        indexes = [
            "CREATE INDEX paper_title IF NOT EXISTS FOR (p:Paper) ON (p.title)",
            "CREATE INDEX author_name IF NOT EXISTS FOR (a:Author) ON (a.name)",
            "CREATE INDEX paper_date IF NOT EXISTS FOR (p:Paper) ON (p.publication_date)",
            "CREATE INDEX method_name IF NOT EXISTS FOR (m:Method) ON (m.name)",
            "CREATE INDEX dataset_name IF NOT EXISTS FOR (d:Dataset) ON (d.name)",
        ]
        
        with self.session() as session:
            for index in indexes:
                try:
                    session.run(index)
                    print(f"Created index: {index.split('ON')[1].strip()}")
                except Exception as e:
                    print(f"Index already exists or error: {e}")
    
    def initialize_database(self):
        """Initialize database with constraints and indexes."""
        print("Initializing Neo4j database...")
        self.create_constraints()
        self.create_indexes()
        print("Database initialization complete!")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary with node and relationship counts
        """
        with self.session() as session:
            # Count nodes by type
            node_counts = {}
            for node_type in ["Paper", "Author", "Institution", "Method", "Dataset", "Result"]:
                result = session.run(f"MATCH (n:{node_type}) RETURN count(n) AS count")
                node_counts[node_type] = result.single()["count"]
            
            # Count relationships by type
            rel_result = session.run("MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count")
            rel_counts = {record["type"]: record["count"] for record in rel_result}
            
            return {
                "nodes": node_counts,
                "total_nodes": sum(node_counts.values()),
                "relationships": rel_counts,
                "total_relationships": sum(rel_counts.values())
            }
    
    def clear_database(self, confirm: bool = False):
        """Clear all data from the database.
        
        Args:
            confirm: Must be True to actually clear the database
        """
        if not confirm:
            print("Warning: This will delete all data. Call with confirm=True to proceed.")
            return
        
        with self.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Database cleared!")


# Global connection instance
_db_connection: Optional[Neo4jConnection] = None


def get_db() -> Neo4jConnection:
    """Get or create the global database connection.
    
    Returns:
        Neo4jConnection instance
    """
    global _db_connection
    if _db_connection is None:
        _db_connection = Neo4jConnection()
    return _db_connection


def close_db():
    """Close the global database connection."""
    global _db_connection
    if _db_connection is not None:
        _db_connection.close()
        _db_connection = None
