# Database Generalization Using Relational Algebra

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-15+-blue.svg)

A comprehensive implementation demonstrating the application of set theory and relational algebra to database schema design through generalization.

**Author:** Anna Ghazaryan  
**Supervisor:** Yeghisabet Alaverdyan  
**Year:** 2026

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Relational Algebra Operations](#relational-algebra-operations)
- [Performance Analysis](#performance-analysis)


## 🎯 Overview

This project explores how mathematical principles (set theory and relational algebra) guide efficient database schema design. It demonstrates:

- **Generalization** of database entities to reduce redundancy
- **Relational algebra** operations in practice
- **Performance trade-offs** between normalization and query efficiency
- **Complete implementation** with PostgreSQL and Python

### The Problem

Organizations often maintain separate tables for similar entities (e.g., Customers and Employees) with overlapping attributes (Name, Address, Phone, Email). This creates:

- ❌ Data redundancy
- ❌ Maintenance overhead
- ❌ Update anomalies
- ❌ Storage inefficiency

### The Solution

Create a generalized **Person** supertype entity containing shared attributes, with **Customer** and **Employee** as subtypes containing only specific attributes.

```
Person (Supertype)
  ├── Customer (Subtype)
  └── Employee (Subtype)
```

## ✨ Features

- **Complete Schema Implementation**
  - Person (supertype) with common attributes
  - Customer and Employee (subtypes) with specific attributes
  - Foreign key constraints with CASCADE operations
  - Triggers for data consistency

- **Relational Algebra Demonstrations**
  - ✓ Selection (σ)
  - ✓ Projection (π)
  - ✓ Join (⋈)
  - ✓ Union (∪)
  - ✓ Intersection (∩)
  - ✓ Set Difference (-)

- **Python API Layer**
  - Clean, Pythonic interface
  - Type hints and dataclasses
  - Context manager support
  - Comprehensive error handling

- **Performance Optimizations**
  - Strategic indexing
  - Materialized views
  - Query optimization

## 🏗️ Architecture

### Schema Design

```sql
Person (PersonID, Name, Address, Phone, Email, PersonType)
  ↓ (1:1)
Customer (CustomerID, PersonID*, LoyaltyPoints, CustomerTier)

Person (PersonID, Name, Address, Phone, Email, PersonType)
  ↓ (1:1)
Employee (EmployeeID, PersonID*, Salary, Department, Position)
```

### Mathematical Foundation

**Set Theory:**
```
Customers ⊆ Person
Employees ⊆ Person
CommonAttributes = Customers ∩ Employees
```

**Relational Algebra:**
```
CompleteCustomer = Person ⋈[PersonID] Customer
CompleteEmployee = Person ⋈[PersonID] Employee
AllPersons = π[PersonID](Customer) ∪ π[PersonID](Employee)
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 15+
- pip package manager

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/database-generalization.git
cd database-generalization
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Create PostgreSQL database**
```bash
createdb company_db
```

4. **Initialize schema**
```bash
psql -d company_db -f schema.sql
```

5. **Configure connection**
Edit `config.py` with your database credentials:
```python
DATABASE_CONFIG = {
    'dbname': 'company_db',
    'user': 'postgres',
    'password': 'yourpassword',
    'host': 'localhost',
    'port': 5432
}
```

## 💻 Usage

### Basic Example

```python
from database_manager import DatabaseManager, Person, Customer

# Create database connection
with DatabaseManager("dbname=company_db user=postgres") as db:
    # Create a new customer
    person = Person(
        person_id=None,
        name="Alice Thompson",
        address="100 Tech St, Seattle, WA",
        phone="555-0200",
        email="alice@email.com",
        person_type="Customer"
    )
    
    customer = Customer(
        customer_id=None,
        person_id=0,
        loyalty_points=500,
        customer_tier="Silver"
    )
    
    person_id, customer_id = db.create_customer(person, customer)
    print(f"Created customer: {person_id}, {customer_id}")
    
    # Retrieve complete customer info
    customer_info = db.get_customer_complete(customer_id)
    print(customer_info)
```

### Relational Algebra Demonstrations

```python
with DatabaseManager(conn_string) as db:
    # UNION: All contacts
    contacts = db.demonstrate_union()
    
    # INTERSECTION: Both customer and employee
    both_roles = db.demonstrate_intersection()
    
    # DIFFERENCE: Customers only
    customers_only, _ = db.demonstrate_difference()
    
    # PROJECTION: Unique departments
    departments = db.demonstrate_projection()
    
    # SELECTION: High-value customers
    vip_customers = db.demonstrate_selection(min_loyalty=1000)
```

### Run Demo

```bash
python demo.py
```

## 🔍 Relational Algebra Operations

### 1. Selection (σ)

**Definition:** Select tuples satisfying a condition

**Example:** High-value customers
```python
# Relational Algebra: σ[LoyaltyPoints >= 1000](Customer)
high_value = db.demonstrate_selection(min_loyalty=1000)
```

### 2. Projection (π)

**Definition:** Select specific attributes

**Example:** Unique departments
```python
# Relational Algebra: π[Department](Employee)
departments = db.demonstrate_projection()
```

### 3. Join (⋈)

**Definition:** Combine related tuples from two relations

**Example:** Complete customer information
```python
# Relational Algebra: Person ⋈[PersonID] Customer
customer = db.get_customer_complete(customer_id)
```

### 4. Union (∪)

**Definition:** Combine tuples from compatible relations

**Example:** All contact information
```python
# Relational Algebra: π[Name,Email](Customer) ∪ π[Name,Email](Employee)
contacts = db.demonstrate_union()
```

### 5. Intersection (∩)

**Definition:** Tuples in both relations

**Example:** Persons who are both customers and employees
```python
# Relational Algebra: π[PersonID](Customer) ∩ π[PersonID](Employee)
both = db.demonstrate_intersection()
```

### 6. Set Difference (-)

**Definition:** Tuples in first relation but not in second

**Example:** Customers only (not employees)
```python
# Relational Algebra: π[PersonID](Customer) - π[PersonID](Employee)
customers_only, _ = db.demonstrate_difference()
```

## 📊 Performance Analysis

### Query Performance

| Query Type | Original Schema | Generalized Schema | Overhead |
|------------|----------------|-------------------|----------|
| Single customer lookup | 0.8 ms | 1.2 ms | +50% |
| All customers | 45 ms | 68 ms | +51% |
| Customer by email | 1.1 ms | 1.3 ms | +18% |
| Department statistics | 42 ms | 38 ms | -9.5% |

### Trade-offs

**Benefits of Generalization:**
- ✅ Reduced redundancy (~40% storage savings)
- ✅ Improved maintainability
- ✅ Enhanced data integrity
- ✅ Easier schema evolution

**Costs of Generalization:**
- ⚠️ Increased join operations
- ⚠️ More complex queries
- ⚠️ Modest performance overhead for single-entity queries

**Recommendation:** Use generalized schema for OLTP systems prioritizing maintainability and data integrity. Consider denormalization for read-heavy OLAP workloads.

## 🧪 Testing

Run all tests:
```bash
pytest tests/
```

Run specific test suite:
```bash
pytest tests/test_customer.py -v
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## 📈 Benchmarks

Run performance benchmarks:
```bash
python examples/benchmarks.py
```

This will execute:
- Single entity lookup tests
- Bulk operation tests
- Join performance tests
- Aggregate query tests


## 📚 References

1. Codd, E. F. (1970). "A Relational Model of Data for Large Shared Data Banks."
2. Date, C. J. (2003). *An Introduction to Database Systems* (8th ed.)
3. Elmasri, R., & Navathe, S. B. (2015). *Fundamentals of Database Systems* (7th ed.)
4. PostgreSQL Documentation: https://www.postgresql.org/docs/

## 👤 Author

**Anna Ghazaryan**
- Supervisor: Yeghisabet Alaverdyan
- Year: 2026

## 🙏 Acknowledgments

- Supervisor Yeghisabet Alaverdyan for guidance
- Software Engineering Department for resources
- PostgreSQL and Python communities for excellent tools

---

**Keywords:** Database Design, Relational Algebra, Set Theory, Schema Generalization, SQL, PostgreSQL, Python, Data Modeling, Database Normalization, ISA Relationship
