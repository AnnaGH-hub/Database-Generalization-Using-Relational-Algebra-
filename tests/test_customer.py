"""
Unit tests for Customer operations.
"""
import pytest
from database_manager import DatabaseManager, Person, Customer
from config import get_connection_string


@pytest.fixture
def db():
    """Create database manager for testing."""
    conn_string = get_connection_string()
    with DatabaseManager(conn_string) as manager:
        yield manager


class TestCustomerOperations:
    """Test suite for Customer operations."""
    
    def test_create_customer(self, db):
        """Test creating a customer with person info."""
        person = Person(
            person_id=None,
            name="Customer Test",
            address="100 Customer Ln",
            phone="555-1000",
            email="customer@test.com",
            person_type="Customer"
        )
        customer = Customer(
            customer_id=None,
            person_id=0,
            loyalty_points=100,
            customer_tier="Bronze"
        )
        
        person_id, customer_id = db.create_customer(person, customer)
        assert person_id is not None
        assert customer_id is not None
        
        # Cleanup
        db.delete_person(person_id)
    
    def test_get_customer_complete(self, db):
        """Test retrieving complete customer information."""
        # Create customer
        person = Person(
            person_id=None,
            name="Complete Test",
            address="200 Complete Ave",
            phone="555-2000",
            email="complete@test.com",
            person_type="Customer"
        )
        customer = Customer(
            customer_id=None,
            person_id=0,
            loyalty_points=500,
            customer_tier="Silver"
        )
        person_id, customer_id = db.create_customer(person, customer)
        
        # Retrieve
        result = db.get_customer_complete(customer_id)
        assert result is not None
        assert result['name'] == "Complete Test"
        assert result['loyaltypoints'] == 500
        assert result['customertier'] == "Silver"
        
        # Cleanup
        db.delete_person(person_id)
    
    def test_update_loyalty_points(self, db):
        """Test updating loyalty points."""
        # Create customer
        person = Person(
            person_id=None,
            name="Loyalty Test",
            address="300 Loyalty Rd",
            phone="555-3000",
            email="loyalty@test.com",
            person_type="Customer"
        )
        customer = Customer(
            customer_id=None,
            person_id=0,
            loyalty_points=100,
            customer_tier="Bronze"
        )
        person_id, customer_id = db.create_customer(person, customer)
        
        # Update loyalty points
        success = db.update_loyalty_points(customer_id, 50)
        assert success is True
        
        # Verify
        result = db.get_customer_complete(customer_id)
        assert result['loyaltypoints'] == 150
        
        # Cleanup
        db.delete_person(person_id)
    
    def test_get_customers_by_tier(self, db):
        """Test retrieving customers by tier."""
        customers = db.get_customers_by_tier("Gold")
        assert isinstance(customers, list)
    
    def test_cascade_delete(self, db):
        """Test that deleting person cascades to customer."""
        # Create customer
        person = Person(
            person_id=None,
            name="Cascade Test",
            address="400 Cascade St",
            phone="555-4000",
            email="cascade@test.com",
            person_type="Customer"
        )
        customer = Customer(
            customer_id=None,
            person_id=0,
            loyalty_points=200,
            customer_tier="Silver"
        )
        person_id, customer_id = db.create_customer(person, customer)
        
        # Delete person (should cascade to customer)
        db.delete_person(person_id)
        
        # Verify customer is also deleted
        result = db.get_customer_complete(customer_id)
        assert result is None

