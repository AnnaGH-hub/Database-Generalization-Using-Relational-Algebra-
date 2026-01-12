import psycopg2
from psycopg2 import sql, extras
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, date
import json


@dataclass
class Person:
    """Person entity (supertype)"""
    person_id: Optional[int]
    name: str
    address: Optional[str]
    phone: Optional[str]
    email: str
    person_type: str
    created_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Customer:
    """Customer entity (subtype of Person)"""
    customer_id: Optional[int]
    person_id: int
    loyalty_points: int = 0
    registration_date: Optional[date] = None
    customer_tier: str = 'Bronze'

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Employee:
    """Employee entity (subtype of Person)"""
    employee_id: Optional[int]
    person_id: int
    salary: float
    department: str
    hire_date: Optional[date] = None
    position: Optional[str] = None
    manager_id: Optional[int] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class DatabaseManager:
    """
    Manager class for database operations with generalized schema.
    
    This class provides a comprehensive interface for managing persons,
    customers, and employees in a generalized database schema following
    the ISA (Is-A) relationship pattern.
    
    Architecture:
        Person (supertype) ← Customer (subtype)
                          ← Employee (subtype)
    
    Example:
        with DatabaseManager(conn_string) as db:
            person = Person(None, "John Doe", "123 St", "555-0100", 
                          "john@email.com", "Customer")
            customer = Customer(None, 0, 500, None, "Silver")
            person_id, customer_id = db.create_customer(person, customer)
    """

    def __init__(self, connection_string: str):
        """
        Initialize database manager.
        
        Args:
            connection_string: PostgreSQL connection string
                             e.g., "dbname=mydb user=postgres password=pass host=localhost"
        """
        self.conn = psycopg2.connect(connection_string)
        self.conn.autocommit = False

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic commit/rollback"""
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()

    # ========================================================================
    # PERSON OPERATIONS
    # ========================================================================

    def create_person(self, person: Person) -> int:
        """
        Create a new person and return PersonID.
        
        Args:
            person: Person object with details
            
        Returns:
            PersonID of created person
            
        Raises:
            psycopg2.IntegrityError: If email already exists
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Person (Name, Address, Phone, Email, PersonType)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING PersonID
            """, (person.name, person.address, person.phone, 
                  person.email, person.person_type))
            person_id = cur.fetchone()[0]
            self.conn.commit()
            return person_id

    def get_person(self, person_id: int) -> Optional[Person]:
        """
        Retrieve person by ID.
        
        Args:
            person_id: PersonID to retrieve
            
        Returns:
            Person object or None if not found
        """
        with self.conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM Person WHERE PersonID = %s", (person_id,))
            row = cur.fetchone()
            if row:
                return Person(**dict(row))
            return None

    def get_all_persons(self) -> List[Person]:
        """
        Retrieve all persons.
        
        Returns:
            List of Person objects ordered by name
        """
        with self.conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM Person ORDER BY Name")
            return [Person(**dict(row)) for row in cur.fetchall()]

    def update_person(self, person_id: int, **kwargs) -> bool:
        """
        Update person attributes.
        
        Args:
            person_id: PersonID to update
            **kwargs: Attributes to update (name, address, phone, email, person_type)
            
        Returns:
            True if updated, False if person not found
        """
        if not kwargs:
            return False

        set_clause = sql.SQL(', ').join(
            sql.Composed([sql.Identifier(k), sql.SQL(" = %s")])
            for k in kwargs.keys()
        )
        query = sql.SQL("UPDATE Person SET {} WHERE PersonID = %s").format(set_clause)

        with self.conn.cursor() as cur:
            cur.execute(query, list(kwargs.values()) + [person_id])
            self.conn.commit()
            return cur.rowcount > 0

    def delete_person(self, person_id: int) -> bool:
        """
        Delete person (cascades to Customer/Employee).
        
        Args:
            person_id: PersonID to delete
            
        Returns:
            True if deleted, False if not found
        """
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM Person WHERE PersonID = %s", (person_id,))
            self.conn.commit()
            return cur.rowcount > 0

    # ========================================================================
    # CUSTOMER OPERATIONS
    # ========================================================================

    def create_customer(self, person: Person, customer: Customer) -> Tuple[int, int]:
        """
        Create a new customer with person information.
        
        Args:
            person: Person details
            customer: Customer-specific details
            
        Returns:
            Tuple of (person_id, customer_id)
            
        Raises:
            Exception: If creation fails (rolled back automatically)
        """
        try:
            # Create person first
            person_id = self.create_person(person)
            
            # Create customer
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO Customer (PersonID, LoyaltyPoints, CustomerTier)
                    VALUES (%s, %s, %s)
                    RETURNING CustomerID
                """, (person_id, customer.loyalty_points, customer.customer_tier))
                customer_id = cur.fetchone()[0]
                self.conn.commit()
                return person_id, customer_id
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_customer_complete(self, customer_id: int) -> Optional[Dict]:
        """
        Retrieve complete customer information using join.
        
        Relational Algebra: Person ⋈[PersonID] Customer
        
        Args:
            customer_id: CustomerID to retrieve
            
        Returns:
            Dictionary with combined Person and Customer data, or None
        """
        with self.conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    p.PersonID, p.Name, p.Address, p.Phone, p.Email,
                    c.CustomerID, c.LoyaltyPoints, c.CustomerTier, c.RegistrationDate
                FROM Person p
                INNER JOIN Customer c ON p.PersonID = c.PersonID
                WHERE c.CustomerID = %s
            """, (customer_id,))
            result = cur.fetchone()
            return dict(result) if result else None

    def get_all_customers(self) -> List[Dict]:
        """
        Retrieve all customers with complete information.
        
        Returns:
            List of dictionaries with customer data
        """
        with self.conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM v_customer_complete ORDER BY Name")
            return [dict(row) for row in cur.fetchall()]

    def get_customers_by_tier(self, tier: str) -> List[Dict]:
        """
        Retrieve customers by tier.
        
        Relational Algebra: σ[CustomerTier=tier](Person ⋈ Customer)
        
        Args:
            tier: Customer tier (Bronze, Silver, Gold, Platinum)
            
        Returns:
            List of customers in specified tier, ordered by loyalty points
        """
        with self.conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM v_customer_complete
                WHERE CustomerTier = %s
                ORDER BY LoyaltyPoints DESC
            """, (tier,))
            return [dict(row) for row in cur.fetchall()]

    def update_loyalty_points(self, customer_id: int, points: int) -> bool:
        """
        Update customer loyalty points (add to existing).
        
        Args:
            customer_id: CustomerID to update
            points: Points to add (can be negative)
            
        Returns:
            True if updated, False if customer not found
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE Customer
                SET LoyaltyPoints = LoyaltyPoints + %s
                WHERE CustomerID = %s
            """, (points, customer_id))
            self.conn.commit()
            return cur.rowcount > 0

    # ========================================================================
    # EMPLOYEE OPERATIONS
    # ========================================================================

    def create_employee(self, person: Person, employee: Employee) -> Tuple[int, int]:
        """
        Create a new employee with person information.
        
        Args:
            person: Person details
            employee: Employee-specific details
            
        Returns:
            Tuple of (person_id, employee_id)
        """
        try:
            # Create person first
            person_id = self.create_person(person)
            
            # Create employee
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO Employee 
                    (PersonID, Salary, Department, Position, ManagerID)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING EmployeeID
                """, (person_id, employee.salary, employee.department,
                      employee.position, employee.manager_id))
                employee_id = cur.fetchone()[0]
                self.conn.commit()
                return person_id, employee_id
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_employee_complete(self, employee_id: int) -> Optional[Dict]:
        """
        Retrieve complete employee information.
        
        Args:
            employee_id: EmployeeID to retrieve
            
        Returns:
            Dictionary with combined Person and Employee data, or None
        """
        with self.conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM v_employee_complete
                WHERE EmployeeID = %s
            """, (employee_id,))
            result = cur.fetchone()
            return dict(result) if result else None

    def get_employees_by_department(self, department: str) -> List[Dict]:
        """
        Retrieve employees by department.
        
        Relational Algebra: σ[Department=dept](Person ⋈ Employee)
        
        Args:
            department: Department name
            
        Returns:
            List of employees in specified department
        """
        with self.conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM v_employee_complete
                WHERE Department = %s
                ORDER BY Name
            """, (department,))
            return [dict(row) for row in cur.fetchall()]

    def get_department_statistics(self) -> List[Dict]:
        """
        Get salary statistics by department.
        
        Relational Algebra: γ[Department; AVG(Salary), COUNT(*), ...](Employee)
        
        Returns:
            List of department statistics
        """
        with self.conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    Department,
                    COUNT(*) AS EmployeeCount,
                    AVG(Salary) AS AvgSalary,
                    MIN(Salary) AS MinSalary,
                    MAX(Salary) AS MaxSalary,
                    SUM(Salary) AS TotalSalary
                FROM Employee
                GROUP BY Department
                ORDER BY AvgSalary DESC
            """)
            return [dict(row) for row in cur.fetchall()]

    # ========================================================================
    # RELATIONAL ALGEBRA DEMONSTRATIONS
    # ========================================================================

    def demonstrate_union(self) -> List[Dict]:
        """
        Demonstrate UNION operation: all contact information.
        
        Relational Algebra:
        π[Name,Phone,Email](Person ⋈ Customer) ∪ π[Name,Phone,Email](Person ⋈ Employee)
        
        Returns:
            List of unique contact information from both customers and employees
        """
        with self.conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT DISTINCT p.Name, p.Phone, p.Email, 'Customer' AS Type
                FROM Person p
                INNER JOIN Customer c ON p.PersonID = c.PersonID
                UNION
                SELECT DISTINCT p.Name, p.Phone, p.Email, 'Employee' AS Type
                FROM Person p
                INNER JOIN Employee e ON p.PersonID = e.PersonID
                ORDER BY Name
            """)
            return [dict(row) for row in cur.fetchall()]

    def demonstrate_intersection(self) -> List[Dict]:
        """
        Demonstrate INTERSECTION: persons who are both customers and employees.
        
        Relational Algebra:
        π[PersonID](Customer) ∩ π[PersonID](Employee)
        
        Returns:
            List of persons who have both customer and employee roles
        """
        with self.conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT p.*, c.LoyaltyPoints, e.Department
                FROM Person p
                INNER JOIN Customer c ON p.PersonID = c.PersonID
                INNER JOIN Employee e ON p.PersonID = e.PersonID
            """)
            return [dict(row) for row in cur.fetchall()]

    def demonstrate_difference(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Demonstrate SET DIFFERENCE: customers only and employees only.
        
        Relational Algebra:
        Customers Only: π[PersonID](Customer) - π[PersonID](Employee)
        Employees Only: π[PersonID](Employee) - π[PersonID](Customer)
        
        Returns:
            Tuple of (customers_only, employees_only)
        """
        with self.conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            # Customers only
            cur.execute("""
                SELECT p.*, c.LoyaltyPoints
                FROM Person p
                INNER JOIN Customer c ON p.PersonID = c.PersonID
                WHERE p.PersonID NOT IN (SELECT PersonID FROM Employee)
            """)
            customers_only = [dict(row) for row in cur.fetchall()]
            
            # Employees only
            cur.execute("""
                SELECT p.*, e.Department, e.Salary
                FROM Person p
                INNER JOIN Employee e ON p.PersonID = e.PersonID
                WHERE p.PersonID NOT IN (SELECT PersonID FROM Customer)
            """)
            employees_only = [dict(row) for row in cur.fetchall()]
            
            return customers_only, employees_only

    def demonstrate_projection(self) -> List[str]:
        """
        Demonstrate PROJECTION: unique departments.
        
        Relational Algebra: π[Department](Employee)
        
        Returns:
            List of unique department names
        """
        with self.conn.cursor() as cur:
            cur.execute("SELECT DISTINCT Department FROM Employee ORDER BY Department")
            return [row[0] for row in cur.fetchall()]

    def demonstrate_selection(self, min_loyalty: int = 1000) -> List[Dict]:
        """
        Demonstrate SELECTION: high-value customers.
        
        Relational Algebra: σ[LoyaltyPoints >= min](Person ⋈ Customer)
        
        Args:
            min_loyalty: Minimum loyalty points threshold
            
        Returns:
            List of customers with loyalty points >= min_loyalty
        """
        with self.conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT p.Name, p.Email, c.LoyaltyPoints, c.CustomerTier
                FROM Person p
                INNER JOIN Customer c ON p.PersonID = c.PersonID
                WHERE c.LoyaltyPoints >= %s
                ORDER BY c.LoyaltyPoints DESC
            """, (min_loyalty,))
            return [dict(row) for row in cur.fetchall()]
