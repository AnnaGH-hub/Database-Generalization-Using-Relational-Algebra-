"""
Unit tests for relational algebra operations.
"""
import pytest
from database_manager import DatabaseManager
from config import get_connection_string


@pytest.fixture
def db():
    """Create database manager for testing."""
    conn_string = get_connection_string()
    with DatabaseManager(conn_string) as manager:
        yield manager


class TestRelationalAlgebraOperations:
    """Test suite for relational algebra demonstrations."""
    
    def test_union_operation(self, db):
        """Test UNION: All contacts from customers and employees."""
        contacts = db.demonstrate_union()
        assert isinstance(contacts, list)
        assert len(contacts) > 0
        
        # Verify structure
        if contacts:
            assert 'name' in contacts[0]
            assert 'email' in contacts[0]
            assert 'type' in contacts[0]
    
    def test_intersection_operation(self, db):
        """Test INTERSECTION: Persons who are both customers and employees."""
        both = db.demonstrate_intersection()
        assert isinstance(both, list)
        
        # Verify structure if any results
        if both:
            assert 'name' in both[0]
            assert 'loyaltypoints' in both[0]
            assert 'department' in both[0]
    
    def test_difference_operation(self, db):
        """Test SET DIFFERENCE: Customers only and employees only."""
        customers_only, employees_only = db.demonstrate_difference()
        
        assert isinstance(customers_only, list)
        assert isinstance(employees_only, list)
        
        # Verify no overlap
        customer_ids = {c['personid'] for c in customers_only}
        employee_ids = {e['personid'] for e in employees_only}
        assert len(customer_ids.intersection(employee_ids)) == 0
    
    def test_projection_operation(self, db):
        """Test PROJECTION: Unique departments."""
        departments = db.demonstrate_projection()
        assert isinstance(departments, list)
        assert len(departments) > 0
        
        # Verify uniqueness
        assert len(departments) == len(set(departments))
    
    def test_selection_operation(self, db):
        """Test SELECTION: High-value customers."""
        high_value = db.demonstrate_selection(min_loyalty=1000)
        assert isinstance(high_value, list)
        
        # Verify all meet criteria
        for customer in high_value:
            assert customer['loyaltypoints'] >= 1000
