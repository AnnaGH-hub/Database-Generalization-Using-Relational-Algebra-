"""
Unit tests for Person operations.
"""
import pytest
from database_manager import DatabaseManager, Person
from config import get_connection_string


@pytest.fixture
def db():
    """Create database manager for testing."""
    conn_string = get_connection_string()
    with DatabaseManager(conn_string) as manager:
        yield manager


class TestPersonOperations:
    """Test suite for Person CRUD operations."""
    
    def test_create_person(self, db):
        """Test creating a new person."""
        person = Person(
            person_id=None,
            name="Test Person",
            address="123 Test St",
            phone="555-0000",
            email="test@example.com",
            person_type="Customer"
        )
        
        person_id = db.create_person(person)
        assert person_id is not None
        assert isinstance(person_id, int)
        
        # Cleanup
        db.delete_person(person_id)
    
    def test_get_person(self, db):
        """Test retrieving a person by ID."""
        # Create person
        person = Person(
            person_id=None,
            name="Get Test",
            address="456 Get St",
            phone="555-0001",
            email="get@example.com",
            person_type="Employee"
        )
        person_id = db.create_person(person)
        
        # Retrieve person
        retrieved = db.get_person(person_id)
        assert retrieved is not None
        assert retrieved.name == "Get Test"
        assert retrieved.email == "get@example.com"
        
        # Cleanup
        db.delete_person(person_id)
    
    def test_update_person(self, db):
        """Test updating person attributes."""
        # Create person
        person = Person(
            person_id=None,
            name="Update Test",
            address="789 Update Ave",
            phone="555-0002",
            email="update@example.com",
            person_type="Customer"
        )
        person_id = db.create_person(person)
        
        # Update
        success = db.update_person(person_id, name="Updated Name", phone="555-9999")
        assert success is True
        
        # Verify
        updated = db.get_person(person_id)
        assert updated.name == "Updated Name"
        assert updated.phone == "555-9999"
        
        # Cleanup
        db.delete_person(person_id)
    
    def test_delete_person(self, db):
        """Test deleting a person."""
        person = Person(
            person_id=None,
            name="Delete Test",
            address="321 Delete Rd",
            phone="555-0003",
            email="delete@example.com",
            person_type="Customer"
        )
        person_id = db.create_person(person)
        
        # Delete
        success = db.delete_person(person_id)
        assert success is True
        
        # Verify deleted
        deleted = db.get_person(person_id)
        assert deleted is None
    
    def test_get_all_persons(self, db):
        """Test retrieving all persons."""
        persons = db.get_all_persons()
        assert isinstance(persons, list)
        assert len(persons) > 0
